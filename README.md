# Sistem Informasi Akademik (SIAKAD) & Website Profil Pondok Pesantren Albarokah

Project ini adalah solusi terintegrasi untuk manajemen akademik pesantren dan portal informasi publik. Terdiri dari dua aplikasi utama:
1.  **SIAKAD App**: Sistem Informasi Akademik untuk manajemen data santri, nilai, absensi, keuangan, dan raport.
2.  **Web Profile**: Website profil publik untuk informasi pesantren, berita, galeri, dan PPDB.

---

## 📚 Dokumentasi Lengkap

Untuk panduan yang lebih spesifik, silakan merujuk ke dokumen berikut:

| Dokumen | Deskripsi | Target Pembaca |
| :--- | :--- | :--- |
| **[PANDUAN_PENGGUNA_LENGKAP.md](PANDUAN_PENGGUNA_LENGKAP.md)** | Manual lengkap penggunaan aplikasi (Admin, Guru, Wali). | End-User, Admin |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Panduan teknis instalasi server, update kode, dan backup. | DevOps, Developer |
| **[DEV_NOTES.md](DEV_NOTES.md)** | Catatan pengembang, SOP, troubleshooting, dan status proyek. | Developer |
| **[ACCESS_CREDENTIALS.md](ACCESS_CREDENTIALS.md)** | **(RAHASIA)** Kredensial server, database, dan password. | **Authorized Only** |

> **Catatan Keamanan:** File `ACCESS_CREDENTIALS.md` tidak boleh di-push ke repository publik (terdaftar di `.gitignore`).

---

## 🌟 Fitur Utama

### 1. SIAKAD App (Internal)
*   **Akademik**: Manajemen Santri, Kelas, Mapel, Nilai, Absensi, dan Hafalan Tahfidz.
*   **E-Raport**: Generate Raport PDF otomatis dengan tanda tangan digital (Format MDT & LPQ).
*   **Keuangan**: Pembayaran SPP, Uang Gedung, Tabungan Santri, dan Laporan Keuangan.
*   **Role**: Admin, Ustadz, Wali Kelas, Wali Santri.

### 2. Web Profile (Publik)
*   **Portal Informasi**: Berita, Agenda, Galeri Foto, Profil Pimpinan.
*   **PPDB Online**: Pendaftaran santri baru terintegrasi.
*   **CMS Admin**: Panel admin khusus untuk mengelola konten website.

---

## 🛠️ Teknologi

*   **Backend**: Python 3.10+ (Flask Framework)
*   **Database**: PostgreSQL 17
*   **Frontend**: Bootstrap 5, Jinja2, Soft UI Dashboard
*   **PDF Engine**: WeasyPrint
*   **Server**: Nginx + Gunicorn (Ubuntu LTS)

---

## 🚀 Instalasi Singkat (Lokal)

1.  **Clone Repository** & Masuk ke direktori.
2.  **Setup Database**:
    *   Pastikan PostgreSQL berjalan.
    *   Jalankan `setup_local_db.bat` (Windows) untuk setup otomatis.
3.  **Jalankan Aplikasi**:
    *   **SIAKAD**: `cd siakad_app && python run.py` (Port 5000)
    *   **Web Profile**: `cd web_profile && python run.py` (Port 5001)

*Untuk panduan deployment server lengkap, lihat [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).*

---

## 🔐 Akun Demo (Default)

Jika menggunakan data seed bawaan (`seed.py` / `setup_local_db.bat`):

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Ustadz** | `ustadz` | `ustadz123` |
| **Wali Kelas** | `wali` | `wali123` |

---

## 🔒 Keamanan Server

Sistem ini dilengkapi dengan:
*   **Fail2Ban**: Proteksi Brute-force login SSH & Web.
*   **ClamAV**: Antivirus untuk scan upload file berbahaya.
*   **Role-Based Access Control (RBAC)**: Pembatasan hak akses user.
*   **Secure Session**: Enkripsi cookie dan CSRF protection.

*Lihat [DEV_NOTES.md](DEV_NOTES.md) untuk SOP Keamanan.*
