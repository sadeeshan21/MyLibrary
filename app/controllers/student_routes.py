from flask import Blueprint, render_template
from flask_login import login_required, current_user

student_bp = Blueprint('student_bp', __name__)

@student_bp.route('/student/dashboard')
@login_required
def dashboard():
    return render_template('student_dashboard.html', user=current_user)