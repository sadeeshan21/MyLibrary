from datetime import date, timedelta
from app import db
from app.models.models import BookCopy, BorrowedBook


class BorrowError(Exception):
    """Raised when a borrow request can't be fulfilled."""
    pass


def borrow_book(user_id, book_id):
    # Find one available copy of this book
    available_copy = BookCopy.query.filter_by(
        book_book_id=book_id,
        copy_status='available'
    ).first()

    if available_copy is None:
        raise BorrowError("No available copies. You may reserve this book instead.")

    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=14)

    new_borrow = BorrowedBook(
        borrow_date=borrow_date,
        due_date=due_date,
        return_date=None,         
        fine_amount=0.00,
        status='active',
        user_user_id=user_id,
        book_copy_copy_id=available_copy.copy_id
    )

    db.session.add(new_borrow)
    db.session.commit()   

    return new_borrow


FINE_PER_DAY = 50.00  # LKR per day late — adjust to whatever your library charges

def return_book(borrow_id):
    borrow_record = BorrowedBook.query.get(borrow_id)

    if borrow_record is None:
        raise BorrowError("Borrow record not found.")

    if borrow_record.return_date is not None:
        raise BorrowError("This book has already been returned.")

    today = date.today()
    borrow_record.return_date = today   # this UPDATE fires trg_after_borrow_return

    days_late = (today - borrow_record.due_date).days
    if days_late > 0:
        borrow_record.fine_amount = round(days_late * FINE_PER_DAY, 2)

    borrow_record.status = 'returned'
    db.session.commit()

    return borrow_record

def mark_overdue_loans():
    """Scans active loans and flips any past their due date to 'overdue'."""
    today = date.today()
    overdue_candidates = BorrowedBook.query.filter(
        BorrowedBook.status == 'active',
        BorrowedBook.due_date < today
    ).all()

    for loan in overdue_candidates:
        loan.status = 'overdue'

    db.session.commit()
    return len(overdue_candidates)