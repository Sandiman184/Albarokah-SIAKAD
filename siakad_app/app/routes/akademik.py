from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.models.akademik import Santri, MataPelajaran, Nilai, Absensi, Tahfidz, Raport
from app.forms.akademik import NilaiForm, AbsensiForm, TahfidzForm, RaportForm
from app.decorators import role_required
from app.services.raport import RaportService
from app.services.audit_service import log_audit
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
            nilai_uts=form.nilai_uts.data,
            nilai_uas=form.nilai_uas.data,
            nilai_praktik=form.nilai_praktik.data
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
        absensis = Absensi.query.options(joinedload(Absensi.santri).joinedload(Santri.kelas)).order_by(Absensi.tanggal.desc()).all()
    return render_template('akademik/absensi_list.html', title='Data Absensi', absensis=absensis)

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

        # For immediate download, we still need to wait, but this structure allows future async expansion.
        # In a full async implementation, we would return a "Processing" status and poll for completion.
        # For now, we keep it synchronous but refactored, or we could save to file and serve static.
        
        html = render_template('akademik/raport_pdf.html', data=data)
        pdf = HTML(string=html).write_pdf()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=Raport_{data["santri"].nama}_{semester}.pdf'
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
        
        db.session.commit()
        flash('Data Raport berhasil disimpan', 'success')
        return redirect(url_for('akademik.raport_list'))
        
    return render_template('akademik/raport_form.html', title='Input Data Raport', form=form)
