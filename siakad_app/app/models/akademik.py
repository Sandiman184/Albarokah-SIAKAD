from app import db
from datetime import datetime

class Santri(db.Model):
    __tablename__ = 'santri'
    
    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.String(10), nullable=False) # L/P
    tempat_lahir = db.Column(db.String(50))
    tanggal_lahir = db.Column(db.Date, nullable=False)
    alamat = db.Column(db.Text)
    nama_ayah = db.Column(db.String(100))
    nama_ibu = db.Column(db.String(100))
    pekerjaan_ayah = db.Column(db.String(50))
    pekerjaan_ibu = db.Column(db.String(50))
    alamat_orang_tua = db.Column(db.Text)
    
    # Wali
    nama_wali = db.Column(db.String(100))
    pekerjaan_wali = db.Column(db.String(50))
    alamat_wali = db.Column(db.Text)
    hubungan_wali = db.Column(db.String(50)) # Paman, Kakek, dll
    
    # Data Tambahan
    agama = db.Column(db.String(20), default='Islam')
    pendidikan_sebelumnya = db.Column(db.String(50)) # TK, SD, dll
    tanggal_masuk = db.Column(db.Date, default=datetime.utcnow)
    
    # New Identity Fields
    anak_ke = db.Column(db.Integer)
    jumlah_saudara = db.Column(db.Integer)
    no_hp_wali = db.Column(db.String(20)) # HP Orang Tua/Wali
    
    status = db.Column(db.String(20), default='aktif') # aktif, lulus, keluar
    jenjang = db.Column(db.String(20)) # SD, SMP, SMA
    foto = db.Column(db.String(255)) # Path relative to static/img/uploads/santri
    
    kelas_id = db.Column(db.Integer, db.ForeignKey('kelas.id'), index=True)
    wali_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True) # Akun ortu
    
    # Relations
    nilai = db.relationship('Nilai', backref='santri', lazy='dynamic')
    tahfidz = db.relationship('Tahfidz', backref='santri', lazy='dynamic')
    absensi = db.relationship('Absensi', backref='santri', lazy='dynamic')
    raport = db.relationship('Raport', backref='santri', lazy='dynamic')

class Pengajar(db.Model):
    __tablename__ = 'pengajar'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    nip = db.Column(db.String(30)) # NIP / NIY
    nuptk = db.Column(db.String(30))
    jenis_kelamin = db.Column(db.String(10)) # L/P
    tempat_lahir = db.Column(db.String(50))
    tanggal_lahir = db.Column(db.Date)
    no_hp = db.Column(db.String(20))
    email = db.Column(db.String(100))
    alamat = db.Column(db.Text)
    pendidikan_terakhir = db.Column(db.String(20)) # SMA, D3, S1, S2, S3
    status_kepegawaian = db.Column(db.String(20)) # Tetap, Kontrak, Honor
    
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
    kelompok = db.Column(db.String(50), default='A') # A: Pokok, B: Penunjang/Muatan Lokal
    kkm = db.Column(db.Float, default=70.0)

class Nilai(db.Model):
    __tablename__ = 'nilai'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'), index=True)
    mapel_id = db.Column(db.Integer, db.ForeignKey('mata_pelajaran.id'), index=True)
    semester = db.Column(db.String(20)) # Ganjil/Genap 2023/2024
    
    nilai_harian = db.Column(db.Float, default=0) # 30%
    nilai_kehadiran = db.Column(db.Float, default=0) # 30%
    nilai_uts = db.Column(db.Float, default=0) # Not used in formula, kept for legacy
    nilai_uas = db.Column(db.Float, default=0) # Used as NU (40%)
    nilai_praktik = db.Column(db.Float, default=0) # Not used in formula, kept for legacy
    
    deskripsi = db.Column(db.String(255)) # Optional custom description/feedback per subject
    
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
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'), index=True)
    tanggal = db.Column(db.Date, default=datetime.utcnow, index=True)
    status = db.Column(db.String(10)) # Hadir, Izin, Sakit, Alpha

class Raport(db.Model):
    __tablename__ = 'raport'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'))
    semester = db.Column(db.String(50)) # e.g. "Ganjil 2023/2024"
    catatan_wali_kelas = db.Column(db.Text)
    status_kenaikan = db.Column(db.String(50)) # "Naik ke Kelas ...", "Lulus", "Tinggal Kelas"
    tanggal_bagi = db.Column(db.Date, default=datetime.utcnow)
    
    # Nilai Sikap / Kepribadian (MDTA & LPQ)
    # Enum: Sangat Baik, Baik, Cukup, Kurang
    sikap_akhlak = db.Column(db.String(20))
    sikap_kerajinan = db.Column(db.String(20))
    sikap_kedisiplinan = db.Column(db.String(20))
    sikap_kebersihan = db.Column(db.String(20))
    
    # Laporan Perkembangan (LPQ Specific - Page 4)
    deskripsi_moral = db.Column(db.Text) # Perkembangan Nilai Moral dan Agama
    deskripsi_kognitif = db.Column(db.Text) # Perkembangan Kognitif
    deskripsi_sosial = db.Column(db.Text) # Perkembangan Sosial Emosional
    deskripsi_bahasa = db.Column(db.Text) # Perkembangan Bahasa / Bicara
    deskripsi_seni = db.Column(db.Text) # Perkembangan Seni dan Keterampilan
    deskripsi_diri = db.Column(db.Text) # Pengembangan Diri
    
    # Statistik Absensi (Snapshot)
    sakit = db.Column(db.Integer, default=0)
    izin = db.Column(db.Integer, default=0)
    alpha = db.Column(db.Integer, default=0)
    
    # Ranking
    rank = db.Column(db.Integer)
    total_students = db.Column(db.Integer)
