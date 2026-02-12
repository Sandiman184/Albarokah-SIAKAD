from app import create_app, db
from app.models import Berita, Agenda, Galeri

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Berita': Berita, 'Agenda': Agenda, 'Galeri': Galeri}

if __name__ == '__main__':
    app.run(port=8001, debug=True)
