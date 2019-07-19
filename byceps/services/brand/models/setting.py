"""
byceps.services.brand.models.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder


class Setting(db.Model):
    """A brand-specific setting."""
    __tablename__ = 'brand_settings'

    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    name = db.Column(db.UnicodeText, primary_key=True)
    value = db.Column(db.UnicodeText)

    def __init__(self, brand_id: BrandID, name: str, value: str) -> None:
        self.brand_id = brand_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('brand_id') \
            .add_with_lookup('name') \
            .add_with_lookup('value') \
            .build()
