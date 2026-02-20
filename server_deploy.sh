#!/bin/bash

# server_deploy.sh
# Script untuk mempermudah update kode dan sinkronisasi di server (Linux/Ubuntu)

echo "========================================="
echo "   ALBAROKAH SYSTEM DEPLOYMENT SCRIPT"
echo "========================================="

# 1. Pull Latest Code
echo "[1] Pulling latest code from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed! Please check your git configuration."
    exit 1
fi

# 2. Update Dependencies (Optional)
echo "[2] Checking for dependency updates..."
# Check if virtualenv exists
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "⚠️  Virtual environment not found. Skipping pip install."
fi

# 3. Restart Services
echo "[3] Restarting application services..."
# Adjust service names as per your server configuration
sudo systemctl restart web_profile
sudo systemctl restart siakad

# 4. Final Status
echo "========================================="
echo "✅ Deployment Completed Successfully!"
echo "   - Code updated"
echo "   - Services restarted"
echo ""
echo "👉 To Sync Data (Database & Files):"
echo "   Use the Admin Panel > System > Backup & Restore menu."
echo "========================================="
