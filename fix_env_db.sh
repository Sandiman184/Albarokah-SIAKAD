#!/bin/bash

# Script untuk memperbaiki konfigurasi database dan environment variables
# Menangani error: "password authentication failed for user postgres"
# Mengubah user database menjadi 'albarokah_user' dengan password 'alnet@2026'

# Variables
DB_USER="albarokah_user"
DB_PASS="alnet@2026"
WEB_DB="web_profile_db"
SIAKAD_DB="siakad_db"
BASE_DIR="/var/www/Albarokah-SIAKAD"

# Warna untuk output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 1. Memastikan User Database & Permissions ===${NC}"

# Create user if not exists and set password
echo "Mengkonfigurasi user PostgreSQL: $DB_USER"
sudo -u postgres psql -c "DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASS';
    ELSE
        ALTER ROLE $DB_USER WITH PASSWORD '$DB_PASS';
    END IF;
END
\$\$;"

# Grant privileges (Looping untuk kedua database)
for DB in "$WEB_DB" "$SIAKAD_DB"; do
    echo "Mengatur permissions untuk database: $DB"
    
    # Pastikan database ada (opsional, tapi bagus untuk safety)
    sudo -u postgres psql -c "SELECT 'CREATE DATABASE $DB' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB')\gexec"
    
    # Grant connect & create
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB TO $DB_USER;"
    
    # Grant schema permissions (penting untuk akses tabel)
    sudo -u postgres psql -d "$DB" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    sudo -u postgres psql -d "$DB" -c "GRANT ALL TABLES IN SCHEMA public TO $DB_USER;"
    sudo -u postgres psql -d "$DB" -c "GRANT ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
    
    # Ensure future tables are accessible
    sudo -u postgres psql -d "$DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
done

echo -e "${GREEN}=== 2. Update File .env ===${NC}"

update_env() {
    local app_dir=$1
    local db_name=$2
    local env_file="$BASE_DIR/$app_dir/.env"

    if [ -f "$env_file" ]; then
        echo "Memperbarui $env_file..."
        # Backup file asli
        cp "$env_file" "$env_file.bak.$(date +%s)"
        
        # Construct new DATABASE_URL
        NEW_URL="postgresql://${DB_USER}:${DB_PASS}@localhost/${db_name}"
        # Escape slashes for sed command
        ESCAPED_URL=$(echo "$NEW_URL" | sed 's/\//\\\//g')
        
        # Cek apakah DATABASE_URL sudah ada
        if grep -q "^DATABASE_URL=" "$env_file"; then
            # Replace baris yang ada
            sed -i "s/^DATABASE_URL=.*/DATABASE_URL=${ESCAPED_URL}/" "$env_file"
        else
            # Append jika belum ada
            echo "" >> "$env_file"
            echo "DATABASE_URL=${NEW_URL}" >> "$env_file"
        fi
        echo "  -> Updated DATABASE_URL ke $db_name"
    else
        echo -e "${RED}WARNING: File $env_file tidak ditemukan!${NC}"
    fi
}

# Update env untuk kedua aplikasi
update_env "web_profile" "$WEB_DB"
update_env "siakad_app" "$SIAKAD_DB"

echo -e "${GREEN}=== 3. Restart Services ===${NC}"
echo "Restarting Gunicorn services..."
sudo systemctl restart albarokah-web
sudo systemctl restart albarokah-siakad

echo "Restarting Nginx..."
sudo systemctl restart nginx

echo -e "${GREEN}=== Selesai! ===${NC}"
echo "Silakan cek log kembali jika masih error: sudo journalctl -u albarokah-web -f"
