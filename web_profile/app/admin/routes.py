from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import secrets
from app import db, login, limiter
from app.models import User, Berita, Agenda, Galeri, Pengaturan
from app.admin.forms import LoginForm, BeritaForm, AgendaForm, GaleriForm, PengaturanForm
from app.services.image_service import ImageService

bp = Blueprint('admin', __name__, url_prefix='/admin')

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Username atau password salah', 'danger')
    return render_template('admin/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    total_berita = Berita.query.count()
    total_agenda = Agenda.query.count()
    total_galeri = Galeri.query.count()
    return render_template('admin/dashboard.html', total_berita=total_berita, total_agenda=total_agenda, total_galeri=total_galeri)

# --- Berita CRUD ---
@bp.route('/berita')
@login_required
def berita_list():
    beritas = Berita.query.order_by(Berita.tanggal.desc()).all()
    return render_template('admin/berita_list.html', beritas=beritas)

@bp.route('/berita/add', methods=['GET', 'POST'])
@login_required
def berita_add():
    form = BeritaForm()
    if form.validate_on_submit():
        gambar_file = "https://picsum.photos/seed/default/800/400"
        if form.gambar.data:
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'berita')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/berita_form.html', form=form, title='Tambah Berita')
            
        berita = Berita(
            judul=form.judul.data,
            slug=form.slug.data,
            konten=form.konten.data,
            gambar=gambar_file,
            status=form.status.data,
            kategori=form.kategori.data,
            penulis=current_user.username
        )
        db.session.add(berita)
        db.session.commit()
        flash('Berita berhasil ditambahkan', 'success')
        return redirect(url_for('admin.berita_list'))
    return render_template('admin/berita_form.html', form=form, title='Tambah Berita')

@bp.route('/berita/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def berita_edit(id):
    berita = Berita.query.get_or_404(id)
    form = BeritaForm(obj=berita)
    if form.validate_on_submit():
        if form.gambar.data:
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'berita')
                berita.gambar = gambar_file
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/berita_form.html', form=form, title='Edit Berita')
            
        berita.judul = form.judul.data
        berita.slug = form.slug.data
        berita.konten = form.konten.data
        berita.status = form.status.data
        berita.kategori = form.kategori.data
        
        db.session.commit()
        flash('Berita berhasil diupdate', 'success')
        return redirect(url_for('admin.berita_list'))
    return render_template('admin/berita_form.html', form=form, title='Edit Berita')

@bp.route('/berita/delete/<int:id>', methods=['POST'])
@login_required
def berita_delete(id):
    berita = Berita.query.get_or_404(id)
    db.session.delete(berita)
    db.session.commit()
    flash('Berita berhasil dihapus', 'success')
    return redirect(url_for('admin.berita_list'))

# --- Agenda CRUD ---
@bp.route('/agenda')
@login_required
def agenda_list():
    agendas = Agenda.query.order_by(Agenda.tanggal_mulai.desc()).all()
    return render_template('admin/agenda_list.html', agendas=agendas)

@bp.route('/agenda/add', methods=['GET', 'POST'])
@login_required
def agenda_add():
    form = AgendaForm()
    if form.validate_on_submit():
        agenda = Agenda(
            nama_kegiatan=form.nama_kegiatan.data,
            tanggal_mulai=form.tanggal_mulai.data,
            tanggal_selesai=form.tanggal_selesai.data,
            lokasi=form.lokasi.data,
            deskripsi=form.deskripsi.data
        )
        db.session.add(agenda)
        db.session.commit()
        flash('Agenda berhasil ditambahkan', 'success')
        return redirect(url_for('admin.agenda_list'))
    return render_template('admin/agenda_form.html', form=form, title='Tambah Agenda')

@bp.route('/agenda/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def agenda_edit(id):
    agenda = Agenda.query.get_or_404(id)
    form = AgendaForm(obj=agenda)
    if form.validate_on_submit():
        form.populate_obj(agenda)
        db.session.commit()
        flash('Agenda berhasil diupdate', 'success')
        return redirect(url_for('admin.agenda_list'))
    return render_template('admin/agenda_form.html', form=form, title='Edit Agenda')

@bp.route('/agenda/delete/<int:id>', methods=['POST'])
@login_required
def agenda_delete(id):
    agenda = Agenda.query.get_or_404(id)
    db.session.delete(agenda)
    db.session.commit()
    flash('Agenda berhasil dihapus', 'success')
    return redirect(url_for('admin.agenda_list'))

# --- Galeri CRUD ---
@bp.route('/galeri')
@login_required
def galeri_list():
    galeris = Galeri.query.order_by(Galeri.tanggal.desc()).all()
    return render_template('admin/galeri_list.html', galeris=galeris)

@bp.route('/galeri/add', methods=['GET', 'POST'])
@login_required
def galeri_add():
    form = GaleriForm()
    if form.validate_on_submit():
        gambar_file = "https://picsum.photos/seed/default/800/600"
        if form.gambar.data:
            gambar_file = save_picture(form.gambar.data, 'galeri')
            
        galeri = Galeri(
            judul=form.judul.data,
            gambar=gambar_file,
            kategori=form.kategori.data,
            deskripsi=form.deskripsi.data
        )
        db.session.add(galeri)
        db.session.commit()
        flash('Foto berhasil ditambahkan ke galeri', 'success')
        return redirect(url_for('admin.galeri_list'))
    return render_template('admin/galeri_form.html', form=form, title='Tambah Foto')

@bp.route('/galeri/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def galeri_edit(id):
    galeri = Galeri.query.get_or_404(id)
    form = GaleriForm(obj=galeri)
    if form.validate_on_submit():
        if form.gambar.data:
            gambar_file = save_picture(form.gambar.data, 'galeri')
            galeri.gambar = gambar_file
            
        galeri.judul = form.judul.data
        galeri.kategori = form.kategori.data
        galeri.deskripsi = form.deskripsi.data
        
        db.session.commit()
        flash('Foto berhasil diupdate', 'success')
        return redirect(url_for('admin.galeri_list'))
    return render_template('admin/galeri_form.html', form=form, title='Edit Foto')

@bp.route('/galeri/delete/<int:id>', methods=['POST'])
@login_required
def galeri_delete(id):
    galeri = Galeri.query.get_or_404(id)
    db.session.delete(galeri)
    db.session.commit()
    flash('Galeri berhasil dihapus', 'success')
    return redirect(url_for('admin.galeri_list'))

# --- Pengaturan CRUD ---
@bp.route('/pengaturan', methods=['GET', 'POST'])
@login_required
def pengaturan():
    pengaturan = Pengaturan.query.first()
    if not pengaturan:
        pengaturan = Pengaturan()
        db.session.add(pengaturan)
        db.session.commit()
    
    form = PengaturanForm(obj=pengaturan)
    if form.validate_on_submit():
        form.populate_obj(pengaturan)
        db.session.commit()
        flash('Pengaturan berhasil disimpan', 'success')
        return redirect(url_for('admin.pengaturan'))
        
    return render_template('admin/pengaturan.html', form=form)
