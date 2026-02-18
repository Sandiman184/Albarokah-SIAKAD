from app import db, cache, limiter, mail
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from app.models import Berita, Agenda, Galeri, Pengaturan, Program, Pimpinan

bp = Blueprint('main', __name__)

@bp.context_processor
@cache.cached(timeout=300, key_prefix='global_pengaturan')
def inject_pengaturan():
    pengaturan = Pengaturan.query.first()
    return dict(pengaturan=pengaturan)

@bp.route('/')
@limiter.limit("30 per minute")
@cache.cached(timeout=60)
def index():
    berita_terbaru = Berita.query.filter_by(status='published').order_by(Berita.tanggal.desc()).limit(3).all()
    agenda_terbaru = Agenda.query.order_by(Agenda.tanggal_mulai.desc()).limit(3).all()
    programs = Program.query.filter_by(parent_id=None).order_by(Program.urutan.asc()).all()
    return render_template('index.html', title='Beranda', beritas=berita_terbaru, agendas=agenda_terbaru, programs=programs)

@bp.route('/profil')
@limiter.limit("30 per minute")
@cache.cached(timeout=300)
def profil():
    pimpinan = Pimpinan.query.order_by(Pimpinan.urutan.asc()).all()
    return render_template('profil.html', title='Profil Pesantren', pimpinan=pimpinan)

@bp.route('/program')
@limiter.limit("30 per minute")
@cache.cached(timeout=300)
def program():
    programs = Program.query.filter_by(parent_id=None).order_by(Program.urutan.asc()).all()
    return render_template('program.html', title='Program Pendidikan', programs=programs)

@bp.route('/ppdb')
@limiter.limit("30 per minute")
@cache.cached(timeout=300)
def ppdb():
    return render_template('ppdb.html', title='PPDB Online')

from sqlalchemy import func
from flask import request

@bp.route('/berita')
@limiter.limit("30 per minute")
# @cache.cached(timeout=60, query_string=True) # Disable cache for realtime updates
def berita():
    kategori_filter = request.args.get('kategori')
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    query = Berita.query.filter_by(status='published')
    
    if kategori_filter:
        query = query.filter_by(kategori=kategori_filter)
        
    pagination = query.order_by(Berita.tanggal.desc()).paginate(page=page, per_page=per_page, error_out=False)
    beritas = pagination.items
    
    agendas = Agenda.query.order_by(Agenda.tanggal_mulai.desc()).limit(5).all()
    
    # Calculate category counts
    # Get counts for active categories
    active_counts = dict(db.session.query(Berita.kategori, func.count(Berita.id)).filter_by(status='published').group_by(Berita.kategori).all())
    
    # Define standard categories to ensure they always appear
    standard_categories = ['berita', 'pengumuman', 'artikel']
    
    kategori_counts = []
    # Add standard categories with their counts (default 0)
    for cat in standard_categories:
        kategori_counts.append((cat, active_counts.get(cat, 0)))
        
    # Add any other categories found in DB that are not in standard list
    for cat, count in active_counts.items():
        if cat not in standard_categories:
            kategori_counts.append((cat, count))
    
    return render_template('berita.html', title='Berita & Agenda', beritas=beritas, pagination=pagination, agendas=agendas, kategori_counts=kategori_counts, current_kategori=kategori_filter)

@bp.route('/berita/<slug>')
@limiter.limit("30 per minute")
@cache.cached(timeout=600)
def berita_detail(slug):
    berita = Berita.query.filter_by(slug=slug).first_or_404()
    berita_lain = Berita.query.filter(Berita.id != berita.id, Berita.status == 'published').order_by(Berita.tanggal.desc()).limit(3).all()
    return render_template('berita_detail.html', title=berita.judul, berita=berita, berita_lain=berita_lain)

@bp.route('/galeri')
@limiter.limit("30 per minute")
# @cache.cached(timeout=300, query_string=True)
def galeri():
    page = request.args.get('page', 1, type=int)
    kategori_filter = request.args.get('kategori')
    per_page = 9
    
    query = Galeri.query
    
    if kategori_filter and kategori_filter != 'all':
        query = query.filter_by(kategori=kategori_filter)
        
    pagination = query.order_by(Galeri.tanggal.desc()).paginate(page=page, per_page=per_page, error_out=False)
    galeris = pagination.items
    
    return render_template('galeri.html', title='Galeri Foto', galeris=galeris, pagination=pagination, current_kategori=kategori_filter)

@bp.route('/kontak', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Stricter limit for contact form page
def kontak():
    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        subjek = request.form.get('subjek')
        pesan = request.form.get('pesan')
        
        if not all([nama, email, subjek, pesan]):
            flash('Harap lengkapi semua kolom!', 'danger')
        else:
            try:
                # Send email
                msg = Message(
                    subject=f"[Kontak Website] {subjek}",
                    sender=current_app.config['MAIL_DEFAULT_SENDER'],
                    recipients=['ppqalbarokahkarangjati@gmail.com'],
                    body=f"""
                    Pesan Baru dari Website Ponpes Al-Barokah
                    
                    Nama: {nama}
                    Email: {email}
                    
                    Pesan:
                    {pesan}
                    """
                )
                mail.send(msg)
                flash('Pesan Anda berhasil dikirim! Kami akan segera menghubungi Anda.', 'success')
            except Exception as e:
                current_app.logger.error(f"Error sending email: {e}")
                flash('Maaf, terjadi kesalahan saat mengirim pesan. Silakan coba lagi nanti atau hubungi kami via WhatsApp.', 'danger')
            
            return redirect(url_for('main.kontak'))
            
    return render_template('kontak.html', title='Kontak Kami')
