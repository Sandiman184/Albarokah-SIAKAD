from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()
cache = Cache()

login.login_view = 'auth.login'
login.login_message = 'Silakan login untuk mengakses halaman ini.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # Configure Talisman (Security Headers)
    # Note: content_security_policy needs careful tuning for external scripts (like FontAwesome, Google Fonts, etc.)
    csp = {
        'default-src': ["'self'", 'https://cdnjs.cloudflare.com', 'https://fonts.googleapis.com', 'https://fonts.gstatic.com', 'https://demos.creative-tim.com', 'https://kit.fontawesome.com', 'https://buttons.github.io', 'https://ui-avatars.com'],
        'script-src': ["'self'", "'unsafe-inline'", 'https://cdnjs.cloudflare.com', 'https://kit.fontawesome.com', 'https://demos.creative-tim.com', 'https://buttons.github.io'],
        'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://demos.creative-tim.com', 'https://cdnjs.cloudflare.com'],
        'img-src': ["'self'", 'data:', 'https://ui-avatars.com', 'https://demos.creative-tim.com']
    }
    # Disable force_https in dev/debug mode to avoid issues on localhost
    talisman.init_app(app, content_security_policy=csp, force_https=not (app.debug or app.testing))

    # Logging Configuration
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler
        import os

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/siakad.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('SIAKAD Startup')

    # Register Blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.master import bp as master_bp
    app.register_blueprint(master_bp)

    from app.routes.akademik import bp as akademik_bp
    app.register_blueprint(akademik_bp)

    from app.routes.keuangan import bp as keuangan_bp
    app.register_blueprint(keuangan_bp)

    from app.routes.audit import bp as audit_bp
    app.register_blueprint(audit_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Import models to ensure they are registered with SQLAlchemy
    # We put this inside create_app or at bottom of file to avoid circular imports
    # But usually models import db from app, so db must be defined.
    # Models are imported here just so Alembic knows about them.
    from app import models

    return app
