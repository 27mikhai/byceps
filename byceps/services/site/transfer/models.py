"""
byceps.services.site.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from attr import attrs

from ....typing import PartyID


SiteID = NewType('SiteID', str)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Site:
    id: SiteID
    party_id: PartyID
    title: str
    server_name: str


@attrs(auto_attribs=True, frozen=True, slots=True)
class SiteSetting:
    site_id: SiteID
    name: str
    value: str
