from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import secrets
from app import db, login, limiter, cache
from app.models import User, Berita, Agenda, Galeri, Pengaturan, Program, Pimpinan
from app.admin.forms import LoginForm, BeritaForm, AgendaForm, GaleriForm, PengaturanForm, ProgramForm, PimpinanForm, ProfileForm, UserForm
from app.services.image_service import ImageService
from functools import wraps
from flask import send_file, make_response
import json
import io

bp = Blueprint('admin', __name__, url_prefix='/admin')

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'superadmin':
            flash('Anda tidak memiliki akses ke halaman tersebut.', 'danger')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(action, target, details=None):
    if current_user.is_authenticated:
        from app.models import ActivityLog
        
        # Support for proxy headers (X-Forwarded-For)
        if request.headers.getlist("X-Forwarded-For"):
            ip_address = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip_address = request.remote_addr
            
        log = ActivityLog(
            user_id=current_user.id,
            action=action,
            target=target,
            details=details,
            ip_address=ip_address,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()

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
            log_activity('LOGIN', 'System', 'User logged in')
            return redirect(url_for('admin.dashboard'))
        flash('Username atau password salah', 'danger')
    return render_template('admin/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    log_activity('LOGOUT', 'System', 'User logged out')
    logout_user()
    return redirect(url_for('admin.login'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        
    if form.validate_on_submit():
        # Handle password change
        if form.new_password.data:
            if not form.current_password.data:
                form.current_password.errors.append('Masukkan password saat ini untuk mengganti password')
                return render_template('admin/profile.html', form=form)
                
            if not current_user.check_password(form.current_password.data):
                form.current_password.errors.append('Password saat ini salah')
                return render_template('admin/profile.html', form=form)
                
            current_user.set_password(form.new_password.data)
            
        current_user.username = form.username.data
        db.session.commit()
        log_activity('UPDATE', 'Profile', f'User {current_user.username} updated profile')
        flash('Profil berhasil diperbarui', 'success')
        return redirect(url_for('admin.profile'))
        
    return render_template('admin/profile.html', form=form)

# --- User Management (Superadmin Only) ---
@bp.route('/users')
@login_required
@superadmin_required
def user_list():
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@superadmin_required
def user_add():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah digunakan! Silakan pilih username lain.', 'danger')
            return render_template('admin/user_form.html', form=form, title='Tambah User')

        user = User(username=form.username.data, role=form.role.data)
        if form.password.data:
            user.set_password(form.password.data)
        else:
            flash('Password wajib diisi untuk user baru', 'warning')
            return render_template('admin/user_form.html', form=form, title='Tambah User')
            
        try:
            db.session.add(user)
            db.session.commit()
            log_activity('CREATE', 'User', f'Created user {user.username}')
            flash('User berhasil ditambahkan', 'success')
            return redirect(url_for('admin.user_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menambahkan user: {str(e)}', 'danger')
            return render_template('admin/user_form.html', form=form, title='Tambah User')
            
    return render_template('admin/user_form.html', form=form, title='Tambah User')

@bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@superadmin_required
def user_edit(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        log_activity('UPDATE', 'User', f'Updated user {user.username}')
        flash('User berhasil diupdate', 'success')
        return redirect(url_for('admin.user_list'))
    return render_template('admin/user_form.html', form=form, title='Edit User')

@bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@superadmin_required
def user_delete(id):
    if id == current_user.id:
        flash('Anda tidak dapat menghapus akun sendiri!', 'danger')
        return redirect(url_for('admin.user_list'))
        
    user = User.query.get_or_404(id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    log_activity('DELETE', 'User', f'Deleted user {username}')
    flash('User berhasil dihapus', 'success')
    return redirect(url_for('admin.user_list'))

def get_all_used_images():
    """Helper to collect all image URLs currently in use by the database."""
    used_images = set()
    
    try:
        # Berita
        for item in Berita.query.with_entities(Berita.gambar).all():
            if item.gambar: used_images.add(item.gambar)
            
        # Galeri
        for item in Galeri.query.with_entities(Galeri.gambar).all():
            if item.gambar: used_images.add(item.gambar)
            
        # Program
        for item in Program.query.with_entities(Program.gambar).all():
            if item.gambar: used_images.add(item.gambar)
            
        # Pimpinan
        for item in Pimpinan.query.with_entities(Pimpinan.gambar).all():
            if item.gambar: used_images.add(item.gambar)
            
        # Pengaturan
        setting = Pengaturan.query.first()
        if setting:
            if setting.sejarah_gambar: used_images.add(setting.sejarah_gambar)
            if hasattr(setting, 'struktur_organisasi_gambar') and setting.struktur_organisasi_gambar:
                used_images.add(setting.struktur_organisasi_gambar)
            # Check other potential image fields in Pengaturan if any
    except Exception as e:
        print(f"Error collecting used images: {e}")
        
    return used_images

@bp.route('/file-manager')
@login_required
@superadmin_required
def file_manager():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    files = []
    
    used_images = get_all_used_images()
    
    # Walk through uploads directory
    for root, dirs, filenames in os.walk(upload_folder):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, upload_folder)
                
                # Generate URL matching how it's stored
                # Note: url_for might return absolute URL if _external=True, but usually relative
                url_path = url_for('static', filename='uploads/' + rel_path.replace('\\', '/'))
                
                size_kb = os.path.getsize(filepath) / 1024
                
                # Determine category based on folder name
                category = os.path.basename(root)
                if category == 'uploads': category = 'Uncategorized'
                
                files.append({
                    'name': filename,
                    'path': filepath, # Absolute path for deletion
                    'url': url_path,
                    'size': f"{size_kb:.1f} KB",
                    'category': category,
                    'is_used': url_path in used_images
                })
    
    return render_template('admin/file_manager.html', files=files)

@bp.route('/file-manager/delete', methods=['POST'])
@login_required
@superadmin_required
def file_delete():
    filepath = request.form.get('filepath')
    if filepath and os.path.exists(filepath):
        try:
            # Security check: ensure file is inside upload folder
            upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
            abs_filepath = os.path.abspath(filepath)
            
            if abs_filepath.startswith(upload_folder):
                os.remove(abs_filepath)
                log_activity('DELETE', 'File', f'Deleted file {os.path.basename(filepath)}')
                flash('File berhasil dihapus', 'success')
            else:
                flash('Akses ditolak: File berada di luar direktori upload', 'danger')
        except Exception as e:
            flash(f'Gagal menghapus file: {str(e)}', 'danger')
    else:
        flash('File tidak ditemukan', 'danger')
        
    return redirect(url_for('admin.file_manager'))

@bp.route('/file-manager/delete-unused', methods=['POST'])
@login_required
@superadmin_required
def file_delete_unused():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    used_images = get_all_used_images()
    deleted_count = 0
    errors = 0
    
    # Walk through uploads directory
    for root, dirs, filenames in os.walk(upload_folder):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, upload_folder)
                
                # Check if file is used
                url_path = url_for('static', filename='uploads/' + rel_path.replace('\\', '/'))
                
                if url_path not in used_images:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Failed to delete {filepath}: {e}")
                        errors += 1
    
    if deleted_count > 0:
        log_activity('DELETE', 'File Manager', f'Deleted {deleted_count} unused files')
        flash(f'Berhasil menghapus {deleted_count} file yang tidak digunakan.', 'success')
    else:
        flash('Tidak ada file tidak digunakan yang ditemukan.', 'info')
        
    if errors > 0:
        flash(f'Gagal menghapus {errors} file.', 'warning')
        
    return redirect(url_for('admin.file_manager'))

# --- System Features (Logs & Backup) ---
@bp.route('/activity-logs')
@login_required
@superadmin_required
def activity_logs():
    from app.models import ActivityLog
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=20)
    return render_template('admin/activity_log.html', logs=logs)

@bp.route('/activity-logs/clear', methods=['POST'])
@login_required
@superadmin_required
def activity_logs_clear():
    from app.models import ActivityLog
    try:
        num_rows = db.session.query(ActivityLog).delete()
        db.session.commit()
        # Re-log the clear action so it's not empty
        log_activity('DELETE', 'System', f'Cleared {num_rows} activity logs')
        flash('Semua log aktivitas berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus log: {str(e)}', 'danger')
        
    return redirect(url_for('admin.activity_logs'))

@bp.route('/backup')
@login_required
@superadmin_required
def backup():
    # Simple JSON Backup
    data = {
        'berita': [b.to_dict() for b in Berita.query.all()] if hasattr(Berita, 'to_dict') else [],
        'agenda': [a.to_dict() for a in Agenda.query.all()] if hasattr(Agenda, 'to_dict') else [],
        # For now, since models don't have to_dict, let's just render the page
    }
    return render_template('admin/backup.html')

@bp.route('/backup/download')
@login_required
@superadmin_required
def backup_download():
    # Manual serialization
    data = {}
    
    # Berita
    berita_list = []
    for b in Berita.query.all():
        berita_list.append({
            'judul': b.judul, 'slug': b.slug, 'konten': b.konten, 
            'gambar': b.gambar, 'status': b.status, 'kategori': b.kategori,
            'tanggal': b.tanggal.isoformat(),
            'penulis': b.penulis
        })
    data['berita'] = berita_list
    
    # Agenda
    agenda_list = []
    for a in Agenda.query.all():
        agenda_list.append({
            'nama_kegiatan': a.nama_kegiatan, 'lokasi': a.lokasi, 'deskripsi': a.deskripsi,
            'tanggal_mulai': a.tanggal_mulai.isoformat(), 'tanggal_selesai': a.tanggal_selesai.isoformat() if a.tanggal_selesai else None
        })
    data['agenda'] = agenda_list
    
    # Galeri
    galeri_list = []
    for g in Galeri.query.all():
        galeri_list.append({
            'judul': g.judul, 'gambar': g.gambar, 'kategori': g.kategori, 'deskripsi': g.deskripsi,
            'tanggal': g.tanggal.isoformat()
        })
    data['galeri'] = galeri_list
    
    # Program
    program_list = []
    for p in Program.query.all():
        program_list.append({
            'nama': p.nama, 'deskripsi': p.deskripsi, 'icon': p.icon,
            'gambar': p.gambar, 'urutan': p.urutan, 'parent_id': p.parent_id
        })
    data['program'] = program_list
    
    # Pimpinan
    pimpinan_list = []
    for pim in Pimpinan.query.all():
        pimpinan_list.append({
            'nama': pim.nama, 'jabatan': pim.jabatan, 'gambar': pim.gambar,
            'urutan': pim.urutan
        })
    data['pimpinan'] = pimpinan_list
    
    # Pengaturan
    p = Pengaturan.query.first()
    if p:
        data['pengaturan'] = {
            'nama_pesantren': p.nama_pesantren, 'alamat': p.alamat, 'telepon': p.telepon,
            'email': p.email, 'facebook': p.facebook, 'instagram': p.instagram,
            'tiktok': getattr(p, 'tiktok', ''), 'youtube': p.youtube,
            'deskripsi_singkat': p.deskripsi_singkat,
            'maps_embed': p.maps_embed, 'maps_link': p.maps_link,
            'jumlah_santri': p.jumlah_santri, 'jumlah_alumni': p.jumlah_alumni,
            'jumlah_ustadz': p.jumlah_ustadz, 'jumlah_kitab': p.jumlah_kitab,
            'sejarah': p.sejarah, 'sejarah_gambar': p.sejarah_gambar,
            'struktur_organisasi_gambar': p.struktur_organisasi_gambar,
            'visi': p.visi, 'misi': p.misi,
            'hero_title_1': p.hero_title_1, 'hero_title_2': p.hero_title_2,
            'hero_title_3': p.hero_title_3, 'hero_subtitle': p.hero_subtitle
        }
        
    response = make_response(json.dumps(data, indent=2))
    response.headers['Content-Disposition'] = f'attachment; filename=backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    response.headers['Content-Type'] = 'application/json'
    
    log_activity('BACKUP', 'System', 'Downloaded database backup')
    return response

@bp.route('/restore', methods=['POST'])
@login_required
@superadmin_required
def restore():
    if 'file' not in request.files:
        flash('Tidak ada file yang diupload', 'danger')
        return redirect(url_for('admin.backup'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Tidak ada file yang dipilih', 'danger')
        return redirect(url_for('admin.backup'))
        
    if file:
        try:
            data = json.load(file)
            count = 0
            
            # Restore Berita
            if 'berita' in data:
                for item in data['berita']:
                    if not Berita.query.filter_by(slug=item['slug']).first():
                        b = Berita(
                            judul=item['judul'], slug=item['slug'], konten=item['konten'],
                            gambar=item.get('gambar'), status=item.get('status', 'published'),
                            kategori=item.get('kategori', 'berita'),
                            tanggal=datetime.fromisoformat(item['tanggal']),
                            penulis=item.get('penulis', 'Admin')
                        )
                        db.session.add(b)
                        count += 1
            
            # Restore Agenda
            if 'agenda' in data:
                for item in data['agenda']:
                    # Check duplicate by name and start date
                    start_date = datetime.fromisoformat(item['tanggal_mulai'])
                    if not Agenda.query.filter_by(nama_kegiatan=item['nama_kegiatan'], tanggal_mulai=start_date).first():
                        a = Agenda(
                            nama_kegiatan=item['nama_kegiatan'], lokasi=item['lokasi'], deskripsi=item['deskripsi'],
                            tanggal_mulai=start_date,
                            tanggal_selesai=datetime.fromisoformat(item['tanggal_selesai']) if item.get('tanggal_selesai') else None
                        )
                        db.session.add(a)
                        count += 1
            
            # Restore Galeri
            if 'galeri' in data:
                for item in data['galeri']:
                    # Check duplicate by image url
                    if not Galeri.query.filter_by(gambar=item['gambar']).first():
                        g = Galeri(
                            judul=item['judul'], gambar=item['gambar'], 
                            kategori=item.get('kategori', 'Kegiatan'), 
                            deskripsi=item.get('deskripsi'),
                            tanggal=datetime.fromisoformat(item['tanggal']) if item.get('tanggal') else datetime.now()
                        )
                        db.session.add(g)
                        count += 1

            # Restore Pimpinan
            if 'pimpinan' in data:
                for item in data['pimpinan']:
                    if not Pimpinan.query.filter_by(nama=item['nama']).first():
                        pim = Pimpinan(
                            nama=item['nama'], jabatan=item['jabatan'],
                            gambar=item.get('gambar'), urutan=item.get('urutan', 0)
                        )
                        db.session.add(pim)
                        count += 1
            
            # Restore Program
            if 'program' in data:
                # First pass: Create all programs without parents to avoid foreign key errors
                pending_parents = []
                for item in data['program']:
                    if not Program.query.filter_by(nama=item['nama']).first():
                        prog = Program(
                            nama=item['nama'], deskripsi=item.get('deskripsi'),
                            icon=item.get('icon'), gambar=item.get('gambar'),
                            urutan=item.get('urutan', 0)
                        )
                        db.session.add(prog)
                        db.session.flush() # Flush to get ID
                        if item.get('parent_id'):
                            pending_parents.append((prog, item['parent_id'])) # Store for second pass (this logic is tricky with IDs from backup vs new IDs)
                        count += 1
                
                # Note: Parent ID mapping is complex because IDs change. 
                # For now, we skip parent mapping restoration in this simple version 
                # or we could try to match by name if parent was also restored.
                # A robust solution requires mapping old_id -> new_id.
                # Simplifying assumption: Users will manually re-assign parents if needed, 
                # or we match by name if possible.
            
            # Restore Pengaturan (Update existing)
            if 'pengaturan' in data:
                p = Pengaturan.query.first()
                if not p:
                    p = Pengaturan()
                    db.session.add(p)
                
                settings = data['pengaturan']
                for key, value in settings.items():
                    if hasattr(p, key):
                        setattr(p, key, value)
                count += 1 # Count settings update as 1 action

            db.session.commit()
            log_activity('RESTORE', 'System', f'Restored/Added {count} items from backup')
            flash(f'Restore berhasil! {count} data ditambahkan/diperbarui.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal melakukan restore: {str(e)}', 'danger')
            
    return redirect(url_for('admin.backup'))

from datetime import datetime

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    # Counts
    total_berita = Berita.query.count()
    total_agenda = Agenda.query.count()
    total_galeri = Galeri.query.count()
    total_program = Program.query.count()
    
    # Recent Data
    recent_berita = Berita.query.order_by(Berita.tanggal.desc()).limit(5).all()
    upcoming_agenda = Agenda.query.filter(Agenda.tanggal_mulai >= datetime.now()).order_by(Agenda.tanggal_mulai.asc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           total_berita=total_berita, 
                           total_agenda=total_agenda, 
                           total_galeri=total_galeri,
                           total_program=total_program,
                           recent_berita=recent_berita,
                           upcoming_agenda=upcoming_agenda,
                           now=datetime.now)

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
    
    # Default author to current user's username if not submitted
    if request.method == 'GET':
        form.penulis.data = current_user.username.title()  # Capitalize first letter
        
    if form.validate_on_submit():
        gambar_file = "https://picsum.photos/seed/default/800/400"
        
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'berita')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/berita_form.html', form=form, title='Tambah Berita')
        elif form.gambar_url.data:
            gambar_file = form.gambar_url.data
        
        # Generate unique slug
        base_slug = form.slug.data
        slug = base_slug
        counter = 1
        while Berita.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        berita = Berita(
            judul=form.judul.data,
            slug=slug,
            konten=form.konten.data,
            gambar=gambar_file,
            status=form.status.data,
            kategori=form.kategori.data,
            penulis=form.penulis.data
        )
        db.session.add(berita)
        db.session.commit()
        log_activity('CREATE', 'Berita', f'Created berita: {berita.judul}')
        flash('Berita berhasil ditambahkan', 'success')
        return redirect(url_for('admin.berita_list'))
    return render_template('admin/berita_form.html', form=form, title='Tambah Berita')

@bp.route('/berita/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def berita_edit(id):
    berita = Berita.query.get_or_404(id)
    form = BeritaForm(obj=berita)
    if form.validate_on_submit():
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'berita')
                berita.gambar = gambar_file
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/berita_form.html', form=form, title='Edit Berita')
        elif form.gambar_url.data:
            berita.gambar = form.gambar_url.data
            
        berita.judul = form.judul.data
        berita.penulis = form.penulis.data
        
        # Generate unique slug (exclude current berita)
        base_slug = form.slug.data
        slug = base_slug
        counter = 1
        while True:
            existing = Berita.query.filter_by(slug=slug).first()
            if not existing or existing.id == berita.id:
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        berita.slug = slug
        berita.konten = form.konten.data
        berita.status = form.status.data
        berita.kategori = form.kategori.data
        
        db.session.commit()
        log_activity('UPDATE', 'Berita', f'Updated berita: {berita.judul}')
        flash('Berita berhasil diupdate', 'success')
        return redirect(url_for('admin.berita_list'))
    return render_template('admin/berita_form.html', form=form, title='Edit Berita', berita=berita)

@bp.route('/berita/delete/<int:id>', methods=['POST'])
@login_required
def berita_delete(id):
    berita = Berita.query.get_or_404(id)
    judul = berita.judul
    db.session.delete(berita)
    db.session.commit()
    log_activity('DELETE', 'Berita', f'Deleted berita: {judul}')
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
        log_activity('CREATE', 'Agenda', f'Created agenda: {agenda.nama_kegiatan}')
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
        log_activity('UPDATE', 'Agenda', f'Updated agenda: {agenda.nama_kegiatan}')
        flash('Agenda berhasil diupdate', 'success')
        return redirect(url_for('admin.agenda_list'))
    return render_template('admin/agenda_form.html', form=form, title='Edit Agenda')

@bp.route('/agenda/delete/<int:id>', methods=['POST'])
@login_required
def agenda_delete(id):
    agenda = Agenda.query.get_or_404(id)
    nama = agenda.nama_kegiatan
    db.session.delete(agenda)
    db.session.commit()
    log_activity('DELETE', 'Agenda', f'Deleted agenda: {nama}')
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
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            gambar_file = ImageService.save_picture(form.gambar.data, 'galeri')
        elif form.gambar_url.data:
            gambar_file = form.gambar_url.data
            
        galeri = Galeri(
            judul=form.judul.data,
            gambar=gambar_file,
            kategori=form.kategori.data,
            deskripsi=form.deskripsi.data
        )
        db.session.add(galeri)
        db.session.commit()
        log_activity('CREATE', 'Galeri', f'Created galeri: {galeri.judul}')
        flash('Foto berhasil ditambahkan ke galeri', 'success')
        return redirect(url_for('admin.galeri_list'))
    return render_template('admin/galeri_form.html', form=form, title='Tambah Foto')

@bp.route('/galeri/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def galeri_edit(id):
    galeri = Galeri.query.get_or_404(id)
    form = GaleriForm(obj=galeri)
    if form.validate_on_submit():
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            gambar_file = ImageService.save_picture(form.gambar.data, 'galeri')
            galeri.gambar = gambar_file
        elif form.gambar_url.data:
            galeri.gambar = form.gambar_url.data
            
        galeri.judul = form.judul.data
        galeri.kategori = form.kategori.data
        galeri.deskripsi = form.deskripsi.data
        
        db.session.commit()
        log_activity('UPDATE', 'Galeri', f'Updated galeri: {galeri.judul}')
        flash('Foto berhasil diupdate', 'success')
        return redirect(url_for('admin.galeri_list'))
    return render_template('admin/galeri_form.html', form=form, title='Edit Foto', galeri=galeri)

@bp.route('/galeri/delete/<int:id>', methods=['POST'])
@login_required
def galeri_delete(id):
    galeri = Galeri.query.get_or_404(id)
    judul = galeri.judul
    db.session.delete(galeri)
    db.session.commit()
    log_activity('DELETE', 'Galeri', f'Deleted galeri: {judul}')
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
        current_sejarah_gambar = pengaturan.sejarah_gambar
        current_struktur_organisasi_gambar = getattr(pengaturan, 'struktur_organisasi_gambar', None)
        
        form.populate_obj(pengaturan)
        
        # Clear cache when settings are updated
        cache.clear()
        
        # Handle Sejarah Gambar
        if form.sejarah_gambar.data and hasattr(form.sejarah_gambar.data, 'filename') and form.sejarah_gambar.data.filename:
            try:
                gambar_file = ImageService.save_picture(form.sejarah_gambar.data, 'sejarah')
                pengaturan.sejarah_gambar = gambar_file
            except ValueError as e:
                pengaturan.sejarah_gambar = current_sejarah_gambar
                flash(str(e), 'danger')
                return render_template('admin/pengaturan.html', form=form)
        elif form.sejarah_gambar_url.data:
            pengaturan.sejarah_gambar = form.sejarah_gambar_url.data
        else:
            pengaturan.sejarah_gambar = current_sejarah_gambar

        # Handle Struktur Organisasi Gambar
        if form.struktur_organisasi_gambar.data and hasattr(form.struktur_organisasi_gambar.data, 'filename') and form.struktur_organisasi_gambar.data.filename:
            try:
                gambar_file = ImageService.save_picture(form.struktur_organisasi_gambar.data, 'struktur')
                pengaturan.struktur_organisasi_gambar = gambar_file
            except ValueError as e:
                pengaturan.struktur_organisasi_gambar = current_struktur_organisasi_gambar
                flash(f"Gagal upload struktur organisasi: {str(e)}", 'danger')
                return render_template('admin/pengaturan.html', form=form)
        elif form.struktur_organisasi_gambar_url.data:
            pengaturan.struktur_organisasi_gambar = form.struktur_organisasi_gambar_url.data
        else:
            pengaturan.struktur_organisasi_gambar = current_struktur_organisasi_gambar

        db.session.commit()
        log_activity('UPDATE', 'System', 'Updated website settings')
        flash('Pengaturan berhasil disimpan', 'success')
        return redirect(url_for('admin.pengaturan'))
        
    return render_template('admin/pengaturan.html', form=form, pengaturan=pengaturan)

# --- Program CRUD ---
@bp.route('/program')
@login_required
def program_list():
    programs = Program.query.order_by(Program.urutan.asc()).all()
    return render_template('admin/program_list.html', programs=programs)

@bp.route('/program/add', methods=['GET', 'POST'])
@login_required
def program_add():
    form = ProgramForm()
    # Populate parent choices
    parents = Program.query.filter_by(parent_id=None).all()
    form.parent_id.choices = [(0, 'Utama')] + [(p.id, p.nama) for p in parents]
    
    if form.validate_on_submit():
        parent = None
        if form.parent_id.data != 0:
            parent = Program.query.get(form.parent_id.data)
        
        gambar_file = "https://picsum.photos/seed/default/600/400"
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'program')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/program_form.html', form=form, title='Tambah Program')
        elif form.gambar_url.data:
            gambar_file = form.gambar_url.data
            
        program = Program(
            nama=form.nama.data,
            deskripsi=form.deskripsi.data,
            icon=form.icon.data,
            gambar=gambar_file,
            urutan=int(form.urutan.data or 0),
            parent=parent
        )
        db.session.add(program)
        db.session.commit()
        log_activity('CREATE', 'Program', f'Created program: {program.nama}')
        flash('Program berhasil ditambahkan', 'success')
        return redirect(url_for('admin.program_list'))
    return render_template('admin/program_form.html', form=form, title='Tambah Program')

@bp.route('/program/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def program_edit(id):
    program = Program.query.get_or_404(id)
    form = ProgramForm(obj=program)
    
    # Populate parent choices
    parents = Program.query.filter(Program.id != id, Program.parent_id == None).all()
    form.parent_id.choices = [(0, 'Utama')] + [(p.id, p.nama) for p in parents]
    
    # Set current parent
    if request.method == 'GET':
        form.parent_id.data = program.parent_id if program.parent_id else 0

    if form.validate_on_submit():
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'program')
                program.gambar = gambar_file
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/program_form.html', form=form, title='Edit Program', program=program)
        elif form.gambar_url.data:
            program.gambar = form.gambar_url.data
        
        program.nama = form.nama.data
        program.deskripsi = form.deskripsi.data
        program.icon = form.icon.data
        
        if form.parent_id.data != 0:
            program.parent_id = form.parent_id.data
        else:
            program.parent_id = None
            
        db.session.commit()
        log_activity('UPDATE', 'Program', f'Updated program: {program.nama}')
        flash('Program berhasil diupdate', 'success')
        return redirect(url_for('admin.program_list'))
    return render_template('admin/program_form.html', form=form, title='Edit Program', program=program)

@bp.route('/program/delete/<int:id>', methods=['POST'])
@login_required
def program_delete(id):
    program = Program.query.get_or_404(id)
    nama = program.nama
    db.session.delete(program)
    db.session.commit()
    log_activity('DELETE', 'Program', f'Deleted program: {nama}')
    flash('Program berhasil dihapus', 'success')
    return redirect(url_for('admin.program_list'))

# --- Pimpinan CRUD ---
@bp.route('/pimpinan')
@login_required
def pimpinan_list():
    pimpinan_list = Pimpinan.query.order_by(Pimpinan.urutan.asc()).all()
    return render_template('admin/pimpinan_list.html', pimpinan_list=pimpinan_list)

@bp.route('/pimpinan/add', methods=['GET', 'POST'])
@login_required
def pimpinan_add():
    form = PimpinanForm()
    if form.validate_on_submit():
        gambar_file = None
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'pimpinan')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/pimpinan_form.html', form=form, title='Tambah Pimpinan')
        elif form.gambar_url.data:
            gambar_file = form.gambar_url.data
            
        pimpinan = Pimpinan(
            nama=form.nama.data,
            jabatan=form.jabatan.data,
            gambar=gambar_file,
            urutan=int(form.urutan.data or 0)
        )
        db.session.add(pimpinan)
        db.session.commit()
        # Clear cache when pimpinan data is updated
        cache.clear()
        
        log_activity('CREATE', 'Pimpinan', f'Created pimpinan: {pimpinan.nama}')
        flash('Data Pimpinan berhasil ditambahkan', 'success')
        return redirect(url_for('admin.pimpinan_list'))
    return render_template('admin/pimpinan_form.html', form=form, title='Tambah Pimpinan')

@bp.route('/pimpinan/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def pimpinan_edit(id):
    pimpinan = Pimpinan.query.get_or_404(id)
    form = PimpinanForm(obj=pimpinan)
    if form.validate_on_submit():
        if form.gambar.data and hasattr(form.gambar.data, 'filename'):
            try:
                gambar_file = ImageService.save_picture(form.gambar.data, 'pimpinan')
                pimpinan.gambar = gambar_file
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/pimpinan_form.html', form=form, title='Edit Pimpinan')
        elif form.gambar_url.data:
            pimpinan.gambar = form.gambar_url.data
            
        pimpinan.nama = form.nama.data
        pimpinan.jabatan = form.jabatan.data
        pimpinan.urutan = int(form.urutan.data or 0)
        
        db.session.commit()
        # Clear cache when pimpinan data is updated
        cache.clear()
        
        log_activity('UPDATE', 'Pimpinan', f'Updated pimpinan: {pimpinan.nama}')
        flash('Data Pimpinan berhasil diupdate', 'success')
        return redirect(url_for('admin.pimpinan_list'))
    return render_template('admin/pimpinan_form.html', form=form, title='Edit Pimpinan', pimpinan=pimpinan)

@bp.route('/pimpinan/delete/<int:id>', methods=['POST'])
@login_required
def pimpinan_delete(id):
    pimpinan = Pimpinan.query.get_or_404(id)
    nama = pimpinan.nama
    db.session.delete(pimpinan)
    db.session.commit()
    # Clear cache when pimpinan data is updated
    cache.clear()
    
    log_activity('DELETE', 'Pimpinan', f'Deleted pimpinan: {nama}')
    flash('Data Pimpinan berhasil dihapus', 'success')
    return redirect(url_for('admin.pimpinan_list'))
