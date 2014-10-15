# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import request

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..shop.models import Article, Order, PaymentState
from ..shop.signals import order_canceled, order_marked_as_paid
from ..party.models import Party

from .authorization import ShopPermission


blueprint = create_blueprint('shop_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/articles')
@permission_required(ShopPermission.list_articles)
@templated
def article_index():
    """List parties to choose from."""
    parties = Party.query.all()
    return {'parties': parties}


@blueprint.route('/parties/<party_id>/articles', defaults={'page': 1})
@blueprint.route('/parties/<party_id>/articles/pages/<int:page>')
@permission_required(ShopPermission.list_articles)
@templated
def article_index_for_party(party_id, page):
    """List articles for that party."""
    party = Party.query.get_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)
    query = Article.query \
        .for_party(party) \
        .order_by(Article.description)

    articles = query.paginate(page, per_page)

    return {
        'party': party,
        'articles': articles,
    }


@blueprint.route('/orders')
@permission_required(ShopPermission.list_orders)
@templated
def order_index():
    """List orders."""
    parties = Party.query.all()
    return {'parties': parties}


@blueprint.route('/parties/<party_id>/orders', defaults={'page': 1})
@blueprint.route('/parties/<party_id>/orders/pages/<int:page>')
@permission_required(ShopPermission.list_orders)
@templated
def order_index_for_party(party_id, page):
    """List orders for that party."""
    party = Party.query.get_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)
    query = Order.query \
        .for_party(party) \
        .order_by(Order.created_at.desc())

    only = request.args.get('only', type=PaymentState.__getitem__)
    if only is not None:
        query = query.filter_by(_payment_state=only.name)

    orders = query.paginate(page, per_page)

    return {
        'party': party,
        'PaymentState': PaymentState,
        'only': only,
        'orders': orders,
    }

@blueprint.route('/orders/<id>')
@permission_required(ShopPermission.list_orders)
@templated
def order_view(id):
    """Show a single order."""
    order = Order.query.get_or_404(id)
    return {
        'order': order,
        'PaymentState': PaymentState,
    }


@blueprint.route('/orders/<id>/mark_as_canceled', methods=['POST'])
@permission_required(ShopPermission.update_orders)
def order_mark_as_canceled(id):
    """Set the payment status of a single order to 'canceled'."""
    order = Order.query.get_or_404(id)
    order.mark_as_canceled()

    # Make the reserved quantity of articles available again.
    for item in order.items:
        item.article.quantity += item.quantity

    db.session.commit()

    flash_success(
        'Die Bestellung wurde als storniert markiert und die betroffenen '
        'Artikel in den entsprechenden Stückzahlen wieder zur Bestellung '
        'freigegeben.')

    order_canceled.send(None, articles=order.collect_articles())

    return redirect_to('.order_view', id=order.id)


@blueprint.route('/orders/<id>/mark_as_paid', methods=['POST'])
@permission_required(ShopPermission.update_orders)
def order_mark_as_paid(id):
    """Set the payment status of a single order to 'paid'."""
    order = Order.query.get_or_404(id)
    order.mark_as_paid()
    db.session.commit()

    flash_success('Die Bestellung wurde als bezahlt markiert.')

    order_mark_as_paid.send(None, articles=order.collect_articles())

    return redirect_to('.order_view', id=order.id)
