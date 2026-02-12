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
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # Konfigurasi Keamanan Cookie (Default untuk Production)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_SECURE = True  # Uncomment saat deploy HTTPS

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False # Localhost biasanya HTTP

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True # Wajib HTTPS di production
