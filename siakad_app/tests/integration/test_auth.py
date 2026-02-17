def test_login_page_loads(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_valid_login(client, app):
    # Create a user
    from app.models.user import User
    from app import db
    
    with app.app_context():
        u = User(username='testadmin', role='admin')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

    response = client.post('/auth/login', data={
        'username': 'testadmin',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check if redirected to dashboard or shows dashboard content
    assert b'Dashboard' in response.data or b'Logout' in response.data

def test_invalid_login(client):
    response = client.post('/auth/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for alert class first to confirm flash rendering works
    assert b'alert-danger' in response.data
    # Check for message - might need to handle encoding if it fails, but let's try
    assert b'Username atau password salah' in response.data

def test_logout(auth_client):
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
