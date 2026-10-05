from flask import Blueprint, jsonify, request
from flask_login import login_required

from ..extensions import db
from ..models.category import Category
from ..utils.decorators import roles_required

categories_bp = Blueprint("categories", __name__)


@categories_bp.get("/categories")
@login_required
def list_categories():
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return jsonify(categories=[c.to_dict() for c in categories])


@categories_bp.post("/categories")
@roles_required("admin")
def create_category():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data.get("name"):
        return jsonify(error="Name is required."), 400

    name = str(data["name"]).strip()
    description = str(data.get("description", "")).strip()

    if not name:
        return jsonify(error="Name cannot be empty."), 400

    existing = db.session.scalar(db.select(Category).filter_by(name=name))

    if existing:
        return jsonify(error="Category already exists."), 409

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    return jsonify(message="Category created.", category=category.to_dict()), 201


@categories_bp.patch("/categories/<int:category_id>")
@roles_required("admin")
def update_category(category_id):
    category = db.session.get(Category, category_id)

    if not category:
        return jsonify(error="Category not found."), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Invalid JSON payload."), 400

    if "name" in data:
        name = str(data["name"]).strip()

        if not name:
            return jsonify(error="Name cannot be empty."), 400

        existing = db.session.scalar(db.select(Category).filter_by(name=name))

        if existing and existing.id != category.id:
            return jsonify(error="Category name already exists."), 409

        category.name = name

    if "description" in data:
        category.description = str(data["description"]).strip()

    db.session.commit()

    return jsonify(message="Category updated.", category=category.to_dict())


@categories_bp.delete("/categories/<int:category_id>")
@roles_required("admin")
def delete_category(category_id):
    category = db.session.get(Category, category_id)

    if not category:
        return jsonify(error="Category not found."), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify(message="Category deleted.")