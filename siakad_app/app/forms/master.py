from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from app.models.akademik import Santri

JENJANG_CHOICES = [
    ('PAUD', 'PAUD'),
    ('TKQ', 'TKQ'),
    ('TPQ', 'TPQ'),
    ('TKA', 'TKA'),
    ('TQA', 'TQA'),
    ('MDTA', 'MDTA'),
    ('MDTW', 'MDTW'),
    ('MDTU', 'MDTU'),
    ('Majelis Taklim', 'Majelis Taklim'),
    ('SD', 'SD'),
    ('SMP', 'SMP'),
    ('SMA', 'SMA'),
    ('Lainnya', 'Lainnya')
]

class SantriForm(FlaskForm):
    nis = StringField('NIS', validators=[DataRequired(), Length(max=20)])
    nama = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=100)])
    jenis_kelamin = SelectField('Jenis Kelamin', choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    tempat_lahir = StringField('Tempat Lahir', validators=[Length(max=50)])
    tanggal_lahir = DateField('Tanggal Lahir', validators=[DataRequired()])
    alamat = TextAreaField('Alamat')
    nama_ayah = StringField('Nama Ayah', validators=[Length(max=100)])
    nama_ibu = StringField('Nama Ibu', validators=[Length(max=100)])
    pekerjaan_ayah = StringField('Pekerjaan Ayah', validators=[Length(max=50)])
    pekerjaan_ibu = StringField('Pekerjaan Ibu', validators=[Length(max=50)])
    alamat_orang_tua = TextAreaField('Alamat Orang Tua')
    nama_wali = StringField('Nama Wali', validators=[Length(max=100)])
    pekerjaan_wali = StringField('Pekerjaan Wali', validators=[Length(max=50)])
    alamat_wali = TextAreaField('Alamat Wali')
    hubungan_wali = StringField('Hubungan dengan Wali', validators=[Length(max=50)])
    agama = StringField('Agama', default='Islam')
    pendidikan_sebelumnya = StringField('Pendidikan Sebelumnya', validators=[Length(max=50)])
    tanggal_masuk = DateField('Tanggal Masuk', default=datetime.utcnow)
    
    anak_ke = StringField('Anak ke-', validators=[Length(max=5)]) # String to allow "1" or "Pertama"
    jumlah_saudara = StringField('Jumlah Saudara', validators=[Length(max=5)])
    no_hp_wali = StringField('No. HP Orang Tua/Wali', validators=[Length(max=20)])
    
    jenjang = SelectField('Jenjang', choices=JENJANG_CHOICES, validators=[DataRequired()])
    status = SelectField('Status', choices=[('aktif', 'Aktif'), ('lulus', 'Lulus'), ('keluar', 'Keluar')], default='aktif')
    kelas_id = SelectField('Kelas', coerce=int)
    foto = FileField('Foto Santri', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Hanya file gambar (jpg, png) yang diperbolehkan!')])
    submit = SubmitField('Simpan')

    def __init__(self, original_nis=None, *args, **kwargs):
        super(SantriForm, self).__init__(*args, **kwargs)
        self.original_nis = original_nis

    def validate_nis(self, nis):
        if self.original_nis and nis.data == self.original_nis:
            return
        user = Santri.query.filter_by(nis=nis.data).first()
        if user:
            raise ValidationError('NIS sudah terdaftar.')

class PengajarForm(FlaskForm):
    nama = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=100)])
    nip = StringField('NIP / NIY', validators=[Length(max=30)])
    nuptk = StringField('NUPTK', validators=[Length(max=30)])
    jenis_kelamin = SelectField('Jenis Kelamin', choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    tempat_lahir = StringField('Tempat Lahir', validators=[Length(max=50)])
    tanggal_lahir = DateField('Tanggal Lahir', validators=[DataRequired()])
    no_hp = StringField('No. HP', validators=[Length(max=20)])
    email = StringField('Email', validators=[Length(max=100)])
    alamat = TextAreaField('Alamat')
    pendidikan_terakhir = SelectField('Pendidikan Terakhir', choices=[
        ('SMA', 'SMA/MA'), 
        ('D3', 'D3'), 
        ('S1', 'S1'), 
        ('S2', 'S2'), 
        ('S3', 'S3')
    ], validators=[DataRequired()])
    status_kepegawaian = SelectField('Status Kepegawaian', choices=[
        ('Tetap', 'Tetap'), 
        ('Kontrak', 'Kontrak'), 
        ('Honor', 'Honor')
    ], default='Tetap')
    submit = SubmitField('Simpan')

class KelasForm(FlaskForm):
    nama_kelas = StringField('Nama Kelas', validators=[DataRequired(), Length(max=50)])
    jenjang = SelectField('Jenjang', choices=JENJANG_CHOICES, validators=[DataRequired()])
    wali_kelas_id = SelectField('Wali Kelas', coerce=int)
    submit = SubmitField('Simpan')

class MapelForm(FlaskForm):
    nama_mapel = StringField('Nama Mata Pelajaran', validators=[DataRequired(), Length(max=100)])
    jenjang = SelectField('Jenjang', choices=JENJANG_CHOICES, validators=[DataRequired()])
    kkm = StringField('KKM', default='70.0') # StringField to handle decimal input easier or FloatField
    submit = SubmitField('Simpan')

class KonfigurasiForm(FlaskForm):
    nama_lembaga = StringField('Nama Lembaga', validators=[DataRequired(), Length(max=100)])
    alamat_lembaga = TextAreaField('Alamat Lembaga')
    kepala_sekolah = StringField('Kepala Madrasah', validators=[Optional()])
    nip_kepala = StringField('NIP Kepala Madrasah')
    tanggal_raport_default = DateField('Tanggal Raport Default', validators=[DataRequired()])
    
    logo_kemenag = FileField('Logo Kemenag', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    logo_lembaga = FileField('Logo Lembaga', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    
    # LPQ
    nama_lpq = StringField('Nama LPQ', default="Taman Pendidikan Al-Qur'an Al-Barokah")
    kepala_lpq = StringField('Kepala LPQ')
    nip_lpq = StringField('NIP Kepala LPQ')

    # MDTA
    nama_mdta = StringField('Nama MDTA', default="Madrasah Diniyah Takmiliyah Al-Barokah")
    kepala_mdta = StringField('Kepala MDTA')
    nip_mdta = StringField('NIP Kepala MDTA')
    
    # Keuangan (Kop & Tanda Tangan)
    kota_ttd = StringField('Kota (Tempat TTD)', validators=[Optional()])
    nama_ttd = StringField('Nama Bendahara/Pembuat Laporan', validators=[Optional()])
    jabatan_ttd = StringField('Jabatan Pembuat Laporan', validators=[Optional()])
    nip_ttd = StringField('NIP/NIY Bendahara', validators=[Optional()])
    pimpinan_ponpes_nama = StringField('Nama Pimpinan Ponpes (Mengetahui)', validators=[Optional()])
    pimpinan_ponpes_nip = StringField('NIP/NIY Pimpinan Ponpes', validators=[Optional()])
    
    submit = SubmitField('Simpan Konfigurasi')
