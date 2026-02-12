from app import db
from flask import Blueprint, render_template
from app.models import Berita, Agenda, Galeri, Pengaturan

bp = Blueprint('main', __name__)

@bp.context_processor
def inject_pengaturan():
    pengaturan = Pengaturan.query.first()
    return dict(pengaturan=pengaturan)

@bp.route('/')
def index():
    berita_terbaru = Berita.query.filter_by(status='published').order_by(Berita.tanggal.desc()).limit(3).all()
    return render_template('index.html', title='Beranda', beritas=berita_terbaru)

@bp.route('/profil')
def profil():
    return render_template('profil.html', title='Profil Pesantren')

@bp.route('/program')
def program():
    return render_template('program.html', title='Program Pendidikan')

@bp.route('/ppdb')
def ppdb():
    return render_template('ppdb.html', title='PPDB Online')

@bp.route('/berita')
def berita():
    beritas = Berita.query.filter_by(status='published').order_by(Berita.tanggal.desc()).all()
    agendas = Agenda.query.order_by(Agenda.tanggal_mulai.desc()).all()
    return render_template('berita.html', title='Berita & Agenda', beritas=beritas, agendas=agendas)

@bp.route('/berita/<slug>')
def berita_detail(slug):
    berita = Berita.query.filter_by(slug=slug).first_or_404()
    berita_lain = Berita.query.filter(Berita.id != berita.id, Berita.status == 'published').order_by(Berita.tanggal.desc()).limit(3).all()
    return render_template('berita_detail.html', title=berita.judul, berita=berita, berita_lain=berita_lain)

@bp.route('/galeri')
def galeri():
    galeris = Galeri.query.order_by(Galeri.tanggal.desc()).all()
    return render_template('galeri.html', title='Galeri Foto', galeris=galeris)

@bp.route('/kontak')
def kontak():
    return render_template('kontak.html', title='Kontak Kami')
