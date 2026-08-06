from flask import Blueprint, render_template
from app.models.models import Book, BookCopy
from flask import Blueprint, render_template, request
from app import db

book_bp = Blueprint('book_bp', __name__)

from flask import Blueprint, render_template, request

@book_bp.route('/books')
def list_books():
    search_query = request.args.get('q', '').strip()

    query = Book.query
    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(Book.title.ilike(like_pattern), Book.author.ilike(like_pattern))
        )

    all_books = query.all()
    return render_template('books.html', books=all_books, search_query=search_query)
@book_bp.route('/books/available')
def available_books():
    available_copies = BookCopy.query.filter_by(copy_status='available').all()
    return render_template('available_books.html', copies=available_copies)