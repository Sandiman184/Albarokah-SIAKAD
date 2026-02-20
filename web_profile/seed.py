from app import create_app, db
from app.models import Berita, Agenda, Galeri, User, Pengaturan, Program, Pimpinan
from datetime import datetime, timedelta

app = create_app()

def seed_data():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create Admin User if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('password123')
            db.session.add(admin)
            print("User admin berhasil dibuat!")
        else:
            print("User admin sudah ada.")

        # Ensure default Pengaturan exists
        pengaturan = Pengaturan.query.first()
        if not pengaturan:
            pengaturan = Pengaturan(
                nama_pesantren="Pondok Pesantren Al Qur'an Al-Barokah",
                hero_title_1='Selamat Datang di',
                hero_title_2="Pondok Pesantren Al Qur'an",
                hero_title_3='Al-Barokah',
                hero_subtitle="Mewujudkan Generasi Qur'ani yang Berakhlak Mulia, Cerdas, dan Mandiri"
            )
            db.session.add(pengaturan)
            print("Pengaturan default dibuat.")
            
        # Update Program Pendidikan
        print("Memperbarui data Program Pendidikan...")
        
        # 1. TKQ Al Barokah
        tkq = Program.query.filter_by(nama='TKQ Al Barokah').first()
        if not tkq:
            tkq = Program(nama='TKQ Al Barokah', deskripsi='Taman Kanak-kanak Al Qur\'an (Usia 3-6 Tahun)', icon='fas fa-child', urutan=1)
            db.session.add(tkq)
            db.session.flush()
        
        # TKQ Sub-programs
        tkq_kelas1 = Program.query.filter_by(nama='Kelas 1 (TKQ)', parent_id=tkq.id).first()
        if not tkq_kelas1:
            db.session.add(Program(
                nama='Kelas 1 (TKQ)', 
                deskripsi='Pengenalan Huruf Hijaiyah Iqro 1-2. Jumlah: 32 Santri. 3 Guru (Syahadah YANBUA).',
                icon='fas fa-star',
                parent_id=tkq.id,
                urutan=1
            ))
            
        tkq_kelas2 = Program.query.filter_by(nama='Kelas 2 (TKQ)', parent_id=tkq.id).first()
        if not tkq_kelas2:
            db.session.add(Program(
                nama='Kelas 2 (TKQ)', 
                deskripsi='Memahami menulis menggabungkan Huruf Hijaiyah. Jumlah: 63 Santri. 4 Guru (Syahadah YANBUA).',
                icon='fas fa-star',
                parent_id=tkq.id,
                urutan=2
            ))

        # 2. TPQ Al Barokah
        tpq = Program.query.filter_by(nama='TPQ Al Barokah').first()
        if not tpq:
            tpq = Program(nama='TPQ Al Barokah', deskripsi='Taman Pendidikan Al Qur\'an (No. Statistik: 411033040032)', icon='fas fa-quran', urutan=2)
            db.session.add(tpq)
            db.session.flush()

        # TPQ Sub-programs
        tpq_kelas1 = Program.query.filter_by(nama='Kelas 1 (TPQ)', parent_id=tpq.id).first()
        if not tpq_kelas1:
            db.session.add(Program(
                nama='Kelas 1 (TPQ)',
                deskripsi='Jumlah: 13 Santri. 2 Guru (Syahadah YANBUA).',
                icon='fas fa-book-open',
                parent_id=tpq.id,
                urutan=1
            ))
            
        tpq_kelas2 = Program.query.filter_by(nama='Kelas 2 (TPQ)', parent_id=tpq.id).first()
        if not tpq_kelas2:
            db.session.add(Program(
                nama='Kelas 2 (TPQ)',
                deskripsi='Jumlah: 27 Santri. 2 Guru (Syahadah YANBUA).',
                icon='fas fa-book-open',
                parent_id=tpq.id,
                urutan=2
            ))
            
        tpq_kelas3 = Program.query.filter_by(nama='Kelas 3 (TPQ)', parent_id=tpq.id).first()
        if not tpq_kelas3:
            db.session.add(Program(
                nama='Kelas 3 (TPQ)',
                deskripsi='Jumlah: 23 Santri. 2 Guru (Syahadah YANBUA).',
                icon='fas fa-book-open',
                parent_id=tpq.id,
                urutan=3
            ))

        # 3. Madrasah Diniyah Takmiliyah
        mdt = Program.query.filter_by(nama='Madrasah Diniyah Takmiliyah Hidayatul Ulum Lilbarokah').first()
        if not mdt:
            mdt = Program(nama='Madrasah Diniyah Takmiliyah Hidayatul Ulum Lilbarokah', deskripsi='No. Statistik: 311233040223. Kurikulum Kemenag, FKDT & Kitab Kuning.', icon='fas fa-mosque', urutan=3)
            db.session.add(mdt)
            db.session.flush()
            
        # MDT Sub-programs
        for i in range(1, 5):
            nama_kelas = f'Kelas {i} (MDT)'
            if not Program.query.filter_by(nama=nama_kelas, parent_id=mdt.id).first():
                santri_count = [27, 24, 36, 19][i-1]
                db.session.add(Program(
                    nama=nama_kelas,
                    deskripsi=f'Jumlah: {santri_count} Santri. 2 Guru.',
                    icon='fas fa-book',
                    parent_id=mdt.id,
                    urutan=i
                ))

        # 4. Pondok Pesantren Al Barokah
        ponpes = Program.query.filter_by(nama='Pondok Pesantren Al Barokah').first()
        if not ponpes:
            ponpes = Program(nama='Pondok Pesantren Al Barokah', deskripsi='Pendidikan Kitab Kuning Berjenjang', icon='fas fa-school', urutan=4)
            db.session.add(ponpes)
            db.session.flush()
            
        # Ponpes Sub-programs
        if not Program.query.filter_by(nama='Ibtida (Ula)', parent_id=ponpes.id).first():
            db.session.add(Program(
                nama='Ibtida (Ula)',
                deskripsi='Jumlah: 36 Santri. Kurikulum: Safinatunnaja, Jurumiyah Mukhtasor Jiddan, Akidatul Awwam, Alala, Tukhfatul Athfal.',
                icon='fas fa-layer-group',
                parent_id=ponpes.id,
                urutan=1
            ))
            
        if not Program.query.filter_by(nama='Tsanawi (Wushto)', parent_id=ponpes.id).first():
            db.session.add(Program(
                nama='Tsanawi (Wushto)',
                deskripsi='Jumlah: 18 Santri. Kurikulum: Sulamunajat, Jurumiyah Asmawi, Imriti, Tijanudaruri, Ta\'limul Mutalalim, Matan Jazariyah.',
                icon='fas fa-layer-group',
                parent_id=ponpes.id,
                urutan=2
            ))
            
        if not Program.query.filter_by(nama='Aliyah (Ulya)', parent_id=ponpes.id).first():
            db.session.add(Program(
                nama='Aliyah (Ulya)',
                deskripsi='Jumlah: 10 Santri. Kurikulum: Taqrib, Jurumiyah Kafrawi, Imriti, Al Fiyah, Kifayatul Awwam, Kifayatul Adzkiya, Matan Jazariyah.',
                icon='fas fa-layer-group',
                parent_id=ponpes.id,
                urutan=3
            ))

        # 5. Takhosus & Keunggulan
        takhosus_prog = Program.query.filter_by(nama='Program Takhosus & Keunggulan').first()
        if not takhosus_prog:
            takhosus_prog = Program(nama='Program Takhosus & Keunggulan', deskripsi='Fokus Pembelajaran Pesantren', icon='fas fa-award', urutan=5)
            db.session.add(takhosus_prog)
            db.session.flush()
            
        if not Program.query.filter_by(nama='Takhosus', parent_id=takhosus_prog.id).first():
            db.session.add(Program(
                nama='Takhosus',
                deskripsi='Kitab Kuning (Alat, Fiqih, Tauhid).',
                icon='fas fa-book-reader',
                parent_id=takhosus_prog.id,
                urutan=1
            ))
            
        if not Program.query.filter_by(nama='Keunggulan', parent_id=takhosus_prog.id).first():
            db.session.add(Program(
                nama='Keunggulan',
                deskripsi='1. Tilawah (Quro)\n2. Tahfidz Qur\'an',
                icon='fas fa-star',
                parent_id=takhosus_prog.id,
                urutan=2
            ))
            
        # Riwayat Prestasi (Galeri)
        print("Memperbarui data Prestasi (Galeri)...")
        prestasi_list = [
            "Juara Umum Festifal Anak Santri TPQ Tingkat Kecamatan",
            "Juara Umum Porsadin Tingkat Kecamatan",
            "Juara 1 Pildacil Tingkat Kabupaten",
            "Juara 1 Kisah Islami Tingkat Kabupaten",
            "Juara 1 Kreasi Santri Tingkat Kabupaten",
            "Juara 1 Pildacil Tingkat Provinsi",
            "Juara 1 Pidato Bahasa Arab Tingkat Kabupaten",
            "Juara 2 Pidato Bahasa Arab Tingkat Kabupaten"
        ]
        
        for i, judul in enumerate(prestasi_list):
            if not Galeri.query.filter_by(judul=judul).first():
                # Menggunakan gambar placeholder yang relevan dengan prestasi
                gambar_url = f"https://ui-avatars.com/api/?name=Juara+{i+1}&background=random&size=800"
                db.session.add(Galeri(
                    judul=judul,
                    gambar=gambar_url,
                    kategori="Prestasi",
                    deskripsi=f"Alhamdulillah, santri kami berhasil meraih {judul}.",
                    tanggal=datetime.utcnow() - timedelta(days=i*10) # Tanggal mundur agar urut
                ))

        db.session.commit()
        print("Seeding selesai. Data yang ada tidak dihapus.")

if __name__ == '__main__':
    seed_data()
