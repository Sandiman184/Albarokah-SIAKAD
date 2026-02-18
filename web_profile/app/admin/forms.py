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
    kategori = SelectField('Kategori', choices=[('Fasilitas', 'Fasilitas'), ('Kegiatan', 'Kegiatan'), ('Prestasi', 'Prestasi'), ('Lainnya', 'Lainnya')])
    deskripsi = TextAreaField('Deskripsi / Caption')
    submit = SubmitField('Simpan')

class PengaturanForm(FlaskForm):
    nama_pesantren = StringField('Nama Pesantren', validators=[DataRequired()])
    alamat = TextAreaField('Alamat Lengkap')
    telepon = StringField('No. Telepon')
    email = StringField('Email')
    deskripsi_singkat = TextAreaField('Deskripsi Singkat (untuk Footer & SEO)')
    
    # Social Media
    facebook = StringField('Link Facebook')
    instagram = StringField('Link Instagram')
    tiktok = StringField('Link TikTok')
    youtube = StringField('Link YouTube')
    
    # Maps
    maps_embed = TextAreaField('Embed Google Maps (HTML)')
    maps_link = StringField('Link Google Maps (untuk tombol Footer)')
    
    # Profile Pesantren
    hero_title_1 = StringField('Judul Hero Baris 1', default='Selamat Datang di')
    hero_title_2 = StringField('Judul Hero Baris 2', default='Pondok Pesantren Al Qur\'an')
    hero_title_3 = StringField('Judul Hero Baris 3', default='Al-Barokah')
    hero_subtitle = TextAreaField('Subjudul Hero', default='Mewujudkan Generasi Qur\'ani yang Berakhlak Mulia, Cerdas, dan Mandiri')
    
    sejarah = TextAreaField('Sejarah Pesantren')
    sejarah_gambar = FileField('Foto Sejarah', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Hanya file gambar yang diperbolehkan!')])
    visi = TextAreaField('Visi')
    misi = TextAreaField('Misi')
    
    submit = SubmitField('Simpan Pengaturan')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    current_password = PasswordField('Password Saat Ini')
    new_password = PasswordField('Password Baru (Kosongkan jika tidak ingin mengganti)')
    confirm_password = PasswordField('Konfirmasi Password Baru')
    submit = SubmitField('Update Profil')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password (Kosongkan jika tidak ingin mengganti)')
    role = SelectField('Role', choices=[('admin', 'Admin'), ('superadmin', 'Super Admin')])
    submit = SubmitField('Simpan User')

class ProgramForm(FlaskForm):
    nama = StringField('Nama Program', validators=[DataRequired()])
    deskripsi = TextAreaField('Deskripsi')
    icon = StringField('Icon FontAwesome (cth: fas fa-book)')
    gambar = FileField('Upload Gambar', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Hanya file gambar yang diperbolehkan!')])
    parent_id = SelectField('Induk Program (Opsional)', coerce=int, choices=[(0, 'Utama')])
    submit = SubmitField('Simpan')

class PimpinanForm(FlaskForm):
    nama = StringField('Nama Lengkap', validators=[DataRequired()])
    jabatan = StringField('Jabatan', validators=[DataRequired()])
    gambar = FileField('Foto Profil', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Hanya file gambar yang diperbolehkan!')])
    urutan = StringField('Urutan Tampil (Angka)', default='0')
    submit = SubmitField('Simpan')
