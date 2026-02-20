import os
import sys

# Ensure web_profile is importable
sys.path.append(os.path.join(os.getcwd(), 'web_profile'))

from app import create_app
from app.services.backup_service import BackupService

def restore_full_backup(backup_zip_path):
    if not os.path.exists(backup_zip_path):
        print(f"❌ Error: Backup file not found: {backup_zip_path}")
        return

    print("⚠️  WARNING: This will OVERWRITE your current databases (Web Profile & SIAKAD) and uploads.")
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Restore cancelled.")
        return

    app = create_app()
    with app.app_context():
        print("Starting system restore via Service Layer...")
        try:
            BackupService.restore_system_snapshot(backup_zip_path)
            print("✅ Restore completed successfully.")
            print("🔄 Please restart your web server.")
        except Exception as e:
            print(f"❌ Restore failed: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        backup_path = sys.argv[1]
    else:
        # Default to finding latest backup in 'backups' folder
        backup_dir = os.path.join(os.getcwd(), 'backups')
        if os.path.exists(backup_dir):
            files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.zip')]
            if files:
                backup_path = max(files, key=os.path.getctime)
                print(f"Found latest backup: {backup_path}")
            else:
                print("No backup file found in backups/ directory.")
                sys.exit(1)
        else:
            print("Usage: python system_restore.py <path_to_backup_zip>")
            sys.exit(1)
            
    restore_full_backup(backup_path)
