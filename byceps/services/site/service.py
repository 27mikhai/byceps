"""
byceps.services.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...database import db
from ...typing import PartyID

from .models.site import Site as DbSite
from .transfer.models import Site, SiteID


class UnknownSiteId(Exception):
    pass


def create_site(site_id: SiteID, party_id: PartyID, title: str) -> Site:
    """Create a site for that party."""
    site = DbSite(site_id, party_id, title)

    db.session.add(site)
    db.session.commit()

    return _db_entity_to_site(site)


def update_site(site_id: SiteID, title: str) -> Site:
    """Update the site."""
    site = DbSite.query.get(site_id)

    if site is None:
        raise UnknownSiteId(site_id)

    site.title = title

    db.session.commit()

    return _db_entity_to_site(site)


def find_site(site_id: SiteID) -> Optional[Site]:
    """Return the site with that id, or `None` if not found."""
    site = DbSite.query.get(site_id)

    if site is None:
        return None

    return _db_entity_to_site(site)


def get_sites_for_party(party_id: PartyID) -> List[Site]:
    """Return the sites for that party."""
    sites = DbSite.query \
        .filter_by(party_id=party_id) \
        .all()

    return [_db_entity_to_site(site) for site in sites]


def _db_entity_to_site(site: DbSite) -> Site:
    return Site(
        site.id,
        site.party_id,
        site.title,
    )
