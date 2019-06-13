"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod

from testfixtures.shop_order import create_orderer

from tests.helpers import create_party, create_session_token, \
    create_user_with_detail
from tests.services.shop.base import ShopTestBase


class ShopOrdersTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        self.user1 = create_user_with_detail('User1')
        self.user2 = create_user_with_detail('User2')

        self.create_brand_and_party()

    def test_view_matching_user_and_party(self):
        shop = self.create_shop(self.party.id)
        self.create_order_number_sequence(shop.id, 'LF-02-B')
        self.create_payment_instructions_snippet(shop.id)

        order_id = self.place_order(shop.id, self.user1)

        response = self.request_view(self.user1, order_id)

        assert response.status_code == 200

    def test_view_matching_party_but_different_user(self):
        shop = self.create_shop(self.party.id)
        self.create_order_number_sequence(shop.id, 'LF-02-B')
        self.create_payment_instructions_snippet(shop.id)

        order_id = self.place_order(shop.id, self.user1)

        response = self.request_view(self.user2, order_id)

        assert response.status_code == 404

    def test_view_matching_user_but_different_party(self):
        other_party = create_party(self.brand.id, 'otherlan-2013',
                                   'OtherLAN 2013')

        shop = self.create_shop(other_party.id)
        self.create_order_number_sequence(shop.id, 'LF-02-B')
        self.create_payment_instructions_snippet(shop.id)

        order_id = self.place_order(shop.id, self.user1)

        response = self.request_view(self.user1, order_id)

        assert response.status_code == 404

    # helpers

    def create_payment_instructions_snippet(self, shop_id):
        self.create_shop_fragment(shop_id, 'payment_instructions',
                                  'Send all ur moneyz!')

    def place_order(self, shop_id, user):
        orderer = create_orderer(user)
        payment_method = PaymentMethod.bank_transfer
        cart = Cart()

        order = order_service.place_order(shop_id, orderer, payment_method,
                                         cart)

        return order.id

    def request_view(self, current_user, order_id):
        create_session_token(current_user.id)

        url = '/shop/orders/{}'.format(str(order_id))

        with self.client(user_id=current_user.id) as client:
            response = client.get(url)

        return response
