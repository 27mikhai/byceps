"""
byceps.services.authentication.password.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from werkzeug.security import check_password_hash as _check_password_hash, \
    generate_password_hash as _generate_password_hash

from ....database import db
from ....typing import UserID

from ...user import event_service as user_event_service

from ..session import service as session_service

from .models import Credential as DbCredential


PASSWORD_HASH_ITERATIONS = 150000
PASSWORD_HASH_METHOD = 'pbkdf2:sha256:%d' % PASSWORD_HASH_ITERATIONS


def generate_password_hash(password: str) -> str:
    """Generate a salted hash value based on the password."""
    return _generate_password_hash(password, method=PASSWORD_HASH_METHOD)


def create_password_hash(user_id: UserID, password: str) -> None:
    """Create a password-based credential and a session token for the user."""
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = DbCredential(user_id, password_hash, now)
    db.session.add(credential)
    db.session.commit()


def update_password_hash(user_id: UserID, password: str, initiator_id: UserID
                        ) -> None:
    """Update the password hash and set a newly-generated authentication
    token for the user.
    """
    now = datetime.utcnow()

    password_hash = generate_password_hash(password)

    credential = DbCredential.query.get(user_id)

    credential.password_hash = password_hash
    credential.updated_at = now

    event = user_event_service.build_event('password-updated', user_id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()

    session_service.delete_session_tokens_for_user(user_id)


def is_password_valid_for_user(user_id: UserID, password: str) -> bool:
    """Return `True` if the password is valid for the user, or `False`
    otherwise.
    """
    credential = DbCredential.query.get(user_id)

    if credential is None:
        # no password stored for user
        return False

    return check_password_hash(credential.password_hash, password)


def check_password_hash(password_hash: str, password: str) -> bool:
    """Hash the password and return `True` if the result matches the
    given hash, `False` otherwise.
    """
    return (password_hash is not None) \
        and _check_password_hash(password_hash, password)
