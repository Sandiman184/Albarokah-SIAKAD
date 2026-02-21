from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, NumberRange, Optional
from flask_wtf.file import FileAllowed

class PosKeuanganForm(FlaskForm):
    nama = StringField('Nama Kategori', validators=[DataRequired()])
    tipe = SelectField('Tipe', choices=[('pemasukan', 'Pemasukan'), ('pengeluaran', 'Pengeluaran')], validators=[DataRequired()])
    kode = StringField('Kode Akun (Optional)')
    keterangan = TextAreaField('Keterangan')
    submit = SubmitField('Simpan')

class TransaksiKeuanganForm(FlaskForm):
    pos_id = SelectField('Kategori', coerce=int, validators=[DataRequired()])
    santri_id = SelectField('Santri (Optional)', coerce=int, validators=[Optional()])
    jumlah = DecimalField('Jumlah (Rp)', validators=[DataRequired(), NumberRange(min=0)])
    jenis = SelectField('Jenis', choices=[('masuk', 'Masuk'), ('keluar', 'Keluar')], validators=[DataRequired()])
    tanggal = DateField('Tanggal', validators=[DataRequired()])
    keterangan = TextAreaField('Keterangan')
    metode_pembayaran = SelectField('Metode Pembayaran', choices=[('Tunai', 'Tunai'), ('Transfer', 'Transfer')], default='Tunai')
    bukti_pembayaran = FileField('Bukti Pembayaran', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images/PDF only!')])
    submit = SubmitField('Simpan')

class TabunganForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    jenis = SelectField('Jenis Transaksi', choices=[('setor', 'Setor Tunai'), ('tarik', 'Tarik Tunai')], validators=[DataRequired()])
    jumlah = DecimalField('Jumlah (Rp)', validators=[DataRequired(), NumberRange(min=0)])
    tanggal = DateField('Tanggal', validators=[DataRequired()])
    keterangan = TextAreaField('Keterangan')
    submit = SubmitField('Simpan')

class KonfigurasiLaporanForm(FlaskForm):
    nama_lembaga = StringField('Nama Lembaga', validators=[DataRequired()])
    alamat_lembaga = TextAreaField('Alamat Lembaga', validators=[DataRequired()])
    telepon_lembaga = StringField('Telepon')
    email_lembaga = StringField('Email')
    logo = FileField('Logo Lembaga', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    
    kota_ttd = StringField('Kota (Tempat TTD)', validators=[DataRequired()])
    nama_ttd = StringField('Nama Penandatangan', validators=[DataRequired()])
    jabatan_ttd = StringField('Jabatan Penandatangan', validators=[DataRequired()])
    nip_ttd = StringField('NIP/NIY (Optional)')
    submit = SubmitField('Simpan Konfigurasi')

class LaporanKeuanganForm(FlaskForm):
    start_date = DateField('Dari Tanggal', validators=[DataRequired()])
    end_date = DateField('Sampai Tanggal', validators=[DataRequired()])
    submit = SubmitField('Tampilkan Laporan')
    cetak_pdf = SubmitField('Cetak PDF')

class PembayaranForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    bulan = SelectField('Bulan', choices=[
        ('Januari', 'Januari'), ('Februari', 'Februari'), ('Maret', 'Maret'),
        ('April', 'April'), ('Mei', 'Mei'), ('Juni', 'Juni'),
        ('Juli', 'Juli'), ('Agustus', 'Agustus'), ('September', 'September'),
        ('Oktober', 'Oktober'), ('November', 'November'), ('Desember', 'Desember')
    ], validators=[DataRequired()])
    tahun = SelectField('Tahun', coerce=int, validators=[DataRequired()])
    jumlah = DecimalField('Jumlah (Rp)', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Status', choices=[('Lunas', 'Lunas'), ('Belum Lunas', 'Belum Lunas')], validators=[DataRequired()])
    tanggal_bayar = DateField('Tanggal Bayar', validators=[DataRequired()])
    submit = SubmitField('Simpan')
