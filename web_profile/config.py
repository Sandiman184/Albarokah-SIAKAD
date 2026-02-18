import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Generate a random secret key if not present, but better to be static for dev to avoid CSRF invalidation on restart
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-web-profile-albarokah-2026'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi Keamanan Cookie
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_SECURE = True  # Uncomment saat deploy HTTPS

    # Caching Configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    # Email Configuration
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'ppqalbarokahkarangjati@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'ppqalbarokahkarangjati@gmail.com'

    # Compression Configuration
    COMPRESS_ALGORITHM = 'gzip'

    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    @classmethod
    def init_app(cls, app):
        # Security checks for production
        import os
        if not os.environ.get('SECRET_KEY'):
             raise RuntimeError("SECRET_KEY environment variable is not set!")
        if not os.environ.get('DATABASE_URL'):
             # We might allow SQLite but warn, or enforce Postgres.
             # For now, enforce consistent secret key at least.
             pass
