"""
byceps.services.news.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Optional, Sequence

from flask import url_for

from ...database import db, paginate, Pagination, Query
from ...typing import BrandID, UserID

from ..brand.models.brand import Brand as DbBrand

from .models.channel import Channel as DbChannel
from .models.item import \
    CurrentVersionAssociation as DbCurrentVersionAssociation, \
    Item as DbItem, ItemVersion as DbItemVersion
from .transfer.models import ChannelID, Item, ItemID, ItemVersionID


def create_item(brand_id: BrandID, slug: str, creator_id: UserID, title: str,
                body: str, *, image_url_path: Optional[str]=None) -> DbItem:
    """Create a news item, a version, and set the version as the item's
    current one.
    """
    item = DbItem(brand_id, slug)
    db.session.add(item)

    version = _create_version(item, creator_id, title, body,
                              image_url_path=image_url_path)
    db.session.add(version)

    current_version_association = DbCurrentVersionAssociation(item, version)
    db.session.add(current_version_association)

    db.session.commit()

    return item


def update_item(item: DbItem, creator_id: UserID, title: str, body: str, *,
                image_url_path: Optional[str]=None) -> None:
    """Update a news item by creating a new version of it and setting
    the new version as the current one.
    """
    version = _create_version(item, creator_id, title, body,
                              image_url_path=image_url_path)
    db.session.add(version)

    item.current_version = version

    db.session.commit()


def _create_version(item: DbItem, creator_id: UserID, title: str, body: str, *,
                    image_url_path: Optional[str]=None) -> DbItemVersion:
    version = DbItemVersion(item, creator_id, title, body)

    if image_url_path:
        version.image_url_path = image_url_path

    return version


def publish_item(item_id: ItemID) -> None:
    """Publish a news item."""
    item = find_item(item_id)
    if item is None:
        raise ValueError('Unknown news item ID "{}".'.format(item_id))

    item.published_at = datetime.utcnow()
    db.session.commit()


def find_item(item_id: ItemID) -> Optional[DbItem]:
    """Return the item with that id, or `None` if not found."""
    return DbItem.query.get(item_id)


def find_aggregated_item_by_slug(channel_id: ChannelID, slug: str,
                                 *, published_only: bool=False
                                ) -> Optional[Item]:
    """Return the news item identified by that slug, or `None` if not found."""
    query = DbItem.query \
        .for_channel(channel_id) \
        .with_current_version() \
        .filter_by(slug=slug)

    if published_only:
        query = query.published()

    item = query.one_or_none()

    if item is None:
        return None

    return _db_entity_to_item(item)


def get_aggregated_items_paginated(channel_id: ChannelID, page: int,
                                   items_per_page: int,
                                   *, published_only: bool=False
                                  ) -> Pagination:
    """Return the news items to show on the specified page."""
    query = _get_items_query(channel_id)

    if published_only:
        query = query.published()

    return paginate(query, page, items_per_page, item_mapper=_db_entity_to_item)


def get_items_paginated(channel_id: ChannelID, page: int, items_per_page: int
                       ) -> Pagination:
    """Return the news items to show on the specified page."""
    return _get_items_query(channel_id) \
        .paginate(page, items_per_page)


def _get_items_query(channel_id: ChannelID) -> Query:
    return DbItem.query \
        .for_channel(channel_id) \
        .with_current_version() \
        .order_by(DbItem.published_at.desc())


def get_item_versions(item_id: ItemID) -> Sequence[DbItemVersion]:
    """Return all item versions, sorted from most recent to oldest."""
    return DbItemVersion.query \
        .for_item(item_id) \
        .order_by(DbItemVersion.created_at.desc()) \
        .all()


def find_item_version(version_id: ItemVersionID) -> DbItemVersion:
    """Return the item version with that ID, or `None` if not found."""
    return DbItemVersion.query.get(version_id)


def count_items_for_brand(brand_id: BrandID) -> int:
    """Return the number of news items for that brand."""
    return DbItem.query \
        .join(DbChannel) \
        .filter(DbChannel.brand_id == brand_id) \
        .count()


def get_item_count_by_brand_id() -> Dict[BrandID, int]:
    """Return news item count (including 0) per brand, indexed by brand ID."""
    brand_ids_and_item_counts = db.session \
        .query(
            DbBrand.id,
            db.func.count(DbItem.id)
        ) \
        .outerjoin(DbChannel) \
        .outerjoin(DbItem) \
        .group_by(DbBrand.id) \
        .all()

    return dict(brand_ids_and_item_counts)


def _db_entity_to_item(item: DbItem) -> Item:
    body = item.current_version.render_body()
    external_url = url_for('news.view', slug=item.slug, _external=True)
    image_url = _assemble_image_url(item)

    return Item(
        id=item.id,
        slug=item.slug,
        published_at=item.published_at,
        published=item.published_at is not None,
        title=item.title,
        body=body,
        external_url=external_url,
        image_url=image_url,
    )


def _assemble_image_url(item: DbItem) -> Optional[str]:
    url_path = item.current_version.image_url_path

    if not url_path:
        return None

    filename = 'news/{}'.format(url_path)
    return url_for('brand_file',
                   filename=filename,
                   _method='GET',
                   _external=True)
