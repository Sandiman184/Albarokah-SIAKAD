from app import create_app, db, cache
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
            
        # Update Konten Sejarah & Visi Misi Default (Upsert)
        print("Memperbarui data Profil (Sejarah & Visi Misi)...")
        if pengaturan:
            # Hanya update jika field masih kosong atau berisi konten placeholder lama
            # Kita menggunakan metode 'setattr' hanya jika ingin memaksa update konten tertentu
            
            # Konten Sejarah Baru
            sejarah_baru = """
            <p>Pondok Pesantren Al-Qur’an Al-Barokah didirikan pada tahun 2010 oleh KH. Ahmad Fauzan. Berawal dari sebuah majelis taklim kecil di rumah beliau, antusiasme masyarakat untuk menitipkan putra-putrinya belajar Al-Qur’an semakin meningkat.</p>
            <p>Pada tahun 2012, dibangunlah asrama pertama yang sederhana untuk menampung santri mukim. Seiring berjalannya waktu, sarana dan prasarana terus dikembangkan. Kini, Al-Barokah telah memiliki gedung asrama putra dan putri, ruang kelas yang representatif, serta masjid jami’.</p>
            <p>Kami memadukan sistem pendidikan salaf (kitab kuning) dengan pendidikan Al-Qur’an (Tahfidz & Tilawah) serta pendidikan formal (Madrasah Diniyah). Hal ini bertujuan untuk mencetak generasi yang tidak hanya hafal Al-Qur’an, tetapi juga memahami ilmu agama secara mendalam dan memiliki akhlakul karimah.</p>
            """
            
            # Konten Visi Baru
            visi_baru = "<p>Terwujudnya generasi Qur’ani yang berilmu amaliah, beramal ilmiah, dan berakhlakul karimah.</p>"
            
            # Konten Misi Baru
            misi_baru = """
            <ol>
                <li>Menyelenggarakan pendidikan Al-Qur’an yang berkualitas (Tahsin, Tahfidz, Tilawah).</li>
                <li>Mengajarkan ilmu-ilmu keislaman melalui pengkajian kitab kuning.</li>
                <li>Membentuk karakter santri yang disiplin, mandiri, dan berbudi pekerti luhur.</li>
                <li>Mengembangkan potensi santri sesuai dengan bakat dan minatnya.</li>
            </ol>
            """

            # Update Pengaturan
            pengaturan.sejarah = sejarah_baru
            pengaturan.visi = visi_baru
            pengaturan.misi = misi_baru
            
            # Pastikan hero title juga terupdate
            pengaturan.hero_title_1 = 'Selamat Datang di'
            pengaturan.hero_title_2 = "Pondok Pesantren Al Qur'an"
            pengaturan.hero_title_3 = 'Al-Barokah'
            pengaturan.hero_subtitle = "Mewujudkan Generasi Qur'ani yang Berakhlak Mulia, Cerdas, dan Mandiri"

            db.session.add(pengaturan)
            db.session.flush()

        # Helper function for upsert (Update or Insert)
        def upsert_program(nama, defaults):
            prog = Program.query.filter_by(nama=nama).first()
            if prog:
                # Update existing
                for key, value in defaults.items():
                    setattr(prog, key, value)
            else:
                # Create new
                prog = Program(nama=nama, **defaults)
                db.session.add(prog)
            db.session.flush() # Ensure ID is available
            return prog

        # Update Program Pendidikan
        print("Memperbarui data Program Pendidikan...")
        
        # 1. TKQ Al Barokah
        tkq = upsert_program('TKQ Al Barokah', {
            'deskripsi': 'Taman Kanak-kanak Al Qur\'an (Usia 3-6 Tahun)',
            'icon': 'fas fa-child',
            'urutan': 1
        })
        
        # TKQ Sub-programs
        upsert_program('Kelas 1 (TKQ)', {
            'deskripsi': 'Pengenalan Huruf Hijaiyah Iqro 1-2. Jumlah: 32 Santri. 3 Guru (Syahadah YANBUA).',
            'icon': 'fas fa-star',
            'parent_id': tkq.id,
            'urutan': 1
        })
            
        upsert_program('Kelas 2 (TKQ)', {
            'deskripsi': 'Memahami menulis menggabungkan Huruf Hijaiyah. Jumlah: 63 Santri. 4 Guru (Syahadah YANBUA).',
            'icon': 'fas fa-star',
            'parent_id': tkq.id,
            'urutan': 2
        })

        # 2. TPQ Al Barokah
        tpq = upsert_program('TPQ Al Barokah', {
            'deskripsi': 'Taman Pendidikan Al Qur\'an (No. Statistik: 411033040032)',
            'icon': 'fas fa-quran',
            'urutan': 2
        })

        # TPQ Sub-programs
        upsert_program('Kelas 1 (TPQ)', {
            'deskripsi': 'Jumlah: 13 Santri. 2 Guru (Syahadah YANBUA).',
            'icon': 'fas fa-book-open',
            'parent_id': tpq.id,
            'urutan': 1
        })
            
        upsert_program('Kelas 2 (TPQ)', {
            'deskripsi': 'Jumlah: 27 Santri. 2 Guru (Syahadah YANBUA).',
            'icon': 'fas fa-book-open',
            'parent_id': tpq.id,
            'urutan': 2
        })
            
        upsert_program('Kelas 3 (TPQ)', {
            'deskripsi': 'Jumlah: 23 Santri. 2 Guru (Syahadah YANBUA).',
            'icon': 'fas fa-book-open',
            'parent_id': tpq.id,
            'urutan': 3
        })

        # 3. Madrasah Diniyah Takmiliyah
        mdt = upsert_program('Madrasah Diniyah Takmiliyah Hidayatul Ulum Lilbarokah', {
            'deskripsi': 'No. Statistik: 311233040223. Kurikulum Kemenag, FKDT & Kitab Kuning.',
            'icon': 'fas fa-mosque',
            'urutan': 3
        })
            
        # MDT Sub-programs
        for i in range(1, 5):
            nama_kelas = f'Kelas {i} (MDT)'
            santri_count = [27, 24, 36, 19][i-1]
            upsert_program(nama_kelas, {
                'deskripsi': f'Jumlah: {santri_count} Santri. 2 Guru.',
                'icon': 'fas fa-book',
                'parent_id': mdt.id,
                'urutan': i
            })

        # 4. Pondok Pesantren Al Barokah
        ponpes = upsert_program('Pondok Pesantren Al Barokah', {
            'deskripsi': 'Pendidikan Kitab Kuning Berjenjang',
            'icon': 'fas fa-school',
            'urutan': 4
        })
            
        # Ponpes Sub-programs
        upsert_program('Ibtida (Ula)', {
            'deskripsi': 'Jumlah: 36 Santri. Kurikulum: Safinatunnaja, Jurumiyah Mukhtasor Jiddan, Akidatul Awwam, Alala, Tukhfatul Athfal.',
            'icon': 'fas fa-layer-group',
            'parent_id': ponpes.id,
            'urutan': 1
        })
            
        upsert_program('Tsanawi (Wushto)', {
            'deskripsi': 'Jumlah: 18 Santri. Kurikulum: Sulamunajat, Jurumiyah Asmawi, Imriti, Tijanudaruri, Ta\'limul Mutalalim, Matan Jazariyah.',
            'icon': 'fas fa-layer-group',
            'parent_id': ponpes.id,
            'urutan': 2
        })
            
        upsert_program('Aliyah (Ulya)', {
            'deskripsi': 'Jumlah: 10 Santri. Kurikulum: Taqrib, Jurumiyah Kafrawi, Imriti, Al Fiyah, Kifayatul Awwam, Kifayatul Adzkiya, Matan Jazariyah.',
            'icon': 'fas fa-layer-group',
            'parent_id': ponpes.id,
            'urutan': 3
        })

        # 5. Takhosus & Keunggulan
        takhosus_prog = upsert_program('Program Takhosus & Keunggulan', {
            'deskripsi': 'Fokus Pembelajaran Pesantren',
            'icon': 'fas fa-award',
            'urutan': 5
        })
            
        upsert_program('Takhosus', {
            'deskripsi': 'Kitab Kuning (Alat, Fiqih, Tauhid).',
            'icon': 'fas fa-book-reader',
            'parent_id': takhosus_prog.id,
            'urutan': 1
        })
            
        upsert_program('Keunggulan', {
            'deskripsi': '1. Tilawah (Quro)\n2. Tahfidz Qur\'an',
            'icon': 'fas fa-star',
            'parent_id': takhosus_prog.id,
            'urutan': 2
        })
            
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
        
        # Clear cache
        try:
            cache.clear()
            print("Cache berhasil dibersihkan.")
        except Exception as e:
            print(f"Gagal membersihkan cache: {e}")
            
        print("Seeding selesai. Data yang ada tidak dihapus.")
        print("PENTING: Jika menggunakan SimpleCache (default), Anda HARUS me-restart service aplikasi agar perubahan terlihat.")
        print("Command: sudo systemctl restart web_profile")

if __name__ == '__main__':
    seed_data()
