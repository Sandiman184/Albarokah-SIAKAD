@echo off
setlocal

echo [SETUP] Memulai konfigurasi database lokal...

:: 1. Cek apakah PostgreSQL terinstall
where psql >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PostgreSQL tidak ditemukan di PATH. Pastikan sudah terinstall.
    echo [INFO] Jika Anda ingin menggunakan SQLite, edit file .env dan nonaktifkan DATABASE_URL.
    goto :EOF
)

:: 2. Konfigurasi Kredensial (Sesuaikan jika berbeda)
set PG_USER=postgres
set PG_PASS=Sandiman184
set APP_USER=albarokah_user
set APP_PASS=alnet@2026
set DB_SIAKAD=siakad_db
set DB_WEB=web_profile_db

echo [SETUP] Membuat User dan Database di PostgreSQL...
set PGPASSWORD=%PG_PASS%

:: Buat User (Abaikan error jika sudah ada)
psql -U %PG_USER% -c "CREATE USER %APP_USER% WITH PASSWORD '%APP_PASS%'; ALTER USER %APP_USER% WITH SUPERUSER;" 2>nul

:: Buat Database
psql -U %PG_USER% -c "CREATE DATABASE %DB_SIAKAD% OWNER %APP_USER%;" 2>nul
psql -U %PG_USER% -c "CREATE DATABASE %DB_WEB% OWNER %APP_USER%;" 2>nul

echo [SETUP] Database berhasil disiapkan.

:: 3. Jalankan Migrasi & Seeding untuk Web Profile
echo [SETUP] Migrasi Web Profile...
cd web_profile
if not exist .env copy ..\.env.example .env
set FLASK_APP=run.py
flask db upgrade
echo [SETUP] Seeding Data Web Profile...
python seed.py
cd ..

:: 4. Jalankan Migrasi untuk SIAKAD
echo [SETUP] Migrasi SIAKAD...
cd siakad_app
if not exist .env copy ..\.env.example .env
set FLASK_APP=run.py
flask db upgrade
cd ..

echo [SUCCESS] Setup selesai! Aplikasi siap dijalankan.
pause
