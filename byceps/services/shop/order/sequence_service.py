"""
byceps.services.shop.order.sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from sqlalchemy.exc import IntegrityError

from ....database import db

from ..shop.transfer.models import ShopID

from .dbmodels.number_sequence import (
    OrderNumberSequence as DbOrderNumberSequence,
)
from .transfer.number import OrderNumberSequence, OrderNumberSequenceID
from .transfer.number import OrderNumber


class OrderNumberSequenceCreationFailed(Exception):
    pass


def create_order_number_sequence(
    shop_id: ShopID, prefix: str, *, value: Optional[int] = None
) -> OrderNumberSequence:
    """Create an order number sequence."""
    db_sequence = DbOrderNumberSequence(shop_id, prefix, value=value)

    db.session.add(db_sequence)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise OrderNumberSequenceCreationFailed(
            f'Could not create order number sequence with prefix "{prefix}"'
        ) from exc

    return _db_entity_to_order_number_sequence(db_sequence)


def delete_order_number_sequence(sequence_id: OrderNumberSequenceID) -> None:
    """Delete the order number sequence."""
    db.session.query(DbOrderNumberSequence) \
        .filter_by(id=sequence_id) \
        .delete()

    db.session.commit()


def get_order_number_sequence(
    sequence_id: OrderNumberSequenceID,
) -> OrderNumberSequence:
    """Return the order number sequence, or raise an exception."""
    db_sequence = db.session \
        .query(DbOrderNumberSequence) \
        .filter_by(id=sequence_id) \
        .one_or_none()

    if db_sequence is None:
        raise ValueError(f'Unknown order number sequence ID "{sequence_id}"')

    return _db_entity_to_order_number_sequence(db_sequence)


def get_order_number_sequences_for_shop(
    shop_id: ShopID,
) -> list[OrderNumberSequence]:
    """Return the order number sequences defined for that shop."""
    db_sequences = db.session \
        .query(DbOrderNumberSequence) \
        .filter_by(shop_id=shop_id) \
        .all()

    return [
        _db_entity_to_order_number_sequence(db_sequence)
        for db_sequence in db_sequences
    ]


class OrderNumberGenerationFailed(Exception):
    """Indicate that generating a prefixed, sequential order number has
    failed.
    """

    def __init__(self, message: str) -> None:
        self.message = message


def generate_order_number(sequence_id: OrderNumberSequenceID) -> OrderNumber:
    """Generate and reserve an unused, unique order number from this
    sequence.
    """
    db_sequence = db.session \
        .query(DbOrderNumberSequence) \
        .filter_by(id=sequence_id) \
        .with_for_update() \
        .one_or_none()

    if db_sequence is None:
        raise OrderNumberGenerationFailed(
            f'No order number sequence found for ID "{sequence_id}".'
        )

    db_sequence.value = DbOrderNumberSequence.value + 1
    db.session.commit()

    return OrderNumber(f'{db_sequence.prefix}{db_sequence.value:05d}')


def _db_entity_to_order_number_sequence(
    db_sequence: DbOrderNumberSequence,
) -> OrderNumberSequence:
    return OrderNumberSequence(
        id=db_sequence.id,
        shop_id=db_sequence.shop_id,
        prefix=db_sequence.prefix,
        value=db_sequence.value,
    )
