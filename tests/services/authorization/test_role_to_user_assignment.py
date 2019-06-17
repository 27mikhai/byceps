"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.authorization import service


PERMISSION_ID = 'board_topic_hide'


def test_assign_role_to_user(admin_app_with_db, normal_user, admin_user, role):
    user_id = normal_user.id
    initiator_id = admin_user.id

    user_permission_ids_before = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID not in user_permission_ids_before

    service.assign_role_to_user(user_id, role.id, initiator_id=initiator_id)

    user_permission_ids_after = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID in user_permission_ids_after


def test_deassign_role_from_user(admin_app_with_db, normal_user, admin_user,
                                 role):
    user_id = normal_user.id
    initiator_id = admin_user.id

    service.assign_role_to_user(user_id, role.id, initiator_id=initiator_id)

    user_permission_ids_before = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID in user_permission_ids_before

    service.deassign_role_from_user(user_id, role.id, initiator_id=initiator_id)

    user_permission_ids_after = service.get_permission_ids_for_user(user_id)
    assert PERMISSION_ID not in user_permission_ids_after


@pytest.fixture
def permission():
    return service.create_permission(PERMISSION_ID, 'Hide board topics')


@pytest.fixture
def role(permission):
    role = service.create_role('board_moderator', 'Board Moderator')
    service.assign_permission_to_role(permission.id, role.id)
    return role
