from app.models.user import User

def test_password_hashing():
    u = User(username='susan')
    u.set_password('cat')
    assert u.check_password('cat')
    assert not u.check_password('dog')

def test_user_representation():
    u = User(username='john') 
    # checking User model again: username, password_hash, role. No email.
    # Ah, User model: username, password_hash, role.
    assert '<User john>' == repr(u)
