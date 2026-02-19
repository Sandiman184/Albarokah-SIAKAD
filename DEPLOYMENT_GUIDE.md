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

### Langkah 2: Di Server (Jalankan Update)
Masuk ke server via SSH, lalu jalankan perintah berikut:
```bash
cd /var/www/Albarokah-SIAKAD
git pull origin main

# Jika ada library baru
source web_profile/.venv/bin/activate
pip install -r web_profile/requirements.txt

# Restart Aplikasi
sudo systemctl restart web_profile
sudo systemctl restart siakad
```

---

## 3. Workflow Sinkronisasi Konten (Foto & Database)
**PENTING:** Git TIDAK menyimpan foto upload atau isi database. Gunakan `scp` untuk transfer manual.

### A. Sinkronisasi Foto (Upload Folder)
Jalankan di Terminal Laptop (PowerShell/Git Bash):
```powershell
# Ganti IP_SERVER dengan IP VPS Anda (misal: 103.158.130.10)
# Port SSH default: 22 (atau 8022 sesuai konfigurasi Anda)
scp -r -P 8022 web_profile/app/static/uploads/* root@IP_SERVER:/var/www/Albarokah-SIAKAD/web_profile/app/static/uploads/
```
*Setelah upload, perbaiki permission di server:*
```bash
# Di Terminal Server
chown -R www-data:www-data /var/www/Albarokah-SIAKAD/web_profile/app/static/uploads/
```

### B. Sinkronisasi Database (Full Restore)
**PERINGATAN:** Ini akan MENGHAPUS data lama di server dan menggantinya dengan data lokal!

1.  **Backup Lokal (Laptop):**
    ```powershell
    pg_dump -U postgres -d web_profile_db -f web_profile_sync.sql
    ```
2.  **Upload ke Server (Laptop):**
    ```powershell
    scp -P 8022 web_profile_sync.sql root@IP_SERVER:/tmp/
    ```
3.  **Restore di Server (SSH):**
    ```bash
    # Masuk sebagai user postgres
    su - postgres
    
    # Reset Database
    psql -c "DROP DATABASE IF EXISTS web_profile_db;"
    psql -c "CREATE DATABASE web_profile_db;"
    
    # Import Data
    psql -d web_profile_db -f /tmp/web_profile_sync.sql
    
    # Berikan Akses ke User Aplikasi
    psql -d web_profile_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO albarokah_user;"
    psql -d web_profile_db -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO albarokah_user;"
    
    exit
    ```
4.  **Restart Aplikasi (SSH):**
    ```bash
    sudo systemctl restart web_profile
    ```

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

## 6. Sinkronisasi Fitur Baru (Google Sheets & Email)

Fitur baru (PPDB & Kontak) membutuhkan file kredensial yang tidak ada di GitHub. Anda wajib menguploadnya manual.

### A. Upload File Kredensial (Laptop)
Gunakan PowerShell atau Git Bash di laptop:

```powershell
# Upload Google Sheets Key
scp -P 8022 google-credentials.json root@IP_SERVER:/var/www/Albarokah-SIAKAD/

# Upload Config Email (.env)
# CATATAN: File .env di server sebaiknya diedit manual (nano) agar tidak tertimpa settingan database.
# Jika ingin upload full, gunakan:
scp -P 8022 web_profile/.env root@IP_SERVER:/var/www/Albarokah-SIAKAD/web_profile/
```

### B. Edit Manual Config Server (Rekomendasi)
Masuk ke SSH server, lalu edit file `.env`:
```bash
nano /var/www/Albarokah-SIAKAD/web_profile/.env
```
*Pastikan isinya:*
```env
DATABASE_URL=postgresql://albarokah_user:alnet%402026@localhost/web_profile_db
MAIL_USERNAME=email_anda@gmail.com
MAIL_PASSWORD=app_password_anda
```

### C. Restart Service (Wajib!)
Setelah file terupload/diedit, restart aplikasi:
```bash
sudo systemctl restart web_profile
```

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

## 7. Sinkronisasi Database & Konten (Foto)

Jika Anda menambah data (berita, foto) di lokal dan ingin memindahkannya ke server, gunakan script otomatis yang sudah disiapkan.

**PENTING:** Proses ini akan **MENGHAPUS** data lama di server dan menggantinya dengan data dari laptop Anda. Pastikan data di laptop adalah yang paling update.

### Cara Menggunakan Script `sync_content.sh`

1.  Buka terminal di laptop Anda (Git Bash atau PowerShell).
2.  Masuk ke folder proyek:
    ```bash
    cd /path/to/Albarokah
    ```
3.  Jalankan script dengan menyertakan IP Server:
    ```bash
    # Ganti IP_SERVER dengan IP VPS Anda
    bash sync_content.sh IP_SERVER
    
    # Contoh:
    bash sync_content.sh 103.158.130.10
    ```

### Apa yang dilakukan script ini?
1.  **Upload Foto:** Mengirim semua file di `web_profile/app/static/uploads` ke server.
2.  **Upload Kredensial:** Mengecek dan mengirim `google-credentials.json` serta `.env` jika ada perubahan.
3.  **Restore Database:** (Opsional, Anda akan ditanya "y/n") Mengambil backup database lokal (`web_profile_db`) dan merestore-nya ke server.

---

## Ringkasan Perintah Penting

| Aksi | Perintah (di Server) |
| :--- | :--- |
| **Update Kode** | `git pull origin main` |
| **Restart App** | `sudo systemctl restart web_profile` |
| **Cek Status** | `sudo systemctl status web_profile` |
| **Cek Error** | `sudo journalctl -u web_profile -f` |
