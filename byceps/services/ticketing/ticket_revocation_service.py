"""
byceps.services.ticketing.ticket_revocation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Set

from ...database import db
from ...typing import UserID

from . import event_service
from .event_service import TicketEvent
from . import ticket_service
from .transfer.models import TicketID


def revoke_ticket(ticket_id: TicketID, *,
                  initiator_id: Optional[UserID]=None,
                  reason: Optional[str]=None
                 ) -> None:
    """Revoke the ticket."""
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket is None:
        raise ValueError('Unknown ticket ID.')

    ticket.revoked = True

    event = _build_ticket_revoked_event(ticket.id, initiator_id, reason)
    db.session.add(event)

    db.session.commit()


def revoke_tickets(ticket_ids: Set[TicketID], *,
                   initiator_id: Optional[UserID]=None,
                   reason: Optional[str]=None
                  ) -> None:
    """Revoke the tickets."""
    tickets = ticket_service.find_tickets(ticket_ids)

    for ticket in tickets:
        ticket.revoked = True

        event = _build_ticket_revoked_event(ticket.id, initiator_id, reason)
        db.session.add(event)

    db.session.commit()


def _build_ticket_revoked_event(ticket_id: TicketID,
                                initiator_id: Optional[UserID]=None,
                                reason: Optional[str]=None
                               ) -> TicketEvent:
    data = {}

    if initiator_id is not None:
        data['initiator_id'] = str(initiator_id)

    if reason:
        data['reason'] = reason

    return event_service._build_event('ticket-revoked', ticket_id, data)
