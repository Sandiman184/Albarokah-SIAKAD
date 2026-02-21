from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.models.keuangan import Keuangan, PosKeuangan, TransaksiKeuangan, TabunganSantri, KonfigurasiLaporan
from app.models.akademik import Santri
from app.forms.keuangan import PembayaranForm, PosKeuanganForm, TransaksiKeuanganForm, TabunganForm, KonfigurasiLaporanForm, LaporanKeuanganForm
from app.decorators import role_required
from datetime import datetime
from werkzeug.utils import secure_filename
from app.services.audit_service import log_audit

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
        pembayaran_list = Keuangan.query.filter(Keuangan.santri_id.in_(santri_ids)).options(joinedload(Keuangan.santri)).order_by(Keuangan.tanggal_bayar.desc()).all()
    else:
        pembayaran_list = Keuangan.query.options(joinedload(Keuangan.santri)).order_by(Keuangan.tanggal_bayar.desc()).all()
        
    return render_template('keuangan/pembayaran_list.html', title='Data Keuangan', pembayaran_list=pembayaran_list)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
@log_audit('CREATE', 'Keuangan')
def add():
    form = PembayaranForm()
    # Populate santri choices
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
    
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
    
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    form.santri_id.choices = [(s.id, f"{s.nama} ({s.kelas.nama_kelas if s.kelas else '-'})") for s in santris]
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
@log_audit('DELETE', 'Keuangan')
def delete(id):
    pembayaran = Keuangan.query.get_or_404(id)
    db.session.delete(pembayaran)
    db.session.commit()
    flash('Data pembayaran berhasil dihapus', 'success')
    return redirect(url_for('keuangan.index'))

# --- POS KEUANGAN (CATEGORIES) ---
@bp.route('/kategori')
@login_required
@role_required('admin')
def kategori_list():
    kategori_list = PosKeuangan.query.all()
    return render_template('keuangan/kategori_list.html', title='Kategori Keuangan', kategori_list=kategori_list)

