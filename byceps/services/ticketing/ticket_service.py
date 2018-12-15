"""
byceps.services.ticketing.ticket_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional, Sequence, Set

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import PartyID, UserID

from ..party.models.party import Party
from ..seating.models.seat import Seat
from ..shop.order.transfer.models import OrderNumber
from ..user.models.user import User

from .models.category import Category
from .models.ticket import Ticket
from .transfer.models import TicketCode, TicketID


def find_ticket(ticket_id: TicketID) -> Optional[Ticket]:
    """Return the ticket with that id, or `None` if not found."""
    return Ticket.query.get(ticket_id)


def find_ticket_by_code(code: TicketCode) -> Optional[Ticket]:
    """Return the ticket with that code, or `None` if not found."""
    return Ticket.query \
        .filter_by(code=code) \
        .one_or_none()


def find_tickets(ticket_ids: Set[TicketID]) -> Sequence[Ticket]:
    """Return the tickets with those ids."""
    if not ticket_ids:
        return []

    return Ticket.query \
        .filter(Ticket.id.in_(ticket_ids)) \
        .all()


def find_tickets_created_by_order(order_number: OrderNumber
                                 ) -> Sequence[Ticket]:
    """Return the tickets created by this order (as it was marked as paid)."""
    return Ticket.query \
        .filter_by(order_number=order_number) \
        .order_by(Ticket.created_at) \
        .all()


def find_tickets_for_seat_manager(user_id: UserID, party_id: PartyID
                                 ) -> Sequence[Ticket]:
    """Return the tickets for that party whose respective seats the user
    is entitled to manage.
    """
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.revoked == False) \
        .filter(
            (
                (Ticket.seat_managed_by_id == None) &
                (Ticket.owned_by_id == user_id)
            ) |
            (Ticket.seat_managed_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat'),
        ) \
        .all()


def find_tickets_related_to_user(user_id: UserID) -> Sequence[Ticket]:
    """Return tickets related to the user."""
    return Ticket.query \
        .filter(
            (Ticket.owned_by_id == user_id) |
            (Ticket.seat_managed_by_id == user_id) |
            (Ticket.user_managed_by_id == user_id) |
            (Ticket.used_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('occupied_seat').joinedload('category'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
            db.joinedload('used_by'),
        ) \
        .order_by(Ticket.created_at) \
        .all()


def find_tickets_related_to_user_for_party(user_id: UserID, party_id: PartyID
                                          ) -> Sequence[Ticket]:
    """Return tickets related to the user for the party."""
    return Ticket.query \
        .for_party(party_id) \
        .filter(
            (Ticket.owned_by_id == user_id) |
            (Ticket.seat_managed_by_id == user_id) |
            (Ticket.user_managed_by_id == user_id) |
            (Ticket.used_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('occupied_seat').joinedload('category'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
            db.joinedload('used_by'),
        ) \
        .order_by(Ticket.created_at) \
        .all()


def find_tickets_used_by_user(user_id: UserID, party_id: PartyID
                             ) -> Sequence[Ticket]:
    """Return the tickets (if any) used by the user for that party."""
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.used_by_id == user_id) \
        .outerjoin(Seat) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .order_by(Seat.coord_x, Seat.coord_y) \
        .all()


def find_tickets_used_by_user_simplified(user_id: UserID, party_id: PartyID
                                        ) -> Sequence[Ticket]:
    """Return the tickets (if any) used by the user for that party."""
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.used_by_id == user_id) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .all()


def uses_any_ticket_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user uses any ticket for that party."""
    q = Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.used_by_id == user_id) \
        .filter(Ticket.revoked == False)

    return db.session.query(q.exists()).scalar()


def select_ticket_users_for_party(user_ids: Set[UserID], party_id: PartyID
                                 ) -> Set[UserID]:
    """Return the IDs of those users that use a ticket for that party."""
    if not user_ids:
        return set()

    q = Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.used_by_id == User.id) \
        .filter(Ticket.revoked == False)

    rows = db.session.query(User.id) \
        .filter(q.exists()) \
        .filter(User.id.in_(user_ids)) \
        .all()

    return {row[0] for row in rows}


def get_ticket_with_details(ticket_id: TicketID) -> Optional[Ticket]:
    """Return the ticket with that id, or `None` if not found."""
    return Ticket.query \
        .options(
            db.joinedload('category'),
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('owned_by'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
        ) \
        .get(ticket_id)


def get_tickets_with_details_for_party_paginated(party_id: PartyID, page: int,
                                                 per_page: int,
                                                 *, search_term=None
                                                ) -> Pagination:
    """Return the party's tickets to show on the specified page."""
    query = Ticket.query \
        .for_party(party_id) \
        .options(
            db.joinedload('category'),
            db.joinedload('owned_by'),
            db.joinedload('occupied_seat').joinedload('area'),
        )

    if search_term:
        ilike_pattern = '%{}%'.format(search_term)
        query = query \
            .filter(Ticket.code.ilike(ilike_pattern))

    return query \
        .order_by(Ticket.created_at) \
        .paginate(page, per_page)


def get_tickets_in_use_for_party_paginated(party_id: PartyID, page: int,
                                           per_page: int,
                                           *, search_term: Optional[str]=None
                                          ) -> Pagination:
    """Return the party's tickets which have a user assigned."""
    ticket_user = db.aliased(User)

    query = Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.revoked == False) \
        .filter(Ticket.used_by_id.isnot(None))

    if search_term:
        query = query \
            .filter(ticket_user.screen_name.ilike('%{}%'.format(search_term)))

    return query \
        .join(ticket_user, Ticket.used_by_id == ticket_user.id) \
        .order_by(db.func.lower(ticket_user.screen_name), Ticket.created_at) \
        .paginate(page, per_page)


def get_ticket_count_by_party_id() -> Dict[PartyID, int]:
    """Return ticket count (including 0) per party, indexed by party ID."""
    party = db.aliased(Party)

    subquery = db.session \
        .query(
            db.func.count(Ticket.id)
        ) \
        .join(Category) \
        .join(Party) \
        .filter(Party.id == party.id) \
        .filter(Ticket.revoked == False) \
        .subquery() \
        .as_scalar()

    party_ids_and_ticket_counts = db.session \
        .query(
            party.id,
            subquery
        ) \
        .all()

    return dict(party_ids_and_ticket_counts)


def count_revoked_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of revoked tickets for that party."""
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.revoked == True) \
        .count()


def count_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of "sold" (i.e. generated and not revoked)
    tickets for that party.
    """
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.revoked == False) \
        .count()


def count_tickets_checked_in_for_party(party_id: PartyID) -> int:
    """Return the number tickets for that party that were used to check
    in their respective user.
    """
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.user_checked_in == True) \
        .count()
