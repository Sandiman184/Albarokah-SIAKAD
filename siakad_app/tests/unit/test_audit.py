import pytest
from app.models.audit import AuditLog
from app.models.user import User
from app import db
import json

def test_audit_log_creation(app):
    with app.app_context():
        log = AuditLog(
            action='CREATE', 
            model_name='TestModel', 
            details='{"foo": "bar"}',
            ip_address='127.0.0.1'
        )
        db.session.add(log)
        db.session.commit()
        
        assert log.id is not None
        assert log.timestamp is not None
        
        fetched_log = db.session.get(AuditLog, log.id)
        assert fetched_log.action == 'CREATE'
        assert fetched_log.ip_address == '127.0.0.1'

def test_audit_log_decorator(client, app):
    # Create admin user
    with app.app_context():
        u = User(username='auditadmin', role='admin')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        
    # Login
    client.post('/auth/login', data={'username': 'auditadmin', 'password': 'password'}, follow_redirects=True)
    
    # Trigger an action that is audited, e.g., create a user
    response = client.post('/master/users/add', data={
        'username': 'newauditeduser',
        'password': 'password123',
        'confirm_password': 'password123',
        'role': 'santri'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check if audit log was created
    with app.app_context():
        # We need to filter by details because other tests might create logs too
        # But we cleared DB in fixture? No, session scope.
        # Let's query carefully.
        logs = AuditLog.query.all()
        found = False
        for log in logs:
            if log.action == 'CREATE' and log.model_name == 'User' and log.details:
                details = json.loads(log.details)
                if 'form_data' in details and details['form_data'].get('username') == 'newauditeduser':
                    found = True
                    break
        assert found
