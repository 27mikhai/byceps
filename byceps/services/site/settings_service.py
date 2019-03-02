"""
byceps.services.site.settings_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...database import db
from ...typing import PartyID

from .models.setting import Setting as DbSetting
from .models.site import Site as DbSite
from .transfer.models import SiteID, SiteSetting


def create_setting(site_id: SiteID, name: str, value: str) -> SiteSetting:
    """Create a setting for that site."""
    setting = DbSetting(site_id, name, value)

    db.session.add(setting)
    db.session.commit()

    return _db_entity_to_site_setting(setting)


def find_setting(site_id: SiteID, name: str) -> Optional[SiteSetting]:
    """Return the setting for that site and with that name, or `None`
    if not found.
    """
    setting = DbSetting.query.get((site_id, name))

    if setting is None:
        return None

    return _db_entity_to_site_setting(setting)


def find_setting_value(site_id: SiteID, name: str) -> Optional[str]:
    """Return the value of the setting for that site and with that
    name, or `None` if not found.
    """
    setting = find_setting(site_id, name)

    if setting is None:
        return None

    return setting.value


def get_settings_for_party(party_id: PartyID) -> List[SiteSetting]:
    """Return all settings for that party's sites."""
    settings = DbSetting.query \
        .join(DbSite).filter(DbSite.party_id == party_id) \
        .order_by(DbSetting.site_id, DbSetting.name) \
        .all()

    return {_db_entity_to_site_setting(setting) for setting in settings}


def get_settings(site_id: SiteID) -> List[SiteSetting]:
    """Return all settings for that site."""
    settings = DbSetting.query \
        .filter_by(site_id=site_id) \
        .all()

    return {_db_entity_to_site_setting(setting) for setting in settings}


def _db_entity_to_site_setting(setting: DbSetting) -> SiteSetting:
    return SiteSetting(
        setting.site_id,
        setting.name,
        setting.value,
    )
