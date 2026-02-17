from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    # In a real app, we might want to rollback the db session here
    from app import db
    db.session.rollback()
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/404.html'), 403 # Hide 403 as 404 for security or use specific 403 template
