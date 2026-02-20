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
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "⚠️  No .venv found, skipping pip install"
fi

# 5. Restart All Services
echo "[5] Restarting services..."
sudo systemctl restart web_profile
sudo systemctl restart siakad
sudo systemctl restart nginx

echo "========================================="
echo "✅ SYNC COMPLETE!"
echo "   Code, Assets, and Services have been refreshed."
echo "   Please clear your browser cache (Ctrl+F5) and check again."
echo "========================================="
