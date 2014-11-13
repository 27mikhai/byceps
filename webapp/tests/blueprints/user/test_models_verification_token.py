# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path
from unittest import TestCase
from uuid import UUID

from freezegun import freeze_time
from nose2.tools import params

from byceps.blueprints.user import models
from byceps.blueprints.user.models import User, VerificationToken, \
    VerificationTokenPurpose
from byceps.util.image import ImageType

from tests import AbstractAppTestCase


NOW = datetime.now()


class AvatarImageTestCase(TestCase):

    def setUp(self):
        self.user = User()

    @params(
        (None, None          , False),
        (NOW , None          , False),
        (None, ImageType.jpeg, False),
        (NOW , ImageType.jpeg, True ),
    )
    def test_has_avatar_image(self, created_at, image_type, expected):
        self.user.avatar_image_created_at = created_at
        self.user.avatar_image_type = image_type

        self.assertEquals(self.user.has_avatar_image, expected)

    @params(
        (None  , None          ),
        ('gif' , ImageType.gif ),
        ('jpeg', ImageType.jpeg),
        ('png' , ImageType.png ),
    )
    def test_hybrid_image_type_getter(self, database_value, expected):
        self.user._avatar_image_type = database_value

        self.assertEquals(self.user.avatar_image_type, expected)

    @params(
        (None          , None  ),
        (ImageType.gif , 'gif' ),
        (ImageType.jpeg, 'jpeg'),
        (ImageType.png , 'png' ),
    )
    def test_hybrid_image_type_setter(self, image_type, expected):
        self.user.avatar_image_type = image_type

        self.assertEquals(self.user._avatar_image_type, expected)


class AvatarImagePathTestCase(AbstractAppTestCase):

    def setUp(self):
        super(AvatarImagePathTestCase, self).setUp()

        user_id = UUID('2e17cb15-d763-4f93-882a-371296a3c63f')
        self.user = User(id=user_id)

    def test_path(self):
        expected = Path(
            '/var/data/avatars/2e17cb15-d763-4f93-882a-371296a3c63f_1406637810.jpeg')

        created_at = datetime(2014, 7, 29, 14, 43, 30, 196165)
        self.user.set_avatar_image(created_at, ImageType.jpeg)

        with self.app.app_context():
            self.app.config['PATH_USER_AVATAR_IMAGES'] = Path('/var/data/avatars')
            self.assertEquals(self.user.avatar_image_path, expected)


class VerificationTokenTest(TestCase):

    @params(
        (
            VerificationTokenPurpose.email_address_confirmation,
            datetime(2014, 11, 26, 19, 54, 38),
            False,
        ),
        (
            VerificationTokenPurpose.email_address_confirmation,
            datetime(2014, 11, 27, 19, 54, 38),
            False,  # Never expires.
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 26, 19, 54, 38),
            False,
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 27, 17, 44, 52),
            False,  # Almost, but not yet.
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 27, 17, 44, 53),
            True,  # Just now.
        ),
        (
            VerificationTokenPurpose.password_reset,
            datetime(2014, 11, 27, 19, 54, 38),
            True,
        ),
    )
    def test_is_expired(self, purpose, now, expected):
        user = User()
        token = VerificationToken(user, purpose)
        token.created_at = datetime(2014, 11, 26, 17, 44, 53)

        with freeze_time(now):
            self.assertEquals(token.is_expired, expected)
