"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.orga import service as orga_service

from tests.helpers import create_brand


def test_flag_changes(admin_app_with_db, admin_user, normal_user):
    brand = create_brand()

    assert not orga_service.is_user_orga(normal_user.id)

    flag = orga_service.add_orga_flag(brand.id, normal_user.id, admin_user.id)

    assert orga_service.is_user_orga(normal_user.id)

    orga_service.remove_orga_flag(flag, admin_user.id)

    assert not orga_service.is_user_orga(normal_user.id)
