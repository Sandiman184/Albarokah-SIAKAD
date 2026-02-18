from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import cache

bp = Blueprint('dashboard', __name__)

from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran

@bp.route('/')
@bp.route('/dashboard')
@login_required
@cache.cached(timeout=60, key_prefix='dashboard_stats_global')
def index():
    total_santri = Santri.query.count()
    total_pengajar = Pengajar.query.count()
    total_kelas = Kelas.query.count()
    total_mapel = MataPelajaran.query.count()
    
    return render_template('dashboard/index.html', 
                           title='Dashboard',
                           total_santri=total_santri,
                           total_pengajar=total_pengajar,
                           total_kelas=total_kelas,
                           total_mapel=total_mapel)
