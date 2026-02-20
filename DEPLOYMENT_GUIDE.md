# Panduan Deployment dan Sinkronisasi Albarokah

Dokumen ini menjelaskan prosedur teknis untuk deployment server dan sinkronisasi data antara lingkungan Lokal (Development) dan Server (Production).

## 1. Arsitektur Sinkronisasi

Sistem ini memiliki dua jenis sinkronisasi yang terpisah namun saling melengkapi:

1.  **Sinkronisasi Kode (Code Sync)**
    *   **Apa yang disinkronkan?**: File Python (`.py`), Template HTML (`.html`), CSS/JS Statis (`static/css`, `static/js`), Konfigurasi.
    *   **Mekanisme**: Melalui **Git** (GitHub).
    *   **Arah**: Lokal -> GitHub -> Server.
    *   **Alat**: Script `sync_server.sh`.

2.  **Sinkronisasi Data (Data Sync)**
    *   **Apa yang disinkronkan?**: Database (Isi berita, santri, nilai, pengaturan), File Media yang diupload (`static/uploads/*`).
    *   **Mekanisme**: Melalui **Fitur Backup & Restore** di Admin Panel Web Profile.
    *   **Arah**: Lokal (Download Backup) -> Server (Upload Restore).
    *   **Alat**: Menu Admin > Backup & Restore > Full System Snapshot.

---

## 2. Prosedur Sinkronisasi Total (Lokal ke Server)

Untuk memastikan Server **100% Identik** dengan Lokal, ikuti urutan langkah berikut:

### Langkah 1: Sinkronisasi Kode (Update Aplikasi)
Lakukan ini jika Anda mengubah kode program, tampilan (HTML/CSS), atau menambah fitur baru.

1.  **Di Komputer Lokal**:
    *   Simpan semua perubahan kode.
    *   Commit dan Push ke GitHub:
        ```bash
        git add .
        git commit -m "Update fitur X dan perbaikan Y"
        git push origin main
        ```

2.  **Di Server (Melalui Terminal/SSH)**:
    *   Login ke server.
    *   Jalankan script sinkronisasi otomatis:
        ```bash
        cd /path/to/Albarokah
        ./sync_server.sh
        ```
    *   **Apa yang dilakukan script ini?**
        *   Mengambil kode terbaru dari GitHub (`git pull`).
        *   **Reset Hard**: Menghapus perubahan "liar" di server agar sama persis dengan GitHub.
        *   **Fix Permissions**: Memperbaiki hak akses file agar bisa dibaca/tulis oleh sistem (`www-data`).
        *   Install dependencies baru (`pip install`).
        *   Jalankan migrasi database (`flask db upgrade`).
        *   Restart service aplikasi.

### Langkah 2: Sinkronisasi Data (Update Konten)
Lakukan ini jika Anda ingin konten di server (berita, galeri, data santri) sama persis dengan data di komputer lokal Anda.

1.  **Di Web Lokal (http://localhost:8001/admin)**:
    *   Masuk ke menu **Pengaturan** -> **Backup & Restore**.
    *   Pada bagian "Full System Snapshot", klik **Download Snapshot**.
    *   Tunggu proses selesai dan simpan file `.zip` yang dihasilkan.

2.  **Di Web Server (http://domain-anda.com/admin)**:
    *   Masuk ke menu **Pengaturan** -> **Backup & Restore**.
    *   Pada bagian "Restore Snapshot", pilih file `.zip` yang tadi didownload.
    *   Klik **Restore System Now**.
    *   Konfirmasi peringatan keamanan.

### 3. Verifikasi
Setelah kedua langkah di atas selesai:
1.  Buka website server.
2.  Pastikan tampilan dan menu sesuai dengan update kode terakhir.
3.  Pastikan berita, gambar, dan data sesuai dengan data lokal.

---

## 3. Troubleshooting (Pemecahan Masalah)

### Masalah: "Konten Tertinggal" (File lama masih muncul)
Jika setelah Restore data, file gambar lama masih muncul atau folder uploads tidak bersih:
*   Penyebab: Masalah hak akses (permissions) sehingga sistem gagal menghapus file lama sebelum menimpa dengan yang baru.
*   Solusi:
    1.  Login ke terminal server.
    2.  Jalankan `./sync_server.sh` lagi. Script ini akan memaksa perbaikan hak akses (`chown www-data`) pada folder uploads.
    3.  Lakukan proses **Restore Snapshot** ulang di Admin Panel.

### Masalah: "Internal Server Error" atau Gagal Restore Database
*   Penyebab: Ada koneksi aktif (misalnya dari user lain atau aplikasi) yang mencegah database dihapus/ditimpa.
*   Solusi:
    1.  Script `backup_service.py` terbaru sudah otomatis mencoba memutus koneksi lain. Pastikan Anda sudah update kode server.
    2.  Jika masih gagal, gunakan **Opsi Nuklir (Hard Reset)**.

### Opsi Nuklir: Hard Reset (Jika semua cara gagal)
Jika fitur Restore via Web terus gagal atau data tetap kacau, gunakan script pamungkas ini di terminal server:

```bash
cd /var/www/Albarokah-SIAKAD
chmod +x hard_reset_server.sh
./hard_reset_server.sh
```

**PERINGATAN KERAS**: Script ini akan menghapus TOTAL database dan folder uploads di server, lalu me-restart service. Setelah script ini selesai, server akan dalam keadaan "kosong". Segera lakukan **Restore Snapshot** via Admin Panel setelahnya.

---

## 4. Struktur Folder Penting

*   `/var/www/Albarokah-SIAKAD`: Root folder aplikasi.
*   `web_profile/app/static/uploads`: Tempat penyimpanan file media (gambar berita, galeri). Folder ini akan **dibersihkan total** saat proses Restore Snapshot.
*   `instance/`: Folder tempat database SQLite (jika tidak pakai PostgreSQL).
