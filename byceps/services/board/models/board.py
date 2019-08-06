"""
byceps.services.board.models.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder

from ..transfer.models import BoardID


class Board(db.Model):
    """A board."""
    __tablename__ = 'boards'

    id = db.Column(db.UnicodeText, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)
    access_restricted = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, board_id: BoardID, brand_id: BrandID) -> None:
        self.id = board_id
        self.brand_id = brand_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .build()
