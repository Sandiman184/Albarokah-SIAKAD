#!/bin/bash

# Script untuk memverifikasi status deployment Albarokah
# Jalankan script ini di server untuk melihat status layanan dan error log

echo "==========================================="
echo "   ALBAROKAH DEPLOYMENT DIAGNOSTIC TOOL    "
echo "==========================================="
echo "Date: $(date)"
echo "Hostname: $(hostname)"

echo -e "\n[1] Memeriksa Direktori Proyek..."
if [ -d "/var/www/Albarokah-SIAKAD" ]; then 
    echo "✅ OK: Direktori /var/www/Albarokah-SIAKAD ditemukan."
    ls -ld /var/www/Albarokah-SIAKAD
else 
    echo "❌ ERROR: Direktori /var/www/Albarokah-SIAKAD TIDAK ditemukan!"
fi

echo -e "\n[2] Memeriksa Status Layanan Systemd..."
SERVICES=("nginx" "web_profile" "siakad")
for SERVICE in "${SERVICES[@]}"; do
    STATUS=$(systemctl is-active $SERVICE)
    if [ "$STATUS" == "active" ]; then
        echo "✅ OK: Service $SERVICE aktif."
    else
        echo "❌ ERROR: Service $SERVICE TIDAK aktif (Status: $STATUS)."
    fi
done

echo -e "\n[3] Memeriksa Koneksi Internal (Gunicorn)..."
# Cek Web Profile Port 8001
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001)
if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ]; then
    echo "✅ OK: Web Profile merespons di port 8001 (HTTP $HTTP_CODE)."
else
    echo "❌ ERROR: Web Profile TIDAK merespons di port 8001 (HTTP $HTTP_CODE)."
fi

# Cek SIAKAD Port 8000
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000)
if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ]; then
    echo "✅ OK: SIAKAD merespons di port 8000 (HTTP $HTTP_CODE)."
else
    echo "❌ ERROR: SIAKAD TIDAK merespons di port 8000 (HTTP $HTTP_CODE)."
fi

echo -e "\n[4] Memeriksa Konfigurasi Nginx..."
sudo nginx -t

echo -e "\n[5] Log Error Terakhir (Web Profile)..."
if [ -f "/var/log/nginx/albarokah_web_error.log" ]; then
    echo "--- 5 Baris Terakhir ---"
    tail -n 5 /var/log/nginx/albarokah_web_error.log
else
    echo "⚠️ Info: File log /var/log/nginx/albarokah_web_error.log belum ada."
fi

echo -e "\n[6] Log Error Terakhir (SIAKAD)..."
if [ -f "/var/log/nginx/albarokah_siakad_error.log" ]; then
    echo "--- 5 Baris Terakhir ---"
    tail -n 5 /var/log/nginx/albarokah_siakad_error.log
else
    echo "⚠️ Info: File log /var/log/nginx/albarokah_siakad_error.log belum ada."
fi

echo -e "\n==========================================="
echo "DIAGNOSA SELESAI"
echo "Silakan copy hasil output ini jika Anda membutuhkan bantuan lebih lanjut."
echo "==========================================="
