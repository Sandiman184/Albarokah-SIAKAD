from app import create_app, db
from app.models import User
import sys

def create_superadmin(username, password):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User '{username}' already exists. Updating role to superadmin...")
            user.role = 'superadmin'
            user.set_password(password)
        else:
            print(f"Creating new superadmin user '{username}'...")
            user = User(username=username, role='superadmin')
            user.set_password(password)
            db.session.add(user)
        
        try:
            db.session.commit()
            print(f"Successfully created/updated superadmin: {username}")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python create_superadmin.py <username> <password>")
        print("Example: python create_superadmin.py superadmin secret123")
    else:
        create_superadmin(sys.argv[1], sys.argv[2])
