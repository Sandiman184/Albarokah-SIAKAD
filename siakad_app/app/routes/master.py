from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
import datetime
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran
from app.models.konfigurasi import Konfigurasi
from app.models.user import User
from app.forms.master import SantriForm, PengajarForm, KelasForm, MapelForm, KonfigurasiForm
from app.forms.auth import UserForm, UserEditForm
from app.decorators import admin_required
from app.services.audit_service import log_audit

from app.services.backup_service import BackupService
import os
from flask import send_file
from werkzeug.utils import secure_filename
from app.utils import save_picture

bp = Blueprint('master', __name__, url_prefix='/master')

from app.models.keuangan import KonfigurasiLaporan

@bp.route('/konfigurasi', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('UPDATE', 'Konfigurasi')
def konfigurasi():
    config = Konfigurasi.query.first()
    config_keuangan = KonfigurasiLaporan.query.first()
    
    # Initialize form with data from both configs
    form = KonfigurasiForm(obj=config)
    
    # Pre-fill Keuangan fields if available
    if request.method == 'GET' and config_keuangan:
        form.kota_ttd.data = config_keuangan.kota_ttd
        form.nama_ttd.data = config_keuangan.nama_ttd
        form.jabatan_ttd.data = config_keuangan.jabatan_ttd
        form.nip_ttd.data = config_keuangan.nip_ttd
        form.pimpinan_ponpes_nama.data = config_keuangan.pimpinan_ponpes_nama
        form.pimpinan_ponpes_nip.data = config_keuangan.pimpinan_ponpes_nip
    
    if form.validate_on_submit():
        # Preserve old logo paths to prevent overwriting with None/Empty FileStorage
        old_logo_kemenag = config.logo_kemenag if config else None
        old_logo_lembaga = config.logo_lembaga if config else None

        if not config:
            config = Konfigurasi()
            db.session.add(config)
        
        if not config_keuangan:
            config_keuangan = KonfigurasiLaporan()
            db.session.add(config_keuangan)
            
        form.populate_obj(config)
        
        # Save Keuangan Fields
        config_keuangan.nama_lembaga = form.nama_lembaga.data
        config_keuangan.alamat_lembaga = form.alamat_lembaga.data
        config_keuangan.kota_ttd = form.kota_ttd.data
        config_keuangan.nama_ttd = form.nama_ttd.data
        config_keuangan.jabatan_ttd = form.jabatan_ttd.data
        config_keuangan.nip_ttd = form.nip_ttd.data
        config_keuangan.pimpinan_ponpes_nama = form.pimpinan_ponpes_nama.data
        config_keuangan.pimpinan_ponpes_nip = form.pimpinan_ponpes_nip.data
        
        # Handle file uploads
        upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        if form.logo_kemenag.data and getattr(form.logo_kemenag.data, 'filename', None):
            config.logo_kemenag = save_picture(form.logo_kemenag.data, folder='')
        else:
            # Restore old value if no new file uploaded
            config.logo_kemenag = old_logo_kemenag
            
        if form.logo_lembaga.data and getattr(form.logo_lembaga.data, 'filename', None):
            fn = save_picture(form.logo_lembaga.data, folder='')
            config.logo_lembaga = fn
            # Also update Keuangan logo (using same file for consistency)
            config_keuangan.logo_path = f"img/uploads/{fn}"
        else:
            # Restore old value if no new file uploaded
            config.logo_lembaga = old_logo_lembaga
            # Ensure Keuangan has path if Master has it
            if old_logo_lembaga:
                config_keuangan.logo_path = f"img/uploads/{old_logo_lembaga}"
            
        db.session.commit()
        flash('Konfigurasi berhasil disimpan', 'success')
        return redirect(url_for('master.konfigurasi'))
        
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error pada {getattr(form, field).label.text}: {error}", 'danger')

    return render_template('master/konfigurasi_form.html', title='Konfigurasi Sistem', form=form, config=config)

# --- BACKUP & RESTORE ---
@bp.route('/backup')
@login_required
@admin_required
def backup_list():
    # List available backups in the backup directory
    backup_dir = os.path.join(current_app.root_path, '..', '..', 'backups')
    backups = []
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            if f.endswith('.zip'):
                path = os.path.join(backup_dir, f)
                size = os.path.getsize(path) / (1024 * 1024) # MB
                backups.append({
                    'filename': f,
                    'size': f"{size:.2f} MB",
                    'created_at': datetime.datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')
                })
    # Sort by filename desc (newest first)
    backups.sort(key=lambda x: x['filename'], reverse=True)
    return render_template('master/backup_list.html', title='Backup & Restore', backups=backups)

@bp.route('/backup/create', methods=['POST'])
@login_required
@admin_required
@log_audit('CREATE', 'Backup')
def backup_create():
    try:
        # Create full system snapshot (Web Profile + SIAKAD)
        # Note: This is a synchronous call, might timeout on large data. 
        # Ideally should be async like in Web Profile, but for now we keep it simple.
        zip_path = BackupService.create_system_snapshot()
        flash('Backup sistem berhasil dibuat!', 'success')
    except Exception as e:
        flash(f'Gagal membuat backup: {str(e)}', 'danger')
    return redirect(url_for('master.backup_list'))

@bp.route('/backup/download/<filename>')
@login_required
@admin_required
def backup_download(filename):
    filename = secure_filename(filename)
    backup_dir = os.path.join(current_app.root_path, '..', '..', 'backups')
    file_path = os.path.join(backup_dir, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash('File backup tidak ditemukan.', 'danger')
        return redirect(url_for('master.backup_list'))

@bp.route('/backup/delete/<filename>', methods=['POST'])
@login_required
@admin_required
@log_audit('DELETE', 'Backup')
def backup_delete(filename):
    filename = secure_filename(filename)
    backup_dir = os.path.join(current_app.root_path, '..', '..', 'backups')
    file_path = os.path.join(backup_dir, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File backup berhasil dihapus.', 'success')
    else:
        flash('File backup tidak ditemukan.', 'danger')
    return redirect(url_for('master.backup_list'))

@bp.route('/backup/restore', methods=['POST'])
@login_required
@admin_required
@log_audit('RESTORE', 'System')
def backup_restore():
    if 'file' not in request.files:
        flash('Tidak ada file yang diunggah.', 'danger')
        return redirect(url_for('master.backup_list'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Tidak ada file yang dipilih.', 'danger')
        return redirect(url_for('master.backup_list'))
        
    if file and file.filename.endswith('.zip'):
        try:
            # Save temp file
            filename = secure_filename(file.filename)
            temp_path = os.path.join(current_app.root_path, 'static', 'temp_restore.zip')
            file.save(temp_path)
            
            # Perform restore
            BackupService.restore_system_snapshot(temp_path)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            flash('Sistem berhasil direstore! Silakan login ulang jika diperlukan.', 'success')
        except Exception as e:
            flash(f'Gagal merestore sistem: {str(e)}', 'danger')
    else:
        flash('Format file harus .zip', 'danger')
        
    return redirect(url_for('master.backup_list'))

# --- USER MANAGEMENT ---
@bp.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('master/user_list.html', title='Manajemen User', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('CREATE', 'User')
def user_add():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah digunakan! Silakan pilih username lain.', 'danger')
            return render_template('master/user_form.html', title='Tambah User', form=form)

        user = User(
            username=form.username.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('User berhasil ditambahkan', 'success')
            return redirect(url_for('master.user_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menambahkan user: {str(e)}', 'danger')
            return render_template('master/user_form.html', title='Tambah User', form=form)
            
    return render_template('master/user_form.html', title='Tambah User', form=form)

@bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('UPDATE', 'User')
def user_edit(id):
    user = User.query.get_or_404(id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User berhasil diperbarui', 'success')
        return redirect(url_for('master.user_list'))
        
    return render_template('master/user_form.html', title='Edit User', form=form)

@bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
@log_audit('DELETE', 'User')
def user_delete(id):
    if id == current_user.id:
        flash('Tidak dapat menghapus akun sendiri', 'danger')
        return redirect(url_for('master.user_list'))
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus', 'success')
    return redirect(url_for('master.user_list'))

# --- SANTRI ---
@bp.route('/santri')
@login_required
@admin_required
def santri_list():
    page = request.args.get('page', 1, type=int)
    santris = Santri.query.options(joinedload(Santri.kelas)).paginate(page=page, per_page=20, error_out=False)
    return render_template('master/santri_list.html', title='Data Santri', santris=santris)

@bp.route('/santri/add', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('CREATE', 'Santri')
def santri_add():
    form = SantriForm()
    # Populate kelas choices
    kelas_list = Kelas.query.all()
    form.kelas_id.choices = [(k.id, k.nama_kelas) for k in kelas_list]

    if form.validate_on_submit():
        santri = Santri(
            nis=form.nis.data,
            nama=form.nama.data,
            jenis_kelamin=form.jenis_kelamin.data,
            tempat_lahir=form.tempat_lahir.data,
            tanggal_lahir=form.tanggal_lahir.data,
            alamat=form.alamat.data,
            nama_ayah=form.nama_ayah.data,
            nama_ibu=form.nama_ibu.data,
            pekerjaan_ayah=form.pekerjaan_ayah.data,
            pekerjaan_ibu=form.pekerjaan_ibu.data,
            alamat_orang_tua=form.alamat_orang_tua.data,
            nama_wali=form.nama_wali.data,
            pekerjaan_wali=form.pekerjaan_wali.data,
            alamat_wali=form.alamat_wali.data,
            hubungan_wali=form.hubungan_wali.data,
            agama=form.agama.data,
            pendidikan_sebelumnya=form.pendidikan_sebelumnya.data,
            tanggal_masuk=form.tanggal_masuk.data,
            jenjang=form.jenjang.data,
            status=form.status.data,
            kelas_id=form.kelas_id.data
        )
        db.session.add(santri)
        db.session.commit()
        flash('Data Santri berhasil ditambahkan', 'success')
        return redirect(url_for('master.santri_list'))
    return render_template('master/santri_form.html', title='Tambah Santri', form=form)

@bp.route('/santri/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('UPDATE', 'Santri')
def santri_edit(id):
    santri = Santri.query.get_or_404(id)
    form = SantriForm(obj=santri, original_nis=santri.nis)
    # Populate kelas choices
    kelas_list = Kelas.query.all()
    form.kelas_id.choices = [(k.id, k.nama_kelas) for k in kelas_list]
    
    if form.validate_on_submit():
        santri.nis = form.nis.data
        santri.nama = form.nama.data
        santri.jenis_kelamin = form.jenis_kelamin.data
        santri.tempat_lahir = form.tempat_lahir.data
        santri.tanggal_lahir = form.tanggal_lahir.data
        santri.alamat = form.alamat.data
        santri.nama_ayah = form.nama_ayah.data
        santri.nama_ibu = form.nama_ibu.data
        santri.pekerjaan_ayah = form.pekerjaan_ayah.data
        santri.pekerjaan_ibu = form.pekerjaan_ibu.data
        santri.alamat_orang_tua = form.alamat_orang_tua.data
        santri.nama_wali = form.nama_wali.data
        santri.pekerjaan_wali = form.pekerjaan_wali.data
        santri.alamat_wali = form.alamat_wali.data
        santri.hubungan_wali = form.hubungan_wali.data
        santri.agama = form.agama.data
        santri.pendidikan_sebelumnya = form.pendidikan_sebelumnya.data
        santri.tanggal_masuk = form.tanggal_masuk.data
        santri.jenjang = form.jenjang.data
        santri.status = form.status.data
        santri.kelas_id = form.kelas_id.data
        db.session.commit()
        flash('Data Santri berhasil diperbarui', 'success')
        return redirect(url_for('master.santri_list'))
    return render_template('master/santri_form.html', title='Edit Santri', form=form)

@bp.route('/santri/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
@log_audit('DELETE', 'Santri')
def santri_delete(id):
    santri = Santri.query.get_or_404(id)
    db.session.delete(santri)
    db.session.commit()
    flash('Data Santri berhasil dihapus', 'success')
    return redirect(url_for('master.santri_list'))

@bp.route('/kelas')
@login_required
@admin_required
def kelas_list():
    kelas_list = Kelas.query.options(joinedload(Kelas.wali_kelas)).all()
    return render_template('master/kelas_list.html', title='Data Kelas', kelas_list=kelas_list)

@bp.route('/kelas/add', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('CREATE', 'Kelas')
def kelas_add():
    form = KelasForm()
    # Populate wali kelas choices (Pengajar)
    pengajars = Pengajar.query.all()
    form.wali_kelas_id.choices = [(p.id, p.nama) for p in pengajars]
    
    if form.validate_on_submit():
        kelas = Kelas(
            nama_kelas=form.nama_kelas.data,
            jenjang=form.jenjang.data,
            wali_kelas_id=form.wali_kelas_id.data
        )
        db.session.add(kelas)
        db.session.commit()
        flash('Data Kelas berhasil ditambahkan', 'success')
        return redirect(url_for('master.kelas_list'))
    return render_template('master/kelas_form.html', title='Tambah Kelas', form=form)

@bp.route('/kelas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('UPDATE', 'Kelas')
def kelas_edit(id):
    kelas = Kelas.query.get_or_404(id)
    form = KelasForm(obj=kelas)
    pengajars = Pengajar.query.all()
    form.wali_kelas_id.choices = [(p.id, p.nama) for p in pengajars]
    
    if form.validate_on_submit():
        form.populate_obj(kelas)
        db.session.commit()
        flash('Data Kelas berhasil diperbarui', 'success')
        return redirect(url_for('master.kelas_list'))
    return render_template('master/kelas_form.html', title='Edit Kelas', form=form)

@bp.route('/kelas/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def kelas_delete(id):
    kelas = Kelas.query.get_or_404(id)
    db.session.delete(kelas)
    db.session.commit()
    flash('Data Kelas berhasil dihapus', 'success')
    return redirect(url_for('master.kelas_list'))

# --- PENGAJAR ---
@bp.route('/pengajar')
@login_required
@admin_required
def pengajar_list():
    pengajars = Pengajar.query.all()
    return render_template('master/pengajar_list.html', title='Data Pengajar', pengajars=pengajars)

@bp.route('/pengajar/add', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('CREATE', 'Pengajar')
def pengajar_add():
    form = PengajarForm()
    if form.validate_on_submit():
        pengajar = Pengajar(
            nama=form.nama.data,
            nip=form.nip.data,
            nuptk=form.nuptk.data,
            jenis_kelamin=form.jenis_kelamin.data,
            tempat_lahir=form.tempat_lahir.data,
            tanggal_lahir=form.tanggal_lahir.data,
            no_hp=form.no_hp.data,
            email=form.email.data,
            alamat=form.alamat.data,
            pendidikan_terakhir=form.pendidikan_terakhir.data,
            status_kepegawaian=form.status_kepegawaian.data
        )
        db.session.add(pengajar)
        db.session.commit()
        flash('Data Pengajar berhasil ditambahkan', 'success')
        return redirect(url_for('master.pengajar_list'))
    return render_template('master/pengajar_form.html', title='Tambah Pengajar', form=form)

@bp.route('/pengajar/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('UPDATE', 'Pengajar')
def pengajar_edit(id):
    pengajar = Pengajar.query.get_or_404(id)
    form = PengajarForm(obj=pengajar)
    if form.validate_on_submit():
        pengajar.nama = form.nama.data
        pengajar.nip = form.nip.data
        pengajar.nuptk = form.nuptk.data
        pengajar.jenis_kelamin = form.jenis_kelamin.data
        pengajar.tempat_lahir = form.tempat_lahir.data
        pengajar.tanggal_lahir = form.tanggal_lahir.data
        pengajar.no_hp = form.no_hp.data
        pengajar.email = form.email.data
        pengajar.alamat = form.alamat.data
        pengajar.pendidikan_terakhir = form.pendidikan_terakhir.data
        pengajar.status_kepegawaian = form.status_kepegawaian.data
        db.session.commit()
        flash('Data Pengajar berhasil diperbarui', 'success')
        return redirect(url_for('master.pengajar_list'))
    return render_template('master/pengajar_form.html', title='Edit Pengajar', form=form)

@bp.route('/pengajar/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
@log_audit('DELETE', 'Pengajar')
def pengajar_delete(id):
    pengajar = Pengajar.query.get_or_404(id)
    db.session.delete(pengajar)
    db.session.commit()
    flash('Data Pengajar berhasil dihapus', 'success')
    return redirect(url_for('master.pengajar_list'))

# --- MATA PELAJARAN ---
@bp.route('/mapel')
@login_required
@admin_required
def mapel_list():
    mapels = MataPelajaran.query.all()
    return render_template('master/mapel_list.html', title='Mata Pelajaran', mapels=mapels)

@bp.route('/mapel/add', methods=['GET', 'POST'])
@login_required
@admin_required
def mapel_add():
    form = MapelForm()
    if form.validate_on_submit():
        mapel = MataPelajaran(
            nama_mapel=form.nama_mapel.data,
            jenjang=form.jenjang.data,
            kkm=float(form.kkm.data) if form.kkm.data else 70.0
        )
        db.session.add(mapel)
        db.session.commit()
        flash('Mata Pelajaran berhasil ditambahkan', 'success')
        return redirect(url_for('master.mapel_list'))
    return render_template('master/mapel_form.html', title='Tambah Mapel', form=form)

@bp.route('/mapel/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@log_audit('UPDATE', 'MataPelajaran')
def mapel_edit(id):
    mapel = MataPelajaran.query.get_or_404(id)
    form = MapelForm(obj=mapel)
    if form.validate_on_submit():
        form.populate_obj(mapel)
        mapel.kkm = float(form.kkm.data) if form.kkm.data else 70.0
        db.session.commit()
        flash('Mata Pelajaran berhasil diperbarui', 'success')
        return redirect(url_for('master.mapel_list'))
    return render_template('master/mapel_form.html', title='Edit Mapel', form=form)

@bp.route('/mapel/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
@log_audit('DELETE', 'MataPelajaran')
def mapel_delete(id):
    mapel = MataPelajaran.query.get_or_404(id)
    db.session.delete(mapel)
    db.session.commit()
    flash('Mata Pelajaran berhasil dihapus', 'success')
    return redirect(url_for('master.mapel_list'))
