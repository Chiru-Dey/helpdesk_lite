import re

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models.user import Role, User

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_json_payload():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    return data


def missing_fields(data, fields):
    return [field for field in fields if not str(data.get(field, "")).strip()]


def error_response(message, status_code):
    return jsonify(error=message), status_code


@auth_bp.post("/auth/register")
def register():
    if current_user.is_authenticated:
        return error_response("You are already logged in.", 400)

    data = get_json_payload()

    if data is None:
        return error_response("Invalid JSON payload.", 400)

    missing = missing_fields(data, ["email", "password", "name"])

    if missing:
        return error_response(
            f"Missing required fields: {', '.join(missing)}.",
            400,
        )

    email = str(data["email"]).strip().lower()
    password = str(data["password"]).strip()
    name = str(data["name"]).strip()

    if not EMAIL_REGEX.fullmatch(email):
        return error_response("Invalid email address.", 400)

    if len(password) < 8:
        return error_response("Password must be at least 8 characters long.", 400)

    existing_user = db.session.scalar(db.select(User).filter_by(email=email))

    if existing_user:
        return error_response("Email is already registered.", 409)

    customer_role = db.session.scalar(db.select(Role).filter_by(name="customer"))

    if not customer_role:
        return error_response("Default customer role missing. Run the seed script first.", 500)

    user = User(email=email, name=name)
    user.set_password(password)
    user.roles.append(customer_role)

    db.session.add(user)
    db.session.commit()

    login_user(user)

    return jsonify(message="Registration successful.", user=user.to_dict()), 201


@auth_bp.post("/auth/login")
def login():
    if current_user.is_authenticated:
        return error_response("You are already logged in.", 400)

    data = get_json_payload()

    if data is None:
        return error_response("Invalid JSON payload.", 400)

    missing = missing_fields(data, ["email", "password"])

    if missing:
        return error_response(
            f"Missing required fields: {', '.join(missing)}.",
            400,
        )

    email = str(data["email"]).strip().lower()
    password = str(data["password"]).strip()

    user = db.session.scalar(db.select(User).filter_by(email=email))

    if not user or not user.check_password(password):
        return error_response("Invalid email or password.", 401)

    if not user.active:
        return error_response("Your account is inactive.", 403)

    login_user(user)

    return jsonify(message="Login successful.", user=user.to_dict())


@auth_bp.post("/auth/logout")
@login_required
def logout():
    logout_user()

    return jsonify(message="Logout successful.")


@auth_bp.get("/auth/me")
@login_required
def me():
    return jsonify(user=current_user.to_dict())