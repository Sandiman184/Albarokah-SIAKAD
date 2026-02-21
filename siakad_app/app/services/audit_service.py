from functools import wraps
from flask import request
from flask_login import current_user
from app import db
from app.models.audit import AuditLog
import json

def log_audit(action, model_name=None):
    """
    Decorator to log user actions.
    Usage: @log_audit('CREATE', 'Santri')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            response = f(*args, **kwargs)
            
            # Log only if successful (usually redirect or 200)
            # This is a simplification; for better accuracy, 
            # we might need to inspect response status or flash messages.
            # Assuming if no exception raised, it's a success for now.
            
            try:
                if current_user.is_authenticated:
                    details = {}
                    if request.method == 'POST':
                        # Safe extract of form data (excluding passwords/tokens)
                        form_data = request.form.to_dict()
                        if 'password' in form_data:
                            form_data['password'] = '***'
                        if 'csrf_token' in form_data:
                            del form_data['csrf_token']
                        details['form_data'] = form_data
                    
                    if kwargs:
                        details['route_args'] = kwargs

                    log = AuditLog(
                        user_id=current_user.id,
                        action=action,
                        model_name=model_name,
                        details=json.dumps(details),
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string if request.user_agent else None
                    )
                    db.session.add(log)
                    db.session.commit()
            except Exception as e:
                # Fail silently to not disrupt the main flow, but log error in real app
                print(f"Audit Log Error: {e}")
                
            return response
        return decorated_function
    return decorator
