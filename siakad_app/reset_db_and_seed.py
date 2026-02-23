
from app import create_app, db
from app.models.user import User
from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran
from app.models.akademik import Nilai, Absensi, Tahfidz, Raport
from app.models.keuangan import PosKeuangan, TransaksiKeuangan, TabunganSantri, KonfigurasiLaporan
from app.models.konfigurasi import Konfigurasi
from datetime import datetime, date, timedelta
import random

app = create_app()

def seed_data():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()

        print("Seeding Konfigurasi...")
        # Konfigurasi Umum
        config = Konfigurasi(
            nama_lembaga="Pondok Pesantren Al-Barokah",
            alamat_lembaga="Sidomakmur, Desa Karangjati, Kecamatan Susukan, Kabupaten Banjarnegara",
            
            # MDTA Config
            nama_mdta="Madrasah Diniyah Takmiliyah Hidayatul Ulum Lil Barokah",
            kepala_mdta="Ust. Ahmad Fauzan",
            nip_mdta="198501012010011001",
            
            # LPQ Config
            nama_lpq="Taman Pendidikan Al-Qur'an Al-Barokah",
            kepala_lpq="Ustazah Siti Aminah",
            nip_lpq="199002022015022002"
        )
        db.session.add(config)
        
        # Konfigurasi Laporan Keuangan
        config_keuangan = KonfigurasiLaporan(
            nama_lembaga="Pondok Pesantren Al-Barokah",
            alamat_lembaga="Sidomakmur, Desa Karangjati, Kecamatan Susukan, Kabupaten Banjarnegara",
            telepon_lembaga="081234567890",
            email_lembaga="admin@albarokah.com",
            kota_ttd="Banjarnegara",
            nama_ttd="Bendahara Umum",
            jabatan_ttd="Bendahara",
            pimpinan_ponpes_nama="Kyai H. Abdullah",
            pimpinan_ponpes_nip="-"
        )
        db.session.add(config_keuangan)

        print("Seeding Users...")
        # Admin
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        # Ustadz / Pengajar
        ustadz1 = User(username='ustadz', role='ustadz')
        ustadz1.set_password('ustadz123')
        db.session.add(ustadz1)
        
        # Wali Kelas
        wali1 = User(username='wali', role='wali_kelas')
        wali1.set_password('wali123')
        db.session.add(wali1)
        
        db.session.commit()

        print("Seeding Pengajar...")
        pengajar_list = []
        names = ["Ust. Ahmad", "Ust. Budi", "Ustazah Rina", "Ust. Cahyo", "Ustazah Dini"]
        for name in names:
            user_id = None
            if "Budi" in name:
                user_id = ustadz1.id
            elif "Rina" in name:
                user_id = wali1.id
                
            p = Pengajar(nama=name, nip=f"19{random.randint(70,99)}{random.randint(1000,9999)}", 
                         alamat="Banjarnegara", no_hp="08123456789", user_id=user_id)
            db.session.add(p)
            pengajar_list.append(p)
        db.session.commit()

        print("Seeding Kelas...")
        kelas_mdt = []
        kelas_lpq = []
        
        # MDTA Classes
        mdt_names = ["1 Awwaliyah", "2 Awwaliyah", "3 Awwaliyah", "4 Awwaliyah", "1 Wustha", "2 Wustha"]
        for name in mdt_names:
            k = Kelas(nama_kelas=name, jenjang='MDTA', wali_kelas_id=random.choice(pengajar_list).id)
            db.session.add(k)
            kelas_mdt.append(k)
            
        # LPQ Classes
        lpq_names = ["Jilid 1", "Jilid 2", "Jilid 3", "Jilid 4", "Jilid 5", "Jilid 6", "Al-Qur'an", "Ghorib", "Tajwid"]
        for name in lpq_names:
            k = Kelas(nama_kelas=name, jenjang='LPQ', wali_kelas_id=random.choice(pengajar_list).id)
            db.session.add(k)
            kelas_lpq.append(k)
            
        db.session.commit()

        print("Seeding Mapel...")
        mapel_mdt = []
        mapel_lpq = []
        
        # MDTA Mapel (Based on typical curriculum)
        mdt_subjects = [
            ("Al-Qur'an Hadits", "A"), ("Aqidah Akhlaq", "A"), ("Fiqih", "A"), 
            ("Sejarah Kebudayaan Islam", "A"), ("Bahasa Arab", "A"),
            ("Praktek Ibadah", "B"), ("Ke-NU-an", "B"), ("Kaligrafi", "B")
        ]
        
        for subj, kel in mdt_subjects:
            m = MataPelajaran(nama_mapel=subj, kkm=75.0, kelompok=kel, jenjang='MDTA')
            db.session.add(m)
            mapel_mdt.append(m)
            
        # LPQ Mapel
        lpq_subjects = [
            ("Materi Pokok (Jilid/Qur'an)", "A"), ("Hafalan Doa Harian", "A"), 
            ("Hafalan Surat Pendek", "A"), ("Hafalan Ayat Pilihan", "A"),
            ("Praktek Wudhu & Sholat", "B"), ("Adab & Akhlaq", "B"), ("Menulis Arab (Khat)", "B")
        ]
        
        for subj, kel in lpq_subjects:
            m = MataPelajaran(nama_mapel=subj, kkm=70.0, kelompok=kel, jenjang='LPQ')
            db.session.add(m)
            mapel_lpq.append(m)
            
        db.session.commit()

        print("Seeding Santri...")
        santri_list = []
        first_names = ["Muhammad", "Ahmad", "Abdul", "Siti", "Nur", "Fatimid", "Rizky", "Putri", "Dewi", "Bagus"]
        last_names = ["Saputra", "Hidayat", "Rahman", "Aminah", "Hasanah", "Zahra", "Pratama", "Lestari", "Kusuma", "Santoso"]
        
        # Create 15 MDT Santri
        for i in range(15):
            nama = f"{random.choice(first_names)} {random.choice(last_names)}"
            k = random.choice(kelas_mdt)
            s = Santri(
                nis=f"2024{str(i).zfill(4)}",
                nama=nama,
                jenis_kelamin=random.choice(['L', 'P']),
                tempat_lahir="Banjarnegara",
                tanggal_lahir=date(2015, 1, 1),
                alamat="Desa Karangjati",
                nama_ayah="Fulan",
                nama_ibu="Fulanah",
                no_hp_wali="08123456789",
                status='aktif',
                kelas_id=k.id,
                jenjang='MDTA'
            )
            db.session.add(s)
            santri_list.append(s)

        # Create 15 LPQ Santri
        for i in range(15):
            nama = f"{random.choice(first_names)} {random.choice(last_names)}"
            k = random.choice(kelas_lpq)
            s = Santri(
                nis=f"2025{str(i).zfill(4)}",
                nama=nama,
                jenis_kelamin=random.choice(['L', 'P']),
                tempat_lahir="Banjarnegara",
                tanggal_lahir=date(2018, 1, 1),
                alamat="Desa Karangjati",
                nama_ayah="Fulan",
                nama_ibu="Fulanah",
                no_hp_wali="08123456789",
                status='aktif',
                kelas_id=k.id,
                jenjang='LPQ'
            )
            db.session.add(s)
            santri_list.append(s)
            
        db.session.commit()
        
        print("Seeding Nilai, Raport, dan Absensi Harian (Ganjil 2025/2026)...")
        semester = "Ganjil 2025/2026"
        
        for s in santri_list:
            # Determine Mapel based on Jenjang
            target_mapels = mapel_mdt if s.jenjang == 'MDTA' else mapel_lpq
            
            # Create Nilai for each Mapel
            for m in target_mapels:
                h = random.randint(75, 95)
                k = random.randint(80, 100)
                u = random.randint(70, 90)
                n = Nilai(
                    santri_id=s.id,
                    mapel_id=m.id,
                    semester=semester,
                    nilai_harian=h,
                    nilai_kehadiran=k,
                    nilai_uas=u,
                    nilai_uts=random.randint(70, 90),
                    deskripsi=f"Ananda mampu memahami materi {m.nama_mapel} dengan baik."
                )
                db.session.add(n)
            
            # Create Absensi Harian (Daily Attendance)
            # Create ~5 records per student in the last month
            statuses = ['Sakit', 'Izin', 'Alpha'] # Hadir is skipped as default
            for _ in range(random.randint(1, 5)):
                d_date = date.today() - timedelta(days=random.randint(1, 30))
                abs_rec = Absensi(
                    santri_id=s.id,
                    tanggal=d_date,
                    status=random.choice(statuses)
                )
                db.session.add(abs_rec)

            # Create Raport Record (Summary)
            r = Raport(
                santri_id=s.id,
                semester=semester,
                sakit=random.randint(0, 3),
                izin=random.randint(0, 2),
                alpha=random.randint(0, 1),
                catatan_wali_kelas="Tingkatkan terus belajarnya!",
                status_kenaikan="Naik Kelas" if "Genap" in semester else "",
                tanggal_bagi=date.today(),
                sikap_akhlak="Baik",
                sikap_kerajinan="Baik",
                sikap_kedisiplinan="Sangat Baik",
                sikap_kebersihan="Baik"
            )
            db.session.add(r)
            
            # Create Tahfidz Record (Randomly)
            if random.choice([True, False]):
                t = Tahfidz(
                    santri_id=s.id,
                    tanggal_setor=date.today(),
                    nama_surat="An-Naba",
                    ayat="1-10",
                    kelancaran="Lancar",
                    tajwid="Bagus"
                )
                db.session.add(t)

        db.session.commit()
        
        print("Seeding Keuangan (Pos, Transaksi, Tabungan)...")
        # Pos Keuangan (Kategori + Kode Akun)
        pos_spp = PosKeuangan(nama="SPP Bulanan", tipe="pemasukan", kode="4001", keterangan="Pembayaran SPP Santri")
        pos_pendaftaran = PosKeuangan(nama="Pendaftaran Santri Baru", tipe="pemasukan", kode="4002", keterangan="Biaya Pendaftaran")
        pos_gedung = PosKeuangan(nama="Uang Gedung/Pembangunan", tipe="pemasukan", kode="4003", keterangan="Sumbangan Pembangunan")
        pos_donasi = PosKeuangan(nama="Donasi/Infaq", tipe="pemasukan", kode="4004", keterangan="Sumbangan Tidak Mengikat")
        pos_seragam = PosKeuangan(nama="Uang Seragam", tipe="pemasukan", kode="4005", keterangan="Pembelian Seragam Santri")
        pos_kegiatan = PosKeuangan(nama="Uang Kegiatan", tipe="pemasukan", kode="4006", keterangan="Iuran Kegiatan PHBI/Ujian")
        
        pos_gaji = PosKeuangan(nama="Gaji Guru & Staff", tipe="pengeluaran", kode="5001", keterangan="Honorarium Pengajar")
        pos_listrik = PosKeuangan(nama="Listrik, Air & Internet", tipe="pengeluaran", kode="5002", keterangan="Biaya Operasional Bulanan")
        pos_atk = PosKeuangan(nama="ATK & Perlengkapan", tipe="pengeluaran", kode="5003", keterangan="Belanja Alat Tulis Kantor")
        pos_konsumsi = PosKeuangan(nama="Konsumsi & Dapur", tipe="pengeluaran", kode="5004", keterangan="Biaya Makan Santri")
        pos_pemeliharaan = PosKeuangan(nama="Pemeliharaan Gedung", tipe="pengeluaran", kode="5005", keterangan="Renovasi dan Perbaikan")
        pos_transport = PosKeuangan(nama="Transportasi", tipe="pengeluaran", kode="5006", keterangan="BBM & Sewa Kendaraan")
        pos_kesehatan = PosKeuangan(nama="Kesehatan (UKS)", tipe="pengeluaran", kode="5007", keterangan="Obat-obatan")
        pos_acara = PosKeuangan(nama="Acara & Kegiatan", tipe="pengeluaran", kode="5008", keterangan="Biaya Pelaksanaan Acara")
        
        all_pos = [
            pos_spp, pos_pendaftaran, pos_gedung, pos_donasi, pos_seragam, pos_kegiatan,
            pos_gaji, pos_listrik, pos_atk, pos_konsumsi, pos_pemeliharaan, pos_transport, pos_kesehatan, pos_acara
        ]
        db.session.add_all(all_pos)
        db.session.commit()
        
        # Transaksi Dummy
        print("Seeding Transaksi SPP & Lainnya...")
        
        # 1. SPP: Generate for ALL students for the last 3 months
        months_back = 3
        current_date = date.today()
        
        for s in santri_list:
            for i in range(months_back):
                # Calculate date (approximate 1st of month)
                tx_date = current_date - timedelta(days=30 * i)
                # Randomize day slightly
                tx_date = tx_date.replace(day=random.randint(1, 28))
                
                # Create SPP Transaction
                t = TransaksiKeuangan(
                    tanggal=tx_date,
                    pos_id=pos_spp.id,
                    jumlah=100000, # Assuming 100k/month
                    keterangan=f"SPP Bulan {tx_date.strftime('%B %Y')} - {s.nama}",
                    jenis="masuk",
                    santri_id=s.id,
                    user_id=admin.id,
                    metode_pembayaran=random.choice(["Tunai", "Transfer"])
                )
                db.session.add(t)
                
            # 2. Uang Gedung (Randomly for some students)
            if random.random() > 0.5:
                t2 = TransaksiKeuangan(
                    tanggal=date.today() - timedelta(days=random.randint(0, 60)),
                    pos_id=pos_gedung.id,
                    jumlah=500000,
                    keterangan=f"Cicilan Uang Gedung - {s.nama}",
                    jenis="masuk",
                    santri_id=s.id,
                    user_id=admin.id,
                    metode_pembayaran="Tunai"
                )
                db.session.add(t2)
                
            # 3. Uang Seragam (Randomly)
            if random.random() > 0.7:
                t3 = TransaksiKeuangan(
                    tanggal=date.today() - timedelta(days=random.randint(0, 90)),
                    pos_id=pos_seragam.id,
                    jumlah=350000,
                    keterangan=f"Pelunasan Seragam - {s.nama}",
                    jenis="masuk",
                    santri_id=s.id,
                    user_id=admin.id,
                    metode_pembayaran="Tunai"
                )
                db.session.add(t3)

        # Pengeluaran Operasional (Lebih Variatif)
        expenses = [
            (pos_listrik, 1500000, "Bayar Listrik Bulan Ini"),
            (pos_gaji, 5000000, "Gaji Guru Bulan Ini"),
            (pos_atk, 250000, "Beli Kertas A4 & Tinta Printer"),
            (pos_konsumsi, 3000000, "Belanja Dapur Mingguan"),
            (pos_pemeliharaan, 750000, "Perbaikan Kran Air Asrama Putra"),
            (pos_transport, 200000, "BBM Operasional Antar Jemput"),
            (pos_acara, 1500000, "Biaya Konsumsi Pengajian Bulanan"),
            (pos_kesehatan, 150000, "Restock Obat P3K UKS")
        ]
        
        for pos, amount, desc in expenses:
            t_out = TransaksiKeuangan(
                tanggal=date.today() - timedelta(days=random.randint(0, 5)),
                pos_id=pos.id,
                jumlah=amount,
                keterangan=desc,
                jenis="keluar",
                user_id=admin.id,
                metode_pembayaran="Transfer" if amount > 1000000 else "Tunai"
            )
            db.session.add(t_out)
            
        # Tabungan Santri (Saldo Awal, Setor, Tarik)
        print("Seeding Tabungan...")
        for s in santri_list:
            # Initial Deposit
            saldo = 0
            
            # Setor 1
            amt1 = random.choice([50000, 100000, 200000])
            saldo += amt1
            tab1 = TabunganSantri(
                santri_id=s.id,
                jenis='setor',
                jumlah=amt1,
                tanggal=datetime.now() - timedelta(days=random.randint(10, 20)),
                keterangan="Tabungan Awal",
                user_id=admin.id,
                saldo_akhir=saldo
            )
            db.session.add(tab1)
            
            # Randomly Setor again
            if random.choice([True, False]):
                amt2 = random.choice([10000, 20000, 50000])
                saldo += amt2
                tab2 = TabunganSantri(
                    santri_id=s.id,
                    jenis='setor',
                    jumlah=amt2,
                    tanggal=datetime.now() - timedelta(days=random.randint(5, 9)),
                    keterangan="Nabung Mingguan",
                    user_id=admin.id,
                    saldo_akhir=saldo
                )
                db.session.add(tab2)
                
            # Randomly Tarik
            if random.choice([True, False]) and saldo > 20000:
                amt3 = 20000
                saldo -= amt3
                tab3 = TabunganSantri(
                    santri_id=s.id,
                    jenis='tarik',
                    jumlah=amt3,
                    tanggal=datetime.now() - timedelta(days=random.randint(1, 4)),
                    keterangan="Jajan Koperasi",
                    user_id=admin.id,
                    saldo_akhir=saldo
                )
                db.session.add(tab3)
            
        db.session.commit()

        print("Done! Database reset and seeded.")

if __name__ == '__main__':
    seed_data()
