#!/bin/bash

# Script Perbaikan Otomatis Albarokah Server
# Jalankan script ini dengan sudo: sudo ./fix_server_full.sh

echo "=== MEMULAI PERBAIKAN SERVER ==="

# 1. Konfigurasi Variable
APP_ROOT="/var/www/Albarokah-SIAKAD"
USER_DB="albarokah_user"
PASS_DB="alnet%402026" # URL Encoded dari alnet@2026
DB_SIAKAD="siakad_db"
DB_WEB="web_profile_db"

# 2. Update .env Web Profile
echo "[1/6] Mengupdate konfigurasi Web Profile..."
cat > $APP_ROOT/web_profile/.env <<EOL
SECRET_KEY=rahasia_web_profile_123
DATABASE_URL=postgresql://$USER_DB:$PASS_DB@localhost/$DB_WEB
FLASK_APP=run.py
FLASK_DEBUG=0
EOL

# 3. Update .env SIAKAD
echo "[2/6] Mengupdate konfigurasi SIAKAD..."
cat > $APP_ROOT/siakad_app/.env <<EOL
SECRET_KEY=rahasia_banget_loh_ini_jangan_disebar
DATABASE_URL=postgresql://$USER_DB:$PASS_DB@localhost/$DB_SIAKAD
FLASK_APP=run.py
FLASK_DEBUG=0
EOL

# 4. Fix Permission
echo "[3/6] Memperbaiki permission file..."
chown -R www-data:www-data $APP_ROOT
chmod -R 775 $APP_ROOT
# Pastikan user saat ini juga bisa akses (misal ubuntu/root)
usermod -a -G www-data $USER

# 5. Jalankan Migrasi Database
echo "[4/6] Menjalankan migrasi database..."

# Cek lokasi venv yang benar
if [ -d "$APP_ROOT/.venv" ]; then
    VENV_PYTHON="$APP_ROOT/.venv/bin/python"
    VENV_FLASK="$APP_ROOT/.venv/bin/flask"
elif [ -d "$APP_ROOT/siakad_app/.venv" ]; then
    VENV_PYTHON="$APP_ROOT/siakad_app/.venv/bin/python"
    VENV_FLASK="$APP_ROOT/siakad_app/.venv/bin/flask"
else
    echo "ERROR: Virtual environment tidak ditemukan!"
    exit 1
fi

echo "   -> Migrasi Web Profile..."
cd $APP_ROOT/web_profile
export FLASK_APP=run.py
$VENV_FLASK db upgrade

echo "   -> Migrasi SIAKAD..."
cd $APP_ROOT/siakad_app
export FLASK_APP=run.py
$VENV_FLASK db upgrade

# 6. Restart Service
echo "[5/6] Merestart service..."
systemctl restart web_profile
systemctl restart siakad
systemctl restart nginx

# 7. Cek Status dan Logs
echo "[6/6] Pengecekan status..."
sleep 3

STATUS_WEB=$(systemctl is-active web_profile)
STATUS_SIAKAD=$(systemctl is-active siakad)

echo "Status Web Profile: $STATUS_WEB"
echo "Status SIAKAD: $STATUS_SIAKAD"

if [ "$STATUS_WEB" != "active" ]; then
    echo "!!! ERROR PADA WEB PROFILE !!!"
    journalctl -u web_profile -n 20 --no-pager
fi

if [ "$STATUS_SIAKAD" != "active" ]; then
    echo "!!! ERROR PADA SIAKAD !!!"
    journalctl -u siakad -n 20 --no-pager
fi

echo "=== SELESAI ==="
