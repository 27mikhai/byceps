# -*- coding: utf-8 -*-

"""
byceps.blueprints.orgateam_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..orga.models import OrgaTeam

from .authorization import OrgaTeamPermission


blueprint = create_blueprint('orgateam_admin', __name__)


permission_registry.register_enum('orga_team', OrgaTeamPermission)


@blueprint.route('/')
@permission_required(OrgaTeamPermission.list)
@templated
def index():
    """List orga teams."""
    teams = OrgaTeam.query.all()
    return {'teams': teams}
