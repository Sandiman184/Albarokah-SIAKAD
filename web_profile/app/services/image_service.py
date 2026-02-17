import os
import secrets
from flask import current_app, url_for
from werkzeug.utils import secure_filename

class ImageService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ImageService.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_image_content(file_storage):
        """
        Basic validation to check if the file has valid image magic numbers.
        This prevents uploading scripts disguised as images.
        """
        # Read the first 512 bytes
        header = file_storage.read(512)
        file_storage.seek(0)  # Reset cursor
        
        # Simple check for common headers (can be expanded)
        # JPEG: FF D8 FF
        # PNG: 89 50 4E 47 0D 0A 1A 0A
        # GIF: 47 49 46 38
        
        if header.startswith(b'\xff\xd8\xff'): return True # JPEG
        if header.startswith(b'\x89PNG\r\n\x1a\n'): return True # PNG
        if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'): return True # GIF
        
        return False

    @staticmethod
    def save_picture(form_picture, folder):
        if not form_picture:
            return None
            
        if not ImageService.allowed_file(form_picture.filename):
            raise ValueError("File extension not allowed")

        # Validate content
        if not ImageService.validate_image_content(form_picture):
            raise ValueError("Invalid image content")
            
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        
        # Determine path relative to app root
        # Assuming web_profile/app/static/uploads
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', folder)
        
        # Ensure directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        picture_path = os.path.join(upload_folder, picture_fn)
        form_picture.save(picture_path)
        
        return url_for('static', filename=f'uploads/{folder}/{picture_fn}')