@bp.route('/kategori/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
@log_audit('CREATE', 'PosKeuangan')
def kategori_add():
    form = PosKeuanganForm()
    if form.validate_on_submit():
        pos = PosKeuangan(
            nama=form.nama.data,
            tipe=form.tipe.data,
            kode=form.kode.data,
            keterangan=form.keterangan.data
        )
        db.session.add(pos)
        db.session.commit()
        flash('Kategori keuangan berhasil ditambahkan', 'success')
        return redirect(url_for('keuangan.kategori_list'))
    return render_template('keuangan/kategori_form.html', title='Tambah Kategori', form=form)

@bp.route('/kategori/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
@log_audit('UPDATE', 'PosKeuangan')
def kategori_edit(id):
    pos = PosKeuangan.query.get_or_404(id)
    form = PosKeuanganForm(obj=pos)
    if form.validate_on_submit():
        form.populate_obj(pos)
        db.session.commit()
        flash('Kategori keuangan berhasil diperbarui', 'success')
        return redirect(url_for('keuangan.kategori_list'))
    return render_template('keuangan/kategori_form.html', title='Edit Kategori', form=form)

@bp.route('/kategori/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
@log_audit('DELETE', 'PosKeuangan')
def kategori_delete(id):
    pos = PosKeuangan.query.get_or_404(id)
    db.session.delete(pos)
    db.session.commit()
    flash('Kategori keuangan berhasil dihapus', 'success')
    return redirect(url_for('keuangan.kategori_list'))

# --- TRANSAKSI KEUANGAN ---
@bp.route('/transaksi')
@login_required
def transaksi_list():
    transaksi_list = TransaksiKeuangan.query.options(
        joinedload(TransaksiKeuangan.pos),
        joinedload(TransaksiKeuangan.santri)
    ).order_by(TransaksiKeuangan.tanggal.desc()).all()
    return render_template('keuangan/transaksi_list.html', title='Transaksi Keuangan', transaksi_list=transaksi_list)

@bp.route('/transaksi/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
def transaksi_add():
    form = TransaksiKeuanganForm()
    form.pos_id.choices = [(p.id, f"{p.nama} ({p.tipe})") for p in PosKeuangan.query.all()]
    santris = Santri.query.all()
    # Add empty option for non-santri transactions
    form.santri_id.choices = [(0, '- Umum -')] + [(s.id, f"{s.nama}") for s in santris]
    
    if form.validate_on_submit():
        filename = None
        if form.bukti_pembayaran.data:
            file = form.bukti_pembayaran.data
            filename = secure_filename(file.filename)
            # Ensure upload folder exists
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'bukti_bayar')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file.save(os.path.join(upload_dir, filename))
            
        santri_id = form.santri_id.data if form.santri_id.data != 0 else None
        
        transaksi = TransaksiKeuangan(
            pos_id=form.pos_id.data,
            santri_id=santri_id,
            jumlah=form.jumlah.data,
            jenis=form.jenis.data,
            tanggal=form.tanggal.data,
            keterangan=form.keterangan.data,
            metode_pembayaran=form.metode_pembayaran.data,
            bukti_pembayaran=filename,
            user_id=current_user.id
        )
        db.session.add(transaksi)
        db.session.commit()
        flash('Transaksi berhasil disimpan', 'success')
        return redirect(url_for('keuangan.transaksi_list'))
        
    return render_template('keuangan/transaksi_form.html', title='Tambah Transaksi', form=form)

# --- TABUNGAN SANTRI ---
@bp.route('/tabungan')
@login_required
def tabungan_list():
    tabungan_list = TabunganSantri.query.options(joinedload(TabunganSantri.santri)).order_by(TabunganSantri.tanggal.desc()).all()
    return render_template('keuangan/tabungan_list.html', title='Tabungan Santri', tabungan_list=tabungan_list)

@bp.route('/tabungan/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ustadz')
def tabungan_add():
    form = TabunganForm()
    santris = Santri.query.all()
    form.santri_id.choices = [(s.id, s.nama) for s in santris]
    
    if form.validate_on_submit():
        last_tx = TabunganSantri.query.filter_by(santri_id=form.santri_id.data).order_by(TabunganSantri.id.desc()).first()
        current_saldo = last_tx.saldo_akhir if last_tx else 0
        
        if form.jenis.data == 'tarik' and current_saldo < form.jumlah.data:
            flash(f'Saldo tidak mencukupi! Saldo saat ini: {current_saldo}', 'danger')
            return render_template('keuangan/tabungan_form.html', title='Transaksi Tabungan', form=form)
            
        if form.jenis.data == 'setor':
            new_saldo = float(current_saldo) + float(form.jumlah.data)
        else:
            new_saldo = float(current_saldo) - float(form.jumlah.data)
            
        tabungan = TabunganSantri(
            santri_id=form.santri_id.data,
            jenis=form.jenis.data,
            jumlah=form.jumlah.data,
            tanggal=form.tanggal.data,
            keterangan=form.keterangan.data,
            user_id=current_user.id,
            saldo_akhir=new_saldo
        )
        db.session.add(tabungan)
        db.session.commit()
        flash('Transaksi tabungan berhasil disimpan', 'success')
        return redirect(url_for('keuangan.tabungan_list'))
        
    return render_template('keuangan/tabungan_form.html', title='Transaksi Tabungan', form=form)

# --- LAPORAN & KONFIGURASI ---
@bp.route('/laporan', methods=['GET', 'POST'])
@login_required
def laporan():
    form = LaporanKeuanganForm()
    
    # Default date range: 1st of current month to today
    if not form.start_date.data:
        today = datetime.today()
        form.start_date.data = today.replace(day=1)
        form.end_date.data = today
        
    laporan_data = None
    konfigurasi = KonfigurasiLaporan.query.first()
    
    if form.validate_on_submit() or request.method == 'GET':
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # Get Transactions
        transaksi = TransaksiKeuangan.query.filter(
            TransaksiKeuangan.tanggal >= start_date,
            TransaksiKeuangan.tanggal <= end_date
        ).options(
            joinedload(TransaksiKeuangan.pos),
            joinedload(TransaksiKeuangan.santri)
        ).order_by(TransaksiKeuangan.tanggal.asc()).all()
        
        # Calculate Totals per Category
        summary = {}
        total_masuk = 0
        total_keluar = 0
        
        for tx in transaksi:
            cat_name = tx.pos.nama
            if cat_name not in summary:
                summary[cat_name] = {'tipe': tx.pos.tipe, 'total': 0}
            
            summary[cat_name]['total'] += float(tx.jumlah)
            
            if tx.jenis == 'masuk':
                total_masuk += float(tx.jumlah)
            else:
                total_keluar += float(tx.jumlah)
                
        laporan_data = {
            'transaksi': transaksi,
            'summary': summary,
            'total_masuk': total_masuk,
            'total_keluar': total_keluar,
            'saldo': total_masuk - total_keluar,
            'periode': f"{start_date.strftime('%d %B %Y')} s/d {end_date.strftime('%d %B %Y')}"
        }
        
        if form.cetak_pdf.data:
            # Render PDF Template (For now just a print-friendly HTML page)
            return render_template('keuangan/laporan_print.html', 
                                   data=laporan_data, 
                                   config=konfigurasi,
                                   title='Laporan Keuangan',
                                   now=datetime.now())

    return render_template('keuangan/laporan_index.html', title='Laporan Keuangan', form=form, data=laporan_data)

@bp.route('/konfigurasi', methods=['GET', 'POST'])
@login_required
@role_required('admin')
@log_audit('UPDATE', 'KonfigurasiLaporan')
def konfigurasi():
    config = KonfigurasiLaporan.query.first()
    form = KonfigurasiLaporanForm(obj=config)
    
    if form.validate_on_submit():
        if not config:
            config = KonfigurasiLaporan()
            db.session.add(config)
            
        form.populate_obj(config)
        
        if form.logo.data:
            file = form.logo.data
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(current_app.root_path, 'static', 'img')
            # Save as 'logo_lembaga.png' or similar to be consistent
            ext = os.path.splitext(filename)[1]
            new_filename = f"logo_lembaga{ext}"
            file.save(os.path.join(upload_dir, new_filename))
            config.logo_path = new_filename
            
        db.session.commit()
        flash('Konfigurasi laporan berhasil disimpan', 'success')
        return redirect(url_for('keuangan.konfigurasi'))
        
    return render_template('keuangan/konfigurasi_form.html', title='Konfigurasi Laporan', form=form, config=config)
