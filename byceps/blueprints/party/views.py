"""
byceps.blueprints.party.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...services.party import service as party_service
from ...services.ticketing import attendance_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated


blueprint = create_blueprint('party', __name__)


@blueprint.route('/info')
@templated
def info():
    """Show information about the current party."""
    party = party_service.find_party(g.party_id)

    return {
        'party': party,
    }


@blueprint.route('/archive')
@templated
def archive():
    """Show archived parties."""
    archived_parties = party_service.get_archived_parties_for_brand(g.brand_id)

    party_ids = {party.id for party in archived_parties}
    attendees_by_party_id = attendance_service.get_attendees_by_party(party_ids)

    return {
        'parties': archived_parties,
        'attendees_by_party_id': attendees_by_party_id,
    }
