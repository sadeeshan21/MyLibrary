from app import db
from flask_login import UserMixin

class Category(db.Model):
    __tablename__ = 'category'
    
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    books = db.relationship('Book', backref='category')


class Book(db.Model):
    __tablename__ = 'book'
    
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False)
    shelf_location = db.Column(db.String(50))
    category_category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    
    copies = db.relationship('BookCopy', backref='book')


class BookCopy(db.Model):
    __tablename__ = 'book_copy'
    
    copy_id = db.Column(db.Integer, primary_key=True)
    copy_status = db.Column(db.Enum('available', 'borrowed', 'lost', 'maintenance'), nullable=False, default='available')
    acquired_date = db.Column(db.Date, nullable=False)
    book_book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
  
    def get_id(self):
        return self.user_id

    user_id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Enum('student', 'faculty', 'librarian'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    student = db.relationship('Student', backref='user', uselist=False)
    faculty = db.relationship('Faculty', backref='user', uselist=False)
    librarian = db.relationship('Librarian', backref='user', uselist=False)


class Student(db.Model):
    __tablename__ = 'student'
    
    user_id = db.Column(db.String(16), db.ForeignKey('user.user_id'), primary_key=True)
    student_id_number = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)


class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    user_id = db.Column(db.String(16), db.ForeignKey('user.user_id'), primary_key=True)
    staff_id_number = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)


class Librarian(db.Model):
    __tablename__ = 'librarian'
    
    user_id = db.Column(db.String(16), db.ForeignKey('user.user_id'), primary_key=True)
    staff_id_number = db.Column(db.String(20), nullable=False)
    shift = db.Column(db.Enum('morning', 'evening', 'night'), nullable=False)


class BorrowedBook(db.Model):
    __tablename__ = 'borrowed_book'
    
    borrow_id = db.Column(db.Integer, primary_key=True)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    fine_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    status = db.Column(db.Enum('active', 'returned', 'overdue'), nullable=False, default='active')
    user_user_id = db.Column(db.String(16), db.ForeignKey('user.user_id'), nullable=False)
    book_copy_copy_id = db.Column(db.Integer, db.ForeignKey('book_copy.copy_id'), nullable=False)

    user = db.relationship('User', backref='borrowed_books')
    book_copy = db.relationship('BookCopy', backref='borrow_records')


class Reservation(db.Model):
    __tablename__ = 'reservation'
    
    reservation_id = db.Column(db.Integer, primary_key=True)
    reservation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'fulfilled', 'cancelled'), nullable=False, default='pending')
    queue_position = db.Column(db.Integer, nullable=False)
    user_user_id = db.Column(db.String(16), db.ForeignKey('user.user_id'), nullable=False)
    book_book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)

    user = db.relationship('User', backref='reservations')
    book = db.relationship('Book', backref='reservations')


class SeatZone(db.Model):
    __tablename__ = 'seat_zone'
    
    zone_id = db.Column(db.Integer, primary_key=True)
    zone_name = db.Column(db.String(100), nullable=False)
    floor = db.Column(db.String(50), nullable=False)

    seats = db.relationship('Seat', backref='zone')


class Seat(db.Model):
    __tablename__ = 'seat'
    
    seat_id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_status = db.Column(db.Enum('active', 'maintenance'), nullable=False, default='active')
    seat_zone_zone_id = db.Column(db.Integer, db.ForeignKey('seat_zone.zone_id'), nullable=False)


class SeatBooking(db.Model):
    __tablename__ = 'seat_booking'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('confirmed', 'cancelled', 'no_show'), nullable=False, default='confirmed')
    seat_seat_id = db.Column(db.Integer, db.ForeignKey('seat.seat_id'), nullable=False)
    user_user_id = db.Column(db.String(16), db.ForeignKey('user.user_id'), nullable=False)

    seat = db.relationship('Seat', backref='bookings')
    user = db.relationship('User', backref='seat_bookings')