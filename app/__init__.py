import os

from flask import Flask

from .config import Config
from .extensions import cors, db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path,
        "helpdesk.db",
    )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                ]
            }
        },
        supports_credentials=True,
    )

    from . import models  # noqa: F401

    from .api.auth import auth_bp
    from .api.categories import categories_bp
    from .api.comments import comments_bp
    from .api.dashboard import dashboard_bp
    from .api.health import health_bp
    from .api.tickets import tickets_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(categories_bp, url_prefix="/api")
    app.register_blueprint(comments_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(tickets_bp, url_prefix="/api")

    return app