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


@login_manager.user_loader
def load_user(user_id):
    from .models.user import User
    return db.session.get(User, int(user_id))