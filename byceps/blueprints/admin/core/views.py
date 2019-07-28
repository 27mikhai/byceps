"""
byceps.blueprints.admin.core.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....services.brand import service as brand_service
from ....services.party import service as party_service
from ....services.shop.shop import service as shop_service
from ....services.site import service as site_service
from ....util.framework.blueprint import create_blueprint

from ...authorization.registry import permission_registry

from .authorization import AdminPermission


blueprint = create_blueprint('core_admin', __name__)


permission_registry.register_enum(AdminPermission)


@blueprint.app_context_processor
def inject_template_variables():
    brands = brand_service.get_brands()

    def get_brand_for_party(party):
        return brand_service.find_brand(party.brand_id)

    def get_party_for_site(site):
        return party_service.find_party(site.party_id)

    def get_shop_for_party(party):
        return shop_service.find_shop_for_party(party.id)

    return {
        'all_brands': brands,
        'get_brand_for_party': get_brand_for_party,
        'get_party_for_site': get_party_for_site,
        'get_parties_for_brand': party_service.get_parties_for_brand,
        'get_shop_for_party': get_shop_for_party,
        'get_sites_for_party': site_service.get_sites_for_party,
    }
