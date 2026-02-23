from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, current_app
from flask_login import login_required, current_user
import os
from sqlalchemy.orm import joinedload
from app import db
from app.models.akademik import Santri, MataPelajaran, Nilai, Absensi, Tahfidz, Raport, Kelas
from app.forms.akademik import NilaiForm, AbsensiForm, TahfidzForm, RaportForm, AbsensiMassalForm
from app.decorators import role_required
from app.services.raport import RaportService
from app.services.audit_service import log_audit
from datetime import datetime
try:
    from weasyprint import HTML
except OSError:
    HTML = None

bp = Blueprint('akademik', __name__, url_prefix='/akademik')

# --- NILAI ---
@bp.route('/nilai')
@login_required
def nilai_list():
    if current_user.role == 'wali_santri':
        santris = Santri.query.filter_by(wali_user_id=current_user.id).all()
        santri_ids = [s.id for s in santris]
        nilais = Nilai.query.filter(Nilai.santri_id.in_(santri_ids)).options(joinedload(Nilai.santri).joinedload(Santri.kelas), joinedload(Nilai.mapel)).all()
    else:
        nilais = Nilai.query.options(joinedload(Nilai.santri).joinedload(Santri.kelas), joinedload(Nilai.mapel)).all()
    return render_template('akademik/nilai_list.html', title='Data Nilai', nilais=nilais)

