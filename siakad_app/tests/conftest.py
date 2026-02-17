import pytest
from app import create_app, db
from app.models.user import User
from config import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """Fixture to create an authenticated client"""
    user = User(username='testuser', role='admin')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    with client:
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        yield client
