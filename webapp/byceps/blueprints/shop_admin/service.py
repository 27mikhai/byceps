# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import Counter

from ...database import db

from ..party.models import Party
from ..shop.models.article import Article
from ..shop.models.order import OrderItem, PaymentState


def get_parties_with_article_counts():
    """Yield (party, article count) pairs."""
    parties = Party.query.all()

    article_counts_by_party_id = _get_article_counts_by_party_id()

    for party in parties:
        article_count = article_counts_by_party_id.get(party.id, 0)
        yield party, article_count


def _get_article_counts_by_party_id():
    return dict(db.session \
        .query(
            Article.party_id,
            db.func.count(Article.party_id)
        ) \
        .group_by(Article.party_id) \
        .all())


def count_ordered_articles(article):
    """Count how often the article has been ordered, grouped by the
    order's payment state.
    """
    order_items = OrderItem.query \
        .options(
            db.joinedload('order'),
            db.joinedload('article'),
        ) \
        .filter_by(article=article) \
        .all()

    # Ensure every payment state is present in the resulting dictionary,
    # even if no orders of the corresponding payment state exist for the
    # article.
    counter = Counter({state: 0 for state in PaymentState})

    for order_item in order_items:
        counter[order_item.order.payment_state] += order_item.quantity

    return dict(counter)
