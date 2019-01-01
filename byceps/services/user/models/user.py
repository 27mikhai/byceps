"""
byceps.services.user.models.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from flask import g
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.utils import cached_property

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user_avatar.models import AvatarSelection

from ..transfer.models import User as UserDTO


GUEST_USER_ID = UUID('00000000-0000-0000-0000-000000000000')


class AnonymousUser:

    id = GUEST_USER_ID
    enabled = False

    @property
    def avatar(self) -> None:
        return None

    @property
    def avatar_url(self) -> None:
        return None

    @property
    def is_orga(self) -> bool:
        return False

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class User(db.Model):
    """A user."""
    __tablename__ = 'users'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    screen_name = db.Column(db.Unicode(40), unique=True, nullable=False)
    email_address = db.Column(db.Unicode(80), unique=True, nullable=False)
    email_address_verified = db.Column(db.Boolean, default=False, nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    suspended = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    legacy_id = db.Column(db.Integer)

    avatar = association_proxy('avatar_selection', 'avatar',
                               creator=lambda avatar:
                                    AvatarSelection(None, avatar.id))

    def __init__(self, screen_name: str, email_address: str) -> None:
        self.screen_name = screen_name
        self.email_address = email_address

    @property
    def avatar_url(self) -> Optional[str]:
        avatar = self.avatar
        return avatar.url if (avatar is not None) else None

    @cached_property
    def is_orga(self) -> bool:
        party_id = getattr(g, 'party_id', None)

        if party_id is None:
            return False

        from ...orga_team import service as orga_team_service
        return orga_team_service.is_orga_for_party(self.id, party_id)

    def to_dto(self, *, include_avatar=False):
        avatar_url = self.avatar_url if include_avatar else None
        is_orga = False  # Information is deliberately not obtained here.

        return UserDTO(
            self.id,
            self.screen_name,
            self.suspended,
            self.deleted,
            avatar_url,
            is_orga,
        )

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)

    def __hash__(self) -> int:
        if self.id is None:
            raise ValueError('User instance is unhashable because its id is None.')

        return hash(self.id)

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('screen_name') \
            .build()
