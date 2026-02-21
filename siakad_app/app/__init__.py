from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache
from flask_compress import Compress
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()
# Use default limits, but allow higher limits for admin routes
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
talisman = Talisman()
cache = Cache()
compress = Compress()

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
    compress.init_app(app)

    # Use ProxyFix to support X-Forwarded-For headers from Nginx
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    
    # Configure Talisman (Security Headers)
    # Note: content_security_policy needs careful tuning for external scripts (like FontAwesome, Google Fonts, etc.)
    csp = {
        'default-src': ["'self'", 'https://cdnjs.cloudflare.com', 'https://fonts.googleapis.com', 'https://fonts.gstatic.com', 'https://cdn.jsdelivr.net', 'https://kit.fontawesome.com', 'https://loremflickr.com', 'https://source.unsplash.com', 'https://images.unsplash.com', 'https://placehold.co', 'https://picsum.photos', 'https://fastly.picsum.photos', 'https://ui-avatars.com', 'https://demos.creative-tim.com', 'https://buttons.github.io'],
        'script-src': ["'self'", "'unsafe-inline'", 'https://cdn.jsdelivr.net', 'https://kit.fontawesome.com', 'https://demos.creative-tim.com', 'https://buttons.github.io', 'https://cdnjs.cloudflare.com'],
        'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://cdn.jsdelivr.net', 'https://demos.creative-tim.com', 'https://cdnjs.cloudflare.com'],
        'img-src': ["'self'", 'data:', 'https://loremflickr.com', 'https://source.unsplash.com', 'https://images.unsplash.com', 'https://placehold.co', 'https://picsum.photos', 'https://fastly.picsum.photos', 'https://ui-avatars.com', 'https://demos.creative-tim.com'],
        'font-src': ["'self'", 'https://fonts.gstatic.com', 'https://cdnjs.cloudflare.com', 'https://demos.creative-tim.com'],
        'frame-src': ["'self'", 'https://www.google.com', 'https://maps.google.com']
    }
    
    # Relaxing security policies to allow external images (fix ORB/CORB issues) - Aligned with Web Profile
    talisman.init_app(
        app, 
        content_security_policy=csp, 
        force_https=not (app.debug or app.testing),
        permissions_policy={}, 
        x_content_type_options='nosniff',
        referrer_policy='no-referrer-when-downgrade',
        # Disable COEP/COOP to prevent ORB blocking external images
        feature_policy=None,
        content_security_policy_report_only=False,
        strict_transport_security=False
    )
    
    # Manually remove headers that trigger strict blocking if Talisman sets them
    @app.after_request
    def remove_strict_headers(response):
        response.headers.pop('Cross-Origin-Embedder-Policy', None)
        response.headers.pop('Cross-Origin-Opener-Policy', None)
        response.headers.pop('Cross-Origin-Resource-Policy', None)
        return response

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
