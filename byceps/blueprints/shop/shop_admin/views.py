"""
byceps.blueprints.shop.shop_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ....services.party import service as party_service
from ....services.shop.article import service as article_service
from ....services.shop.order import action_service as order_action_service, \
    service as order_service
from ....services.shop.order.transfer.models import PaymentState
from ....services.shop.sequence import service as sequence_service
from ....services.shop.shop import service as shop_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import ShopPermission


blueprint = create_blueprint('shop_shop_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopPermission.view)
@templated
def view_for_shop(shop_id):
    """Show the shop."""
    shop = _get_shop_or_404(shop_id)

    party = party_service.find_party(shop.party_id)

    most_recent_article_number = _get_most_recent_article_number(shop.id)
    most_recent_order_number = _get_most_recent_order_number(shop.id)

    article_count = article_service.count_articles_for_shop(shop.id)
    order_counts_by_payment_state = order_service \
        .count_orders_per_payment_state(shop.id)

    order_actions = order_action_service.get_actions(shop.id)

    return {
        'party': party,
        'shop': shop,

        'most_recent_article_number': most_recent_article_number,
        'most_recent_order_number': most_recent_order_number,

        'article_count': article_count,
        'order_counts_by_payment_state': order_counts_by_payment_state,
        'PaymentState': PaymentState,

        'order_actions': order_actions,
    }


def _get_most_recent_article_number(shop_id):
    sequence = sequence_service.find_article_number_sequence(shop_id)
    return sequence_service.format_article_number(sequence)


def _get_most_recent_order_number(shop_id):
    sequence = sequence_service.find_order_number_sequence(shop_id)
    return sequence_service.format_order_number(sequence)


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
