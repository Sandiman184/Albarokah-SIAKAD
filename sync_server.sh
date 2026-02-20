#!/bin/bash

# sync_server.sh
# Script untuk MEMAKSA sinkronisasi total server dengan GitHub
# Menangani: Code, Static Files, Permissions, dan Restart Service

echo "========================================="
echo "   ALBAROKAH FORCE SYNC SCRIPT"
echo "========================================="

# 1. Force Git Pull (Reset local changes if any)
echo "[1] Fetching latest code..."
git fetch origin
git reset --hard origin/main
git clean -fd

# 2. Update Permissions (Crucial for static files)
echo "[2] Fixing permissions..."
# Ensure www-data (Nginx/Gunicorn user) owns the files
sudo chown -R www-data:www-data /var/www/Albarokah-SIAKAD
sudo chmod -R 755 /var/www/Albarokah-SIAKAD
# Khusus folder uploads butuh write access
sudo chmod -R 775 /var/www/Albarokah-SIAKAD/web_profile/app/static/uploads

# 3. Clear Python Cache (Bytecode)
echo "[3] Clearing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 4. Install/Update Dependencies
echo "[4] Updating dependencies..."
# Check for venv
if [ ! -d ".venv" ]; then
    echo "Creating .venv..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install requirements from both apps
if [ -f "siakad_app/requirements.txt" ]; then
    echo "Installing siakad_app dependencies..."
    pip install -r siakad_app/requirements.txt
fi
if [ -f "web_profile/requirements.txt" ]; then
    echo "Installing web_profile dependencies..."
    pip install -r web_profile/requirements.txt
fi

# 5. Database Migrations
echo "[5] Running database migrations..."
# SIAKAD
if [ -d "siakad_app/migrations" ]; then
    echo "Migrating SIAKAD..."
    export FLASK_APP=siakad_app/run.py
    flask db upgrade -d siakad_app/migrations
fi
# Web Profile
if [ -d "web_profile/migrations" ]; then
    echo "Migrating Web Profile..."
    export FLASK_APP=web_profile/run.py
    flask db upgrade -d web_profile/migrations
fi

# 6. Restart All Services
echo "[6] Restarting services..."
sudo systemctl restart web_profile
sudo systemctl restart siakad
sudo systemctl restart nginx

echo "========================================="
echo "✅ SYNC COMPLETE!"
echo "   Code, Assets, and Services have been refreshed."
echo "   Please clear your browser cache (Ctrl+F5) and check again."
echo "========================================="
