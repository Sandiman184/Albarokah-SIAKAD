# Panduan Deployment dan Sinkronisasi SIAKAD Al-Barokah

Dokumen ini berisi panduan teknis lengkap untuk melakukan sinkronisasi kode, database, dan konten antara environment lokal (Development) dan server production.

**Path Server Production:** `/var/www/albarokah`
**User System:** `albarokah` (atau user deployment yang relevan)
**Service Name:** `albarokah-siakad` & `albarokah-web`

---

## 1. Persiapan Awal

Pastikan Anda memiliki akses SSH ke server dan sudah setup remote git.

```bash
# Cek remote repository
git remote -v
# Output harus mengarah ke repo GitHub project
# origin  https://github.com/username/albarokah.git (fetch)
# origin  https://github.com/username/albarokah.git (push)
```

---

## 2. Sinkronisasi Kode (Git)

Lakukan ini setiap kali ada perubahan fitur atau perbaikan bug.

### Di Lokal (Developer PC):
```bash
# 1. Pastikan branch main clean
git status

# 2. Add dan Commit perubahan
git add .
git commit -m "Deskripsi update: Fix footer, add finance module, etc"

# 3. Push ke GitHub
git push origin main
```

### Di Server Production (SSH):
```bash
# 1. Login ke server
ssh user@ip-server

# 2. Masuk ke direktori project
cd /var/www/albarokah

# 3. Pull perubahan terbaru
git pull origin main

# 4. (Opsional) Jika ada perubahan dependencies python
source venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Sinkronisasi Database (Schema Migration)

**PENTING:** Jangan pernah menimpa file database SQLite (`app.db`) di server jika menggunakan SQLite, atau men-drop tabel PostgreSQL sembarangan. Gunakan **Migration**.

### Kasus A: Ada Perubahan Struktur Tabel (Misal: Tambah Kolom/Tabel Baru)

Setelah `git pull` di server, jalankan perintah berikut:

```bash
# Di Server (/var/www/albarokah)
source venv/bin/activate

# Masuk ke folder aplikasi SIAKAD
cd siakad_app
export FLASK_APP=run.py

# Jalankan migrasi
flask db upgrade

# Masuk ke folder Web Profile (jika ada perubahan di sana)
cd ../web_profile
export FLASK_APP=run.py
flask db upgrade
```

### Kasus B: Reset Data / Seeding Ulang (HATI-HATI: MENGHAPUS DATA LAMA)
Hanya lakukan ini jika Anda yakin ingin me-reset data server dengan data dummy baru.

```bash
# Di Server (siakad_app)
python seed_siakad_full.py
```

---

## 4. Sinkronisasi Konten Statis (Uploads)

Folder `static/uploads` biasanya di-ignore oleh Git agar tidak memenuhi repo dan menjaga privasi data user. Anda perlu menyinkronkannya secara manual jika ada file baru dari lokal yang harus ada di server (misal: gambar default baru).

### Mengirim File dari Lokal ke Server (SCP):

```bash
# Contoh: Mengirim logo baru atau gambar aset
# Jalankan dari terminal lokal (Git Bash / PowerShell)

# Path Lokal: d:\Project\Albarokah\Albarokah\siakad_app\app\static\img\
# Path Server: /var/www/albarokah/siakad_app/app/static/img/

scp d:\Project\Albarokah\Albarokah\siakad_app\app\static\img\hero-bg.jpg user@ip-server:/var/www/albarokah/siakad_app/app/static/img/
```

### Mengambil Data Upload User dari Server ke Lokal (Backup):

```bash
# Jalankan dari terminal lokal
scp -r user@ip-server:/var/www/albarokah/siakad_app/app/static/uploads d:\Project\Albarokah\backup_uploads\
```

---

## 5. Restart Service Aplikasi

Setiap kali ada perubahan kode Python (`.py`) atau template HTML, Gunicorn harus di-restart agar perubahan efektif.

```bash
# Di Server
sudo systemctl restart albarokah-siakad
sudo systemctl restart albarokah-web

# Cek status untuk memastikan tidak ada error
sudo systemctl status albarokah-siakad
```

---

## 6. Troubleshooting Umum

### Permission Error (Permission denied)
Jika terjadi error saat upload file atau `git pull` karena masalah permission:

```bash
# Di Server
# Ubah owner folder ke user saat ini (misal: www-data atau albarokah)
sudo chown -R www-data:www-data /var/www/albarokah
sudo chmod -R 775 /var/www/albarokah
```

### Error 500 Internal Server Error
Cek logs aplikasi untuk detail error:

```bash
# Cek log Gunicorn/Service
journalctl -u albarokah-siakad -f

# Atau cek log Nginx
tail -f /var/log/nginx/error.log
```

---

## Ringkasan Perintah Deployment (Cheat Sheet)

```bash
cd /var/www/albarokah
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd siakad_app && flask db upgrade
cd ../web_profile && flask db upgrade
sudo systemctl restart albarokah-siakad albarokah-web
```
