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
    all_seats = Seat.query.filter_by(seat_status='active').all()
    return render_template('seats.html', seats=all_seats)




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
    start_time = datetime.strptime(request.form['start_time'], '%H:%M:%S').time()
    end_time = datetime.strptime(request.form['end_time'], '%H:%M:%S').time()

    try:
        book_seat(current_user.user_id, seat_id, booking_date, start_time, end_time)
        flash('Seat booked successfully!')
    except SeatBookingError as e:
        flash(str(e))

    return redirect(url_for('student_bp.seat_availability', seat_id=seat_id, date=booking_date_str))

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