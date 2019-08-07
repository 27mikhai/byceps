"""
byceps.services.shop.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....typing import PartyID
from ....util.instances import ReprBuilder

from .transfer.models import ShopID


class Shop(db.Model):
    """A shop."""
    __tablename__ = 'shops'

    id = db.Column(db.Unicode(40), primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), unique=True, nullable=False)
    closed = db.Column(db.Boolean, default=False, nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, shop_id: ShopID, party_id: PartyID) -> None:
        self.id = shop_id
        self.party_id = party_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .build()
