#!/bin/bash

# Script Perbaikan Migrasi Database Albarokah
# Jalankan dengan: sudo ./fix_db_migration.sh

echo "=== MEMULAI PERBAIKAN MIGRASI DATABASE ==="

APP_ROOT="/var/www/Albarokah-SIAKAD"
USER_DB="albarokah_user"
PASS_DB="alnet%402026"
DB_SIAKAD="siakad_db"
DB_WEB="web_profile_db"

# Deteksi Venv
if [ -d "$APP_ROOT/.venv" ]; then
    VENV_ACTIVATE="$APP_ROOT/.venv/bin/activate"
    VENV_FLASK="$APP_ROOT/.venv/bin/flask"
elif [ -d "$APP_ROOT/siakad_app/.venv" ]; then
    VENV_ACTIVATE="$APP_ROOT/siakad_app/.venv/bin/activate"
    VENV_FLASK="$APP_ROOT/siakad_app/.venv/bin/flask"
else
    echo "ERROR: Virtual environment tidak ditemukan!"
    exit 1
fi

echo "Virtual Environment: $VENV_FLASK"

# 1. Perbaiki Web Profile (UndefinedTable)
# Masalah: Tabel belum ada tapi mungkin migrasi dianggap sudah jalan atau belum inisialisasi
echo "[1/2] Memperbaiki Web Profile Database..."
cd $APP_ROOT/web_profile
export FLASK_APP=run.py
export DATABASE_URL="postgresql://$USER_DB:$PASS_DB@localhost/$DB_WEB"

# Cek status migrasi saat ini
echo "   -> Cek status migrasi..."
$VENV_FLASK db current

# Paksa stamp head jika tabel alembic_version kosong tapi tabel lain ada,
# atau jalankan upgrade jika memang belum ada.
# Strategi aman: Coba upgrade dulu. Jika error, kita stamp head.
echo "   -> Mencoba upgrade..."
$VENV_FLASK db upgrade 2>/tmp/web_mig_err.log

if grep -q "UndefinedTable" /tmp/web_mig_err.log; then
    echo "   -> Terdeteksi UndefinedTable. Mencoba inisialisasi ulang..."
    # Hapus folder migrations dan init ulang (opsi drastis tapi efektif untuk fresh deploy)
    # TAPI JANGAN HAPUS DATA.
    # Lebih baik: Stamp head untuk menandai bahwa kita "sudah" di versi terbaru
    # lalu jalankan upgrade.
    $VENV_FLASK db stamp head
    $VENV_FLASK db upgrade
elif grep -q "DuplicateTable" /tmp/web_mig_err.log; then
    echo "   -> Terdeteksi DuplicateTable. Menandai migrasi sebagai selesai (stamp head)..."
    $VENV_FLASK db stamp head
fi

# 2. Perbaiki SIAKAD (DuplicateTable: audit_logs)
echo "[2/2] Memperbaiki SIAKAD Database..."
cd $APP_ROOT/siakad_app
export FLASK_APP=run.py
export DATABASE_URL="postgresql://$USER_DB:$PASS_DB@localhost/$DB_SIAKAD"

echo "   -> Mencoba upgrade..."
$VENV_FLASK db upgrade 2>/tmp/siakad_mig_err.log

if grep -q "DuplicateTable" /tmp/siakad_mig_err.log; then
    echo "   -> Terdeteksi DuplicateTable (audit_logs). Menandai migrasi sebagai selesai..."
    # Ini berarti database sudah punya tabelnya, tapi alembic belum tau.
    # Kita paksa alembic untuk loncat ke versi terbaru (head).
    $VENV_FLASK db stamp head
elif grep -q "already exists" /tmp/siakad_mig_err.log; then
    echo "   -> Terdeteksi obyek sudah ada. Menandai migrasi sebagai selesai..."
    $VENV_FLASK db stamp head
fi

# 3. Restart Service
echo "=== ME-RESTART SERVICE ==="
systemctl restart web_profile
systemctl restart siakad

echo "=== SELESAI. SILAKAN CEK WEBSITE ==="
