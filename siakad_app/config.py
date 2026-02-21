import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-wajib-ganti-nanti'
    # Default fallback to SQLite if Postgres not set, but blueprint mandates Postgres.
    # We keep SQLite fallback only for initial sanity check if Postgres isn't ready.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfigurasi Upload
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload (Increased for restore)

    # Konfigurasi Keamanan Cookie (Default untuk Production)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_SECURE = True  # Uncomment saat deploy HTTPS
    
    # Session Management
    PERMANENT_SESSION_LIFETIME = 1800 # 30 minutes in seconds
    
    # Caching Configuration
    # Use FileSystemCache to share cache between Gunicorn workers and persist across restarts
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'FileSystemCache'
    CACHE_DIR = os.path.join(basedir, 'cache')
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 1000
    
    # Compression Configuration
    COMPRESS_ALGORITHM = 'gzip'

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False # Localhost biasanya HTTP

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True # Wajib HTTPS di production
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Security checks for production
        import os
        if not os.environ.get('SECRET_KEY'):
             raise RuntimeError("SECRET_KEY environment variable is not set!")
        if not os.environ.get('DATABASE_URL'):
             raise RuntimeError("DATABASE_URL environment variable is not set!")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory DB for tests
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing
    SESSION_COOKIE_SECURE = False
    DEBUG = False
