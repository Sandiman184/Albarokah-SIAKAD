#!/bin/bash

# Konfigurasi
PROJECT_DIR="/var/www/Albarokah-SIAKAD"
OLD_DIR="/root/Albarokah-SIAKAD"
USER="alnet"
GROUP="www-data"
DOMAIN_WEB="albarokahsidomakmur.ponpes.id"
DOMAIN_SIAKAD="siakad.albarokahsidomakmur.ponpes.id"

echo "=== Memulai Proses Deployment Otomatis ==="

# 1. Pindahkan Proyek jika belum ada di /var/www
if [ -d "$OLD_DIR" ] && [ ! -d "$PROJECT_DIR" ]; then
    echo "[1/7] Memindahkan proyek ke $PROJECT_DIR..."
    mv "$OLD_DIR" "$PROJECT_DIR"
elif [ -d "$PROJECT_DIR" ]; then
    echo "[1/7] Proyek sudah ada di $PROJECT_DIR. Melanjutkan..."
else
    echo "[ERROR] Direktori proyek tidak ditemukan di $OLD_DIR atau $PROJECT_DIR"
    exit 1
fi

# 2. Atur Hak Akses
echo "[2/7] Mengatur hak akses..."
chown -R $USER:$GROUP "$PROJECT_DIR"
chmod -R 775 "$PROJECT_DIR"

# 3. Install Dependencies System
echo "[3/7] Menginstall paket sistem..."
apt update
apt install -y python3-venv python3-pip python3-certbot-nginx nginx libpq-dev git

# 4. Setup Virtual Environments
echo "[4/7] Setup Python Virtual Environments..."

# Web Profile
echo "   -> Setup Web Profile..."
cd "$PROJECT_DIR/web_profile"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
deactivate

# SIAKAD
echo "   -> Setup SIAKAD..."
cd "$PROJECT_DIR/siakad_app"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
deactivate

# 5. Konfigurasi Nginx
echo "[5/7] Konfigurasi Nginx..."
rm -f /etc/nginx/sites-enabled/default
cp "$PROJECT_DIR/deployment/nginx/albarokah_domain.conf" /etc/nginx/sites-available/albarokah
ln -sf /etc/nginx/sites-available/albarokah /etc/nginx/sites-enabled/

nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx
    echo "   -> Nginx Restarted."
else
    echo "[ERROR] Konfigurasi Nginx tidak valid!"
    exit 1
fi

# 6. Konfigurasi Systemd
echo "[6/7] Konfigurasi Service Systemd..."
cp "$PROJECT_DIR/deployment/systemd/web_profile.service" /etc/systemd/system/
cp "$PROJECT_DIR/deployment/systemd/siakad.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable web_profile
systemctl enable siakad
systemctl restart web_profile
systemctl restart siakad

echo "   -> Service Aplikasi Restarted."

# 7. Informasi Certbot
echo "[7/7] Selesai! Langkah terakhir (SSL):"
echo "Silakan jalankan perintah ini secara manual untuk mengaktifkan HTTPS:"
echo "certbot --nginx -d $DOMAIN_WEB -d www.$DOMAIN_WEB -d $DOMAIN_SIAKAD"

echo "=== Deployment Selesai ==="
