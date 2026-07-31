from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils import role_required
from app.models.models import Book, BookCopy, BorrowedBook, SeatBooking, Reservation, User
from datetime import date
from flask import request, redirect, url_for, flash
from app.services.reservation_service import approve_reservation, reject_reservation, ReservationError
from app.models.models import Reservation

librarian_bp = Blueprint('librarian_bp', __name__)


@librarian_bp.route('/librarian/dashboard')
@login_required
@role_required('librarian')
def dashboard():
    total_books = Book.query.count()
    total_students = User.query.filter_by(role='student').count()
    currently_borrowed = BorrowedBook.query.filter_by(status='active').count()
    overdue_count = BorrowedBook.query.filter_by(status='overdue').count()
    seats_booked_today = SeatBooking.query.filter_by(
        booking_date=date.today(),
        status='confirmed'
    ).count()
    pending_reservations = Reservation.query.filter_by(status='pending').count()

    stats = {
        'total_books': total_books,
        'total_students': total_students,
        'currently_borrowed': currently_borrowed,
        'overdue_count': overdue_count,
        'seats_booked_today': seats_booked_today,
        'pending_reservations': pending_reservations
    }

    return render_template('librarian_dashboard.html', user=current_user, stats=stats)

@librarian_bp.route('/librarian/reservations')
@login_required
@role_required('librarian')
def manage_reservations():
    pending = Reservation.query.filter_by(status='pending').all()
    return render_template('manage_reservations.html', reservations=pending)


@librarian_bp.route('/librarian/reservations/<int:reservation_id>/approve', methods=['POST'])
@login_required
@role_required('librarian')
def approve_reservation_route(reservation_id):
    try:
        approve_reservation(reservation_id)
        flash('Reservation approved.')
    except ReservationError as e:
        flash(str(e))
    return redirect(url_for('librarian_bp.manage_reservations'))


@librarian_bp.route('/librarian/reservations/<int:reservation_id>/reject', methods=['POST'])
@login_required
@role_required('librarian')
def reject_reservation_route(reservation_id):
    try:
        reject_reservation(reservation_id)
        flash('Reservation rejected.')
    except ReservationError as e:
        flash(str(e))
    return redirect(url_for('librarian_bp.manage_reservations'))