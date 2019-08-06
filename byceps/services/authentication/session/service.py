"""
byceps.services.authentication.session.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from ....database import db
from ....typing import UserID

from ..exceptions import AuthenticationFailed

from .models.session_token import SessionToken as DbSessionToken


def get_session_token(user_id: UserID) -> DbSessionToken:
    """Return existing session token or create a new one."""
    session_token = find_session_token_for_user(user_id)

    if session_token is None:
        session_token = create_session_token(user_id)

    return session_token


def create_session_token(user_id: UserID) -> DbSessionToken:
    """Create a session token."""
    token = uuid4()
    created_at = datetime.utcnow()

    session_token = DbSessionToken(user_id, token, created_at)

    db.session.add(session_token)
    db.session.commit()

    return session_token


def delete_session_tokens_for_user(user_id: UserID) -> None:
    """Delete all session tokens that belong to the user."""
    db.session.query(DbSessionToken) \
        .filter_by(user_id=user_id) \
        .delete()
    db.session.commit()


def delete_all_session_tokens() -> int:
    """Delete all users' session tokens.

    Return the number of records deleted.
    """
    deleted_total = db.session.query(DbSessionToken).delete()
    db.session.commit()

    return deleted_total


def find_session_token_for_user(user_id: UserID) -> Optional[DbSessionToken]:
    """Return the session token for the user with that ID, or `None` if
    not found.
    """
    return DbSessionToken.query \
        .filter_by(user_id=user_id) \
        .one_or_none()


def authenticate_session(user_id: UserID, auth_token: str) -> None:
    """Check the client session's validity.

    Return nothing on success, or raise an exception on failure.
    """
    if user_id is None:
        # User ID must not be empty.
        raise AuthenticationFailed()

    if not auth_token:
        # Authentication token must not be empty.
        raise AuthenticationFailed()

    if not _is_token_valid_for_user(auth_token, user_id):
        # Session token is unknown or the user ID provided by the
        # client does not match the one stored on the server.
        raise AuthenticationFailed()


def _is_token_valid_for_user(token: str, user_id: UserID) -> bool:
    """Return `True` if a session token with that ID exists for that user."""
    if not user_id:
        raise ValueError('User ID is invalid.')

    subquery = DbSessionToken.query \
        .filter_by(token=token, user_id=user_id) \
        .exists()

    return db.session.query(subquery).scalar()
