#!/bin/bash

# Script untuk memperbaiki konfigurasi database dan environment variables
# Menangani error: "password authentication failed for user postgres"
# Mengubah user database menjadi 'albarokah_user' dengan password 'alnet@2026'

# Variables
DB_USER="albarokah_user"
DB_PASS="alnet@2026"
# URL Encoded Password untuk connection string (ganti @ dengan %40)
DB_PASS_ENCODED="alnet%402026"
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
    
    # Cek apakah database ada, jika tidak buat baru
    DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB'")
    if [ "$DB_EXISTS" != "1" ]; then
        echo "Database $DB tidak ditemukan. Membuat database..."
        sudo -u postgres psql -c "CREATE DATABASE $DB OWNER $DB_USER;"
    else
        echo "Database $DB sudah ada."
        # Pastikan owner benar
        sudo -u postgres psql -c "ALTER DATABASE $DB OWNER TO $DB_USER;"
    fi
    
    # Grant connect & create
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB TO $DB_USER;"
    
    # Grant schema permissions (penting untuk akses tabel)
    # Kita harus connect ke database spesifik untuk grant schema permissions
    sudo -u postgres psql -d "$DB" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
    sudo -u postgres psql -d "$DB" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
    sudo -u postgres psql -d "$DB" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
    
    # Ensure future tables are accessible
    sudo -u postgres psql -d "$DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
    sudo -u postgres psql -d "$DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"
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
        # PENTING: Menggunakan DB_PASS_ENCODED karena ada karakter '@' di password
        # Karakter '@' di password akan dianggap sebagai pemisah user:pass@host jika tidak di-encode
        NEW_URL="postgresql://${DB_USER}:${DB_PASS_ENCODED}@127.0.0.1:5432/${db_name}"
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
        echo "  -> Updated DATABASE_URL ke $db_name (Password Encoded)"
    else
        echo -e "${RED}WARNING: File $env_file tidak ditemukan!${NC}"
    fi
}

# Update env untuk kedua aplikasi
update_env "web_profile" "$WEB_DB"
update_env "siakad_app" "$SIAKAD_DB"

echo -e "${GREEN}=== 3. Restart Services ===${NC}"
# Nama service disesuaikan dengan file systemd yang ada (web_profile.service dan siakad.service)
SERVICES=("web_profile" "siakad" "nginx")

for SERVICE in "${SERVICES[@]}"; do
    if systemctl list-units --full -all | grep -Fq "$SERVICE.service"; then
        echo "Restarting $SERVICE..."
        sudo systemctl restart $SERVICE
    else
        echo -e "${RED}Service $SERVICE tidak ditemukan!${NC}"
    fi
done

echo -e "${GREEN}=== Selesai! ===${NC}"
echo "Silakan cek log kembali jika masih error: sudo journalctl -u web_profile -f"
