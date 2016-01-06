# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import session

from .service import load_user


KEY_USER_ID = 'user_id'
KEY_USER_AUTH_TOKEN = 'user_auth_token'


class UserSession(object):

    @classmethod
    def start(cls, user, *, permanent=False):
        """Initialize the user's session by putting the relevant data
        into the session cookie.
        """
        session[KEY_USER_ID] = str(user.id)
        session[KEY_USER_AUTH_TOKEN] = str(user.auth_token)
        session.permanent = permanent

    @classmethod
    def end(cls):
        """End the user's session by deleting the session cookie."""
        session.pop(KEY_USER_ID, None)
        session.pop(KEY_USER_AUTH_TOKEN, None)
        session.permanent = False

    @classmethod
    def get_user(cls):
        """Return the current user, falling back to the anonymous user."""
        return load_user(cls.get_user_id(), cls.get_auth_token())

    @classmethod
    def get_user_id(cls):
        """Return the current user's ID, or `None` if not available."""
        return session.get(KEY_USER_ID)

    @classmethod
    def get_auth_token(cls):
        """Return the current user's auth token, or `None` if not available."""
        return session.get(KEY_USER_AUTH_TOKEN)
