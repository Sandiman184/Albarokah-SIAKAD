from app import db
from datetime import datetime

class Santri(db.Model):
    __tablename__ = 'santri'
    
    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.String(10), nullable=False) # L/P
    tanggal_lahir = db.Column(db.Date, nullable=False)
    alamat = db.Column(db.Text)
    status = db.Column(db.String(20), default='aktif') # aktif, lulus, keluar
    jenjang = db.Column(db.String(20)) # SD, SMP, SMA
    
    kelas_id = db.Column(db.Integer, db.ForeignKey('kelas.id'))
    wali_user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Akun ortu
    
    # Relations
    nilai = db.relationship('Nilai', backref='santri', lazy='dynamic')
    tahfidz = db.relationship('Tahfidz', backref='santri', lazy='dynamic')
    absensi = db.relationship('Absensi', backref='santri', lazy='dynamic')
    keuangan = db.relationship('Keuangan', backref='santri', lazy='dynamic')
    raport = db.relationship('Raport', backref='santri', lazy='dynamic')

class Pengajar(db.Model):
    __tablename__ = 'pengajar'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(20))
    alamat = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Kelas(db.Model):
    __tablename__ = 'kelas'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String(50), nullable=False)
    jenjang = db.Column(db.String(20))
    wali_kelas_id = db.Column(db.Integer, db.ForeignKey('pengajar.id'))
    
    # Relations
    wali_kelas = db.relationship('Pengajar', foreign_keys=[wali_kelas_id])
    santri_list = db.relationship('Santri', backref='kelas', lazy='dynamic')

class MataPelajaran(db.Model):
    __tablename__ = 'mata_pelajaran'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_mapel = db.Column(db.String(100), nullable=False)
    jenjang = db.Column(db.String(20))
    kkm = db.Column(db.Float, default=70.0)

class Nilai(db.Model):
    __tablename__ = 'nilai'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'))
    mapel_id = db.Column(db.Integer, db.ForeignKey('mata_pelajaran.id'))
    semester = db.Column(db.String(20)) # Ganjil/Genap 2023/2024
    
    nilai_harian = db.Column(db.Float, default=0)
    nilai_uts = db.Column(db.Float, default=0)
    nilai_uas = db.Column(db.Float, default=0)
    nilai_praktik = db.Column(db.Float, default=0)
    
    mapel = db.relationship('MataPelajaran')

class Tahfidz(db.Model):
    __tablename__ = 'tahfidz'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'))
    nama_surat = db.Column(db.String(50))
    ayat = db.Column(db.String(50))
    kelancaran = db.Column(db.String(20)) # Lancar, Kurang, Ulang
    tajwid = db.Column(db.String(20)) # Bagus, Cukup, Kurang
    tanggal_setor = db.Column(db.Date, default=datetime.utcnow)

class Absensi(db.Model):
    __tablename__ = 'absensi'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'))
    tanggal = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(10)) # Hadir, Izin, Sakit, Alpha

class Raport(db.Model):
    __tablename__ = 'raport'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'))
    semester = db.Column(db.String(50)) # e.g. "Ganjil 2023/2024"
    catatan_wali_kelas = db.Column(db.Text)
    status_kenaikan = db.Column(db.String(50)) # "Naik ke Kelas ...", "Lulus", "Tinggal Kelas"
    tanggal_bagi = db.Column(db.Date, default=datetime.utcnow)
