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
            '--if-exists', # Add IF EXISTS to DROP commands
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
    def _drop_all_tables(db_uri):
        """
        Helper untuk menghapus semua tabel di database sebelum restore
        agar benar-benar bersih (clean slate).
        """
        parsed = urlparse(db_uri)
        hostname = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        username = parsed.username
        password = unquote(parsed.password) if parsed.password else None
        database = parsed.path.lstrip('/')
        
        psql = BackupService._get_postgres_bin('psql')
        if not psql:
            return False
            
        env = os.environ.copy()
        if password:
            env['PGPASSWORD'] = password
            
        # SQL command to terminate other connections first
        kill_conns_sql = f"""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = '{database}' 
          AND pid <> pg_backend_pid();
        """
        
        # SQL command to drop public schema and recreate it
        # This is the most effective way to clear everything
        drop_schema_sql = "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;"
        
        # Combined command
        # Note: We need to execute these as separate commands or combined carefully
        # psql -c executes one string.
        
        # 1. Kill Connections
        try:
            print(f"Terminating active connections to {database}...")
            # We use a separate connection to 'postgres' DB if possible to kill connections to target DB
            # But here we connect to target DB itself.
            # Terminating other backends is usually allowed for owner.
            subprocess.run(
                [psql, '-h', hostname, '-p', str(port), '-U', username, '-d', database, '-c', kill_conns_sql],
                env=env, check=True, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Warning killing connections: {e.stderr}")
        except Exception as e:
            print(f"Warning killing connections: {e}")

        # 2. Drop Schema
        try:
            print(f"Dropping all tables in {database}...")
            subprocess.run(
                [psql, '-h', hostname, '-p', str(port), '-U', username, '-d', database, '-c', drop_schema_sql], 
                env=env, 
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to drop schema for {database}: {e.stderr}")
            # Fallback: Try to drop tables individually if schema drop fails?
            # For now, we just proceed. The restore might still work for existing tables.
            return False

    @staticmethod
    def _restore_postgres_db(db_uri, input_file):
        """
        Helper untuk restore database PostgreSQL.
        """
        # Step 0: Try to clear database first for clean restore
        BackupService._drop_all_tables(db_uri)

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
    def _get_web_profile_db_uri():
        """
        Mencoba mendapatkan URI database Web Profile dari file .env di sibling directory.
        """
        try:
            # Asumsi: siakad_app ada di sebelah web_profile (parent dari current_app.root_path)
            project_root = os.path.abspath(os.path.join(current_app.root_path, '..', '..'))
            web_env_path = os.path.join(project_root, 'web_profile', '.env')
            
            if os.path.exists(web_env_path):
                with open(web_env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('DATABASE_URL='):
                            return line.split('=', 1)[1].strip()
        except Exception as e:
            print(f"Warning: Could not load Web Profile config: {e}")
        return None

    @staticmethod
    def create_system_snapshot(backup_dir=None, progress_callback=None):
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

        # 1. SIAKAD Paths (Current App)
        siakad_db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # 2. Web Profile Paths (Sibling App)
        web_db_uri = BackupService._get_web_profile_db_uri()
        project_root = os.path.abspath(os.path.join(current_app.root_path, '..', '..'))
        web_static_dir = os.path.join(project_root, 'web_profile', 'app', 'static')
        web_uploads_dir = os.path.join(web_static_dir, 'uploads')
        
        temp_files = []

        try:
            if progress_callback: progress_callback(10, "Initializing backup...")
            
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. SIAKAD Database
                print("--- Backing up SIAKAD ---")
                if progress_callback: progress_callback(20, "Backing up SIAKAD Database...")
                
                if siakad_db_uri.startswith('postgresql'):
                    print("Backing up PostgreSQL (SIAKAD)...")
                    dump_file = os.path.join(backup_dir, f'siakad_{timestamp}.sql')
                    if BackupService._backup_postgres_db(siakad_db_uri, dump_file):
                        zipf.write(dump_file, arcname='siakad.sql')
                        temp_files.append(dump_file)
                else:
                    print(f"Skipping SIAKAD DB (Unsupported URI scheme): {siakad_db_uri}")

                # 2. Web Profile Database & Uploads
                if web_db_uri:
                    print("--- Backing up Web Profile ---")
                    if progress_callback: progress_callback(50, "Backing up Web Profile Database...")
                    
                    if web_db_uri.startswith('postgresql'):
                        print("Backing up PostgreSQL (Web Profile)...")
                        dump_file = os.path.join(backup_dir, f'web_profile_{timestamp}.sql')
                        if BackupService._backup_postgres_db(web_db_uri, dump_file):
                            zipf.write(dump_file, arcname='web_profile.sql')
                            temp_files.append(dump_file)
                    
                    # Web Profile Uploads
                    if os.path.exists(web_uploads_dir):
                        print(f"Backing up Web Profile uploads...")
                        if progress_callback: progress_callback(70, "Backing up Uploaded Files...")
                        for root, dirs, files in os.walk(web_uploads_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                rel_path = os.path.relpath(file_path, web_static_dir)
                                # Store as uploads/web_profile/... or just uploads/...
                                # Current structure: uploads/berita/file.jpg
                                # We keep it as is relative to static: uploads/...
                                zipf.write(file_path, arcname=rel_path)
                else:
                    print("Warning: Web Profile database configuration not found.")
                
                if progress_callback: progress_callback(90, "Finalizing backup archive...")

        finally:
            # Cleanup temp files
            for f in temp_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except:
                        pass
        
        if progress_callback: progress_callback(100, "Backup complete!")
        return zip_filepath

    @staticmethod
    def restore_system_snapshot(zip_source_path, progress_callback=None):
        """
        Merestore snapshot sistem (Web Profile + SIAKAD).
        """
        if not os.path.exists(zip_source_path):
            raise FileNotFoundError("Backup file not found")

        # SIAKAD Targets
        siakad_db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Web Profile Targets
        web_db_uri = BackupService._get_web_profile_db_uri()
        project_root = os.path.abspath(os.path.join(current_app.root_path, '..', '..'))
        web_static_dir = os.path.join(project_root, 'web_profile', 'app', 'static')
        web_uploads_dir = os.path.join(web_static_dir, 'uploads')

        if progress_callback: progress_callback(10, "Reading backup archive...")

        with zipfile.ZipFile(zip_source_path, 'r') as zipf:
            file_list = zipf.namelist()
            
            # --- Restore SIAKAD ---
            print("--- Restoring SIAKAD ---")
            if progress_callback: progress_callback(20, "Restoring SIAKAD Database...")
            
            if 'siakad.sql' in file_list and siakad_db_uri.startswith('postgresql'):
                print("Restoring PostgreSQL (SIAKAD)...")
                # Extract to temp location
                temp_dir = os.path.join(project_root, 'temp_restore')
                if not os.path.exists(temp_dir): os.makedirs(temp_dir)
                
                zipf.extract('siakad.sql', path=temp_dir)
                dump_path = os.path.join(temp_dir, 'siakad.sql')
                try:
                    BackupService._restore_postgres_db(siakad_db_uri, dump_path)
                finally:
                    if os.path.exists(dump_path): os.remove(dump_path)
                    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
            elif 'siakad.sql' not in file_list:
                print("Skipping SIAKAD: No siakad.sql found in backup.")

            # --- Restore Web Profile ---
            if web_db_uri:
                print("--- Restoring Web Profile ---")
                if progress_callback: progress_callback(50, "Restoring Web Profile Database...")
                
                # 1. Database
                if 'web_profile.sql' in file_list and web_db_uri.startswith('postgresql'):
                    print("Restoring PostgreSQL (Web Profile)...")
                    temp_dir = os.path.join(project_root, 'temp_restore')
                    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
                    
                    zipf.extract('web_profile.sql', path=temp_dir)
                    dump_path = os.path.join(temp_dir, 'web_profile.sql')
                    try:
                        BackupService._restore_postgres_db(web_db_uri, dump_path)
                    finally:
                        if os.path.exists(dump_path): os.remove(dump_path)
                        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
                
                # 2. Uploads
                if progress_callback: progress_callback(70, "Restoring Uploaded Files...")
                # Filter files starting with uploads/
                upload_files = [f for f in file_list if f.startswith('uploads/') or f.startswith('uploads\\')]
                
                if upload_files:
                    print("Restoring Uploads...")
                    # Clean existing by renaming first (atomic) then deleting
                    if os.path.exists(web_uploads_dir):
                        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                        trash_dir = f"{web_uploads_dir}_trash_{timestamp}"
                        try:
                            shutil.move(web_uploads_dir, trash_dir)
                            print(f"Moved existing uploads to {trash_dir}")
                        except Exception as e:
                            print(f"Warning: Could not move uploads dir: {e}")
                            try:
                                shutil.rmtree(web_uploads_dir)
                            except Exception as e2:
                                print(f"Warning: Could not delete uploads dir: {e2}")

                    if not os.path.exists(web_uploads_dir):
                        os.makedirs(web_uploads_dir)

                    for file in upload_files:
                        zipf.extract(file, path=web_static_dir)
                    
                    # Try to clean up trash
                    if 'trash_dir' in locals() and os.path.exists(trash_dir):
                        try:
                            shutil.rmtree(trash_dir)
                        except Exception as e:
                            print(f"Warning: Could not delete trash dir {trash_dir}: {e}")
            else:
                print("Skipping Web Profile: Configuration not found.")

        if progress_callback: progress_callback(100, "Restore complete!")
        return True
