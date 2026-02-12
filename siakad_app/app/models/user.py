from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app import db, login

ph = PasswordHasher()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # admin, ustadz, wali_kelas, wali_santri
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Relationships
    pengajar = db.relationship('Pengajar', backref='user', uselist=False)
    
    def set_password(self, password):
        # Menggunakan Argon2 langsung
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False
        
    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
