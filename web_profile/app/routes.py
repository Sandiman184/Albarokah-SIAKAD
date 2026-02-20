from app import db, cache, limiter, mail
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from app.models import Berita, Agenda, Galeri, Pengaturan, Program, Pimpinan
from sqlalchemy.orm import joinedload
from datetime import datetime
import os
import json

# Optional: Import gspread if you want to use it
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

bp = Blueprint('main', __name__)

def append_to_google_sheet(data):
    """
    Helper function to append data to Google Sheet.
    Requires 'gspread' and 'oauth2client' packages installed.
    Requires 'credentials.json' in the root folder.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Define scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load credentials
        # Ensure you have 'google-credentials.json' in your web_profile folder or root
        creds_path = os.path.join(current_app.root_path, '..', '..', 'google-credentials.json')
        if not os.path.exists(creds_path):
             # Try fallback to project root if not found relative to app/routes
             creds_path = os.path.join(os.getcwd(), 'google-credentials.json')
        
        if not os.path.exists(creds_path):
            current_app.logger.warning(f"Google Sheets credentials not found at {creds_path}. Skipping sheet update.")
            return False
            
        credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
        client = gspread.authorize(credentials)
        
        # Open the sheet
        # You must share your sheet with the client_email from json file
        sheet_name = os.environ.get('GOOGLE_SHEET_NAME', 'PPDB_Albarokah_2026')
        sheet = client.open(sheet_name).sheet1
        
        # Prepare row
        row = [
            data['timestamp'],
            data['nama'],
            data['tempat_lahir'],
            data['tanggal_lahir'],
            data['alamat'],
            data['asal_sekolah'],
            data['nama_ortu'],
            data['no_hp_ortu']
        ]
        
        sheet.append_row(row)
        return True
        
    except ImportError:
        current_app.logger.warning("gspread library not installed. Skipping sheet update.")
        return False
    except Exception as e:
        current_app.logger.error(f"Google Sheets Error: {e}")
        return False

@bp.context_processor
@cache.cached(timeout=300, key_prefix='global_pengaturan')
def inject_pengaturan():
    pengaturan = Pengaturan.query.first()
    return dict(pengaturan=pengaturan)

@bp.route('/')
@limiter.limit("30 per minute")
@cache.cached(timeout=60)
def index():
    berita_terbaru = Berita.query.filter_by(status='published').order_by(Berita.tanggal.desc()).limit(3).all()
    agenda_terbaru = Agenda.query.order_by(Agenda.tanggal_mulai.desc()).limit(3).all()
    # Relationship 'children' is lazy='dynamic', so joinedload cannot be used directly.
    # We revert to standard query, or we would need to change model definition to lazy='select'/'joined' for eager loading.
    # Given the small number of programs, standard lazy loading is acceptable here.
    programs = Program.query.filter_by(parent_id=None).order_by(Program.urutan.asc()).all()
    return render_template('index.html', title='Beranda', beritas=berita_terbaru, agendas=agenda_terbaru, programs=programs)

@bp.route('/profil')
@limiter.limit("30 per minute")
# @cache.cached(timeout=300) # Disable cache temporarily for debugging
def profil():
    pimpinan = Pimpinan.query.order_by(Pimpinan.urutan.asc()).all()
    return render_template('profil.html', title='Profil Pesantren', pimpinan=pimpinan)

@bp.route('/program')
@limiter.limit("30 per minute")
@cache.cached(timeout=300)
def program():
    programs = Program.query.filter_by(parent_id=None).order_by(Program.urutan.asc()).all()
    return render_template('program.html', title='Program Pendidikan', programs=programs)

@bp.route('/ppdb')
@limiter.limit("30 per minute")
# @cache.cached(timeout=300) # Disable cache for PPDB to show flash messages
def ppdb():
    return render_template('ppdb.html', title='PPDB Online')

from datetime import datetime, timedelta

# ... imports ...

@bp.route('/ppdb/register', methods=['POST'])
@limiter.limit("5 per minute")
def ppdb_register():
    if request.method == 'POST':
        try:
            # Set timezone to WIB (UTC+7)
            wib_time = datetime.utcnow() + timedelta(hours=7)
            timestamp_str = wib_time.strftime('%Y-%m-%d %H:%M:%S')

            # Collect form data
            data = {
                'nama': request.form.get('nama'),
                'tempat_lahir': request.form.get('tempat_lahir'),
                'tanggal_lahir': request.form.get('tanggal_lahir'),
                'alamat': request.form.get('alamat'),
                'asal_sekolah': request.form.get('asal_sekolah'),
                'nama_ortu': request.form.get('nama_ortu'),
                'no_hp_ortu': request.form.get('no_hp_ortu'),
                'timestamp': timestamp_str
            }
            
            # 1. SECURITY: Input Validation & Sanitization
            # Check if all fields are filled
            if not all(data.values()):
                flash('Harap lengkapi semua kolom pendaftaran!', 'warning')
                return redirect(url_for('main.ppdb'))
            
            # Simple XSS Sanitization: Remove dangerous characters
            for key in data:
                if isinstance(data[key], str):
                    # Strip whitespace
                    data[key] = data[key].strip()
                    # Escape HTML characters to prevent XSS (Cross-Site Scripting)
                    data[key] = data[key].replace('<', '&lt;').replace('>', '&gt;')
            
            # 2. SECURITY: CSRF Protection is handled automatically by Flask-WTF 
            # if we use FlaskForm, but here we use HTML form.
            # We must ensure csrf_token is present in the form (checked in template).
            
            # Here you would typically save to database or Google Sheets
            # For now, we'll just flash a success message as a placeholder
            # The actual Google Sheets integration will be implemented in the next step
            
            # Example placeholder for Google Sheets logic:
            # append_to_sheet(data)
            append_to_google_sheet(data)
            
            # Get contact number from settings if available
            contact_info = ""
            try:
                pengaturan = Pengaturan.query.first()
                if pengaturan and pengaturan.telepon:
                    contact_info = f" di nomor {pengaturan.telepon}"
            except:
                pass
            
            flash(f'Alhamdulillah, formulir pendaftaran berhasil dikirim! Data Anda telah kami terima. Silakan konfirmasi pendaftaran ke Panitia melalui WhatsApp{contact_info} untuk proses selanjutnya.', 'success')
            
        except Exception as e:
            current_app.logger.error(f"PPDB Error: {e}")
            flash('Mohon maaf, terjadi kesalahan saat mengirim pendaftaran. Silakan coba lagi atau hubungi Panitia secara langsung.', 'danger')
            
    return redirect(url_for('main.ppdb'))

from sqlalchemy import func
from flask import request

@bp.route('/berita')
@limiter.limit("30 per minute")
# @cache.cached(timeout=60, query_string=True) # Disable cache for realtime updates
def berita():
    kategori_filter = request.args.get('kategori')
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    query = Berita.query.filter_by(status='published')
    
    if kategori_filter:
        query = query.filter_by(kategori=kategori_filter)
        
    pagination = query.order_by(Berita.tanggal.desc()).paginate(page=page, per_page=per_page, error_out=False)
    beritas = pagination.items
    
    agendas = Agenda.query.order_by(Agenda.tanggal_mulai.desc()).limit(5).all()
    
    # Calculate category counts
    # Get counts for active categories
    active_counts = dict(db.session.query(Berita.kategori, func.count(Berita.id)).filter_by(status='published').group_by(Berita.kategori).all())
    
    # Define standard categories to ensure they always appear
    standard_categories = ['berita', 'pengumuman', 'artikel']
    
    kategori_counts = []
    # Add standard categories with their counts (default 0)
    for cat in standard_categories:
        kategori_counts.append((cat, active_counts.get(cat, 0)))
        
    # Add any other categories found in DB that are not in standard list
    for cat, count in active_counts.items():
        if cat not in standard_categories:
            kategori_counts.append((cat, count))
    
    return render_template('berita.html', title='Berita & Agenda', beritas=beritas, pagination=pagination, agendas=agendas, kategori_counts=kategori_counts, current_kategori=kategori_filter)

@bp.route('/berita/<slug>')
@limiter.limit("30 per minute")
@cache.cached(timeout=600)
def berita_detail(slug):
    berita = Berita.query.filter_by(slug=slug).first_or_404()
    berita_lain = Berita.query.filter(Berita.id != berita.id, Berita.status == 'published').order_by(Berita.tanggal.desc()).limit(3).all()
    return render_template('berita_detail.html', title=berita.judul, berita=berita, berita_lain=berita_lain)

@bp.route('/galeri')
@limiter.limit("30 per minute")
# @cache.cached(timeout=300, query_string=True)
def galeri():
    page = request.args.get('page', 1, type=int)
    kategori_filter = request.args.get('kategori')
    per_page = 9
    
    query = Galeri.query
    
    if kategori_filter and kategori_filter != 'all':
        query = query.filter_by(kategori=kategori_filter)
        
    pagination = query.order_by(Galeri.tanggal.desc()).paginate(page=page, per_page=per_page, error_out=False)
    galeris = pagination.items
    
    return render_template('galeri.html', title='Galeri Foto', galeris=galeris, pagination=pagination, current_kategori=kategori_filter)

@bp.route('/kontak', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Stricter limit for contact form page
def kontak():
    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        subjek = request.form.get('subjek')
        pesan = request.form.get('pesan')
        
        if not all([nama, email, subjek, pesan]):
            flash('Harap lengkapi semua kolom!', 'danger')
        else:
            # Get destination email from settings or default
            dest_email = 'ppqalbarokahkarangjati@gmail.com'
            try:
                pengaturan = Pengaturan.query.first()
                if pengaturan and pengaturan.email:
                    dest_email = pengaturan.email
            except:
                pass
            
            try:
                # Send email via SMTP
                msg = Message(
                    subject=f"[Kontak Website] {subjek}",
                    sender=current_app.config['MAIL_DEFAULT_SENDER'], # Must match MAIL_USERNAME
                    recipients=[dest_email],
                    body=f"""
                    Pesan Baru dari Website Ponpes Al-Barokah
                    
                    Pengirim: {nama}
                    Email: {email}
                    
                    Pesan:
                    {pesan}
                    """
                )
                mail.send(msg)
                
                # Prepare data for Google Sheet (using same format as PPDB for simplicity or a new sheet)
                # Ideally we should have a separate sheet for Contacts, but for now let's reuse the append function
                # Or create a slightly different structure if needed.
                # Let's add a "Contact" tag to differentiate in the sheet or just log it.
                
                # Set timezone to WIB (UTC+7)
                wib_time = datetime.utcnow() + timedelta(hours=7)
                timestamp_str = wib_time.strftime('%Y-%m-%d %H:%M:%S')
                
                contact_data = {
                    'timestamp': timestamp_str,
                    'nama': nama,
                    'tempat_lahir': '-', # Not used in contact
                    'tanggal_lahir': '-', # Not used in contact
                    'alamat': email, # Storing email in alamat column for now
                    'asal_sekolah': subjek, # Storing subject in asal_sekolah
                    'nama_ortu': '-',
                    'no_hp_ortu': '-' 
                }
                append_to_google_sheet(contact_data)
                
                # Custom notification message
                contact_info = ""
                try:
                    if pengaturan and pengaturan.telepon:
                        contact_info = f" ({pengaturan.telepon})"
                except:
                    pass
                    
                flash(f'Alhamdulillah, pesan Anda berhasil dikirim! Terima kasih telah menghubungi kami. Untuk respon lebih cepat, Anda juga dapat menghubungi kami melalui WhatsApp{contact_info}.', 'success')
                
            except Exception as e:
                current_app.logger.error(f"Error sending email: {e}")
                # Provide helpful error message if on localhost
                if "ConnectionRefusedError" in str(e) or "authentication required" in str(e):
                    flash('Gagal mengirim email: Konfigurasi Server Email belum disetting. Silakan hubungi admin.', 'danger')
                else:
                    flash('Maaf, terjadi kesalahan saat mengirim pesan. Silakan coba lagi nanti atau hubungi kami via WhatsApp.', 'danger')
            
            return redirect(url_for('main.kontak'))
            
    return render_template('kontak.html', title='Kontak Kami')
