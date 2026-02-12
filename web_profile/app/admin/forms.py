from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BeritaForm(FlaskForm):
    judul = StringField('Judul', validators=[DataRequired()])
    slug = StringField('Slug (URL)', validators=[DataRequired()])
    konten = TextAreaField('Konten', validators=[DataRequired()])
    gambar = FileField('Upload Gambar', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Hanya file gambar yang diperbolehkan!')])
    status = SelectField('Status', choices=[('published', 'Published'), ('draft', 'Draft')])
    kategori = SelectField('Kategori', choices=[('berita', 'Berita'), ('pengumuman', 'Pengumuman'), ('artikel', 'Artikel')])
    submit = SubmitField('Simpan')

class AgendaForm(FlaskForm):
    nama_kegiatan = StringField('Nama Kegiatan', validators=[DataRequired()])
    tanggal_mulai = DateTimeField('Mulai', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    tanggal_selesai = DateTimeField('Selesai', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    lokasi = StringField('Lokasi', validators=[DataRequired()])
    deskripsi = TextAreaField('Deskripsi')
    submit = SubmitField('Simpan')

class GaleriForm(FlaskForm):
    judul = StringField('Judul')
    gambar = FileField('Upload Gambar', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Hanya file gambar yang diperbolehkan!')])
    kategori = SelectField('Kategori', choices=[('Fasilitas', 'Fasilitas'), ('Kegiatan', 'Kegiatan'), ('Prestasi', 'Prestasi')])
    deskripsi = TextAreaField('Deskripsi / Caption')
    submit = SubmitField('Simpan')

class PengaturanForm(FlaskForm):
    nama_pesantren = StringField('Nama Pesantren', validators=[DataRequired()])
    alamat = TextAreaField('Alamat Lengkap')
    telepon = StringField('No. Telepon')
    email = StringField('Email')
    deskripsi_singkat = TextAreaField('Deskripsi Singkat (untuk Footer & SEO)')
    facebook = StringField('Link Facebook')
    instagram = StringField('Link Instagram')
    youtube = StringField('Link YouTube')
    maps_embed = TextAreaField('Embed Google Maps (HTML)')
    submit = SubmitField('Simpan Pengaturan')
