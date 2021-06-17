"""
byceps.blueprints.admin.ticketing.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ....services.ticketing import ticket_code_service
from ....services.user import service as user_service
from ....util.l10n import LocalizedForm


def validate_user(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

    if user is None:
        raise ValidationError(lazy_gettext('Unknown username'))

    field.data = user


class UpdateCodeForm(LocalizedForm):
    code = StringField(lazy_gettext('Code'), [InputRequired()])

    @staticmethod
    def validate_code(form, field):
        if not ticket_code_service.is_ticket_code_wellformed(field.data):
            raise ValidationError(lazy_gettext('Invalid format'))


class SpecifyUserForm(LocalizedForm):
    user = StringField(
        lazy_gettext('Username'), [InputRequired(), validate_user]
    )
