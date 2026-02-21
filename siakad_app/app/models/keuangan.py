from app import db
from datetime import datetime

class Keuangan(db.Model):
    __tablename__ = 'keuangan'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'))
    bulan = db.Column(db.String(20)) # Januari
    tahun = db.Column(db.Integer) # 2024
    jumlah = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20)) # Lunas, Belum Lunas
    tanggal_bayar = db.Column(db.Date, nullable=True)

    santri = db.relationship('Santri', backref='pembayaran')

    def __repr__(self):
        return f'<Keuangan {self.santri.nama} - {self.bulan} {self.tahun}>'

class PosKeuangan(db.Model):
    __tablename__ = 'pos_keuangan'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False) # e.g. "SPP", "Pendaftaran", "Uang Gedung", "Donasi", "Bantuan Pemerintah", "Usaha Kantin"
    tipe = db.Column(db.String(20), nullable=False) # 'pemasukan', 'pengeluaran'
    kode = db.Column(db.String(20)) # Kode Akun (e.g. 4001)
    keterangan = db.Column(db.String(255))
    
    transaksi = db.relationship('TransaksiKeuangan', backref='pos', lazy='dynamic')

    def __repr__(self):
        return f'<PosKeuangan {self.nama}>'

class TransaksiKeuangan(db.Model):
    __tablename__ = 'transaksi_keuangan'
    
    id = db.Column(db.Integer, primary_key=True)
    pos_id = db.Column(db.Integer, db.ForeignKey('pos_keuangan.id'), nullable=False, index=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'), nullable=True, index=True) # Nullable for general transactions
    jumlah = db.Column(db.Numeric(15, 2), nullable=False)
    jenis = db.Column(db.String(10), nullable=False) # 'masuk', 'keluar'
    tanggal = db.Column(db.Date, default=datetime.utcnow, index=True)
    keterangan = db.Column(db.String(255))
    metode_pembayaran = db.Column(db.String(50)) # Tunai, Transfer
    bukti_pembayaran = db.Column(db.String(255)) # File path
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Who recorded it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    santri = db.relationship('Santri', backref='transaksi_keuangan')
    user = db.relationship('User', backref='transaksi_keuangan')

    def __repr__(self):
        return f'<TransaksiKeuangan {self.jenis} - {self.jumlah}>'

class TabunganSantri(db.Model):
    __tablename__ = 'tabungan_santri'
    
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'), nullable=False, index=True)
    jenis = db.Column(db.String(10), nullable=False) # 'setor', 'tarik'
    jumlah = db.Column(db.Numeric(15, 2), nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    keterangan = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Who processed it
    saldo_akhir = db.Column(db.Numeric(15, 2)) # Running balance snapshot
    
    santri = db.relationship('Santri', backref='tabungan')
    user = db.relationship('User', backref='tabungan_procesor')

    def __repr__(self):
        return f'<TabunganSantri {self.santri.nama} - {self.jenis} {self.jumlah}>'

class KonfigurasiLaporan(db.Model):
    __tablename__ = 'konfigurasi_laporan'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_lembaga = db.Column(db.String(100), default='Pondok Pesantren Al-Barokah')
    alamat_lembaga = db.Column(db.Text, default='Jl. Raya Puncak KM. 77 Cisarua, Bogor')
    telepon_lembaga = db.Column(db.String(50), default='(0251) 825xxxx')
    email_lembaga = db.Column(db.String(100), default='info@albarokah.ponpes.id')
    logo_path = db.Column(db.String(255)) # Path to logo image
    
    # Tanda Tangan
    kota_ttd = db.Column(db.String(50), default='Bogor')
    nama_ttd = db.Column(db.String(100), default='H. Abdullah')
    jabatan_ttd = db.Column(db.String(100), default='Bendahara Yayasan')
    nip_ttd = db.Column(db.String(50)) # Optional
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<KonfigurasiLaporan {self.nama_lembaga}>'
