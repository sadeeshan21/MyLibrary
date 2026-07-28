from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config


db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models.models import User
    return User.query.get(user_id)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'  # redirect here if login is required but user isn't logged in

    with app.app_context():
        from app.models import models

    from app.controllers.book_routes import book_bp
    app.register_blueprint(book_bp)

    from app.controllers.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.controllers.student_routes import student_bp
    app.register_blueprint(student_bp)

    from app.controllers.librarian_routes import librarian_bp
    app.register_blueprint(librarian_bp)

    return app