from functools import wraps
from flask import request
from flask_login import current_user
from app import db
from app.models.audit import AuditLog
import json

def record_audit(action, model_name=None, details=None, user_id=None):
    """
    Standalone function to log user actions.
    Can be used manually in routes (e.g., login/logout).
    """
    try:
        # Determine user_id: pass explicitly or use current_user
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                # If no user is logged in and no ID provided, we can't link to a user.
                # But for LOGIN attempts (failed) or pre-login, maybe we want to log?
                # For now, we only log authenticated actions or explicit user_id actions (like successful login)
                return

        # Prepare details JSON
        details_json = json.dumps(details) if details else None
        
        # Get IP Address (ProxyFix should handle X-Forwarded-For, but we can be explicit if needed)
        # With ProxyFix, remote_addr is the real client IP.
        ip_address = request.remote_addr
        
        log = AuditLog(
            user_id=user_id,
            action=action,
            model_name=model_name,
            details=details_json,
            ip_address=ip_address,
            user_agent=request.user_agent.string if request.user_agent else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # Fail silently to not disrupt the main flow
        print(f"Audit Log Error: {e}")

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
            
            # Log only if successful (no exception raised)
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

                    record_audit(action, model_name, details)
            except Exception as e:
                print(f"Audit Log Decorator Error: {e}")
                
            return response
        return decorated_function
    return decorator
