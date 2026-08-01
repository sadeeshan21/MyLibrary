from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.borrow_service import borrow_book, return_book, BorrowError
from app.models.models import Book, BorrowedBook
from datetime import date, datetime
from app.services.seat_service import book_seat, cancel_booking, SeatBookingError
from app.models.models import Seat, SeatBooking, SeatZone
from app.services.reservation_service import reserve_book, cancel_reservation, ReservationError
from app.models.models import Reservation
from app.services.seat_service import get_seat_availability
from datetime import datetime as dt
from app.services.seat_service import get_seat_availability, book_seat, cancel_booking, SeatBookingError, get_seats_with_today_status
from app.services.seat_service import LIBRARY_HOURS, get_seats_status_for_slot
from datetime import datetime as dt, timedelta
from datetime import datetime, date, time

student_bp = Blueprint('student_bp', __name__)

@student_bp.route('/books/<int:book_id>/reserve', methods=['POST'])
@login_required
def reserve(book_id):
    try:
        reserve_book(current_user.user_id, book_id)
        flash('Book reserved! You are in the queue.')
    except ReservationError as e:
        flash(str(e))
    return redirect(url_for('book_bp.list_books'))


@student_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation_route(reservation_id):
    try:
        cancel_reservation(reservation_id, current_user.user_id)
        flash('Reservation cancelled.')
    except ReservationError as e:
        flash(str(e))
    return redirect(url_for('student_bp.my_reservations'))


@student_bp.route('/my-reservations')
@login_required
def my_reservations():
    my_res = Reservation.query.filter_by(user_user_id=current_user.user_id).all()
    return render_template('my_reservations.html', reservations=my_res)

@student_bp.route('/student/dashboard')
@login_required
def dashboard():
    return render_template('student_dashboard.html', user=current_user)


@student_bp.route('/books/<int:book_id>/borrow', methods=['POST'])
@login_required
def borrow(book_id):
    try:
        borrow_book(current_user.user_id, book_id)
        flash('Book borrowed successfully!')
    except BorrowError as e:
        flash(str(e))
    return redirect(url_for('book_bp.list_books'))


@student_bp.route('/borrowed-books/<int:borrow_id>/return', methods=['POST'])
@login_required
def return_book_route(borrow_id):
    try:
        return_book(borrow_id)
        flash('Book returned successfully!')
    except BorrowError as e:
        flash(str(e))
    return redirect(url_for('student_bp.my_books'))


@student_bp.route('/my-books')
@login_required
def my_books():
    my_borrowed = BorrowedBook.query.filter_by(user_user_id=current_user.user_id).all()
    return render_template('my_books.html', borrowed_books=my_borrowed)


@student_bp.route('/seats')
@login_required
def list_seats():
    all_seats = Seat.query.filter_by(seat_status='active').filter(Seat.desk_type.isnot(None)).all()

    quad_seats = [s for s in all_seats if s.desk_type == 'quad']
    pair_seats = [s for s in all_seats if s.desk_type == 'pair']
    single_seats = [s for s in all_seats if s.desk_type == 'single']

    # Group quad/pair seats by their desk
    from itertools import groupby
    quad_desks = {k: list(v) for k, v in groupby(sorted(quad_seats, key=lambda s: s.desk_group), key=lambda s: s.desk_group)}
    pair_desks = {k: list(v) for k, v in groupby(sorted(pair_seats, key=lambda s: s.desk_group), key=lambda s: s.desk_group)}

    seat_status = get_seats_with_today_status(all_seats)

    return render_template('seats.html', quad_desks=quad_desks, pair_desks=pair_desks, single_seats=single_seats, seat_status=seat_status, total_seats=len(all_seats))



@student_bp.route('/my-seat-bookings')
@login_required
def my_seat_bookings():
    my_bookings = SeatBooking.query.filter_by(user_user_id=current_user.user_id).all()
    return render_template('my_seat_bookings.html', bookings=my_bookings)


@student_bp.route('/seat-bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_seat_booking_route(booking_id):
    try:
        cancel_booking(booking_id, current_user.user_id)
        flash('Booking cancelled.')
    except SeatBookingError as e:
        flash(str(e))
    return redirect(url_for('student_bp.my_seat_bookings'))


@student_bp.route('/seats/<int:seat_id>/book', methods=['POST'])
@login_required
def book_seat_route(seat_id):
    booking_date_str = request.form['booking_date']
    booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
    start_time_str = request.form['start_time']
    start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
    end_time = datetime.strptime(request.form['end_time'], '%H:%M:%S').time()

    try:
        book_seat(current_user.user_id, seat_id, booking_date, start_time, end_time)
        flash('Seat booked successfully!')
    except SeatBookingError as e:
        flash(str(e))

    return redirect(url_for('student_bp.seating_plan', date=booking_date_str, start=start_time_str))

@student_bp.route('/seats/<int:seat_id>/availability')
@login_required
def seat_availability(seat_id):
    booking_date_str = request.args.get('date')
    if booking_date_str:
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
    else:
        booking_date = date.today()

    seat = Seat.query.get_or_404(seat_id)
    slots = get_seat_availability(seat_id, booking_date)

    return render_template('seat_availability.html', seat=seat, booking_date=booking_date, slots=slots)

from app.services.seat_service import LIBRARY_HOURS, get_seats_status_for_slot

@student_bp.route('/seats/select-time', methods=['GET', 'POST'])
@login_required
def select_seat_time():
    if request.method == 'POST':
        selected_date = request.form['booking_date']
        selected_start = request.form['selected_slot']  # e.g. "09:00:00"
        return redirect(url_for('student_bp.seating_plan', date=selected_date, start=selected_start))

    today_str = date.today().isoformat()
    slots = [{'start': time(h, 0), 'end': time(h+1, 0)} for h, _ in LIBRARY_HOURS]
    return render_template('select_seat_time.html', slots=slots, today=today_str)


@student_bp.route('/seats/plan')
@login_required
def seating_plan():
    date_str = request.args.get('date')
    start_str = request.args.get('start')

    if not date_str or not start_str:
        return redirect(url_for('student_bp.select_seat_time'))

    booking_date = dt.strptime(date_str, '%Y-%m-%d').date()
    start_time_obj = dt.strptime(start_str, '%H:%M:%S').time()
    end_dt = dt.combine(booking_date, start_time_obj) + timedelta(hours=1)
    end_time_obj = end_dt.time()

    all_seats = Seat.query.filter_by(seat_status='active').filter(Seat.desk_type.isnot(None)).all()

    quad_seats = [s for s in all_seats if s.desk_type == 'quad']
    pair_seats = [s for s in all_seats if s.desk_type == 'pair']
    single_seats = [s for s in all_seats if s.desk_type == 'single']

    from itertools import groupby
    quad_desks = {k: list(v) for k, v in groupby(sorted(quad_seats, key=lambda s: s.desk_group), key=lambda s: s.desk_group)}
    pair_desks = {k: list(v) for k, v in groupby(sorted(pair_seats, key=lambda s: s.desk_group), key=lambda s: s.desk_group)}

    seat_status = get_seats_status_for_slot(all_seats, booking_date, start_time_obj, end_time_obj)

    return render_template('seating_plan.html',
        quad_desks=quad_desks, pair_desks=pair_desks, single_seats=single_seats,
        seat_status=seat_status, total_seats=len(all_seats),
        booking_date=date_str, start_time=start_str, end_time=end_time_obj.strftime('%H:%M:%S'),
        display_start=start_time_obj.strftime('%H:%M'), display_end=end_time_obj.strftime('%H:%M')
    )