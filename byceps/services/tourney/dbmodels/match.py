"""
byceps.services.tourney.dbmodels.match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....database import db, generate_uuid


class Match(db.Model):
    """A match between two opponents."""

    __tablename__ = 'tourney_matches'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
