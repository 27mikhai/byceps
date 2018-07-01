"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence.service import generate_article_number, \
    generate_order_number

from tests.services.shop.base import ShopTestBase


class SequenceNumberGenerationTestCase(ShopTestBase):

    def test_generate_article_number_default(self):
        self.create_brand_and_party()
        shop = self.create_shop(self.party.id)
        self.create_article_number_sequence(shop.id, 'AEC-01-A')

        actual = generate_article_number(shop.id)

        assert actual == 'AEC-01-A00001'

    def test_generate_article_number_custom(self):
        party = self.create_custom_brand_and_party()
        shop = self.create_shop(party.id)
        last_assigned_article_sequence_number = 41

        self.create_article_number_sequence(shop.id, 'XYZ-09-A',
            value=last_assigned_article_sequence_number)

        actual = generate_article_number(shop.id)

        assert actual == 'XYZ-09-A00042'

    def test_generate_order_number_default(self):
        self.create_brand_and_party()
        shop = self.create_shop(self.party.id)
        self.create_order_number_sequence(shop.id, 'AEC-01-B')

        actual = generate_order_number(shop.id)

        assert actual == 'AEC-01-B00001'

    def test_generate_order_number_custom(self):
        party = self.create_custom_brand_and_party()
        shop = self.create_shop(party.id)
        last_assigned_order_sequence_number = 206

        self.create_order_number_sequence(shop.id, 'LOL-03-B',
            value=last_assigned_order_sequence_number)

        actual = generate_order_number(shop.id)

        assert actual == 'LOL-03-B00207'

    # -------------------------------------------------------------------- #
    # helpers

    def create_custom_brand_and_party(self):
        brand = self.create_brand('custom', 'Custom Events')
        party = self.create_party(brand.id, 'custom-party-4', 'Custom Party 4')

        return party
