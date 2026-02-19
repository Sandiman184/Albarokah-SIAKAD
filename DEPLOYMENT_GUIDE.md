# Panduan Deployment & Update Server Albarokah

Dokumen ini berisi panduan lengkap untuk melakukan update kode, migrasi database, sinkronisasi konten, dan maintenance server Albarokah (Web Profile & SIAKAD).

## 1. Struktur Server
- **OS:** Ubuntu
- **Web Server:** Nginx (Reverse Proxy)
- **App Server:** Gunicorn (Python WSGI)
- **Database:** PostgreSQL
- **Lokasi Project:** `/var/www/Albarokah-SIAKAD`
- **User Aplikasi:** `www-data` (Demi keamanan, JANGAN gunakan root)
- **Domain:**
  - Web Profile: `albarokahsidomakmur.ponpes.id` (Port 8001)
  - SIAKAD: `siakad.albarokahsidomakmur.ponpes.id` (Port 8000)

---

## 2. Workflow Update Rutin (Kode & Fitur)

### Langkah 1: Di Laptop/Lokal (Push ke GitHub)
Lakukan perubahan kode, lalu kirim ke GitHub:
```bash
git add .
git commit -m "Perbaikan fitur X"
git push origin main
```

### Langkah 2: Di Server (Jalankan Update Otomatis)
Masuk ke server via SSH, lalu jalankan satu perintah ini:
```bash
cd /var/www/Albarokah-SIAKAD
./update_server.sh
```
*Script ini akan otomatis:*
1. Mengambil kode terbaru dari GitHub (`git pull`)
2. Mengupdate library Python jika ada perubahan
3. Merestart service aplikasi (Web & SIAKAD)
4. Mengecek status server

---

## 3. Workflow Sinkronisasi Konten (Foto & Database)
**PENTING:** Git TIDAK menyimpan foto upload atau isi database. Jika Anda menambah berita/foto di lokal dan ingin menampilkannya di server, gunakan script `sync_content.sh`.

### Cara Sinkronisasi (Dari Laptop Lokal)
Jalankan script ini menggunakan Git Bash atau Terminal Linux di laptop Anda:
```bash
# Pastikan script bisa dieksekusi
chmod +x sync_content.sh

# Jalankan sinkronisasi (Ganti IP_SERVER dengan IP VPS Anda)
./sync_content.sh IP_SERVER
```
*Script ini akan:*
1. Mengirim folder `web_profile/app/static/uploads/` ke server via `rsync/scp`.
2. (Opsional) Mem-backup database lokal dan me-restore-nya di server (Hati-hati: Data server akan tertimpa!).

---

## 4. Cara Migrasi Database (Update Schema)

Jika Anda mengubah struktur database (menambah tabel/kolom) di lokal:

### Langkah 1: Generate Migrasi di Lokal
```bash
# Web Profile
cd web_profile
flask db migrate -m "Pesan migrasi"
flask db upgrade

# SIAKAD
cd siakad_app
flask db migrate -m "Pesan migrasi"
flask db upgrade
```
*Jangan lupa commit folder `migrations` ke GitHub!*

### Langkah 2: Terapkan Migrasi di Server
Setelah update kode di server:
```bash
# Web Profile
cd /var/www/Albarokah-SIAKAD/web_profile
../web_profile/.venv/bin/flask db upgrade

# SIAKAD
cd /var/www/Albarokah-SIAKAD/siakad_app
../siakad_app/.venv/bin/flask db upgrade
```

---

## 5. Verifikasi Keamanan Server

### Cek User Aplikasi (Wajib www-data)
Pastikan aplikasi TIDAK berjalan sebagai root:
```bash
ps aux | grep gunicorn
```
*   **Aman:** Jika kolom user tertulis `www-data`.
*   **Bahaya:** Jika kolom user tertulis `root`.

### Cek Port yang Terbuka
Pastikan hanya port penting (22, 80, 443) yang terbuka untuk publik:
```bash
sudo ufw status verbose
sudo ss -tulpn
```

### Cek Log Error
Jika ada masalah, cek log berikut:
```bash
# Log Aplikasi
journalctl -u siakad -n 50
journalctl -u web_profile -n 50

# Log Nginx
tail -n 50 /var/log/nginx/error.log
```
