import threading
from flask import render_template, current_app
try:
    from weasyprint import HTML
except OSError:
    HTML = None

def generate_pdf_task(html_content, output_path):
    """
    Background task to generate PDF.
    In a real production environment, use Celery.
    For this setup, we use a simple thread to demonstrate non-blocking behavior 
    (though Python threads are still GIL-bound, WeasyPrint releases GIL for I/O).
    """
    if HTML:
        HTML(string=html_content).write_pdf(output_path)
    else:
        print("WeasyPrint not available")

class PdfService:
    @staticmethod
    def generate_raport_pdf_async(data, output_path):
        """
        Starts a background thread to generate PDF.
        """
        # Render HTML in the main thread (requires app context)
        html = render_template('akademik/raport_pdf.html', data=data)
        
        # Start background thread
        thread = threading.Thread(target=generate_pdf_task, args=(html, output_path))
        thread.start()
        return thread
