import os
import shutil
import zipfile
import sys
import time

def restore_full_backup(backup_zip_path):
    """
    Restores a full system snapshot from a zip file.
    WARNING: This will OVERWRITE the current database and uploads!
    """
    if not os.path.exists(backup_zip_path):
        print(f"❌ Error: Backup file not found: {backup_zip_path}")
        return

    print("⚠️  WARNING: This will OVERWRITE your current database and uploads!")
    print("    Any data added since this backup was created will be LOST.")
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Restore cancelled.")
        return

    # Paths
    project_root = os.getcwd()
    target_db_path = os.path.join(project_root, 'web_profile', 'app.db')
    target_uploads_dir = os.path.join(project_root, 'web_profile', 'app', 'static', 'uploads')
    
    try:
        print(f"Opening backup archive: {backup_zip_path}...")
        with zipfile.ZipFile(backup_zip_path, 'r') as zipf:
            # 1. Restore Database
            if 'app.db' in zipf.namelist():
                print("Restoring database...")
                # Backup current DB just in case (safety first)
                if os.path.exists(target_db_path):
                    shutil.copy2(target_db_path, target_db_path + '.pre_restore_bak')
                    print(f"  - Created safety backup: {target_db_path}.pre_restore_bak")
                
                # Extract app.db to temp and move
                zipf.extract('app.db', path=os.path.join(project_root, 'web_profile'))
                print("  - Database restored.")
            else:
                print("WARNING: app.db not found in backup archive!")

            # 2. Restore Uploads
            print("Restoring uploads...")
            # We look for files starting with 'uploads/' in the zip
            upload_files = [f for f in zipf.namelist() if f.startswith('uploads/')]
            
            if upload_files:
                # Optional: Clear existing uploads to match snapshot exactly?
                # For safety, we usually just overwrite/add, but for true snapshot restore we should clear.
                # Let's clear to ensure deleted files are removed.
                if os.path.exists(target_uploads_dir):
                    print("  - Clearing current uploads directory...")
                    shutil.rmtree(target_uploads_dir)
                os.makedirs(target_uploads_dir)
                
                # Extract
                for file in upload_files:
                    # Zip structure: uploads/subdir/file.jpg
                    # Target: web_profile/app/static/uploads/subdir/file.jpg
                    
                    # Extraction path needs to be adjusted because zip contains 'uploads/...'
                    # We extract to web_profile/app/static
                    extract_root = os.path.join(project_root, 'web_profile', 'app', 'static')
                    zipf.extract(file, path=extract_root)
                print(f"  - Restored {len(upload_files)} files/directories.")
            else:
                print("No upload files found in backup.")

        print("✅ Restore completed successfully!")
        print("NOTE: You may need to restart the application server.")
        print("      Command: sudo systemctl restart web_profile")

    except Exception as e:
        print(f"❌ Restore failed: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python system_restore.py <path_to_backup_zip>")
        print("Example: python system_restore.py backups/full_system_backup_20260220_120000.zip")
    else:
        restore_full_backup(sys.argv[1])
