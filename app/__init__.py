from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask_mail import Mail
from config import Config
# Replace any existing bootstrap imports with:
from flask_bootstrap import Bootstrap5

def create_app():
    app = Flask(__name__)
    # ... other configs ...
    Bootstrap5(app)  # Initialize after app creation
    return app

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.vendor import bp as vendor_bp
    app.register_blueprint(vendor_bp, url_prefix='/vendor')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    # Create tables
    with app.app_context():
        db.create_all()

    return app