from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import cache, db

bp = Blueprint('dashboard', __name__)

from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran
from app.models.audit import AuditLog
from app.models.keuangan import TransaksiKeuangan
from datetime import datetime, date
from sqlalchemy import func

@bp.route('/')
@bp.route('/dashboard')
@login_required
# @cache.cached(timeout=60, key_prefix='dashboard_stats_global') -- Disable cache to prevent role leakage and delay
def index():
    total_santri = Santri.query.filter_by(status='aktif').count()
    total_pengajar = Pengajar.query.count()
    total_kelas = Kelas.query.count()
    total_mapel = MataPelajaran.query.count()
    
    # Recent Activities
    recent_activities = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
    
    # Financial Summary (Current Month)
    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    
    # Optimize: Use SQL SUM instead of fetching all objects
    income_month = db.session.query(func.sum(TransaksiKeuangan.jumlah)).filter(
        TransaksiKeuangan.tanggal >= first_of_month, 
        TransaksiKeuangan.jenis == 'masuk'
    ).scalar() or 0
        
    return render_template('dashboard/index.html', 
                           title='Dashboard',
                           total_santri=total_santri,
                           total_pengajar=total_pengajar,
                           total_kelas=total_kelas,
                           total_mapel=total_mapel,
                           recent_activities=recent_activities,
                           income_month=income_month,
                           current_semester="Ganjil 2025/2026")
