"""
byceps.services.authentication.session.models.session_token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from uuid import UUID

from .....database import db
from .....typing import UserID


class SessionToken(db.Model):
    """A user's session token."""
    __tablename__ = 'authn_session_tokens'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    token = db.Column(db.Uuid, unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id: UserID, token: UUID, created_at: datetime) -> None:
        self.user_id = user_id
        self.token = token
        self.created_at = created_at
