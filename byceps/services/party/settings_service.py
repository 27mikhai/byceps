"""
byceps.services.party.settings_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Set

from sqlalchemy.dialects.postgresql import insert

from ...database import db
from ...typing import PartyID

from .models.setting import Setting as DbSetting
from .transfer.models import PartySetting


def create_setting(party_id: PartyID, name: str, value: str) -> PartySetting:
    """Create a setting for that party."""
    setting = DbSetting(party_id, name, value)

    db.session.add(setting)
    db.session.commit()

    return _db_entity_to_party_setting(setting)


def create_or_update_setting(party_id: PartyID, name: str, value: str
                            ) -> PartySetting:
    """Create or update a setting for that party, depending on whether
    it already exists or not.
    """
    table = DbSetting.__table__

    # UPSERT
    query = insert(table) \
        .values(
            party_id=party_id,
            name=name,
            value=value
        ) \
        .on_conflict_do_update(
            constraint=table.primary_key,
            set_={'value': value})

    db.session.execute(query)

    return find_setting(party_id, name)


def find_setting(party_id: PartyID, name: str) -> Optional[PartySetting]:
    """Return the setting for that party and with that name, or `None`
    if not found.
    """
    setting = DbSetting.query.get((party_id, name))

    if setting is None:
        return None

    return _db_entity_to_party_setting(setting)


def find_setting_value(party_id: PartyID, name: str) -> Optional[str]:
    """Return the value of the setting for that party and with that
    name, or `None` if not found.
    """
    setting = find_setting(party_id, name)

    if setting is None:
        return None

    return setting.value


def get_settings(party_id: PartyID) -> Set[PartySetting]:
    """Return all settings for that party."""
    settings = DbSetting.query \
        .filter_by(party_id=party_id) \
        .all()

    return {_db_entity_to_party_setting(setting) for setting in settings}


def _db_entity_to_party_setting(setting: DbSetting) -> PartySetting:
    return PartySetting(
        setting.party_id,
        setting.name,
        setting.value,
    )
