from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils import role_required
from app.models.models import Book, BookCopy, BorrowedBook, SeatBooking, Reservation, User
from datetime import date
from flask import request, redirect, url_for, flash
from app.services.reservation_service import approve_reservation, reject_reservation, ReservationError
from app.models.models import Reservation
from app.services.book_service import add_book, update_book, BookError
from app.services.seat_service import approve_seat_booking, reject_seat_booking, SeatBookingActionError
from app.models.models import SeatBooking
from app.models.models import Book, BookCopy, BorrowedBook, SeatBooking, Reservation, User, Category
from app.services.borrow_service import mark_overdue_loans
from flask import Response
import csv
import io
from app import db

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

@librarian_bp.route('/librarian/books')
@login_required
@role_required('librarian')
def manage_books():
    all_books = Book.query.all()
    all_categories = Category.query.all()
    return render_template('manage_books.html', books=all_books, categories=all_categories)

@librarian_bp.route('/librarian/books/add', methods=['GET', 'POST'])
@login_required
@role_required('librarian')
def add_book_route():
    if request.method == 'POST':
        try:
            add_book(
                title=request.form['title'],
                author=request.form['author'],
                isbn=request.form['isbn'],
                total_copies=int(request.form['total_copies']),
                shelf_location=request.form['shelf_location'],
                category_id=int(request.form['category_id'])
            )
            flash('Book added successfully!')
            return redirect(url_for('librarian_bp.manage_books'))
        except BookError as e:
            flash(str(e))

    all_categories = Category.query.all()
    return render_template('book_form.html', book=None, categories=all_categories)


@librarian_bp.route('/librarian/books/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('librarian')
def edit_book_route(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        try:
            update_book(
                book_id=book_id,
                title=request.form['title'],
                author=request.form['author'],
                isbn=request.form['isbn'],
                total_copies=int(request.form['total_copies']),
                shelf_location=request.form['shelf_location'],
                category_id=int(request.form['category_id'])
            )
            flash('Book updated successfully!')
            return redirect(url_for('librarian_bp.manage_books'))
        except BookError as e:
            flash(str(e))

    all_categories = Category.query.all()
    return render_template('book_form.html', book=book, categories=all_categories)

@librarian_bp.route('/librarian/seat-bookings')
@login_required
@role_required('librarian')
def manage_seat_bookings():
    pending = SeatBooking.query.filter_by(status='pending').all()
    return render_template('manage_seat_bookings.html', bookings=pending)


@librarian_bp.route('/librarian/seat-bookings/<int:booking_id>/approve', methods=['POST'])
@login_required
@role_required('librarian')
def approve_seat_booking_route(booking_id):
    try:
        approve_seat_booking(booking_id)
        flash('Seat booking approved.')
    except SeatBookingActionError as e:
        flash(str(e))
    return redirect(url_for('librarian_bp.manage_seat_bookings'))


@librarian_bp.route('/librarian/seat-bookings/<int:booking_id>/reject', methods=['POST'])
@login_required
@role_required('librarian')
def reject_seat_booking_route(booking_id):
    try:
        reject_seat_booking(booking_id)
        flash('Seat booking rejected.')
    except SeatBookingActionError as e:
        flash(str(e))
    return redirect(url_for('librarian_bp.manage_seat_bookings'))


@librarian_bp.route('/librarian/students')
@login_required
@role_required('librarian')
def manage_students():
    students = User.query.filter_by(role='student').all()
    return render_template('manage_students.html', students=students)


@librarian_bp.route('/librarian/borrowed-books')
@login_required
@role_required('librarian')
def manage_borrowed_books():
    filter_status = request.args.get('filter')

    query = BorrowedBook.query
    if filter_status == 'overdue':
        query = query.filter_by(status='overdue')
    elif filter_status == 'active':
        query = query.filter_by(status='active')

    records = query.all()
    return render_template('manage_borrowed_books.html', records=records, filter_status=filter_status)


@librarian_bp.route('/librarian/seat-bookings/today')
@login_required
@role_required('librarian')
def todays_seat_bookings():
    today_bookings = SeatBooking.query.filter_by(
        booking_date=date.today(),
        status='confirmed'
    ).all()
    return render_template('todays_seat_bookings.html', bookings=today_bookings)

@librarian_bp.route('/librarian/run-overdue-check', methods=['POST'])
@login_required
@role_required('librarian')
def run_overdue_check():
    count = mark_overdue_loans()
    flash(f'{count} loan(s) marked as overdue.')
    return redirect(url_for('librarian_bp.dashboard'))


@librarian_bp.route('/librarian/reports/overdue')
@login_required
@role_required('librarian')
def export_overdue_report():
    overdue = BorrowedBook.query.filter_by(status='overdue').all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Borrower', 'Role', 'Book', 'Borrow Date', 'Due Date', 'Fine Amount'])

    for r in overdue:
        writer.writerow([
            r.user.name, r.user.role, r.book_copy.book.title,
            r.borrow_date, r.due_date, r.fine_amount
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=overdue_report.csv'}
    )


@librarian_bp.route('/librarian/reports/most-borrowed')
@login_required
@role_required('librarian')
def export_most_borrowed_report():
    from app.models.models import BookCopy
    results = db.session.query(
        Book.title, db.func.count(BorrowedBook.borrow_id).label('times_borrowed')
    ).join(BookCopy, BookCopy.book_book_id == Book.book_id
    ).join(BorrowedBook, BorrowedBook.book_copy_copy_id == BookCopy.copy_id
    ).group_by(Book.book_id, Book.title
    ).order_by(db.func.count(BorrowedBook.borrow_id).desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Book Title', 'Times Borrowed'])
    for title, count in results:
        writer.writerow([title, count])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=most_borrowed_report.csv'}
    )