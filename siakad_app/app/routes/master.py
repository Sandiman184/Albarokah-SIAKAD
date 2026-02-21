from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
import datetime
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran
from app.models.user import User
from app.forms.master import SantriForm, PengajarForm, KelasForm, MapelForm
from app.forms.auth import UserForm, UserEditForm
from app.decorators import admin_required
from app.services.audit_service import log_audit

from app.services.backup_service import BackupService
import os
from flask import send_file
from werkzeug.utils import secure_filename

bp = Blueprint('master', __name__, url_prefix='/master')

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

@bp.route('/santri')
@login_required
@admin_required
def santri_list():
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
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
            tanggal_lahir=form.tanggal_lahir.data,
            alamat=form.alamat.data,
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
        form.populate_obj(santri)
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
            no_hp=form.no_hp.data,
            alamat=form.alamat.data
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
        form.populate_obj(pengajar)
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
            jenjang=form.jenjang.data
        )
        db.session.add(mapel)
        db.session.commit()
        flash('Mata Pelajaran berhasil ditambahkan', 'success')
        return redirect(url_for('master.mapel_list'))
    return render_template('master/mapel_form.html', title='Tambah Mapel', form=form)

@bp.route('/mapel/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def mapel_edit(id):
    mapel = MataPelajaran.query.get_or_404(id)
    form = MapelForm(obj=mapel)
    if form.validate_on_submit():
        form.populate_obj(mapel)
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
