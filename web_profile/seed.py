from app import create_app, db
from app.models import Berita, Agenda, Galeri, User
from datetime import datetime, timedelta

app = create_app()

def seed_data():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create Admin User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('password123')
            db.session.add(admin)
            print("User admin berhasil dibuat!")
        else:
            print("User admin sudah ada.")

        # Clear existing data
        db.session.query(Berita).delete()
        db.session.query(Agenda).delete()
        db.session.query(Galeri).delete()
        
        # Seed Berita
        berita1 = Berita(
            judul="Penerimaan Santri Baru Tahun Ajaran 2026/2027",
            slug="penerimaan-santri-baru-2026",
            konten="Pondok Pesantren Albarokah membuka pendaftaran santri baru untuk jenjang SMP dan SMA. Pendaftaran dibuka mulai tanggal 1 Februari 2026 hingga 30 Mei 2026. Segera daftarkan putra-putri Anda untuk mendapatkan pendidikan agama dan umum yang berkualitas.",
            gambar="https://picsum.photos/seed/santri/800/400",
            tanggal=datetime.utcnow() - timedelta(days=2),
            penulis="Admin"
        )
        
        berita2 = Berita(
            judul="Kunjungan Syekh dari Al-Azhar Mesir",
            slug="kunjungan-syekh-al-azhar",
            konten="Alhamdulillah, Pondok Pesantren Albarokah mendapat kehormatan dikunjungi oleh Syekh Muhammad dari Al-Azhar Mesir. Beliau memberikan motivasi kepada para santri untuk semangat dalam menuntut ilmu agama.",
            gambar="https://picsum.photos/seed/syekh/800/400",
            tanggal=datetime.utcnow() - timedelta(days=5),
            penulis="Humas"
        )
        
        berita3 = Berita(
            judul="Santri Albarokah Juara 1 Lomba Pidato Bahasa Arab",
            slug="juara-pidato-bahasa-arab",
            konten="Selamat kepada Ananda Fulan bin Fulan yang telah berhasil meraih Juara 1 dalam Lomba Pidato Bahasa Arab tingkat Provinsi. Semoga prestasi ini dapat memotivasi santri lainnya.",
            gambar="https://picsum.photos/seed/juara/800/400",
            tanggal=datetime.utcnow() - timedelta(days=10),
            penulis="Kesiswaan"
        )
        
        db.session.add_all([berita1, berita2, berita3])
        
        # Seed Agenda
        agenda1 = Agenda(
            nama_kegiatan="Ujian Akhir Semester Genap",
            tanggal_mulai=datetime.utcnow() + timedelta(days=10),
            tanggal_selesai=datetime.utcnow() + timedelta(days=20),
            lokasi="Ruang Kelas",
            deskripsi="Pelaksanaan Ujian Akhir Semester Genap untuk seluruh santri."
        )
        
        agenda2 = Agenda(
            nama_kegiatan="Wisuda Tahfidz Angkatan V",
            tanggal_mulai=datetime.utcnow() + timedelta(days=45),
            tanggal_selesai=datetime.utcnow() + timedelta(days=45),
            lokasi="Aula Utama",
            deskripsi="Wisuda bagi santri yang telah menyelesaikan hafalan 30 Juz."
        )
        
        db.session.add_all([agenda1, agenda2])
        
        # Seed Galeri
        galeri_items = [
            Galeri(judul="Kegiatan Belajar Mengajar", gambar="https://picsum.photos/seed/belajar/800/600", kategori="Kegiatan"),
            Galeri(judul="Sholat Berjamaah", gambar="https://picsum.photos/seed/sholat/800/600", kategori="Kegiatan"),
            Galeri(judul="Asrama Santri", gambar="https://picsum.photos/seed/asrama/800/600", kategori="Fasilitas"),
            Galeri(judul="Laboratorium Komputer", gambar="https://picsum.photos/seed/komputer/800/600", kategori="Fasilitas"),
            Galeri(judul="Juara Umum Porseni", gambar="https://picsum.photos/seed/porseni/800/600", kategori="Prestasi"),
            Galeri(judul="Ekstrakurikuler Panahan", gambar="https://picsum.photos/seed/panahan/800/600", kategori="Kegiatan")
        ]
        
        db.session.add_all(galeri_items)
        
        db.session.commit()
        print("Data dummy berhasil ditambahkan!")

if __name__ == '__main__':
    seed_data()
