#!/bin/bash

# setup_fail2ban.sh
# Script otomatis untuk mengamankan server dengan Fail2Ban
# Melindungi SSH (Port 8022) dan Nginx (Port 80, 8080, 8001)

# Pastikan dijalankan sebagai root
if [ "$EUID" -ne 0 ]; then 
  echo "Mohon jalankan script ini sebagai root (sudo ./setup_fail2ban.sh)"
  exit
fi

echo "========================================="
echo "   ALBAROKAH FAIL2BAN SETUP"
echo "========================================="

# 1. Install Fail2Ban
echo "[1] Menginstall Fail2Ban..."
apt-get update
apt-get install -y fail2ban

# 2. Backup config default
if [ ! -f /etc/fail2ban/jail.conf.bak ]; then
    cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.conf.bak
    echo "Backup jail.conf dibuat."
fi

# 3. Buat konfigurasi jail.local
echo "[2] Membuat konfigurasi Jail (jail.local)..."
# Kita gunakan konfigurasi agresif untuk bot
cat > /etc/fail2ban/jail.local <<EOL
[DEFAULT]
# Ban IP selama 1 jam (3600 detik)
bantime = 3600

# Jika mencoba login X kali dalam 10 menit (600 detik)
findtime = 600

# Jumlah percobaan gagal sebelum ban
maxretry = 5

# Whitelist IP Localhost (PENTING!)
ignoreip = 127.0.0.1/8 ::1 103.158.130.10

# Backend systemd (Cocok untuk Ubuntu 20.04+)
backend = systemd

# --- SSH PROTECTION ---
[sshd]
enabled = true
port = ssh,8022
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400  # Ban 24 jam untuk SSH brute force

# --- NGINX PROTECTION ---
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https,8080,8001
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https,8080,8001
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400 # Ban bot scanner 24 jam

[nginx-badbots]
enabled  = true
port     = http,https,8080,8001
filter   = nginx-badbots
logpath  = /var/log/nginx/access.log
maxretry = 2
EOL

# 4. Tambahkan filter nginx-badbots (Custom Filter)
if [ ! -f /etc/fail2ban/filter.d/nginx-badbots.conf ]; then
    echo "[3] Menambahkan filter custom..."
    cat > /etc/fail2ban/filter.d/nginx-badbots.conf <<EOL
[Definition]
failregex = ^<HOST> -.*"(GET|POST|HEAD).*HTTP.*"(?:%(badbots)s|%(badbots)s)
ignoreregex =
EOL
fi

# 5. Restart Service
echo "[4] Restarting Fail2Ban Service..."
# Hapus file socket lama jika ada (kadang menyebabkan error startup)
rm -f /var/run/fail2ban/fail2ban.sock

systemctl restart fail2ban
systemctl enable fail2ban

# Tunggu sebentar agar service benar-benar up
echo "Menunggu Fail2Ban startup (5 detik)..."
sleep 5

# 6. Verifikasi
echo "========================================="
echo "   STATUS FAIL2BAN"
echo "========================================="
fail2ban-client status
echo "-----------------------------------------"
echo "Status SSH Jail:"
fail2ban-client status sshd
echo "-----------------------------------------"
echo "Status Nginx Botsearch Jail:"
fail2ban-client status nginx-botsearch
echo "========================================="
echo "✅ Setup Selesai! Server Anda sekarang lebih aman."
echo "   Log aktivitas ada di: /var/log/fail2ban.log"
