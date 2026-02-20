@echo off
echo =========================================
echo    ALBAROKAH LOCAL SYNC (WINDOWS)
echo =========================================

echo [1] Pulling latest code...
git pull origin main

echo [2] Updating dependencies...
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate

if exist siakad_app\requirements.txt pip install -r siakad_app\requirements.txt
if exist web_profile\requirements.txt pip install -r web_profile\requirements.txt

echo [3] Running migrations...
set FLASK_APP=siakad_app/run.py
flask db upgrade -d siakad_app/migrations

set FLASK_APP=web_profile/run.py
flask db upgrade -d web_profile/migrations

echo [4] Cleaning cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo =========================================
echo    SYNC COMPLETE!
echo    Please restart your local server terminals.
echo =========================================
pause
