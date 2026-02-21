# Panduan Sinkronisasi dan Deployment SIAKAD Al-Barokah

Dokumen ini menjelaskan langkah-langkah untuk menyinkronkan kode, database, dan konten statis (gambar/upload) dari lingkungan lokal (Localhost) ke Server Production.

**Path Server Production:** `/var/www/albarokah`
**Service Name:** `albarokah-siakad` & `albarokah-web`

## 1. Sinkronisasi Kode (Git)

Aplikasi ini menggunakan Git untuk manajemen versi.

### Di Komputer Lokal:
1.  Pastikan semua perubahan sudah di-commit:
    ```bash
    git add .
    git commit -m "Deskripsi perubahan Anda"
    ```
2.  Push ke repository GitHub:
    ```bash
    git push origin main
    ```

### Di Server Production:
1.  Masuk ke folder aplikasi di server:
    ```bash
    cd /var/www/albarokah
    ```
2.  Pull perubahan terbaru:
    ```bash
    git pull origin main
    ```
3.  Jika ada perubahan pada `requirements.txt`, install dependensi baru:
    ```bash
    source venv/bin/activate
    pip install -r requirements.txt
    ```

---

## 2. Sinkronisasi Database

Karena database di server mungkin sudah berisi data riil, **JANGAN** menimpa database server dengan database lokal secara langsung.

### A. Jika ada perubahan Struktur Database (Schema Migration):
Gunakan Flask-Migrate untuk menerapkan perubahan struktur tabel.

**Di Server Production:**
```bash
# Masuk ke folder aplikasi
cd siakad_app
export FLASK_APP=run.py
flask db upgrade

# Jika ada perubahan di Web Profile
cd ../web_profile
export FLASK_APP=run.py
flask db upgrade
```

### B. Jika ingin menyalin Data Dummy ke Server (Hanya untuk Dev/Testing):
```bash
# Di Server (folder siakad_app)
python seed_siakad_full.py
```

---

## 3. Sinkronisasi Konten Statis (Uploads)

File gambar tersimpan di folder `static/uploads` dan `static/img`. Folder ini tidak ikut di-push ke Git.

### Cara Menyalin File Upload (Lokal ke Server):
Gunakan `SCP` (Secure Copy) dari terminal lokal Anda.

**Contoh:**
```bash
# Menyalin file gambar tertentu (misal background baru)
scp d:\Project\Albarokah\Albarokah\siakad_app\app\static\img\hero-bg.jpg user@ip-server:/var/www/albarokah/siakad_app/app/static/img/

# Menyalin satu folder upload
scp -r d:\Project\Albarokah\Albarokah\siakad_app\app\static\uploads\bukti_bayar user@ip-server:/var/www/albarokah/siakad_app/app/static/uploads/
```

---

## 4. Restart Aplikasi

Setelah melakukan perubahan kode atau update database, restart service aplikasi di server.

**Perintah Restart:**
```bash
sudo systemctl restart albarokah-siakad
sudo systemctl restart albarokah-web
```

**Cek Status:**
```bash
sudo systemctl status albarokah-siakad
```
