from datetime import datetime
from app import db
from app.models.models import Reservation, BookCopy


class ReservationError(Exception):
    """Raised when a reservation request can't be fulfilled."""
    pass


def reserve_book(user_id, book_id):
    # Sanity check: don't let someone reserve a book that actually has a copy free right now
    available_copy = BookCopy.query.filter_by(
        book_book_id=book_id,
        copy_status='available'
    ).first()

    if available_copy is not None:
        raise ReservationError("This book currently has an available copy — please borrow it instead.")

    # Find current queue length for this book, to assign the next position
    current_queue_length = Reservation.query.filter_by(
        book_book_id=book_id,
        status='pending'
    ).count()

    new_reservation = Reservation(
        reservation_date=datetime.now(),
        status='pending',
        queue_position=current_queue_length + 1,
        user_user_id=user_id,
        book_book_id=book_id
    )

    db.session.add(new_reservation)
    db.session.commit()

    return new_reservation


def cancel_reservation(reservation_id, user_id):
    reservation = Reservation.query.get(reservation_id)

    if reservation is None:
        raise ReservationError("Reservation not found.")

    if reservation.user_user_id != user_id:
        raise ReservationError("You can only cancel your own reservations.")

    reservation.status = 'cancelled'
    db.session.commit()

    return reservation