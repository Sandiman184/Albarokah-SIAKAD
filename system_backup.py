import os
import sys

# Ensure web_profile is importable
sys.path.append(os.path.join(os.getcwd(), 'web_profile'))

from app import create_app
from app.services.backup_service import BackupService

def create_full_backup():
    app = create_app()
    with app.app_context():
        print("Starting system backup via Service Layer...")
        try:
            # BackupService defaults to creating 'backups' folder in project root
            zip_path = BackupService.create_system_snapshot()
            print(f"✅ Backup created successfully: {zip_path}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")

if __name__ == '__main__':
    create_full_backup()