@bp.route('/nilai/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('CREATE', 'Nilai')
def nilai_add():
    form = NilaiForm()
    
    # Populate choices with eager loading
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    mapels = MataPelajaran.query.all()
    form.mapel_id.choices = [(m.id, f"{m.nama_mapel} ({m.jenjang})") for m in mapels]
    
    if form.validate_on_submit():
        nilai = Nilai(
            santri_id=form.santri_id.data,
            mapel_id=form.mapel_id.data,
            semester=form.semester.data,
            nilai_harian=form.nilai_harian.data,
            nilai_kehadiran=form.nilai_kehadiran.data,
            nilai_uts=form.nilai_uts.data,
            nilai_uas=form.nilai_uas.data,
            nilai_praktik=form.nilai_praktik.data,
            deskripsi=form.deskripsi.data
        )
        db.session.add(nilai)
        db.session.commit()
        flash('Nilai berhasil disimpan', 'success')
        return redirect(url_for('akademik.nilai_list'))
        
    return render_template('akademik/nilai_form.html', title='Input Nilai', form=form)

@bp.route('/nilai/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('UPDATE', 'Nilai')
def nilai_edit(id):
    nilai = Nilai.query.get_or_404(id)
    form = NilaiForm(obj=nilai)
    
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    mapels = MataPelajaran.query.all()
    form.mapel_id.choices = [(m.id, f"{m.nama_mapel} ({m.jenjang})") for m in mapels]
    
    if form.validate_on_submit():
        form.populate_obj(nilai)
        # Ensure deskripsi is saved (populate_obj should handle it if field names match)
        db.session.commit()
        flash('Nilai berhasil diperbarui', 'success')
        return redirect(url_for('akademik.nilai_list'))
        
    return render_template('akademik/nilai_form.html', title='Edit Nilai', form=form)

@bp.route('/nilai/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin', 'ustadz')
def nilai_delete(id):
    nilai = Nilai.query.get_or_404(id)
    db.session.delete(nilai)
    db.session.commit()
    flash('Nilai berhasil dihapus', 'success')
    return redirect(url_for('akademik.nilai_list'))


# --- ABSENSI ---
@bp.route('/absensi')
@login_required
def absensi_list():
    if current_user.role == 'wali_santri':
        santris = Santri.query.filter_by(wali_user_id=current_user.id).all()
        santri_ids = [s.id for s in santris]
        absensis = Absensi.query.filter(Absensi.santri_id.in_(santri_ids)).options(joinedload(Absensi.santri).joinedload(Santri.kelas)).order_by(Absensi.tanggal.desc()).all()
    else:
        absensis = Absensi.query.options(joinedload(Absensi.santri).joinedload(Santri.kelas)).order_by(Absensi.tanggal.desc()).limit(100).all()
    return render_template('akademik/absensi_list.html', title='Data Absensi', absensis=absensis)

@bp.route('/absensi/massal', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('BULK_UPDATE', 'Absensi')
def absensi_massal():
    form = AbsensiMassalForm()
    # Populate kelas choices
    kelases = Kelas.query.order_by(Kelas.nama_kelas).all()
    form.kelas_id.choices = [(k.id, f"{k.nama_kelas} ({k.jenjang or '-'})") for k in kelases]
    
    students = []
    existing_data = {}
    selected_kelas = None
    selected_date = None
    
    # Check if we are filtering (GET with args) or submitting (POST)
    if request.method == 'GET' and request.args.get('kelas_id') and request.args.get('tanggal'):
        try:
            form.kelas_id.data = int(request.args.get('kelas_id'))
            form.tanggal.data = datetime.strptime(request.args.get('tanggal'), '%Y-%m-%d').date()
        except ValueError:
            pass
            
    if (request.method == 'GET' and form.kelas_id.data and form.tanggal.data) or \
       (request.method == 'POST' and form.validate_on_submit() and 'btn_filter' in request.form):
        
        selected_kelas = Kelas.query.get(form.kelas_id.data)
        selected_date = form.tanggal.data
        
        # Get students
        students = Santri.query.filter_by(kelas_id=selected_kelas.id, status='aktif').order_by(Santri.nama).all()
        
        # Get existing attendance
        existing = Absensi.query.filter_by(tanggal=selected_date).filter(Absensi.santri_id.in_([s.id for s in students])).all()
        existing_data = {e.santri_id: e.status for e in existing}

    # Handle Save (POST)
    if request.method == 'POST' and 'btn_save' in request.form:
        kelas_id = request.form.get('kelas_id')
        tanggal_str = request.form.get('tanggal')
        tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        
        # Re-fetch students to be safe
        students = Santri.query.filter_by(kelas_id=kelas_id, status='aktif').all()
        
        count_saved = 0
        for student in students:
            status_key = f"status_{student.id}"
            status_val = request.form.get(status_key)
            
            if status_val:
                # Check if exists
                absen = Absensi.query.filter_by(santri_id=student.id, tanggal=tanggal).first()
                if absen:
                    absen.status = status_val
                else:
                    absen = Absensi(santri_id=student.id, tanggal=tanggal, status=status_val)
                    db.session.add(absen)
                count_saved += 1
        
        db.session.commit()
        flash(f'Absensi berhasil disimpan untuk {count_saved} santri.', 'success')
        return redirect(url_for('akademik.absensi_list'))

    return render_template('akademik/absensi_massal.html', title='Input Absensi Massal', form=form, students=students, existing_data=existing_data, selected_kelas=selected_kelas, selected_date=selected_date)

@bp.route('/absensi/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('CREATE', 'Absensi')
def absensi_add():
    form = AbsensiForm()
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    
    if form.validate_on_submit():
        absen = Absensi(
            santri_id=form.santri_id.data,
            tanggal=form.tanggal.data,
            status=form.status.data
        )
        db.session.add(absen)
        db.session.commit()
        flash('Absensi berhasil disimpan', 'success')
        return redirect(url_for('akademik.absensi_list'))
        
    return render_template('akademik/absensi_form.html', title='Input Absensi', form=form)

@bp.route('/absensi/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('UPDATE', 'Absensi')
def absensi_edit(id):
    absen = Absensi.query.get_or_404(id)
    form = AbsensiForm(obj=absen)
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    
    if form.validate_on_submit():
        form.populate_obj(absen)
        db.session.commit()
        flash('Absensi berhasil diperbarui', 'success')
        return redirect(url_for('akademik.absensi_list'))
        
    return render_template('akademik/absensi_form.html', title='Edit Absensi', form=form)

@bp.route('/absensi/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('DELETE', 'Absensi')
def absensi_delete(id):
    absen = Absensi.query.get_or_404(id)
    db.session.delete(absen)
    db.session.commit()
    flash('Absensi berhasil dihapus', 'success')
    return redirect(url_for('akademik.absensi_list'))

# --- TAHFIDZ ---
@bp.route('/tahfidz')
@login_required
def tahfidz_list():
    if current_user.role == 'wali_santri':
        santris = Santri.query.filter_by(wali_user_id=current_user.id).all()
        santri_ids = [s.id for s in santris]
        hafalan = Tahfidz.query.filter(Tahfidz.santri_id.in_(santri_ids)).options(joinedload(Tahfidz.santri).joinedload(Santri.kelas)).order_by(Tahfidz.tanggal_setor.desc()).all()
    else:
        hafalan = Tahfidz.query.options(joinedload(Tahfidz.santri).joinedload(Santri.kelas)).order_by(Tahfidz.tanggal_setor.desc()).all()
    return render_template('akademik/tahfidz_list.html', title='Data Tahfidz', hafalan=hafalan)

@bp.route('/tahfidz/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('CREATE', 'Tahfidz')
def tahfidz_add():
    form = TahfidzForm()
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    
    if form.validate_on_submit():
        tahfidz = Tahfidz(
            santri_id=form.santri_id.data,
            nama_surat=form.nama_surat.data,
            ayat=form.ayat.data,
            kelancaran=form.kelancaran.data,
            tajwid=form.tajwid.data,
            tanggal_setor=form.tanggal_setor.data
        )
        db.session.add(tahfidz)
        db.session.commit()
        flash('Hafalan berhasil disimpan', 'success')
        return redirect(url_for('akademik.tahfidz_list'))
        
    return render_template('akademik/tahfidz_form.html', title='Input Hafalan', form=form)

@bp.route('/tahfidz/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('UPDATE', 'Tahfidz')
def tahfidz_edit(id):
    hafalan = Tahfidz.query.get_or_404(id)
    form = TahfidzForm(obj=hafalan)
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    
    if form.validate_on_submit():
        form.populate_obj(hafalan)
        db.session.commit()
        flash('Hafalan berhasil diperbarui', 'success')
        return redirect(url_for('akademik.tahfidz_list'))
        
    return render_template('akademik/tahfidz_form.html', title='Edit Hafalan', form=form)

@bp.route('/tahfidz/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('DELETE', 'Tahfidz')
def tahfidz_delete(id):
    hafalan = Tahfidz.query.get_or_404(id)
    db.session.delete(hafalan)
    db.session.commit()
    flash('Hafalan berhasil dihapus', 'success')
    return redirect(url_for('akademik.tahfidz_list'))

# --- RAPORT ---
@bp.route('/raport')
@login_required
def raport_list():
    if current_user.role == 'wali_santri':
        santris = Santri.query.filter_by(wali_user_id=current_user.id).options(joinedload(Santri.kelas)).all()
    else:
        santris = Santri.query.options(joinedload(Santri.kelas)).all()
    return render_template('akademik/raport_list.html', title='E-Raport', santris=santris)

@bp.route('/raport/generate', methods=['GET'])
@login_required
def raport_generate():
    santri_id = request.args.get('santri_id')
    semester = request.args.get('semester')
    
    if not santri_id or not semester:
        flash('Pilih Santri dan Semester terlebih dahulu', 'warning')
        return redirect(url_for('akademik.raport_list'))
        
    service = RaportService()
    data = service.get_raport_data(santri_id, semester)
    
    if request.args.get('format') == 'pdf':
        if HTML is None:
            flash('Fitur PDF belum tersedia di server ini (Missing GTK libraries).', 'warning')
            return render_template('akademik/raport_detail.html', title='Detail Raport', data=data)

        # Handle split generation
        pdf_type = request.args.get('type', 'full') # full, cover, identitas, nilai
        
        # Filter content in template using 'pdf_type'
        data['pdf_type'] = pdf_type
        
        # Prepare absolute paths for WeasyPrint (fix image loading)
        if data.get('config'):
            upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'uploads')
            
            # Helper to resolve path (handle both filename only and relative path)
            def resolve_path(path_str):
                if not path_str:
                    return None
                
                # Normalize path separators
                path_str = path_str.replace('\\', '/')
                
                full_path = None
                
                # If path contains 'static', assumes it's relative path from static or root
                if 'static' in path_str or 'img' in path_str:
                    # 1. Try full match from root (e.g., 'app/static/img/uploads/logo.png')
                    # Go up one level from 'app' if path starts with 'app'
                    candidate = os.path.join(current_app.root_path, '..', path_str)
                    if os.path.exists(candidate):
                        full_path = candidate
                    else:
                        # Try from root directly
                        candidate = os.path.join(current_app.root_path, path_str.replace('app/', '', 1) if path_str.startswith('app/') else path_str)
                        if os.path.exists(candidate):
                            full_path = candidate
                        else:
                            # 2. Try basename in uploads folder
                            basename = os.path.basename(path_str)
                            candidate = os.path.join(upload_folder, basename)
                            if os.path.exists(candidate):
                                full_path = candidate
                            else:
                                # 3. Try relative to static folder
                                if path_str.startswith('img/'):
                                     candidate = os.path.join(current_app.root_path, 'static', path_str)
                                     if os.path.exists(candidate):
                                        full_path = candidate

                else:
                    # Assumes it's just filename in uploads folder
                    candidate = os.path.join(upload_folder, path_str)
                    if os.path.exists(candidate):
                        full_path = candidate
                
                if full_path:
                    # Convert to file URI
                    from pathlib import Path
                    return Path(full_path).absolute().as_uri()
                
                return None

            if data['config'].logo_kemenag:
                data['logo_kemenag_path'] = resolve_path(data['config'].logo_kemenag)
            
            if data['config'].logo_lembaga:
                data['logo_lembaga_path'] = resolve_path(data['config'].logo_lembaga)
                
            # Also santri photo
            if data['santri'].foto:
                data['foto_santri_path'] = os.path.join(current_app.root_path, 'static', 'img', 'uploads', 'santri', data['santri'].foto).replace('\\', '/')
        
        html = render_template('akademik/raport_pdf.html', data=data)
        pdf = HTML(string=html).write_pdf()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        filename_suffix = f"_{pdf_type.capitalize()}" if pdf_type != 'full' else ""
        response.headers['Content-Disposition'] = f'inline; filename=Raport_{data["santri"].nama}_{semester}{filename_suffix}.pdf'
        return response
        
    return render_template('akademik/raport_detail.html', title='Detail Raport', data=data)

@bp.route('/raport/input', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz', 'wali_kelas')
@log_audit('UPDATE', 'Raport')
def raport_input():
    santri_id = request.args.get('santri_id')
    semester = request.args.get('semester')
    
    form = RaportForm()
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    
    if request.method == 'GET' and santri_id and semester:
        form.santri_id.data = int(santri_id)
        form.semester.data = semester
        
        # Try to load existing data
        raport = Raport.query.filter_by(santri_id=santri_id, semester=semester).first()
        if raport:
            form.catatan_wali_kelas.data = raport.catatan_wali_kelas
            form.status_kenaikan.data = raport.status_kenaikan
            form.tanggal_bagi.data = raport.tanggal_bagi
            
            # Load Sikap
            form.sikap_akhlak.data = raport.sikap_akhlak
            form.sikap_kerajinan.data = raport.sikap_kerajinan
            form.sikap_kedisiplinan.data = raport.sikap_kedisiplinan
            form.sikap_kebersihan.data = raport.sikap_kebersihan
            
            # Load Deskripsi (LPQ)
            form.deskripsi_moral.data = raport.deskripsi_moral
            form.deskripsi_kognitif.data = raport.deskripsi_kognitif
            form.deskripsi_sosial.data = raport.deskripsi_sosial
            form.deskripsi_bahasa.data = raport.deskripsi_bahasa
            form.deskripsi_seni.data = raport.deskripsi_seni
            form.deskripsi_diri.data = raport.deskripsi_diri
            
            # Load Absensi Snapshot
            form.sakit.data = raport.sakit
            form.izin.data = raport.izin
            form.alpha.data = raport.alpha
            
            # Load Rank
            form.rank.data = raport.rank
            form.total_students.data = raport.total_students
            
    if form.validate_on_submit():
        raport = Raport.query.filter_by(santri_id=form.santri_id.data, semester=form.semester.data).first()
        if not raport:
            raport = Raport(
                santri_id=form.santri_id.data,
                semester=form.semester.data
            )
            db.session.add(raport)
            
        raport.catatan_wali_kelas = form.catatan_wali_kelas.data
        raport.status_kenaikan = form.status_kenaikan.data
        raport.tanggal_bagi = form.tanggal_bagi.data
        
        # Save Sikap
        raport.sikap_akhlak = form.sikap_akhlak.data
        raport.sikap_kerajinan = form.sikap_kerajinan.data
        raport.sikap_kedisiplinan = form.sikap_kedisiplinan.data
        raport.sikap_kebersihan = form.sikap_kebersihan.data
        
        # Save Deskripsi (LPQ)
        raport.deskripsi_moral = form.deskripsi_moral.data
        raport.deskripsi_kognitif = form.deskripsi_kognitif.data
        raport.deskripsi_sosial = form.deskripsi_sosial.data
        raport.deskripsi_bahasa = form.deskripsi_bahasa.data
        raport.deskripsi_seni = form.deskripsi_seni.data
        raport.deskripsi_diri = form.deskripsi_diri.data
        
        # Save Absensi Snapshot
        raport.sakit = form.sakit.data
        raport.izin = form.izin.data
        raport.alpha = form.alpha.data
        
        # Save Rank
        if form.rank.data:
            raport.rank = form.rank.data
            raport.total_students = form.total_students.data
        
        db.session.commit()
        flash('Data Raport berhasil disimpan', 'success')
        return redirect(url_for('akademik.raport_list'))
        
    return render_template('akademik/raport_form.html', title='Input Data Raport', form=form)
