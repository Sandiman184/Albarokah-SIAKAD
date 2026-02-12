from app import db
from app.models.akademik import Nilai, Absensi, Tahfidz, Santri, MataPelajaran, Raport
from sqlalchemy import func
from datetime import datetime

class RaportService:
    def get_raport_data(self, santri_id, semester):
        santri = Santri.query.get_or_404(santri_id)
        
        # 1. Nilai Akademik
        # Filter by semester
        nilai_list = Nilai.query.filter_by(santri_id=santri_id, semester=semester).all()
        
        raport_nilai = []
        for n in nilai_list:
            # Simple average calculation
            # Assuming fields are not None (default 0 in model if set correctly, otherwise handle None)
            h = n.nilai_harian or 0
            u = n.nilai_uts or 0
            a = n.nilai_uas or 0
            p = n.nilai_praktik or 0
            
            rata_rata = (h + u + a + p) / 4
            
            raport_nilai.append({
                'mapel': n.mapel.nama_mapel,
                'kkm': n.mapel.kkm,
                'harian': h,
                'uts': u,
                'uas': a,
                'praktik': p,
                'nilai_akhir': round(rata_rata, 2),
                'predikat': self.get_predikat(rata_rata),
                'deskripsi': f"Ananda {self.get_predikat_desc(rata_rata)} dalam memahami materi {n.mapel.nama_mapel}."
            })
            
        # 2. Absensi (Total for the semester - strictly speaking should filter by date range of semester, 
        # but for simplicity we'll just count all for now or I need a date range logic)
        # Let's assume we count all for the santri for now as 'Semester' date range isn't defined in DB yet.
        absensi_counts = db.session.query(
            Absensi.status, func.count(Absensi.id)
        ).filter_by(santri_id=santri_id).group_by(Absensi.status).all()
        
        absensi_summary = {'Hadir': 0, 'Sakit': 0, 'Izin': 0, 'Alpha': 0}
        for status, count in absensi_counts:
            # Normalize status string just in case
            s = status.capitalize()
            if s in absensi_summary:
                absensi_summary[s] = count
                
        # 3. Tahfidz
        tahfidz_entries = Tahfidz.query.filter_by(santri_id=santri_id).order_by(Tahfidz.tanggal_setor.desc()).all()
        
        # 4. Data Tambahan Raport (Catatan & Status)
        raport_data = Raport.query.filter_by(santri_id=santri_id, semester=semester).first()
        
        catatan = raport_data.catatan_wali_kelas if raport_data else "-"
        status_kenaikan = raport_data.status_kenaikan if raport_data else "-"
        tanggal_bagi = raport_data.tanggal_bagi.strftime("%d %B %Y") if raport_data and raport_data.tanggal_bagi else datetime.now().strftime("%d %B %Y")
        
        return {
            'santri': santri,
            'semester': semester,
            'nilai': raport_nilai,
            'absensi': absensi_summary,
            'tahfidz': tahfidz_entries,
            'catatan': catatan,
            'status_kenaikan': status_kenaikan,
            'tanggal_cetak': tanggal_bagi,
            'raport_exists': True if raport_data else False
        }
        
    def get_predikat(self, nilai):
        if nilai >= 90: return 'A'
        elif nilai >= 80: return 'B'
        elif nilai >= 70: return 'C'
        else: return 'D'

    def get_predikat_desc(self, nilai):
        if nilai >= 90: return 'Sangat Baik'
        elif nilai >= 80: return 'Baik'
        elif nilai >= 70: return 'Cukup'
        else: return 'Perlu Bimbingan'
