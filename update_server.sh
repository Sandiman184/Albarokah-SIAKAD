#!/bin/bash

# ==========================================
# SCRIPT UPDATE OTOMATIS ALBAROKAH SERVER
# ==========================================
# Cara Penggunaan di Server:
# 1. Pastikan script ini ada di folder project: /var/www/Albarokah-SIAKAD/
# 2. Beri izin eksekusi: chmod +x update_server.sh
# 3. Jalankan: ./update_server.sh
# ==========================================

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MEMULAI PROSES UPDATE SERVER ===${NC}"
date

# 1. Pindah ke direktori project
cd /var/www/Albarokah-SIAKAD || { echo "Direktori tidak ditemukan!"; exit 1; }

# 2. Ambil kode terbaru dari GitHub
echo -e "\n${YELLOW}[1/4] Mengambil kode terbaru dari GitHub...${NC}"
git reset --hard
git pull origin main

# 3. Update Dependencies (Python Libraries)
echo -e "\n${YELLOW}[2/4] Memeriksa dan update library Python...${NC}"

echo " -> Update Web Profile..."
source web_profile/.venv/bin/activate
pip install -r web_profile/requirements.txt
deactivate

echo " -> Update SIAKAD..."
source siakad_app/.venv/bin/activate
pip install -r siakad_app/requirements.txt
deactivate

# 4. Migrasi Database (Opsional - Uncomment jika yakin)
# echo -e "\n${YELLOW}[Opsional] Menjalankan migrasi database...${NC}"
# ./web_profile/.venv/bin/flask --app web_profile/run.py db upgrade
# ./siakad_app/.venv/bin/flask --app siakad_app/run.py db upgrade

# 5. Restart Service
echo -e "\n${YELLOW}[3/4] Merestart service aplikasi...${NC}"
sudo systemctl restart web_profile
sudo systemctl restart siakad

echo -e "\n${YELLOW}[4/4] Cek status service...${NC}"
if systemctl is-active --quiet web_profile && systemctl is-active --quiet siakad; then
    echo -e "${GREEN}SUCCESS: Semua service berjalan normal!${NC}"
else
    echo -e "${RED}WARNING: Ada service yang gagal restart. Cek dengan 'sudo systemctl status web_profile siakad'${NC}"
fi

echo -e "\n${GREEN}=== UPDATE SELESAI ===${NC}"
