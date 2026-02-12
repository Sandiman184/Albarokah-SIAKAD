from flask import render_template
from app import create_app, db

app = create_app()

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.shell_context_processor
def make_shell_context():
    from app.models.user import User
    from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran, Nilai, Absensi, Tahfidz
    from app.models.keuangan import Keuangan
    return {'db': db, 'User': User, 'Santri': Santri, 'Pengajar': Pengajar, 'Kelas': Kelas, 'MataPelajaran': MataPelajaran, 'Nilai': Nilai, 'Absensi': Absensi, 'Tahfidz': Tahfidz, 'Keuangan': Keuangan}

if __name__ == '__main__':
    app.run(debug=True)
