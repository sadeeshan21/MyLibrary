from app import db
from app.models.models import Book, Category


class BookError(Exception):
    """Raised when a book add/edit request is invalid."""
    pass


def add_book(title, author, isbn, total_copies, shelf_location, category_id):
    existing = Book.query.filter_by(isbn=isbn).first()
    if existing:
        raise BookError("A book with this ISBN already exists.")

    new_book = Book(
        title=title,
        author=author,
        isbn=isbn,
        total_copies=total_copies,
        shelf_location=shelf_location,
        category_category_id=category_id
    )
    db.session.add(new_book)
    db.session.commit()
    return new_book


def update_book(book_id, title, author, isbn, total_copies, shelf_location, category_id):
    book = Book.query.get(book_id)
    if book is None:
        raise BookError("Book not found.")

    book.title = title
    book.author = author
    book.isbn = isbn
    book.total_copies = total_copies
    book.shelf_location = shelf_location
    book.category_category_id = category_id

    db.session.commit()
    return book