from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..extensions import db
from ..models.comment import Comment
from ..models.ticket import Ticket
from ..models.user import Role, User
from ..utils.decorators import roles_required

users_bp = Blueprint("users", __name__)

VALID_ROLES = {"admin", "agent", "customer"}


@users_bp.get("/users")
@roles_required("admin")
def list_users():
    role_name = request.args.get("role")

    query = db.select(User).order_by(User.id)

    if role_name:
        query = query.join(User.roles).filter(Role.name == role_name)

    users = db.session.scalars(query).all()

    return jsonify(users=[u.to_dict() for u in users])


@users_bp.get("/users/<int:user_id>")
@roles_required("admin")
def get_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify(error="User not found."), 404

    return jsonify(user=user.to_dict())


@users_bp.post("/users")
@roles_required("admin")
def create_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Invalid JSON payload."), 400

    missing = [
        field
        for field in ("email", "password", "name")
        if not str(data.get(field, "")).strip()
    ]

    if missing:
        return jsonify(error=f"Missing required fields: {', '.join(missing)}."), 400

    email = str(data["email"]).strip().lower()
    password = str(data["password"]).strip()
    name = str(data["name"]).strip()

    if len(password) < 8:
        return jsonify(error="Password must be at least 8 characters long."), 400

    if db.session.scalar(db.select(User).filter_by(email=email)):
        return jsonify(error="Email is already registered."), 409

    role_names = data.get("roles", ["customer"])

    if not isinstance(role_names, list) or not role_names:
        return jsonify(error="Roles must be a non-empty list."), 400

    invalid_roles = [r for r in role_names if r not in VALID_ROLES]

    if invalid_roles:
        return jsonify(error=f"Invalid roles: {', '.join(invalid_roles)}."), 400

    user = User(email=email, name=name)
    user.set_password(password)

    for role_name in role_names:
        role = db.session.scalar(db.select(Role).filter_by(name=role_name))

        if not role:
            return jsonify(error=f"Role '{role_name}' does not exist. Run the seed script."), 500

        user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return jsonify(message="User created.", user=user.to_dict()), 201


@users_bp.patch("/users/<int:user_id>")
@roles_required("admin")
def update_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify(error="User not found."), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Invalid JSON payload."), 400

    if "name" in data:
        name = str(data["name"]).strip()

        if not name:
            return jsonify(error="Name cannot be empty."), 400

        user.name = name

    if "active" in data:
        if not isinstance(data["active"], bool):
            return jsonify(error="Field 'active' must be a boolean."), 400

        if user.id == current_user.id and data["active"] is False:
            return jsonify(error="You cannot deactivate your own account."), 400

        user.active = data["active"]

    if "roles" in data:
        role_names = data["roles"]

        if not isinstance(role_names, list) or not role_names:
            return jsonify(error="Roles must be a non-empty list."), 400

        invalid_roles = [r for r in role_names if r not in VALID_ROLES]

        if invalid_roles:
            return jsonify(error=f"Invalid roles: {', '.join(invalid_roles)}."), 400

        if user.id == current_user.id and "admin" not in role_names:
            return jsonify(error="You cannot remove your own admin role."), 400

        new_roles = []

        for role_name in role_names:
            role = db.session.scalar(db.select(Role).filter_by(name=role_name))

            if not role:
                return jsonify(error=f"Role '{role_name}' does not exist."), 500

            new_roles.append(role)

        user.roles = new_roles

    db.session.commit()

    return jsonify(message="User updated.", user=user.to_dict())


@users_bp.delete("/users/<int:user_id>")
@roles_required("admin")
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify(error="User not found."), 404

    if user.id == current_user.id:
        return jsonify(error="You cannot delete your own account."), 400

    has_customer_tickets = db.session.scalar(
        db.select(Ticket.id).where(Ticket.customer_id == user.id).limit(1)
    )
    has_assigned_tickets = db.session.scalar(
        db.select(Ticket.id).where(Ticket.assignee_id == user.id).limit(1)
    )
    has_comments = db.session.scalar(
        db.select(Comment.id).where(Comment.author_id == user.id).limit(1)
    )

    if has_customer_tickets or has_assigned_tickets or has_comments:
        return jsonify(
            error="User has related tickets or comments. Deactivate the user instead of deleting."
        ), 409

    db.session.delete(user)
    db.session.commit()

    return jsonify(message="User deleted.")