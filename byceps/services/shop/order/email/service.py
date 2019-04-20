"""
byceps.services.shop.order.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notification e-mails about shop orders

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os.path
from typing import Any, Dict, Optional

from attr import attrib, attrs
from flask import current_app
from jinja2 import FileSystemLoader

from .....services.email import service as email_service
from .....services.email.transfer.models import Message
from .....services.party import service as party_service
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import Order, OrderID
from .....services.shop.shop import service as shop_service
from .....services.snippet import service as snippet_service
from .....services.snippet.service import SnippetNotFound
from .....services.snippet.transfer.models import Scope
from .....services.user.models.user import User
from .....typing import BrandID
from .....util.money import format_euro_amount
from .....util.templating import create_sandboxed_environment, load_template

from ...shop.transfer.models import ShopID


@attrs(frozen=True, slots=True)
class OrderEmailData:
    order = attrib(type=Order)
    brand_id = attrib(type=BrandID)
    orderer_screen_name = attrib(type=str)
    orderer_email_address = attrib(type=str)


def send_email_for_incoming_order_to_orderer(order_id: OrderID) -> None:
    message = _assemble_email_for_incoming_order_to_orderer(order_id)

    _send_email(message)


def send_email_for_canceled_order_to_orderer(order_id: OrderID) -> None:
    message = _assemble_email_for_canceled_order_to_orderer(order_id)

    _send_email(message)


def send_email_for_paid_order_to_orderer(order_id: OrderID) -> None:
    message = _assemble_email_for_paid_order_to_orderer(order_id)

    _send_email(message)


def _assemble_email_for_incoming_order_to_orderer(order_id: OrderID) -> Message:
    data = _get_order_email_data(order_id)

    order = data.order

    subject = 'Deine Bestellung ({}) ist eingegangen.' \
        .format(order.order_number)
    template_name = 'order_placed.txt'
    template_context = _get_template_context(data)
    template_context['payment_instructions'] = _get_payment_instructions(order)
    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(subject, template_name, template_context,
                                      data.brand_id, recipient_address)


def _get_payment_instructions(order: Order) -> str:
    fragment = _get_snippet_body(order.shop_id, 'email_payment_instructions')

    template = load_template(fragment)
    return template.render(order_number=order.order_number)


def _assemble_email_for_canceled_order_to_orderer(order_id: OrderID) -> Message:
    data = _get_order_email_data(order_id)

    subject = '\u274c Deine Bestellung ({}) wurde storniert.' \
        .format(data.order.order_number)
    template_name = 'order_canceled.txt'
    template_context = _get_template_context(data)
    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(subject, template_name, template_context,
                                      data.brand_id, recipient_address)


def _assemble_email_for_paid_order_to_orderer(order_id: OrderID) -> Message:
    data = _get_order_email_data(order_id)

    subject = '\u2705 Deine Bestellung ({}) ist bezahlt worden.' \
        .format(data.order.order_number)
    template_name = 'order_paid.txt'
    template_context = _get_template_context(data)
    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(subject, template_name, template_context,
                                      data.brand_id, recipient_address)


def _get_order_email_data(order_id: OrderID) -> OrderEmailData:
    """Collect data required for an order e-mail template."""
    order_entity = order_service.find_order(order_id)

    order = order_entity.to_transfer_object()
    shop = shop_service.get_shop(order.shop_id)
    party = party_service.find_party(shop.party_id)
    placed_by = order_entity.placed_by

    return OrderEmailData(
        order=order,
        brand_id=party.brand_id,
        orderer_screen_name=placed_by.screen_name,
        orderer_email_address=placed_by.email_address,
    )


def _get_template_context(order_email_data: OrderEmailData) -> Dict[str, Any]:
    """Collect data required for an order e-mail template."""
    footer = _get_footer(order_email_data.order)

    return {
        'order': order_email_data.order,
        'orderer_screen_name': order_email_data.orderer_screen_name,
        'footer': footer,
    }


def _get_footer(order: Order) -> str:
    fragment = _get_snippet_body(order.shop_id, 'email_footer')

    template = load_template(fragment)
    return template.render()


def _assemble_email_to_orderer(subject: str, template_name: str,
                               template_context: Dict[str, Any],
                               brand_id: BrandID, recipient_address: str
                              ) -> Message:
    """Assemble an email message with the rendered template as its body."""
    sender = _get_sender_address_for_brand(brand_id)
    body = _render_template(template_name, **template_context)
    recipients = [recipient_address]

    return Message(sender, recipients, subject, body)


def _get_sender_address_for_brand(brand_id: BrandID) -> Optional[str]:
    sender_address = email_service.find_sender_address_for_brand(brand_id)

    if not sender_address:
        current_app.logger.warning(
            'No e-mail sender address configured for brand ID "%s".', brand_id)

    return sender_address


def _get_snippet_body(shop_id: ShopID, name: str) -> str:
    scope = Scope('shop', str(shop_id))

    version = snippet_service \
        .find_current_version_of_snippet_with_name(scope, name)

    if not version:
        raise SnippetNotFound(scope, name)

    return version.body


def _render_template(name: str, **context: Dict[str, Any]) -> str:
    templates_path = os.path.join(
        current_app.root_path,
        'services/shop/order/email/templates')

    loader = FileSystemLoader(templates_path)

    env = create_sandboxed_environment(loader=loader)
    env.filters['format_euro_amount'] = format_euro_amount

    template = env.get_template(name)

    return template.render(**context)


def _send_email(message: Message) -> None:
    email_service.enqueue_message(message)
