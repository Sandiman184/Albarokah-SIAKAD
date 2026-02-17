from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.audit import AuditLog
from app.decorators import admin_required

bp = Blueprint('audit', __name__, url_prefix='/audit')

@bp.route('/logs')
@login_required
@admin_required
def logs_list():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('master/audit_list.html', title='Audit Logs', logs=logs)
