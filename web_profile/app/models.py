from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    konten = db.Column(db.Text, nullable=False)
    gambar = db.Column(db.String(255))
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    penulis = db.Column(db.String(100))
    status = db.Column(db.String(20), default='published') # published, draft
    kategori = db.Column(db.String(50), default='berita') # berita, pengumuman, artikel

class Agenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_kegiatan = db.Column(db.String(255), nullable=False)
    tanggal_mulai = db.Column(db.DateTime, nullable=False)
    tanggal_selesai = db.Column(db.DateTime)
    lokasi = db.Column(db.String(255))
    deskripsi = db.Column(db.Text)

class Galeri(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(255))
    gambar = db.Column(db.String(255), nullable=False)
    kategori = db.Column(db.String(50)) # Fasilitas, Kegiatan, Prestasi
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    deskripsi = db.Column(db.Text) # Alt text/caption

class Pengaturan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_pesantren = db.Column(db.String(100), default='Pondok Pesantren Albarokah')
    alamat = db.Column(db.Text)
    telepon = db.Column(db.String(20))
    email = db.Column(db.String(100))
    deskripsi_singkat = db.Column(db.Text)
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    youtube = db.Column(db.String(255))
    maps_embed = db.Column(db.Text)
