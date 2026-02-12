# Sistem Informasi Akademik (SIAKAD) & Website Profil Pondok Pesantren Albarokah

Project ini adalah solusi terintegrasi untuk manajemen akademik pesantren dan portal informasi publik. Terdiri dari dua aplikasi utama:
1.  **SIAKAD App**: Sistem Informasi Akademik untuk manajemen data santri, nilai, absensi, keuangan, dan raport.
2.  **Web Profile**: Website profil publik untuk informasi pesantren, berita, galeri, dan PPDB.

## Fitur Utama

### SIAKAD App
*   **Autentikasi & Otorisasi**: Login dengan role `admin`, `ustadz`, `wali_santri`.
*   **Master Data**: CRUD Santri, Pengajar, Kelas, Mata Pelajaran, User.
*   **Akademik**: Input Nilai, Absensi, Hafalan Tahfidz, Generate E-Raport (PDF).
*   **Keuangan**: Pembayaran SPP dan history pembayaran.
*   **Keamanan**:
    *   Password Hashing (Argon2).
    *   CSRF Protection (Flask-WTF).
    *   Security Headers (Flask-Talisman, CSP).
    *   Rate Limiting (Flask-Limiter) pada login.
    *   Data Isolation (Wali Santri hanya melihat data anaknya).

### Web Profile
*   **Landing Page**: Informasi umum dan fitur unggulan.
*   **Profil**: Sejarah, Visi Misi.
*   **Program**: Tahfidz, Madrasah, Sekolah Formal.
*   **Berita & Agenda**: Artikel dan pengumuman.
*   **Galeri**: Foto kegiatan.
*   **PPDB**: Informasi pendaftaran santri baru.

## Persyaratan Sistem

*   Python 3.8+
*   PostgreSQL (Disarankan untuk Production) atau SQLite (Development).
*   Library GTK (untuk WeasyPrint/PDF Generation).

## Instalasi

1.  **Clone Repository**
    ```bash
    git clone <repository_url>
    cd Albarokah
    ```

2.  **Setup Virtual Environment**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    # source .venv/bin/activate  # Linux/Mac
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r siakad_app/requirements.txt
    pip install -r web_profile/requirements.txt
    ```

4.  **Konfigurasi Database**
    *   Buat file `.env` di folder `siakad_app` dan `web_profile`.
    *   Isi dengan:
        ```env
        SECRET_KEY=kunci-rahasia-anda
        DATABASE_URL=sqlite:///app.db  # Atau URL PostgreSQL
        ```

5.  **Inisialisasi Database**
    ```bash
    # Untuk SIAKAD
    cd siakad_app
    flask db upgrade
    python seed.py  # Isi data dummy

    # Untuk Web Profile
    cd ../web_profile
    flask db upgrade
    python seed.py
    ```

## Menjalankan Aplikasi

Jalankan kedua aplikasi di terminal terpisah:

**Terminal 1 (SIAKAD - Port 5000)**
```bash
cd siakad_app
python run.py
```

**Terminal 2 (Web Profile - Port 8001)**
```bash
cd web_profile
python run.py
```

Akses di browser:
*   SIAKAD: `http://localhost:5000`
*   Web Profile: `http://localhost:8001`

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
