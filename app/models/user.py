import secrets
from datetime import datetime, timezone

import bcrypt
from flask_login import UserMixin

from ..extensions import db

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    api_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def generate_api_token(self):
        self.api_token = secrets.token_hex(32)
        return self.api_token

    def has_role(self, role_name):
        return any(r.name == role_name for r in self.roles)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "roles": [r.to_dict() for r in self.roles],
        }