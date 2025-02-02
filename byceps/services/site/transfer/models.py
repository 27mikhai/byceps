"""
byceps.services.site.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import NewType, Optional

from ....typing import BrandID, PartyID

from ...board.transfer.models import BoardID
from ...brand.transfer.models import Brand
from ...news.transfer.models import ChannelID as NewsChannelID
from ...shop.storefront.transfer.models import StorefrontID


SiteID = NewType('SiteID', str)


@dataclass(frozen=True)
class Site:
    id: SiteID
    title: str
    server_name: str
    brand_id: BrandID
    party_id: PartyID
    enabled: bool
    user_account_creation_enabled: bool
    login_enabled: bool
    news_channel_ids: frozenset[NewsChannelID]
    board_id: Optional[BoardID]
    storefront_id: Optional[StorefrontID]
    archived: bool


@dataclass(frozen=True)
class SiteWithBrand(Site):
    brand: Brand


@dataclass(frozen=True)
class SiteSetting:
    site_id: SiteID
    name: str
    value: str
