from app import db

class Konfigurasi(db.Model):
    __tablename__ = 'konfigurasi'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_lembaga = db.Column(db.String(100), default='Pondok Pesantren Al-Barokah')
    alamat_lembaga = db.Column(db.Text, default='Jl. Raya...')
    
    # Logo paths (stored in static/img/uploads usually)
    logo_kemenag = db.Column(db.String(255))
    logo_lembaga = db.Column(db.String(255))
    
    # Kepala Sekolah Info (DEPRECATED/General)
    kepala_sekolah = db.Column(db.String(100))
    nip_kepala = db.Column(db.String(50))
    
    # LPQ Config
    nama_lpq = db.Column(db.String(100), default="Taman Pendidikan Al-Qur'an Al-Barokah")
    kepala_lpq = db.Column(db.String(100))
    nip_lpq = db.Column(db.String(50))

    # MDTA Config
    nama_mdta = db.Column(db.String(100), default="Madrasah Diniyah Takmiliyah Al-Barokah")
    kepala_mdta = db.Column(db.String(100))
    nip_mdta = db.Column(db.String(50))
    
    # Default settings for report
    tanggal_raport_default = db.Column(db.Date)
    
    # Tanda Tangan
    kota_ttd = db.Column(db.String(50), default='Karangjati')
