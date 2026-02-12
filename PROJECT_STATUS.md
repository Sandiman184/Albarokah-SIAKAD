# Dokumentasi Status Proyek Albarokah
**Tanggal Pembaruan Terakhir:** 12 Februari 2026

Dokumen ini merangkum kondisi teknis, fitur, arsitektur, dan status keamanan terkini dari sistem **SIAKAD** dan **Web Profile** Pondok Pesantren Albarokah.

---

## 1. Ikhtisar Arsitektur

Sistem terdiri dari dua aplikasi Flask terpisah yang berbagi basis data konsep (namun saat ini menggunakan file database SQLite terpisah untuk development):

| Komponen | Deskripsi | Port Lokal | Teknologi Utama |
| :--- | :--- | :--- | :--- |
| **SIAKAD App** | Sistem Informasi Akademik Internal | `5000` | Flask, Flask-Login, Flask-SQLAlchemy, WeasyPrint (PDF) |
| **Web Profile** | Website Informasi Publik (CMS) | `8001` | Flask, Flask-Admin (Custom), Flask-Talisman, WTForms |
| **Database** | Penyimpanan Data | - | SQLite (Dev), PostgreSQL (Rec. Prod) |

---

## 2. Status Fitur Terkini

### A. Web Profile (Aplikasi Publik)
Aplikasi ini berfungsi sebagai "Wajah" pesantren dan CMS sederhana.

*   **Manajemen Konten (CMS)**:
    *   ✅ **Berita/Artikel**: CRUD lengkap dengan *rich text* sederhana dan upload gambar.
    *   ✅ **Agenda**: Manajemen jadwal kegiatan pesantren.
    *   ✅ **Galeri**: Manajemen foto kegiatan dengan kategori.
    *   ✅ **Pengaturan**: Edit profil pesantren (Nama, Alamat, Kontak, Sosmed) dinamis.
*   **Fitur Upload**:
    *   ✅ Mendukung upload file fisik (disimpan di `static/uploads`).
    *   ✅ Mendukung input URL gambar eksternal (Picsum/Unsplash).
    *   ✅ Sanitasi nama file otomatis (random hex) untuk keamanan.
*   **Tampilan (Frontend)**:
    *   ✅ Responsif menggunakan Bootstrap 5.
    *   ✅ Integrasi FontAwesome (via CDNJS).
    *   ✅ Gambar placeholder otomatis menggunakan Picsum Photos (stabil).
    *   ⚠️ Beberapa bagian (Sejarah, Visi Misi, Detail Program) masih *hardcoded* di template HTML, belum dinamis via database.

### B. SIAKAD App (Aplikasi Internal)
Sistem manajemen operasional pendidikan.

*   **Autentikasi Multi-Role**:
    *   ✅ **Admin**: Akses penuh ke Master Data & Pengaturan.
    *   ✅ **Ustadz (Guru)**: Input Nilai, Absensi, Hafalan.
    *   ✅ **Wali Santri**: Lihat Raport, Tagihan SPP, Riwayat Hafalan anak.
*   **Akademik**:
    *   ✅ Manajemen Kelas & Mata Pelajaran.
    *   ✅ Input & Rekap Nilai.
    *   ✅ **E-Raport**: Generate raport format PDF siap cetak.
*   **Keuangan**:
    *   ✅ Manajemen Tagihan SPP.
    *   ✅ Pencatatan Pembayaran & Kwitansi.

---

## 3. Keamanan & Konfigurasi

Sistem telah diaudit dan diperkuat dengan standar keamanan web modern:

1.  **Content Security Policy (CSP)**:
    *   Menggunakan `Flask-Talisman`.
    *   Dikonfigurasi untuk mengizinkan resource terpercaya: `cdnjs` (FontAwesome), `picsum.photos` (Gambar), `fonts.googleapis.com`.
    *   *Catatan*: Header COEP/COOP dinonaktifkan di `Web Profile` untuk mencegah pemblokiran gambar lintas-domain (ORB Error).
2.  **Proteksi CSRF**:
    *   `Flask-WTF` aktif secara global. Semua form wajib memiliki `hidden_tag()`.
3.  **Password Security**:
    *   Hashing menggunakan algoritma standar Werkzeug (`pbkdf2:sha256` atau `argon2` jika tersedia).
4.  **Upload Security**:
    *   Validasi ekstensi file (`jpg`, `png`, `jpeg`, `gif`).
    *   Rename file otomatis untuk mencegah *Path Traversal*.

---

## 4. Struktur Direktori & Deployment

```
Albarokah/
├── deployment/                 # Konfigurasi Server Produksi
│   ├── nginx/albarokah.conf    # Config Reverse Proxy (Port 80 -> 5000/8001)
│   └── systemd/                # Service file untuk Auto-start
├── siakad_app/                 # Source Code SIAKAD
│   ├── app.db                  # Database SQLite (Development)
│   └── ...
├── web_profile/                # Source Code Web Profile
│   ├── app/
│   │   ├── static/uploads/     # Penyimpanan Gambar Upload
│   │   └── templates/admin/    # View Panel Admin
│   └── ...
└── README.md                   # Panduan Instalasi
```

## 5. Isu yang Diketahui & Rencana Pengembangan

1.  **Integrasi Database**: Saat ini SIAKAD dan Web Profile menggunakan file `app.db` yang berbeda.
    *   *Rencana*: Migrasi ke satu instance PostgreSQL untuk kedua aplikasi agar data bisa terintegrasi (jika diperlukan).
2.  **Konten Statis**: Halaman Profil dan Program di Web Profile masih statis.
    *   *Rencana*: Buat model `Halaman` di database agar admin bisa mengedit seluruh teks di website.
3.  **PDF Generation**: Memerlukan dependensi sistem (GTK+) yang kadang sulit diinstall di Windows.
    *   *Solusi*: Gunakan Docker untuk deployment agar lingkungan konsisten.

## 6. Kredensial Demo

| Aplikasi | Role | Username | Password |
| :--- | :--- | :--- | :--- |
| **Web Profile** | Admin | `admin` | `password123` |
| **SIAKAD** | Admin | `admin` | `admin123` |
| **SIAKAD** | Guru | `ustadz1` | `ustadz123` |
| **SIAKAD** | Wali | `wali1` | `wali123` |
