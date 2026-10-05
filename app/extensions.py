from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cors = CORS()


@login_manager.unauthorized_handler
def unauth_handler():
    return {"error": "Authentication required"}, 401


@login_manager.request_loader
def load_user_from_request(request):
    """Allow API clients to authenticate with 'Authorization: Bearer <token>'."""
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").strip()

    if not token:
        return None

    from .models.user import User

    return db.session.scalar(db.select(User).filter_by(api_token=token))


@login_manager.user_loader
def load_user(user_id):
    from .models.user import User
    return db.session.get(User, int(user_id))