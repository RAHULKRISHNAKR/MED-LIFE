from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os
from datetime import datetime

# Initialize database and login manager globally
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Creates and configures the Flask app."""
    # Fix the template folder path to point to app/templates
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "routes.login"

    # Import models to prevent circular imports
    from app.models import User, SearchHistory, Allergy

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login session management."""
        return User.query.get(int(user_id))

    # Register blueprints (Import inside function to avoid circular imports)
    from app.routes import routes
    app.register_blueprint(routes)

    # Create database tables inside the application context
    with app.app_context():
        db.create_all()

    return app