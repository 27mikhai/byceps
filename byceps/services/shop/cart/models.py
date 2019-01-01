"""
byceps.services.shop.cart.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal
from typing import List, Sequence

from ....util.instances import ReprBuilder

from ..article.models.article import Article


class CartItem:
    """An article with a quantity."""

    def __init__(self, article: Article, quantity: int) -> None:
        if quantity < 1:
            raise ValueError('Quantity must be a positive number.')

        self.article = article
        self.quantity = quantity
        self.line_amount = article.price * quantity

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('article', self.article.item_number) \
            .add_with_lookup('quantity') \
            .add_with_lookup('line_amount') \
            .build()


class Cart:
    """A shopping cart."""

    def __init__(self) -> None:
        self._items = []  # type: List[CartItem]

    def add_item(self, article: Article, quantity: int) -> None:
        item = CartItem(article, quantity)
        self._items.append(item)

    def get_items(self) -> Sequence[CartItem]:
        return self._items

    def calculate_total_amount(self) -> Decimal:
        return sum(item.line_amount for item in self._items)

    def is_empty(self) -> bool:
        return not self._items

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_custom('{:d} items'.format(len(self._items))) \
            .build()
