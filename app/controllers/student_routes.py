from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.borrow_service import borrow_book, return_book, BorrowError
from app.models.models import Book, BorrowedBook

student_bp = Blueprint('student_bp', __name__)

from app.services.reservation_service import reserve_book, cancel_reservation, ReservationError
from app.models.models import Reservation

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