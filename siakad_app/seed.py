from app import create_app, db
from app.models.user import User
from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran, Nilai, Raport, Absensi
from app.models.konfigurasi import Konfigurasi
from datetime import date, datetime
import random

app = create_app()

def seed_data():
    with app.app_context():
        print("Mulai seeding data...")
        
        # Ensure tables exist
        db.create_all()
        
        # 1. Config
        config = Konfigurasi.query.first()
        if not config:
            config = Konfigurasi(
                nama_lembaga="MDTA & LPQ AL-BAROKAH",
                alamat_lembaga="Jl. Contoh No. 123, Yogyakarta",
                kepala_sekolah="H. Fulan, S.Pd.I",
                nip_kepala="198001012005011001"
            )
            db.session.add(config)
        
        # 2. Users & Pengajar
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
        ustadz = User.query.filter_by(username='ustadz').first()
        if not ustadz:
            ustadz = User(username='ustadz', role='ustadz')
            ustadz.set_password('ustadz123')
            db.session.add(ustadz)
            db.session.flush()
            
            p = Pengajar(nama="Ustadz Abdullah", no_hp="08123456789", user_id=ustadz.id)
            db.session.add(p)
            db.session.commit()
        else:
            p = Pengajar.query.filter_by(user_id=ustadz.id).first()

        # 3. Kelas (MDTA & LPQ)
        kelas_mdta = Kelas.query.filter_by(nama_kelas='1 Awaliyah').first()
        if not kelas_mdta:
            kelas_mdta = Kelas(nama_kelas='1 Awaliyah', jenjang='MDTA', wali_kelas_id=p.id)
            db.session.add(kelas_mdta)
            
        kelas_lpq = Kelas.query.filter_by(nama_kelas='TKQ A').first()
        if not kelas_lpq:
            kelas_lpq = Kelas(nama_kelas='TKQ A', jenjang='LPQ', wali_kelas_id=p.id)
            db.session.add(kelas_lpq)
            
        db.session.commit()
        
        # 4. Mapel (MDTA with Groups)
        mapels_mdta = [
            ('Al-Qur\'an Hadits', 'A'),
            ('Aqidah Akhlak', 'A'),
            ('Fiqih', 'A'),
            ('Sejarah Kebudayaan Islam', 'A'),
            ('Bahasa Arab', 'A'),
            ('Praktek Ibadah', 'B'),
            ('Tahfidz', 'B')
        ]
        
        ids_mapel_mdta = []
        for name, group in mapels_mdta:
            m = MataPelajaran.query.filter_by(nama_mapel=name, jenjang='MDTA').first()
            if not m:
                m = MataPelajaran(nama_mapel=name, jenjang='MDTA', kelompok=group, kkm=70)
                db.session.add(m)
                db.session.flush()
            ids_mapel_mdta.append(m.id)
            
        # Mapel LPQ (Single Group usually)
        mapels_lpq = ['Membaca Jilid', 'Hafalan Surat Pendek', 'Hafalan Doa Harian', 'Praktek Sholat', 'Menulis']
        ids_mapel_lpq = []
        for name in mapels_lpq:
            m = MataPelajaran.query.filter_by(nama_mapel=name, jenjang='LPQ').first()
            if not m:
                m = MataPelajaran(nama_mapel=name, jenjang='LPQ', kelompok='A', kkm=75)
                db.session.add(m)
                db.session.flush()
            ids_mapel_lpq.append(m.id)
            
        db.session.commit()
        
        # 5. Santri & Nilai
        # MDTA Santri
        for i in range(1, 6):
            nis = f'MDT{i:03d}'
            s = Santri.query.filter_by(nis=nis).first()
            if not s:
                s = Santri(
                    nis=nis,
                    nama=f'Santri MDTA {i}',
                    jenis_kelamin='L' if i % 2 != 0 else 'P',
                    tanggal_lahir=date(2015, 1, 1),
                    kelas_id=kelas_mdta.id,
                    status='aktif',
                    jenjang='MDTA'
                )
                db.session.add(s)
                db.session.flush()
                
                # Nilai
                for mid in ids_mapel_mdta:
                    n = Nilai(
                        santri_id=s.id,
                        mapel_id=mid,
                        semester='Ganjil 2024/2025',
                        nilai_harian=random.randint(70, 95),
                        nilai_kehadiran=random.randint(80, 100),
                        nilai_uas=random.randint(65, 90)
                    )
                    db.session.add(n)
                
                # Raport Snapshot
                r = Raport(
                    santri_id=s.id,
                    semester='Ganjil 2024/2025',
                    catatan_wali_kelas="Tingkatkan terus prestasimu.",
                    status_kenaikan="Naik Kelas",
                    sikap_akhlak="Baik",
                    sikap_kerajinan="Sangat Baik",
                    sikap_kedisiplinan="Baik",
                    sikap_kebersihan="Cukup",
                    sakit=random.randint(0, 2),
                    izin=random.randint(0, 2),
                    alpha=0,
                    rank=i, # Dummy rank
                    total_students=5
                )
                db.session.add(r)

        # LPQ Santri
        for i in range(1, 4):
            nis = f'LPQ{i:03d}'
            s = Santri.query.filter_by(nis=nis).first()
            if not s:
                s = Santri(
                    nis=nis,
                    nama=f'Santri LPQ {i}',
                    jenis_kelamin='P',
                    tanggal_lahir=date(2018, 1, 1),
                    kelas_id=kelas_lpq.id,
                    status='aktif',
                    jenjang='LPQ'
                )
                db.session.add(s)
                db.session.flush()
                
                # Nilai
                for mid in ids_mapel_lpq:
                    n = Nilai(
                        santri_id=s.id,
                        mapel_id=mid,
                        semester='Ganjil 2024/2025',
                        nilai_harian=random.randint(70, 90),
                        nilai_kehadiran=random.randint(70, 90),
                        nilai_uas=random.randint(70, 90)
                    )
                    db.session.add(n)
                    
                # Raport Snapshot (LPQ has narratives)
                r = Raport(
                    santri_id=s.id,
                    semester='Ganjil 2024/2025',
                    catatan_wali_kelas="Ananda ceria dan semangat.",
                    status_kenaikan="Naik Kelas",
                    sikap_akhlak="Sangat Baik",
                    deskripsi_moral="Ananda mampu menghafal doa harian dengan baik.",
                    deskripsi_kognitif="Ananda mampu mengenal huruf hijaiyah.",
                    deskripsi_sosial="Ananda mudah bergaul dengan teman.",
                    deskripsi_bahasa="Ananda mampu berbicara dengan sopan.",
                    deskripsi_seni="Ananda suka mewarnai kaligrafi.",
                    deskripsi_diri="Ananda perlu bimbingan dalam menulis.",
                    sakit=1,
                    izin=0,
                    alpha=0
                )
                db.session.add(r)
                
        db.session.commit()
        print("Seeding selesai dengan data MDTA & LPQ lengkap.")

if __name__ == '__main__':
    seed_data()
