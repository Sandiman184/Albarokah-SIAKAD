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

# 2.1 Copy Nginx Configuration (Ensure 100MB limit is applied)
echo "[2.1] Updating Nginx configuration..."
sudo cp deployment/nginx/albarokah.conf /etc/nginx/sites-available/albarokah.conf
# Ensure symlink exists
if [ ! -L /etc/nginx/sites-enabled/albarokah.conf ]; then
    sudo ln -s /etc/nginx/sites-available/albarokah.conf /etc/nginx/sites-enabled/
fi
# Remove default nginx site if exists to avoid conflicts
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi
# Test Nginx config
sudo nginx -t

# 2.5. Generate Production .env Files (Prevent local env override)
echo "[2.5] Generating production .env files..."
# Generate stable secret key based on machine ID or fallback to fixed production key
# Using fixed key for production stability to prevent session invalidation on re-deploy
PROD_SECRET_KEY="prod-secret-key-albarokah-2026-fixed"

# SIAKAD .env
cat <<EOF > siakad_app/.env
SECRET_KEY=${PROD_SECRET_KEY}
DATABASE_URL=postgresql://albarokah_user:alnet%402026@localhost/siakad_db
FLASK_APP=run.py
FLASK_DEBUG=0
EOF

# Web Profile .env
cat <<EOF > web_profile/.env
SECRET_KEY=${PROD_SECRET_KEY}
DATABASE_URL=postgresql://albarokah_user:alnet%402026@localhost/web_profile_db
FLASK_APP=run.py
FLASK_DEBUG=0

# Email Configuration (SMTP)
MAIL_USERNAME=beritamasuk2020@gmail.com
MAIL_PASSWORD=recm kbxv zcab lreq
MAIL_DEFAULT_SENDER=beritamasuk2020@gmail.com
EOF

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
# Reload daemon to pick up systemd changes (timeout increase)
sudo systemctl daemon-reload
sudo systemctl restart web_profile
sudo systemctl restart siakad
sudo systemctl restart nginx

# Give services some time to start up
echo "Waiting 5 seconds for services to initialize..."
sleep 5

# 7. Verification
echo "[7] Verifying deployment..."
# Web Profile runs on port 8001 (based on systemd service)
# SIAKAD runs on port 8000 (based on nginx conf)

echo "Checking Web Profile on port 8001..."
WEB_HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001)
if [ "$WEB_HTTP_CODE" -eq 200 ] || [ "$WEB_HTTP_CODE" -eq 302 ]; then
    echo "✅ Web Profile is UP (Port 8001) - HTTP $WEB_HTTP_CODE"
else
    echo "❌ Web Profile might be DOWN (Port 8001) - HTTP $WEB_HTTP_CODE"
    echo "   Diagnostic info:"
    sudo systemctl status web_profile --no-pager | head -n 20
    echo "   Recent logs:"
    sudo journalctl -u web_profile --no-pager -n 20
fi

echo "Checking SIAKAD on port 8000..."
SIAKAD_HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000)
if [ "$SIAKAD_HTTP_CODE" -eq 200 ] || [ "$SIAKAD_HTTP_CODE" -eq 302 ]; then
    echo "✅ SIAKAD is UP (Port 8000) - HTTP $SIAKAD_HTTP_CODE"
else
    echo "❌ SIAKAD might be DOWN (Port 8000) - HTTP $SIAKAD_HTTP_CODE"
    echo "   Diagnostic info:"
    sudo systemctl status siakad --no-pager | head -n 20
    echo "   Recent logs:"
    sudo journalctl -u siakad --no-pager -n 20
fi

echo "========================================="
echo "✅ SYNC COMPLETE!"
echo "   Code, Assets, and Services have been refreshed."
echo "   Please clear your browser cache (Ctrl+F5) and check again."
echo "========================================="
