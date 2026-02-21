# Sistem Informasi Akademik (SIAKAD) & Website Profil Pondok Pesantren Albarokah

Project ini adalah solusi terintegrasi untuk manajemen akademik pesantren dan portal informasi publik. Terdiri dari dua aplikasi utama:
1.  **SIAKAD App**: Sistem Informasi Akademik untuk manajemen data santri, nilai, absensi, keuangan, dan raport.
2.  **Web Profile**: Website profil publik untuk informasi pesantren, berita, galeri, dan PPDB.

## Fitur Utama

### SIAKAD App (Sistem Akademik)
*   **Role Management**: Admin, Ustadz, Wali Santri, Santri.
*   **Akademik**: Input Nilai, Absensi, Hafalan Tahfidz, E-Raport (PDF).
*   **Keuangan**: Pembayaran SPP, Tabungan, Laporan Keuangan.
*   **Keamanan**: Enkripsi Password, CSRF Protection, Rate Limiting.

### Web Profile (Portal Publik)
*   **Informasi Publik**: Profil Pesantren, Berita, Agenda, Galeri.
*   **PPDB Online**: Formulir pendaftaran santri baru (Terintegrasi Google Sheets).
*   **Kontak**: Formulir hubungi kami (Notifikasi via Email SMTP & WhatsApp).
*   **SEO & Performance**: Caching (Flask-Caching), Kompresi Aset.

## Persyaratan Sistem

*   **Server**: Ubuntu 20.04/22.04/24.04 LTS
*   **Bahasa**: Python 3.10+
*   **Database**: PostgreSQL
*   **Web Server**: Nginx + Gunicorn
*   **Lainnya**: Supervisor (Process Control)

## Instalasi & Deployment

Proyek ini menggunakan struktur folder terpisah untuk `siakad_app` dan `web_profile`.

### 1. Setup Lokal (Development)
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
    *   Copy `.env.example` menjadi `.env` di masing-masing folder.
    *   Sesuaikan `DATABASE_URL`, `MAIL_USERNAME`, `MAIL_PASSWORD`.

### 2. Deployment ke Server (VPS)
Panduan lengkap deployment, update, dan sinkronisasi database/konten tersedia di file **`DEPLOYMENT_GUIDE.md`**.

**Cara Update Cepat (Server):**
```bash
cd /var/www/Albarokah-SIAKAD
./sync_server.sh
```

## Struktur Project
```
Albarokah/
├── siakad_app/       # Aplikasi Sistem Akademik
├── web_profile/      # Website Profil & PPDB
├── deployment/       # Konfigurasi Nginx & Systemd
├── DEPLOYMENT_GUIDE.md # Panduan Teknis Server (Git Ignored)
└── README.md         # Dokumentasi Umum
```

## Akun Demo

| Role | Username | Password |
| :--- | :--- | :--- |
| **SIAKAD Admin** | admin | admin123 |
| **SIAKAD Guru** | ustadz1 | ustadz123 |
| **SIAKAD Wali** | wali1 | wali123 |
| **Web Profile Admin** | admin | password123 |

## Catatan Penting
*   **Generate PDF**: Memerlukan library GTK+ terinstall di sistem operasi (untuk WeasyPrint).
*   **Database**: Default menggunakan SQLite untuk kemudahan setup. Untuk production, disarankan PostgreSQL.
*   **Upload Gambar**: Web Profile mendukung upload gambar lokal (disimpan di `web_profile/app/static/uploads`) atau penggunaan URL eksternal (Picsum/Unsplash).

## Struktur Folder

```
Albarokah/
├── siakad_app/          # Aplikasi SIAKAD (Internal)
│   ├── app/
│   │   ├── models/      # Database Models
│   │   ├── routes/      # Controller/Views
│   │   ├── templates/   # HTML Templates
│   │   └── static/      # CSS, JS, Images
│   └── ...
├── web_profile/         # Website Profil (Publik)
│   ├── app/
│   │   ├── admin/       # Panel Admin Web Profile
│   │   ├── templates/
│   │   └── static/
│   │       └── uploads/ # Folder Upload Gambar
│   └── ...
└── deployment/          # Konfigurasi Nginx & Systemd (Siap Deploy)
```

## Troubleshooting

1.  **Gambar tidak muncul (ORB/CORB Error)**:
    *   Pastikan `Flask-Talisman` dikonfigurasi dengan benar untuk mengizinkan domain gambar eksternal (seperti `picsum.photos`).
    *   Cek console browser untuk detail error CSP.

2.  **Error PDF Generation**:
    *   Pastikan GTK+ Runtime sudah terinstall dan ada di PATH environment variable.
| Admin | `admin` | `password123` |
| Ustadz | `ustadz` | `password123` |
| Wali Santri | `wali` | `password123` |

## Catatan Keamanan (Production)

Saat deploy ke production, pastikan untuk:
1.  Mengganti `SECRET_KEY` dengan string acak yang kuat.
2.  Mengaktifkan HTTPS (SSL) agar fitur `Secure Cookie` dan `HSTS` berfungsi.
3.  Menggunakan web server production seperti Gunicorn + Nginx.
4.  Menyesuaikan `Content-Security-Policy` di `app/__init__.py` jika menggunakan domain/CDN lain.
