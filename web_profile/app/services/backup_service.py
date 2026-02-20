import os
import zipfile
import shutil
import datetime
import subprocess
import platform
from urllib.parse import urlparse, unquote
from flask import current_app

class BackupService:
    @staticmethod
    def _get_postgres_bin(binary_name):
        """
        Mencoba menemukan binary PostgreSQL (pg_dump/pg_restore/psql).
        Mendukung Windows dan Linux (via shutil.which).
        """
        # 1. Cek jika ada di PATH (Linux usually falls here)
        path = shutil.which(binary_name)
        if path:
            return path
            
        # 2. Cek lokasi umum instalasi PostgreSQL di Windows dan Linux
        common_paths = [
            # Linux common paths
            "/usr/bin",
            "/usr/local/bin",
            "/usr/lib/postgresql/16/bin",
            "/usr/lib/postgresql/15/bin",
            "/usr/lib/postgresql/14/bin",
            "/usr/lib/postgresql/13/bin",
            "/usr/lib/postgresql/12/bin",
            # Windows paths
            r"C:\Program Files\PostgreSQL\17\bin",
            r"C:\Program Files\PostgreSQL\16\bin",
            r"C:\Program Files\PostgreSQL\15\bin",
            r"C:\Program Files\PostgreSQL\14\bin",
            r"C:\Program Files\PostgreSQL\13\bin",
            r"C:\Program Files\PostgreSQL\12\bin",
            # Add x86 paths if needed
            r"C:\Program Files (x86)\PostgreSQL\17\bin",
            r"C:\Program Files (x86)\PostgreSQL\16\bin",
        ]
        
        for path in common_paths:
            # Check for binary with or without .exe extension
            bin_path = os.path.join(path, binary_name)
            if os.path.exists(bin_path) and os.access(bin_path, os.X_OK):
                return bin_path
                
            bin_path_exe = os.path.join(path, binary_name + ".exe")
            if os.path.exists(bin_path_exe):
                return bin_path_exe
        
        # 3. Log warning if not found
        print(f"Warning: {binary_name} not found in PATH or common locations.")
        return None

    @staticmethod
    def _backup_postgres_db(db_uri, output_file):
        """
        Helper untuk melakukan dump database PostgreSQL.
        """
        parsed = urlparse(db_uri)
        hostname = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        username = parsed.username
        password = unquote(parsed.password) if parsed.password else None
        database = parsed.path.lstrip('/')
        
        pg_dump = BackupService._get_postgres_bin('pg_dump')
        if not pg_dump:
            raise Exception("pg_dump not found! Pastikan PostgreSQL terinstall dan ada di PATH.")
            
        env = os.environ.copy()
        if password:
            env['PGPASSWORD'] = password
            
        # Dump structure and data to plain SQL text with CLEAN (DROP commands)
        cmd = [
            pg_dump,
            '-h', hostname,
            '-p', str(port),
            '-U', username,
            '-c', # Clean (Drop then Create)
            '-f', output_file,
            database
        ]
        
        # Run command and capture output
        try:
            result = subprocess.run(
                cmd, 
                env=env, 
                check=True,
                capture_output=True,
                text=True
            )
            return os.path.exists(output_file)
        except subprocess.CalledProcessError as e:
            print(f"Error dumping database {database}:")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False

    @staticmethod
    def _restore_postgres_db(db_uri, input_file):
        """
        Helper untuk restore database PostgreSQL.
        """
        parsed = urlparse(db_uri)
        hostname = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        username = parsed.username
        password = unquote(parsed.password) if parsed.password else None
        database = parsed.path.lstrip('/')
        
        psql = BackupService._get_postgres_bin('psql')
        if not psql:
            raise Exception("psql not found! Cannot restore database.")
            
        env = os.environ.copy()
        if password:
            env['PGPASSWORD'] = password
        
        # psql -U user -d db -f file.sql
        cmd = [
            psql,
            '-h', hostname,
            '-p', str(port),
            '-U', username,
            '-d', database,
            '-f', input_file
        ]
        
        # Run command and capture output
        try:
            result = subprocess.run(
                cmd, 
                env=env, 
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error restoring database {database}:")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise Exception(f"Restore failed: {e.stderr}")

    @staticmethod
    def _get_siakad_db_uri():
        """
        Mencoba mendapatkan URI database SIAKAD dari file .env di sibling directory.
        """
        try:
            # Asumsi: siakad_app ada di sebelah web_profile (parent dari current_app.root_path)
            # current_app.root_path = .../web_profile/app
            # project_root = .../
            project_root = os.path.abspath(os.path.join(current_app.root_path, '..', '..'))
            siakad_env_path = os.path.join(project_root, 'siakad_app', '.env')
            
            if os.path.exists(siakad_env_path):
                with open(siakad_env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('DATABASE_URL='):
                            return line.split('=', 1)[1].strip()
        except Exception as e:
            print(f"Warning: Could not load SIAKAD config: {e}")
        return None

    @staticmethod
    def create_system_snapshot(backup_dir=None):
        """
        Membuat snapshot sistem (Web Profile + SIAKAD).
        """
        if backup_dir is None:
            backup_dir = os.path.join(current_app.root_path, '..', '..', 'backups')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'full_system_snapshot_{timestamp}.zip'
        zip_filepath = os.path.join(backup_dir, zip_filename)

        # 1. Web Profile Paths
        web_static_dir = os.path.join(current_app.root_path, 'static')
        web_uploads_dir = os.path.join(web_static_dir, 'uploads')
        web_db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # 2. SIAKAD Paths (Optional)
        siakad_db_uri = BackupService._get_siakad_db_uri()
        
        temp_files = []

        try:
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                print("--- Backing up Web Profile ---")
                # 1. Web Profile Database
                if web_db_uri.startswith('sqlite:///'):
                    db_path = web_db_uri.replace('sqlite:///', '')
                    if not os.path.isabs(db_path):
                        db_path = os.path.join(current_app.root_path, '..', db_path)
                    if os.path.exists(db_path):
                        print(f"Backing up SQLite: {db_path}")
                        zipf.write(db_path, arcname='web_profile.db')
                elif web_db_uri.startswith('postgresql'):
                    print("Backing up PostgreSQL (Web Profile)...")
                    dump_file = os.path.join(backup_dir, f'web_profile_{timestamp}.sql')
                    if BackupService._backup_postgres_db(web_db_uri, dump_file):
                        zipf.write(dump_file, arcname='web_profile.sql')
                        temp_files.append(dump_file)

                # 2. Web Profile Uploads
                if os.path.exists(web_uploads_dir):
                    print(f"Backing up Web Profile uploads...")
                    for root, dirs, files in os.walk(web_uploads_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, web_static_dir)
                            # Store as uploads/web_profile/... or just uploads/...
                            # Current structure: uploads/berita/file.jpg
                            # We keep it as is relative to static: uploads/...
                            zipf.write(file_path, arcname=rel_path)

                # 3. SIAKAD Database
                if siakad_db_uri:
                    print("--- Backing up SIAKAD ---")
                    if siakad_db_uri.startswith('postgresql'):
                        print("Backing up PostgreSQL (SIAKAD)...")
                        dump_file = os.path.join(backup_dir, f'siakad_{timestamp}.sql')
                        if BackupService._backup_postgres_db(siakad_db_uri, dump_file):
                            zipf.write(dump_file, arcname='siakad.sql')
                            temp_files.append(dump_file)
                    else:
                        print(f"Skipping SIAKAD DB (Unsupported URI scheme): {siakad_db_uri}")
                else:
                    print("Warning: SIAKAD database configuration not found.")

        finally:
            # Cleanup temp files
            for f in temp_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass
        
        return zip_filepath

    @staticmethod
    def restore_system_snapshot(zip_source_path):
        """
        Merestore snapshot sistem (Web Profile + SIAKAD).
        """
        if not os.path.exists(zip_source_path):
            raise FileNotFoundError("Backup file not found")

        # Web Profile Targets
        web_static_dir = os.path.join(current_app.root_path, 'static')
        web_uploads_dir = os.path.join(web_static_dir, 'uploads')
        web_db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # SIAKAD Targets
        siakad_db_uri = BackupService._get_siakad_db_uri()

        with zipfile.ZipFile(zip_source_path, 'r') as zipf:
            file_list = zipf.namelist()
            
            # --- Restore Web Profile ---
            print("--- Restoring Web Profile ---")
            
            # 1. Database
            # Check for legacy names first (database.sql / app.db) for backward compatibility
            if 'web_profile.sql' in file_list and web_db_uri.startswith('postgresql'):
                print("Restoring PostgreSQL (Web Profile)...")
                zipf.extract('web_profile.sql', path=web_static_dir)
                dump_path = os.path.join(web_static_dir, 'web_profile.sql')
                try:
                    BackupService._restore_postgres_db(web_db_uri, dump_path)
                finally:
                    if os.path.exists(dump_path): os.remove(dump_path)
            elif 'database.sql' in file_list and web_db_uri.startswith('postgresql'):
                # Legacy support
                print("Restoring PostgreSQL (Legacy Format)...")
                zipf.extract('database.sql', path=web_static_dir)
                dump_path = os.path.join(web_static_dir, 'database.sql')
                try:
                    BackupService._restore_postgres_db(web_db_uri, dump_path)
                finally:
                    if os.path.exists(dump_path): os.remove(dump_path)
            
            elif 'web_profile.db' in file_list and web_db_uri.startswith('sqlite:///'):
                print("Restoring SQLite (Web Profile)...")
                db_path = web_db_uri.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    db_path = os.path.join(current_app.root_path, '..', db_path)
                
                target_dir = os.path.dirname(db_path)
                zipf.extract('web_profile.db', path=target_dir)
                extracted = os.path.join(target_dir, 'web_profile.db')
                if os.path.exists(extracted):
                    shutil.move(extracted, db_path)

            elif 'app.db' in file_list and web_db_uri.startswith('sqlite:///'):
                 # Legacy support
                print("Restoring SQLite (Legacy Format)...")
                db_path = web_db_uri.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    db_path = os.path.join(current_app.root_path, '..', db_path)
                
                # Zip extract path behavior depends on if it has folders.
                # Assuming app.db is at root of zip.
                zipf.extract('app.db', path=os.path.dirname(db_path))

            # 2. Uploads
            # Filter files starting with uploads/
            upload_files = [f for f in file_list if f.startswith('uploads/') or f.startswith('uploads\\')]
            
            if upload_files:
                print("Restoring Uploads...")
                # Clean existing
                if os.path.exists(web_uploads_dir):
                    try:
                        shutil.rmtree(web_uploads_dir)
                    except Exception as e:
                        print(f"Warning: Could not empty uploads dir: {e}")
                if not os.path.exists(web_uploads_dir):
                    os.makedirs(web_uploads_dir)

                for file in upload_files:
                    zipf.extract(file, path=web_static_dir)

            # --- Restore SIAKAD ---
            if siakad_db_uri:
                print("--- Restoring SIAKAD ---")
                if 'siakad.sql' in file_list and siakad_db_uri.startswith('postgresql'):
                    print("Restoring PostgreSQL (SIAKAD)...")
                    zipf.extract('siakad.sql', path=web_static_dir)
                    dump_path = os.path.join(web_static_dir, 'siakad.sql')
                    try:
                        BackupService._restore_postgres_db(siakad_db_uri, dump_path)
                    finally:
                        if os.path.exists(dump_path): os.remove(dump_path)
                elif 'siakad.sql' not in file_list:
                    print("Skipping SIAKAD: No siakad.sql found in backup.")
            else:
                print("Skipping SIAKAD: Configuration not found.")

        return True
