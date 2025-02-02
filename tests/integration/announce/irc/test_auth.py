"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.services.authentication.session import service as session_service
from byceps.signals import auth as auth_signals

from .helpers import assert_submitted_data, CHANNEL_INTERNAL, mocked_irc_bot


EXPECTED_CHANNEL = CHANNEL_INTERNAL


def test_user_logged_in_into_admin_app_announced(app, user):
    expected_text = 'Logvogel hat sich eingeloggt.'

    _, event = session_service.log_in_user(user.id, '10.10.23.42')

    with mocked_irc_bot() as mock:
        auth_signals.user_logged_in.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_user_logged_in_into_site_app_announced(app, site, user):
    expected_text = (
        'Logvogel hat sich auf Site "ACMECon 2014 website" eingeloggt.'
    )

    _, event = session_service.log_in_user(
        user.id, '10.10.23.42', site_id=site.id
    )

    with mocked_irc_bot() as mock:
        auth_signals.user_logged_in.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


# helpers


@pytest.fixture(scope='module')
def user(make_user):
    return make_user('Logvogel')
