from functools import wraps
from flask import jsonify
from flask_login import current_user, login_required


def roles_required(*role_names):
    """
    Decorator that ensures the current user has at least one of the required roles.
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            for role in role_names:
                if current_user.has_role(role):
                    return f(*args, **kwargs)
            return jsonify({"error": f"Forbidden. Required roles: {', '.join(role_names)}"}), 403
        return decorated_function
    return decorator