from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils import role_required
from app.models.models import Book, BookCopy, BorrowedBook, SeatBooking, Reservation, User
from datetime import date

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