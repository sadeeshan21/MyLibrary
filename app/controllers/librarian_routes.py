from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils import role_required



librarian_bp = Blueprint('librarian_bp', __name__)

@librarian_bp.route('/librarian/dashboard')
@login_required
@role_required('librarian')
def dashboard():
    return render_template('librarian_dashboard.html', user=current_user)