"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.news import service as news_service
from byceps.services.news.transfer.models import BodyFormat, Channel

from tests.integration.services.news.conftest import make_channel


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user()


@pytest.fixture(scope='module')
def brand(make_brand):
    return make_brand()


@pytest.fixture
def channel(brand, make_channel) -> Channel:
    return make_channel(brand.id)


@pytest.fixture
def news_item_with_image(channel: Channel, editor):
    item = create_item(
        channel.id,
        'with-image',
        editor.id,
        image_url_path='breaking.png',
    )

    yield item

    news_service.delete_item(item.id)


@pytest.fixture
def news_item_without_image(channel: Channel, editor):
    item = create_item(channel.id, 'without-image', editor.id)

    yield item

    news_service.delete_item(item.id)


def test_image_url_with_image(news_item_with_image):
    channel = news_item_with_image.channel

    assert (
        news_item_with_image.image_url_path
        == f'/data/global/news_channels/{channel.id}/breaking.png'
    )


def test_image_url_without_image(news_item_without_image):
    assert news_item_without_image.image_url_path is None


# helpers


def create_item(channel_id, slug, editor_id, *, image_url_path=None):
    title = 'the title'
    body = 'the body'
    body_format = BodyFormat.html

    item = news_service.create_item(
        channel_id,
        slug,
        editor_id,
        title,
        body,
        body_format,
        image_url_path=image_url_path,
    )

    # Return aggregated version of item.
    channel_ids = {channel_id}
    return news_service.find_aggregated_item_by_slug(channel_ids, slug)
