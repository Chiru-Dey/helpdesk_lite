from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..extensions import db
from ..models.comment import Comment
from ..models.ticket import Ticket

comments_bp = Blueprint("comments", __name__)


def can_access_ticket(ticket):
    """Check if the current user is allowed to view/interact with this ticket."""
    if current_user.has_role("admin"):
        return True
    if current_user.has_role("agent"):
        # Agents can access assigned tickets or unassigned tickets
        if ticket.assignee_id == current_user.id or ticket.assignee_id is None:
            return True
        return False
    if current_user.has_role("customer"):
        # Customers can only access their own tickets
        if ticket.customer_id == current_user.id:
            return True
    return False


@comments_bp.get("/tickets/<int:ticket_id>/comments")
def list_comments(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(error="Ticket not found."), 404

    if not can_access_ticket(ticket):
        return jsonify(error="Forbidden."), 403

    comments = db.session.scalars(
        db.select(Comment).filter_by(ticket_id=ticket_id).order_by(Comment.created_at.asc())
    ).all()

    return jsonify(comments=[c.to_dict() for c in comments])


@comments_bp.post("/tickets/<int:ticket_id>/comments")
def add_comment(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(error="Ticket not found."), 404

    if not can_access_ticket(ticket):
        return jsonify(error="Forbidden."), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data.get("body"):
        return jsonify(error="Comment body is required."), 400

    body = str(data["body"]).strip()
    if not body:
        return jsonify(error="Comment body cannot be empty."), 400

    comment = Comment(body=body, ticket_id=ticket.id, author_id=current_user.id)
    db.session.add(comment)
    db.session.commit()

    return jsonify(message="Comment added.", comment=comment.to_dict()), 201