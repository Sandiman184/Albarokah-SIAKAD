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
