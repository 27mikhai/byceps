"""
byceps.blueprints.consent_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...services.consent import subject_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import ConsentPermission


blueprint = create_blueprint('consent_admin', __name__)


permission_registry.register_enum(ConsentPermission)


@blueprint.route('/')
@permission_required(ConsentPermission.administrate)
@templated
def index():
    """List consent subjects."""
    subjects_with_consent_counts = subject_service \
        .get_subjects_with_consent_counts()

    subjects_with_consent_counts = list(subjects_with_consent_counts.items())

    return {
        'subjects_with_consent_counts': subjects_with_consent_counts,
    }
