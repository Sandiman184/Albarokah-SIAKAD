#!/bin/bash

# ==========================================
# SCRIPT SINKRONISASI KONTEN (FOTO & DATABASE)
# DARI LOKAL KE SERVER
# ==========================================
# Jalankan script ini di Terminal Lokal (Git Bash / WSL)
# Usage: ./sync_content.sh [SERVER_IP]
# Contoh: ./sync_content.sh 103.123.45.67
# ==========================================

SERVER_USER="root" # Ganti dengan user SSH Anda jika bukan root
SERVER_IP="$1"
PROJECT_DIR="/var/www/Albarokah-SIAKAD"

if [ -z "$SERVER_IP" ]; then
    echo "Usage: ./sync_content.sh [SERVER_IP]"
    echo "Contoh: ./sync_content.sh 103.193.123.45"
    exit 1
fi

echo "=== MEMULAI SINKRONISASI KONTEN KE $SERVER_IP ==="
echo "Pastikan Anda menjalankan ini dari root project di laptop/komputer lokal Anda."

# 1. Sync File Uploads (Foto/Dokumen)
echo -e "\n[1/2] Mengupload file foto (web_profile/app/static/uploads)..."
# Menggunakan rsync jika ada, atau scp
if command -v rsync &> /dev/null; then
    echo "Menggunakan rsync..."
    rsync -avz --progress web_profile/app/static/uploads/ $SERVER_USER@$SERVER_IP:$PROJECT_DIR/web_profile/app/static/uploads/
    
    # Fix permissions di server
    ssh $SERVER_USER@$SERVER_IP "chown -R www-data:www-data $PROJECT_DIR/web_profile/app/static/uploads/"
else
    echo "Rsync tidak ditemukan, menggunakan SCP (Mungkin lebih lambat)..."
    scp -r web_profile/app/static/uploads/* $SERVER_USER@$SERVER_IP:$PROJECT_DIR/web_profile/app/static/uploads/
fi

# 2. Sync Database (Opsional)
echo -e "\n[2/2] Apakah Anda ingin menimpa Database Server dengan Database Lokal?"
echo "PERINGATAN: Data di server akan HILANG dan diganti dengan data lokal Anda!"
read -p "Lanjutkan? (y/n): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Memproses database..."
    
    # Dump lokal
    echo " -> Exporting database lokal (web_profile_db)..."
    # Sesuaikan perintah pg_dump dengan environment Windows/Linux lokal Anda
    # Asumsi pg_dump ada di PATH
    pg_dump -U postgres -d web_profile_db -f web_profile_sync.sql
    pg_dump -U postgres -d siakad_db -f siakad_db_sync.sql
    
    # Upload SQL
    echo " -> Uploading SQL dumps..."
    scp web_profile_sync.sql siakad_db_sync.sql $SERVER_USER@$SERVER_IP:/tmp/
    
    # Restore di Server
    echo " -> Restoring di Server..."
    ssh $SERVER_USER@$SERVER_IP "
        # Restore Web Profile
        sudo -u postgres psql -d web_profile_db -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
        sudo -u postgres psql -d web_profile_db -c 'GRANT ALL ON SCHEMA public TO albarokah_user;'
        sudo -u postgres psql -d web_profile_db -f /tmp/web_profile_sync.sql
        
        # Restore SIAKAD
        sudo -u postgres psql -d siakad_db -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
        sudo -u postgres psql -d siakad_db -c 'GRANT ALL ON SCHEMA public TO albarokah_user;'
        sudo -u postgres psql -d siakad_db -f /tmp/siakad_db_sync.sql
        
        # Cleanup
        rm /tmp/web_profile_sync.sql /tmp/siakad_db_sync.sql
    "
    
    # Cleanup lokal
    rm web_profile_sync.sql siakad_db_sync.sql
    
    echo "Database berhasil disinkronisasi."
else
    echo "Skip sinkronisasi database."
fi

echo -e "\n=== SINKRONISASI SELESAI ==="
