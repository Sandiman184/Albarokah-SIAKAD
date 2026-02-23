from app import db
from app.models.akademik import Nilai, Absensi, Tahfidz, Santri, MataPelajaran, Raport
from app.models.konfigurasi import Konfigurasi
from sqlalchemy import func
from datetime import datetime, date

class RaportService:
    def get_raport_data(self, santri_id, semester):
        santri = Santri.query.get_or_404(santri_id)
        config = Konfigurasi.query.first()
        
        # Determine Template Type
        jenjang = santri.kelas.jenjang if santri.kelas else santri.jenjang
        if jenjang in ['TKQ', 'TPQ', 'LPQ', 'PAUD', 'TKA', 'TQA']:
            template_type = 'LPQ'
        else:
            template_type = 'MDT' # Default to MDT (MDTA, MDTW, MDTU, dll)
            
        # 1. Nilai Akademik
        # Fetch all Mapel for this jenjang to ensure they appear even without grades
        all_mapel = MataPelajaran.query.filter_by(jenjang=jenjang).all()
        
        # Filter existing grades by semester
        # Optimize N+1 query: Eager load Mapel
        nilai_list = Nilai.query.options(db.joinedload(Nilai.mapel))\
            .filter_by(santri_id=santri_id, semester=semester).all()
            
        # Create lookup dict: mapel_id -> Nilai object
        nilai_dict = {n.mapel_id: n for n in nilai_list}
            
        raport_nilai = []
        # Iterate over ALL subjects for the jenjang, not just those with grades
        for mapel in all_mapel:
            n = nilai_dict.get(mapel.id)
            
            if n:
                # 1. New Calculation Formula: 30% NH + 30% NK + 40% NU
                h = n.nilai_harian or 0
                k = n.nilai_kehadiran or 0
                u = n.nilai_uas or 0 # Mapped to NU (Nilai Ulangan)
                
                # Additional optional fields (legacy support or if needed)
                uts = n.nilai_uts or 0
                p = n.nilai_praktik or 0
                
                deskripsi_db = n.deskripsi
            else:
                # Default values if no grade exists
                h = 0
                k = 0
                u = 0
                uts = 0
                p = 0
                deskripsi_db = None
            
            # Formula: (30% * H) + (30% * K) + (40% * U)
            nilai_akhir = (0.3 * h) + (0.3 * k) + (0.4 * u)
            
            # Use standard rounded integer for consistency between display and terbilang
            nilai_akhir_bulat = int(round(nilai_akhir))
            
            # 2. Determine Predicate/Description based on Template Type
            kkm = mapel.kkm or 70.0
            
            if template_type == 'MDT':
                predikat = self.get_keterangan_mdta(nilai_akhir_bulat, kkm)
                # Prioritize manual description
                if deskripsi_db:
                    deskripsi = deskripsi_db
                else:
                    deskripsi = self.get_deskripsi_mdta(nilai_akhir_bulat, kkm, mapel.nama_mapel)
            else: # LPQ
                predikat = self.get_keterangan_lpq(nilai_akhir_bulat, kkm)
                deskripsi = self.get_deskripsi_lpq(nilai_akhir_bulat, kkm, mapel.nama_mapel)
            
            raport_nilai.append({
                'mapel': mapel.nama_mapel,
                'kelompok': mapel.kelompok or 'A',
                'kkm': kkm,
                'harian': h,
                'kehadiran': k,
                'ulangan': u,
                'uts': uts,
                'praktik': p,
                'nilai_akhir': nilai_akhir_bulat,
                'nilai_huruf': self.terbilang(nilai_akhir_bulat),
                'predikat': predikat,
                'deskripsi': deskripsi
            })
            
        # Group by Kelompok (A, B, etc.)
        kelompok_a = [n for n in raport_nilai if n['kelompok'] == 'A']
        kelompok_b = [n for n in raport_nilai if n['kelompok'] == 'B']
        # Others if any
        kelompok_lain = [n for n in raport_nilai if n['kelompok'] not in ['A', 'B']]
            
        # 3. Data Tambahan Raport (Catatan & Status) - Moved up for Absensi logic
        raport_data = Raport.query.filter_by(santri_id=santri_id, semester=semester).first()
        
        # 2. Absensi (Prioritize Snapshot in Raport, fallback to Absensi table)
        if raport_data and (raport_data.sakit or raport_data.izin or raport_data.alpha):
            absensi_summary = {
                'Hadir': 0, # Not usually manually input in Raport, but we can keep it 0 or calc
                'Sakit': raport_data.sakit,
                'Izin': raport_data.izin,
                'Alpha': raport_data.alpha
            }
        else:
            # Fallback to calculation
            absensi_counts = db.session.query(
                Absensi.status, func.count(Absensi.id)
            ).filter_by(santri_id=santri_id).group_by(Absensi.status).all()
            
            absensi_summary = {'Hadir': 0, 'Sakit': 0, 'Izin': 0, 'Alpha': 0}
            for status, count in absensi_counts:
                s = status.capitalize()
                if s in absensi_summary:
                    absensi_summary[s] = count
                
        # 4. Tahfidz (Renumbered)
        tahfidz_entries = Tahfidz.query.filter_by(santri_id=santri_id).order_by(Tahfidz.tanggal_setor.desc()).all()
        
        catatan = raport_data.catatan_wali_kelas if raport_data else "-"
        status_kenaikan = raport_data.status_kenaikan if raport_data else "-"
        
        # Determine Date
        if raport_data and raport_data.tanggal_bagi:
            tanggal_bagi = raport_data.tanggal_bagi
        elif config and config.tanggal_raport_default:
            tanggal_bagi = config.tanggal_raport_default
        else:
            tanggal_bagi = date.today()
            
        tanggal_bagi_str = tanggal_bagi.strftime("%d %B %Y")
        
        # 5. Peringkat Kelas (Rank)
        rank = "-"
        total_students = 0
        
        # Check if rank is already stored in Raport
        if raport_data and raport_data.rank:
            rank = raport_data.rank
            total_students = raport_data.total_students or Santri.query.filter_by(kelas_id=santri.kelas_id, status='aktif').count()
        elif santri.kelas_id:
            # Calculate rank dynamically
            classmates = Santri.query.filter_by(kelas_id=santri.kelas_id, status='aktif').all()
            total_students = len(classmates)
            classmate_ids = [s.id for s in classmates]
            
            # Get grades for all classmates in this semester
            all_grades = Nilai.query.filter(
                Nilai.santri_id.in_(classmate_ids),
                Nilai.semester == semester
            ).all()
            
            # Calculate average per student
            student_averages = {}
            for g in all_grades:
                sid = g.santri_id
                if sid not in student_averages:
                    student_averages[sid] = []
                
                # Formula: (30% * H) + (30% * K) + (40% * U)
                h = g.nilai_harian or 0
                k = g.nilai_kehadiran or 0
                u = g.nilai_uas or 0
                final = (0.3 * h) + (0.3 * k) + (0.4 * u)
                student_averages[sid].append(final)
            
            # Compute mean of all subjects for each student
            final_scores = []
            for sid in classmate_ids: # Iterate over all classmates to include those with 0 grades
                scores = student_averages.get(sid, [])
                avg = sum(scores) / len(scores) if scores else 0
                final_scores.append({'sid': sid, 'avg': avg})
            
            # Sort by avg descending
            final_scores.sort(key=lambda x: x['avg'], reverse=True)
            
            # Find rank
            for i, item in enumerate(final_scores):
                if item['sid'] == santri_id:
                    rank = i + 1
                    break

        return {
            'santri': santri,
            'semester': semester,
            'nilai': raport_nilai, # Full list for backward compatibility
            'kelompok_a': kelompok_a,
            'kelompok_b': kelompok_b,
            'kelompok_lain': kelompok_lain,
            'absensi': absensi_summary,
            'tahfidz': tahfidz_entries,
            'catatan': catatan,
            'status_kenaikan': status_kenaikan,
            'tanggal_cetak': tanggal_bagi_str,
            'raport_exists': True if raport_data else False,
            'template_type': template_type,
            'config': config,
            'rank': rank,
            'total_students': total_students,
            'raport_data': raport_data # Pass the full object for new fields
        }
        
    def get_keterangan_mdta(self, nilai, kkm):
        # Rounding for safety
        nilai = round(nilai)
        kkm = int(kkm)
        
        if nilai > kkm:
            return "KKM Terlampaui"
        elif nilai == kkm:
            return "KKM Tercapai"
        else:
            return "KKM Belum Tercapai"

    def get_deskripsi_mdta(self, nilai, kkm, mapel):
        # Logic to match "Berkembang Sangat Baik" style
        nilai = round(nilai)
        kkm = int(kkm)
        
        if nilai >= (kkm + 10):
            return "Berkembang Sangat Baik"
        elif nilai >= kkm:
            return "Berkembang Sesuai Harapan"
        elif nilai >= (kkm - 10):
            return "Mulai Berkembang"
        else:
            return "Belum Berkembang"

    def get_keterangan_lpq(self, nilai, kkm):
        # KKM = 75 example
        # < 65: Belum Berkembang
        # 65 - 74: Mulai Berkembang
        # 75: Berkembang Sesuai Harapan
        # > 75: Berkembang Sangat Baik
        
        # Dynamic logic relative to KKM
        # Assuming ranges:
        # < KKM-10: BB
        # KKM-10 <= x < KKM: MB
        # KKM <= x < KKM+10: BSH (Actually user said 75 is BSH)
        # >= KKM+10: BSB (User said . 75 BSB, probably > 75)
        
        # Let's align strictly with user input example "75"
        # 75 = KKM
        # < 65 (KKM - 10) -> BB
        # 65 - 74 (KKM - 10 to KKM - 1) -> MB
        # 75 (KKM) -> BSH
        # > 75 -> BSB
        
        nilai = round(nilai) # Use rounded value for comparison
        kkm = int(kkm)
        
        if nilai < (kkm - 10):
            return "Belum Berkembang (BB)"
        elif nilai < kkm:
            return "Mulai Berkembang (MB)"
        elif nilai == kkm:
            return "Berkembang Sesuai Harapan (BSH)"
        else:
            return "Berkembang Sangat Baik (BSB)"

    def get_deskripsi_lpq(self, nilai, kkm, mapel):
        ket = self.get_keterangan_lpq(nilai, kkm)
        # Extract just the text part without (BB)
        ket_text = ket.split('(')[0].strip()
        return f"Ananda {ket_text} dalam mata pelajaran {mapel}."

    def terbilang(self, n):
        satuan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
        n = int(n)
        if n < 12:
            return satuan[n]
        elif n < 20:
            return self.terbilang(n - 10) + " Belas"
        elif n < 100:
            return (self.terbilang(n // 10) + " Puluh " + self.terbilang(n % 10)).strip()
        elif n < 200:
            return ("Seratus " + self.terbilang(n - 100)).strip()
        elif n < 1000:
            return (self.terbilang(n // 100) + " Ratus " + self.terbilang(n % 100)).strip()
        return str(n)
