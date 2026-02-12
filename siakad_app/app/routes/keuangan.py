from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.keuangan import Keuangan
from app.models.akademik import Santri
from app.forms.keuangan import PembayaranForm
from app.decorators import role_required
from datetime import datetime

bp = Blueprint('keuangan', __name__, url_prefix='/keuangan')

@bp.route('/')
@login_required
def index():
    # Admin/Ustadz can see all, Wali Santri only sees their child's data
    if current_user.role == 'wali_santri':
        # Assuming there is a relationship or logic to filter by wali_santri
        # For now, let's assume filtering by santri related to user if applicable, 
        # but based on models, User doesn't directly link to Santri except via 'wali_user_id' in Santri model
        # Let's check Santri model again.
        # Santri has wali_user_id.
        santris = Santri.query.filter_by(wali_user_id=current_user.id).all()
        santri_ids = [s.id for s in santris]
        pembayaran_list = Keuangan.query.filter(Keuangan.santri_id.in_(santri_ids)).order_by(Keuangan.tanggal_bayar.desc()).all()
    else:
        pembayaran_list = Keuangan.query.order_by(Keuangan.tanggal_bayar.desc()).all()
        
    return render_template('keuangan/pembayaran_list.html', title='Data Keuangan', pembayaran_list=pembayaran_list)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
def add():
    form = PembayaranForm()
    # Populate santri choices
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in Santri.query.all()]
    
    # Populate tahun choices (current year - 2 to current year + 2)
    current_year = datetime.now().year
    form.tahun.choices = [(y, y) for y in range(current_year - 2, current_year + 3)]
    
    if form.validate_on_submit():
        pembayaran = Keuangan(
            santri_id=form.santri_id.data,
            bulan=form.bulan.data,
            tahun=form.tahun.data,
            jumlah=form.jumlah.data,
            status=form.status.data,
            tanggal_bayar=form.tanggal_bayar.data
        )
        db.session.add(pembayaran)
        db.session.commit()
        flash('Data pembayaran berhasil disimpan', 'success')
        return redirect(url_for('keuangan.index'))
        
    # Set default date to today
    if not form.tanggal_bayar.data:
        form.tanggal_bayar.data = datetime.today()
    
    # Set default tahun to current year
    if not form.tahun.data:
        form.tahun.data = current_year

    return render_template('keuangan/pembayaran_form.html', title='Input Pembayaran', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
def edit(id):
    pembayaran = Keuangan.query.get_or_404(id)
    form = PembayaranForm(obj=pembayaran)
    
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in Santri.query.all()]
    current_year = datetime.now().year
    form.tahun.choices = [(y, y) for y in range(current_year - 2, current_year + 3)]
    
    if form.validate_on_submit():
        form.populate_obj(pembayaran)
        db.session.commit()
        flash('Data pembayaran berhasil diperbarui', 'success')
        return redirect(url_for('keuangan.index'))
        
    return render_template('keuangan/pembayaran_form.html', title='Edit Pembayaran', form=form)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete(id):
    pembayaran = Keuangan.query.get_or_404(id)
    db.session.delete(pembayaran)
    db.session.commit()
    flash('Data pembayaran berhasil dihapus', 'success')
    return redirect(url_for('keuangan.index'))
