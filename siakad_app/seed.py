from app import create_app, db
from app.models.user import User
from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran, Nilai
from datetime import date

app = create_app()

def seed_data():
    with app.app_context():
        print("Mulai seeding data...")
        
        # Buat tabel jika belum ada (untuk dev cepat, idealnya pakai migrasi)
        db.create_all()
        
        # 1. Buat Admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("User Admin dibuat.")
        
        # 2. Buat Ustadz (Guru)
        ustadz_user = User.query.filter_by(username='ustadz1').first()
        if not ustadz_user:
            ustadz_user = User(username='ustadz1', role='ustadz')
            ustadz_user.set_password('ustadz123')
            db.session.add(ustadz_user)
            db.session.flush() # Agar ID ter-generate
            
            pengajar = Pengajar(nama="Ustadz Abdullah", no_hp="08123456789", user_id=ustadz_user.id)
            db.session.add(pengajar)
            print("User Ustadz dibuat.")
        else:
            pengajar = ustadz_user.pengajar

        # 3. Buat Kelas
        kelas = Kelas.query.filter_by(nama_kelas='7A').first()
        if not kelas:
            kelas = Kelas(nama_kelas='7A', jenjang='SMP', wali_kelas_id=pengajar.id if pengajar else None)
            db.session.add(kelas)
            print("Kelas 7A dibuat.")
            
        # 4. Buat Santri
        santri = Santri.query.filter_by(nis='12345').first()
        if not santri:
            santri = Santri(
                nis='12345',
                nama='Ahmad Santri',
                jenis_kelamin='L',
                tanggal_lahir=date(2010, 5, 15),
                alamat='Jl. Pesantren No. 1',
                jenjang='SMP',
                kelas=kelas
            )
            db.session.add(santri)
            print("Santri Ahmad dibuat.")
            
        # 5. Buat Mapel
        mapel = MataPelajaran.query.filter_by(nama_mapel='Bahasa Arab').first()
        if not mapel:
            mapel = MataPelajaran(nama_mapel='Bahasa Arab', jenjang='SMP')
            db.session.add(mapel)
            print("Mapel Bahasa Arab dibuat.")

        db.session.commit()
        print("Seeding selesai!")

if __name__ == '__main__':
    seed_data()
