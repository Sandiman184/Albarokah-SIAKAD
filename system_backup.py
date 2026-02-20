import os
import shutil
import zipfile
import datetime
from app import create_app, db

def create_full_backup():
    """
    Creates a full system snapshot including:
    1. SQLite Database file (app.db)
    2. Uploaded files (web_profile/app/static/uploads)
    
    Output: A zip file named 'full_backup_YYYYMMDD_HHMMSS.zip' in the backups directory.
    """
    app = create_app()
    with app.app_context():
        # Configuration
        backup_dir = os.path.join(os.getcwd(), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'full_system_backup_{timestamp}.zip'
        zip_filepath = os.path.join(backup_dir, zip_filename)
        
        # Paths to backup
        db_path = os.path.join(os.getcwd(), 'web_profile', 'app.db')
        uploads_dir = os.path.join(os.getcwd(), 'web_profile', 'app', 'static', 'uploads')
        
        print(f"Starting full system backup...")
        print(f"Database: {db_path}")
        print(f"Uploads: {uploads_dir}")
        
        try:
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. Backup Database
                if os.path.exists(db_path):
                    print("Backing up database...")
                    zipf.write(db_path, arcname='app.db')
                else:
                    print("WARNING: Database file not found!")
                
                # 2. Backup Uploads
                if os.path.exists(uploads_dir):
                    print("Backing up uploads directory...")
                    for root, dirs, files in os.walk(uploads_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Create relative path for zip archive to maintain structure
                            # We want 'uploads/folder/file.jpg' in the zip
                            rel_path = os.path.relpath(file_path, os.path.join(os.getcwd(), 'web_profile', 'app', 'static'))
                            zipf.write(file_path, arcname=rel_path)
                else:
                    print("WARNING: Uploads directory not found!")
                    
            print(f"✅ Full backup created successfully: {zip_filepath}")
            print(f"File size: {os.path.getsize(zip_filepath) / (1024*1024):.2f} MB")
            
        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")
            if os.path.exists(zip_filepath):
                os.remove(zip_filepath)

if __name__ == '__main__':
    create_full_backup()
