from datetime import date, time
from sqlalchemy import and_
from app import db
from app.models.models import Seat, SeatBooking
from datetime import date, time, datetime

class SeatBookingError(Exception):
    """Raised when a seat booking request can't be fulfilled."""
    pass


def book_seat(user_id, seat_id, booking_date, start_time, end_time):
    now = datetime.now()

    if booking_date < now.date():
        raise SeatBookingError("You cannot book a seat for a past date.")

    if booking_date == now.date() and start_time < now.time():
        raise SeatBookingError("You cannot book a seat for a time that has already passed today.")

    if end_time <= start_time:
        raise SeatBookingError("End time must be after start time.")

    # Start a transaction, and lock any overlapping rows for this seat/date
    conflicting_bookings = db.session.query(SeatBooking).filter(
        SeatBooking.seat_seat_id == seat_id,
        SeatBooking.booking_date == booking_date,
        SeatBooking.status != 'cancelled',
        SeatBooking.start_time < end_time,
        SeatBooking.end_time > start_time
    ).with_for_update().all()

    if conflicting_bookings:
        raise SeatBookingError("This seat is already booked for an overlapping time slot.")

    new_booking = SeatBooking(
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        status='confirmed',
        seat_seat_id=seat_id,
        user_user_id=user_id
    )
    db.session.add(new_booking)
    db.session.commit()

    return new_booking


def cancel_booking(booking_id, user_id):
    booking = SeatBooking.query.get(booking_id)

    if booking is None:
        raise SeatBookingError("Booking not found.")

    if booking.user_user_id != user_id:
        raise SeatBookingError("You can only cancel your own bookings.")

    booking.status = 'cancelled'
    db.session.commit()

    return booking