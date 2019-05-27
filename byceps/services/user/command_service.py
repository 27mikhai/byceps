"""
byceps.services.user.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from ...database import db
from ...typing import UserID

from . import event_service
from .models.detail import UserDetail as DbUserDetail
from .models.user import User as DbUser


def enable_user(user_id: UserID, initiator_id: UserID) -> None:
    """Enable the user account."""
    user = _get_user(user_id)

    user.enabled = True

    event = event_service.build_event('user-enabled', user.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def disable_user(user_id: UserID, initiator_id: UserID) -> None:
    """Disable the user account."""
    user = _get_user(user_id)

    user.enabled = False

    event = event_service.build_event('user-disabled', user.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def suspend_account(user_id: UserID, initiator_id: UserID, reason: str) -> None:
    """Suspend the user account."""
    user = _get_user(user_id)

    user.suspended = True

    event = event_service.build_event('user-suspended', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()


def unsuspend_account(user_id: UserID, initiator_id: UserID, reason: str
                     ) -> None:
    """Unsuspend the user account."""
    user = _get_user(user_id)

    user.suspended = False

    event = event_service.build_event('user-unsuspended', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()


def delete_account(user_id: UserID, initiator_id: UserID, reason: str) -> None:
    """Delete the user account."""
    user = _get_user(user_id)

    user.deleted = True
    _anonymize_account(user)

    event = event_service.build_event('user-deleted', user.id, {
        'initiator_id': str(initiator_id),
        'reason': reason,
    })
    db.session.add(event)

    db.session.commit()


def update_user_details(user_id: UserID, first_names: str, last_name: str,
                        date_of_birth: date, country: str, zip_code, city: str,
                        street: str, phone_number: str) -> None:
    """Update the user's details."""
    detail = _get_user_detail(user_id)

    detail.first_names = first_names
    detail.last_name = last_name
    detail.date_of_birth = date_of_birth
    detail.country = country
    detail.zip_code = zip_code
    detail.city = city
    detail.street = street
    detail.phone_number = phone_number

    db.session.commit()


def set_user_detail_extra(user_id: UserID, key: str, value: str) -> None:
    """Set a value for a key in the user's detail extras map."""
    detail = _get_user_detail(user_id)

    if detail.extras is None:
        detail.extras = {}

    detail.extras[key] = value

    db.session.commit()


def remove_user_detail_extra(user_id: UserID, key: str) -> None:
    """Remove the entry with that key from the user's detail extras map."""
    detail = _get_user_detail(user_id)

    if (detail.extras is None) or (key not in detail.extras):
        return

    del detail.extras[key]
    db.session.commit()


def _anonymize_account(user: DbUser) -> None:
    """Remove or replace user details of the account."""
    user.screen_name = 'deleted-{}'.format(user.id.hex)
    user.email_address = '{}@user.invalid'.format(user.id.hex)
    user.legacy_id = None

    # Remove details.
    user.detail.first_names = None
    user.detail.last_name = None
    user.detail.date_of_birth = None
    user.detail.country = None
    user.detail.zip_code = None
    user.detail.city = None
    user.detail.street = None
    user.detail.phone_number = None

    # Remove avatar association.
    if user.avatar_selection is not None:
        db.session.delete(user.avatar_selection)


def _get_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    user = DbUser.query.get(user_id)

    if user is None:
        raise ValueError("Unknown user ID '{}'.".format(user_id))

    return user


def _get_user_detail(user_id: UserID) -> DbUserDetail:
    """Return the user's details, or raise an exception."""
    detail = DbUserDetail.query \
        .filter_by(user_id=user_id) \
        .one_or_none()

    if detail is None:
        raise ValueError("Unknown user ID '{}'.".format(user_id))

    return detail
