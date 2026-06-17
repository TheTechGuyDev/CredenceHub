import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

# Login manager settings
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        if config_name == 'development':
            config_name = 'development'
        else:
            config_name = 'production'

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Create upload folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

    from app.deals import deals as deals_blueprint
    app.register_blueprint(deals_blueprint, url_prefix='/deals')

    from app.construction import construction as construction_blueprint
    app.register_blueprint(construction_blueprint, url_prefix='/construction')

    from app.projects import projects as projects_blueprint
    app.register_blueprint(projects_blueprint, url_prefix='/projects')

    from app.documents import documents as documents_blueprint
    app.register_blueprint(documents_blueprint, url_prefix='/documents')

    from app.marketing import marketing as marketing_blueprint
    app.register_blueprint(marketing_blueprint, url_prefix='/marketing')

    from app.funding import funding as funding_blueprint
    app.register_blueprint(funding_blueprint, url_prefix='/funding')

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # Register main/landing blueprint
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app