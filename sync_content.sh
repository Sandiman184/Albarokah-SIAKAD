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

# Cek IP Server
if [ -z "$SERVER_IP" ]; then
    echo "Usage: ./sync_content.sh [SERVER_IP]"
    echo "Contoh: ./sync_content.sh 103.193.123.45"
    exit 1
fi

echo "=== MEMULAI SINKRONISASI KONTEN KE $SERVER_IP ==="
echo "Pastikan Anda menjalankan ini dari root project di laptop/komputer lokal Anda."

# ==========================================
# 1. Sync File Uploads (Foto/Dokumen)
# ==========================================
echo -e "\n[1/3] Mengupload file foto (web_profile/app/static/uploads)..."

# Pastikan folder lokal ada
if [ ! -d "web_profile/app/static/uploads" ]; then
    echo "Warning: Folder upload lokal tidak ditemukan!"
else
    # Menggunakan rsync jika ada, atau scp
    if command -v rsync &> /dev/null; then
        echo "Menggunakan rsync..."
        # Upload folder uploads ke server
        rsync -avz --progress web_profile/app/static/uploads/ $SERVER_USER@$SERVER_IP:$PROJECT_DIR/web_profile/app/static/uploads/
    else
        echo "Rsync tidak ditemukan, menggunakan SCP (Mungkin lebih lambat)..."
        scp -r web_profile/app/static/uploads/* $SERVER_USER@$SERVER_IP:$PROJECT_DIR/web_profile/app/static/uploads/
    fi
    
    # Fix permissions di server
    echo "Memperbaiki permission di server..."
    ssh $SERVER_USER@$SERVER_IP "chown -R www-data:www-data $PROJECT_DIR/web_profile/app/static/uploads/"
fi

# ==========================================
# 2. Sync Kredensial Baru (Google Sheets & Email)
# ==========================================
echo -e "\n[2/3] Mengecek file kredensial baru..."

if [ -f "google-credentials.json" ]; then
    echo "Mengupload google-credentials.json..."
    scp google-credentials.json $SERVER_USER@$SERVER_IP:$PROJECT_DIR/
fi

if [ -f "web_profile/.env" ]; then
    echo "Mengupload web_profile/.env..."
    scp web_profile/.env $SERVER_USER@$SERVER_IP:$PROJECT_DIR/web_profile/
fi


# ==========================================
# 3. Sync Database (Opsional & Berbahaya)
# ==========================================
echo -e "\n[3/3] Apakah Anda ingin menimpa Database Server dengan Database Lokal?"
echo "PERINGATAN: Data di server akan HILANG dan diganti dengan data lokal Anda!"
read -p "Lanjutkan? (y/n): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Memproses database..."
    
    # Dump lokal
    echo " -> Exporting database lokal (web_profile_db)..."
    
    # Cek pg_dump
    if ! command -v pg_dump &> /dev/null; then
        echo "Error: pg_dump tidak ditemukan di komputer lokal. Pastikan PostgreSQL terinstall."
        exit 1
    fi

    # Set password postgres lokal jika perlu (PGPASSWORD=...)
    # Dump Schema + Data
    pg_dump -U postgres -d web_profile_db -f web_profile_sync.sql
    
    # Upload SQL
    echo " -> Uploading SQL dumps..."
    scp web_profile_sync.sql $SERVER_USER@$SERVER_IP:/tmp/
    
    # Restore di Server
    echo " -> Restoring di Server..."
    ssh $SERVER_USER@$SERVER_IP "
        # Stop service sebentar agar tidak ada koneksi aktif
        sudo systemctl stop albarokah_web || true
        
        # Drop & Recreate Database (Cara paling bersih)
        # Asumsi user database di server adalah 'postgres' atau 'albarokah_user'
        
        echo 'Dropping existing database...'
        sudo -u postgres psql -c 'DROP DATABASE IF EXISTS web_profile_db;'
        sudo -u postgres psql -c 'CREATE DATABASE web_profile_db;'
        
        # Restore
        echo 'Importing new data...'
        sudo -u postgres psql -d web_profile_db -f /tmp/web_profile_sync.sql
        
        # Cleanup
        rm /tmp/web_profile_sync.sql
        
        # Start service kembali
        sudo systemctl start albarokah_web || true
    "
    
    # Cleanup lokal
    rm web_profile_sync.sql
    
    echo "Database berhasil disinkronisasi."
else
    echo "Skip sinkronisasi database."
fi

echo -e "\n=== SINKRONISASI SELESAI ==="
