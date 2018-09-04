"""
byceps.blueprints.user_message.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send messages from one user to another.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ...services.user import service as user_service
from ...services.user_message import service as user_message_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
from ...util.framework.templating import templated
from ...util.views import redirect_to

from ..authentication.decorators import login_required

from .forms import CreateForm


blueprint = create_blueprint('user_message', __name__)


@blueprint.route('/to/<uuid:recipient_id>/create')
@login_required
@templated
def create_form(recipient_id, erroneous_form=None):
    """Show a form to create a message to send to the user."""
    recipient = _get_user_or_404(recipient_id)

    form = erroneous_form if erroneous_form else CreateForm()

    return {
        'recipient': recipient,
        'form': form,
    }


@blueprint.route('/to/<uuid:recipient_id>/create', methods=['POST'])
@login_required
def create(recipient_id):
    """Create a message to send to the user."""
    recipient = _get_user_or_404(recipient_id)

    form = CreateForm(request.form)
    if not form.validate():
        return create_form(recipient.id, form)

    sender = g.current_user
    body = form.body.data.strip()

    user_message_service.send_message(sender.id, recipient.id, body, g.brand_id)

    flash_success(
        'Deine Nachricht an {} wurde versendet.'.format(recipient.screen_name))

    return redirect_to('user.view', user_id=recipient.id)


def _get_user_or_404(user_id):
    user = user_service.find_user(user_id)

    if user is None:
        abort(404)

    return user
