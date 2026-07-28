from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models.models import User, Student, Faculty, Librarian
from datetime import datetime

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        new_user = User(
            user_id=user_id,
            name=name,
            email=email,
            password_hash=hashed_password,
            phone=phone,
            role=role,
            created_at=datetime.now()
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('auth_bp.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!')

            if user.role == 'librarian':
                return redirect(url_for('librarian_bp.dashboard'))  # placeholder until librarian dashboard exists
            else:
                return redirect(url_for('student_bp.dashboard'))  # placeholder until student dashboard exists

        flash('Invalid email or password.')
        return redirect(url_for('auth_bp.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth_bp.login'))