"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.user.dbmodels.user import User as DbUser
from byceps.services.user.dbmodels.detail import UserDetail as DbUserDetail


@pytest.mark.parametrize(
    'first_names, last_name, expected',
    [
        (None,          None    , None                ),
        ('Giesbert Z.', None    , 'Giesbert Z.'       ),
        (None,          'Blümli', 'Blümli'            ),
        ('Giesbert Z.', 'Blümli', 'Giesbert Z. Blümli'),
    ],
)
def test_full_name(first_names, last_name, expected):
    user = create_user(first_names, last_name)

    assert user.detail.full_name == expected


def create_user(first_names: str, last_name: str) -> DbUser:
    created_at = datetime.utcnow()
    screen_name = 'Anyone'
    email_address = 'anyone@example.test'

    user = DbUser(created_at, screen_name, email_address)

    detail = DbUserDetail(user=user)
    detail.first_names = first_names
    detail.last_name = last_name

    return user
