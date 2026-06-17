import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'credencehub-dev-secret-2026'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///credencehub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Upload settings
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB max file size
    UPLOAD_FOLDER = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'gif'}
    
    # App settings
    PLATFORM_NAME = 'CredenceHub'
    PLATFORM_VERSION = '1.0.0'
    PRIMARY_COLOR = '#0F2D5E'
    ACCENT_COLOR = '#F5A623'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        # Fix PostgreSQL URL for Railway (they use postgres:// but SQLAlchemy needs postgresql://)
        db_url = os.environ.get('DATABASE_URL', '')
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        cls.SQLALCHEMY_DATABASE_URI = db_url


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}