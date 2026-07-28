from flask import Blueprint, render_template
from app.models.models import Book, BookCopy

book_bp = Blueprint('book_bp', __name__)

@book_bp.route('/books')
def list_books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

@book_bp.route('/books/available')
def available_books():
    available_copies = BookCopy.query.filter_by(copy_status='available').all()
    return render_template('available_books.html', copies=available_copies)