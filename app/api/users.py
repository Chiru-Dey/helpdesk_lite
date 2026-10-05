from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models.user import Role, User
from ..utils.decorators import roles_required

users_bp = Blueprint("users", __name__)


@users_bp.get("/users")
@roles_required("admin")
def list_users():
    role_name = request.args.get("role")

    query = db.select(User).order_by(User.id)

    if role_name:
        query = query.join(User.roles).filter(Role.name == role_name)

    users = db.session.scalars(query).all()

    return jsonify(users=[u.to_dict() for u in users])