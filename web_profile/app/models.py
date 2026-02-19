from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='admin') # superadmin, admin, editor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        # Support legacy Werkzeug hashes
        if self.password_hash.startswith(('pbkdf2:', 'sha256:')):
            return check_password_hash(self.password_hash, password)
            
        try:
            return ph.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False
            
    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='logs')
    action = db.Column(db.String(50), nullable=False) # CREATE, UPDATE, DELETE, LOGIN, BACKUP, RESTORE
    target = db.Column(db.String(50)) # Berita, Agenda, User, System
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    konten = db.Column(db.Text, nullable=False)
    gambar = db.Column(db.String(255))
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    penulis = db.Column(db.String(100))
    status = db.Column(db.String(20), default='published', index=True) # published, draft
    kategori = db.Column(db.String(50), default='berita', index=True) # berita, pengumuman, artikel

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
    nama_pesantren = db.Column(db.String(100), default='Pondok Pesantren Al Qur\'an Al-Barokah')
    alamat = db.Column(db.Text)
    telepon = db.Column(db.String(20))
    email = db.Column(db.String(100))
    deskripsi_singkat = db.Column(db.Text)
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    tiktok = db.Column(db.String(255))
    youtube = db.Column(db.String(255))
    maps_embed = db.Column(db.Text)
    maps_link = db.Column(db.String(255)) # For clickable map link in footer
    
    # Statistics
    jumlah_santri = db.Column(db.Integer, default=150)
    jumlah_alumni = db.Column(db.Integer, default=500)
    jumlah_ustadz = db.Column(db.Integer, default=25)
    jumlah_kitab = db.Column(db.Integer, default=50)
    
    # New fields for Profile
    sejarah = db.Column(db.Text)
    sejarah_gambar = db.Column(db.String(255))
    struktur_organisasi_gambar = db.Column(db.String(255))
    visi = db.Column(db.Text)
    misi = db.Column(db.Text)
    
    # New fields for Homepage Hero
    hero_title_1 = db.Column(db.String(100), default='Selamat Datang di')
    hero_title_2 = db.Column(db.String(100), default='Pondok Pesantren Al Qur\'an')
    hero_title_3 = db.Column(db.String(100), default='Al-Barokah')
    hero_subtitle = db.Column(db.String(255), default='Mewujudkan Generasi Qur\'ani yang Berakhlak Mulia, Cerdas, dan Mandiri')
    
class Pimpinan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    jabatan = db.Column(db.String(100)) # e.g. Pengasuh, Kepala Madrasah
    gambar = db.Column(db.String(255))
    urutan = db.Column(db.Integer, default=0)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False) # e.g. LPQ, MDT
    deskripsi = db.Column(db.Text)
    icon = db.Column(db.String(50)) # FontAwesome class
    gambar = db.Column(db.String(255)) # URL
    urutan = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('program.id')) # For sub-programs like TKQ under LPQ
    children = db.relationship('Program', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
