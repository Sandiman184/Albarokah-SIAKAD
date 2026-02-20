#!/bin/bash

# hard_reset_server.sh
# Script PAMUNGKAS untuk mereset total database dan folder uploads jika via web gagal.
# PERINGATAN: Semua data akan DIHAPUS.

echo "========================================="
echo "   ALBAROKAH HARD RESET SCRIPT"
echo "========================================="
echo "WARNING: This will DESTROY all data in databases and uploads folder."
read -p "Are you sure? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# 1. Stop Services to release DB locks
echo "[1] Stopping services..."
sudo systemctl stop web_profile
sudo systemctl stop siakad
sudo systemctl stop nginx

# 2. Drop and Recreate Databases
echo "[2] Resetting Databases..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS web_profile_db;"
sudo -u postgres psql -c "CREATE DATABASE web_profile_db OWNER albarokah_user;"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS siakad_db;"
sudo -u postgres psql -c "CREATE DATABASE siakad_db OWNER albarokah_user;"

# 3. Clear Uploads
echo "[3] Clearing Uploads..."
UPLOADS_DIR="/var/www/Albarokah-SIAKAD/web_profile/app/static/uploads"
if [ -d "$UPLOADS_DIR" ]; then
    sudo rm -rf "$UPLOADS_DIR"
    sudo mkdir -p "$UPLOADS_DIR"
    sudo chown -R www-data:www-data "$UPLOADS_DIR"
    sudo chmod -R 775 "$UPLOADS_DIR"
fi

# 4. Start Services
echo "[4] Starting services..."
sudo systemctl start web_profile
sudo systemctl start siakad
sudo systemctl start nginx

echo "========================================="
echo "HARD RESET COMPLETE"
echo "Sekarang lakukan 'Restore System' via Admin Panel dengan file backup .zip Anda."
echo "========================================="
