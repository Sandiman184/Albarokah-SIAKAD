# Sistem Informasi Akademik (SIAKAD) & Website Profil Pondok Pesantren Albarokah

Project ini adalah solusi terintegrasi untuk manajemen akademik pesantren dan portal informasi publik. Terdiri dari dua aplikasi utama:
1.  **SIAKAD App**: Sistem Informasi Akademik untuk manajemen data santri, nilai, absensi, keuangan, dan raport.
2.  **Web Profile**: Website profil publik untuk informasi pesantren, berita, galeri, dan PPDB.

## Fitur Utama

### SIAKAD App (Sistem Akademik)
*   **Role Management**: Admin, Ustadz (Pengajar), Wali Kelas, Wali Santri.
*   **Akademik**: 
    *   Manajemen Data Santri, Pengajar, Kelas, Mata Pelajaran.
    *   Input Nilai Akademik & Non-Akademik (Hafalan Tahfidz, Ibadah).
    *   Absensi Harian & Rekapitulasi.
    *   **E-Raport**: Generate PDF Raport Otomatis (Format MDT & LPQ) dengan Tanda Tangan Digital.
*   **Keuangan**: 
    *   Manajemen Pos Keuangan (SPP, Gedung, Donasi, dll).
    *   Pencatatan Pemasukan & Pengeluaran.
    *   Tabungan Santri.
    *   Laporan Keuangan Bulanan/Tahunan.
*   **Keamanan**: Enkripsi Password, CSRF Protection, Rate Limiting.

### Web Profile (Portal Publik)
*   **Informasi Publik**: Profil Pesantren, Sejarah, Struktur Organisasi, Berita, Agenda, Galeri Foto.
*   **PPDB Online**: Formulir pendaftaran santri baru yang terintegrasi.
*   **Kontak**: Formulir hubungi kami.
*   **Panel Admin**: CMS untuk mengelola konten berita, galeri, dan pimpinan.

## Persyaratan Sistem

*   **Server**: Ubuntu 20.04/22.04 LTS
*   **Bahasa**: Python 3.10+
*   **Database**: PostgreSQL
*   **Web Server**: Nginx (Reverse Proxy) + Gunicorn
*   **PDF Engine**: WeasyPrint (Membutuhkan GTK+ libraries)

## Instalasi & Deployment

Proyek ini menggunakan struktur folder terpisah untuk `siakad_app` dan `web_profile`.

### 1. Setup Lokal (Development)

**PENTING: Gunakan Database Lokal!**
Jangan pernah menghubungkan aplikasi lokal ke database produksi server. Gunakan database terpisah di komputer Anda.

**Cara Cepat (Windows):**
1.  Pastikan PostgreSQL sudah terinstall.
2.  Jalankan script otomatis:
    ```bash
    setup_local_db.bat
    ```
    Script ini akan membuat user database, melakukan migrasi, dan mengisi data awal.

**Cara Manual:**
1.  **Clone Repository**
2.  **Buat Virtual Environment**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
3.  **Install Dependencies**
    ```bash
    pip install -r web_profile/requirements.txt
    pip install -r siakad_app/requirements.txt
    ```
4.  **Konfigurasi Environment (.env)**
    *   Copy `.env.example` menjadi `.env` di folder `siakad_app` DAN `web_profile`.
    *   **Edit .env**: Pastikan `DATABASE_URL` mengarah ke localhost (misal: `postgresql://albarokah_user:alnet%402026@localhost/siakad_db`).
    *   Jangan gunakan kredensial server di sini!

### 2. Deployment ke Server (VPS)
Gunakan script `sync_server.sh` untuk melakukan update otomatis di server production.

**Cara Update Cepat (Server):**
```bash
cd /var/www/Albarokah-SIAKAD
./sync_server.sh
```

## Keamanan Server

### A. Antivirus (ClamAV)
Gunakan script `setup_clamav.sh` (jangan di-push ke git) untuk instalasi otomatis.
1.  Upload script ke server: `scp -P 8022 setup_clamav.sh root@IP:/var/www/Albarokah-SIAKAD/`
2.  Jalankan: `./setup_clamav.sh`

**Scan Manual:**
```bash
sudo clamscan -r -i /var/www/Albarokah-SIAKAD
```
*Note: Scan manual membutuhkan waktu beberapa menit untuk loading database virus.*

### B. Anti Brute-Force (Fail2Ban)
Gunakan script `setup_fail2ban.sh` untuk memblokir IP yang gagal login berulang kali.

## Struktur Project
```
Albarokah/
├── siakad_app/       # Aplikasi Sistem Akademik (Flask)
│   ├── app/
│   │   ├── models/      # Database Models (Akademik, Keuangan, User)
│   │   ├── routes/      # Controller/Views
│   │   ├── templates/   # HTML Templates (Jinja2)
│   │   ├── services/    # Business Logic (Raport, PDF, Backup)
│   │   └── static/      # CSS, JS, Images
├── web_profile/      # Website Profil & PPDB (Flask)
│   ├── app/
│   │   ├── admin/       # Panel Admin CMS
│   │   ├── templates/
│   │   └── static/
├── deployment/       # Konfigurasi Nginx & Systemd
├── README.md         # Dokumentasi Umum
└── sync_server.sh    # Script Sinkronisasi Server
```

## Akun Demo (Default Seed)
