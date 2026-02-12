from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
talisman = Talisman()
login = LoginManager()
login.login_view = 'admin.login'
login.login_message = 'Silakan login untuk mengakses halaman admin.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login.init_app(app)
    
    # Configure Talisman (Security Headers)
    csp = {
        'default-src': ["'self'", 'https://cdnjs.cloudflare.com', 'https://fonts.googleapis.com', 'https://fonts.gstatic.com', 'https://cdn.jsdelivr.net', 'https://kit.fontawesome.com', 'https://loremflickr.com', 'https://source.unsplash.com', 'https://images.unsplash.com', 'https://placehold.co', 'https://picsum.photos', 'https://fastly.picsum.photos', 'https://ui-avatars.com'],
        'script-src': ["'self'", "'unsafe-inline'", 'https://cdn.jsdelivr.net', 'https://kit.fontawesome.com'],
        'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com', 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com'],
        'img-src': ["'self'", 'data:', 'https://loremflickr.com', 'https://source.unsplash.com', 'https://images.unsplash.com', 'https://placehold.co', 'https://picsum.photos', 'https://fastly.picsum.photos', 'https://ui-avatars.com'],
        'font-src': ["'self'", 'https://fonts.gstatic.com', 'https://cdnjs.cloudflare.com']
    }
    # Relaxing security policies to allow external images (fix ORB/CORB issues)
    talisman.init_app(
        app, 
        content_security_policy=csp, 
        force_https=not app.debug,
        permissions_policy={}, 
        x_content_type_options=None,
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

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.admin.routes import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app
