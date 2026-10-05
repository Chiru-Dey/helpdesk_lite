from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..extensions import db
from ..models.category import Category
from ..models.ticket import Ticket
from ..models.user import User
from ..utils.decorators import roles_required

tickets_bp = Blueprint("tickets", __name__)

VALID_STATUSES = ["open", "in_progress", "resolved", "closed"]
VALID_PRIORITIES = ["low", "medium", "high", "urgent"]


@tickets_bp.post("/tickets")
def create_ticket():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Invalid JSON payload."), 400

    subject = str(data.get("subject", "")).strip()
    description = str(data.get("description", "")).strip()
    priority = str(data.get("priority", "medium")).strip().lower()
    category_id = data.get("category_id")

    if not subject or not description or not category_id:
        return jsonify(error="Subject, description, and category_id are required."), 400

    if priority not in VALID_PRIORITIES:
        return jsonify(error=f"Invalid priority. Must be one of: {', '.join(VALID_PRIORITIES)}"), 400

    category = db.session.get(Category, category_id)
    if not category:
        return jsonify(error="Category not found."), 404

    # Determine customer
    customer_id = data.get("customer_id")
    if customer_id:
        if not current_user.has_role("admin"):
            return jsonify(error="Only admins can create tickets for other users."), 403
        customer = db.session.get(User, customer_id)
        if not customer:
            return jsonify(error="Customer not found."), 404
    else:
        customer = current_user

    ticket = Ticket(
        subject=subject,
        description=description,
        priority=priority,
        status="open",
        customer_id=customer.id,
        category_id=category.id,
    )

    # Optional assignee
    assignee_id = data.get("assignee_id")
    if assignee_id:
        if not current_user.has_role("admin"):
            return jsonify(error="Only admins can assign tickets during creation."), 403
        assignee = db.session.get(User, assignee_id)
        if not assignee or not assignee.has_role("agent"):
            return jsonify(error="Assignee must be a valid agent."), 400
        ticket.assignee_id = assignee.id

    db.session.add(ticket)
    db.session.commit()

    return jsonify(message="Ticket created.", ticket=ticket.to_dict()), 201


@tickets_bp.get("/tickets")
def list_tickets():
    query = db.select(Ticket)

    if current_user.has_role("customer"):
        query = query.filter_by(customer_id=current_user.id)
    elif current_user.has_role("agent"):
        # Agents see tickets assigned to them OR unassigned open tickets
        query = query.filter(
            db.or_(
                Ticket.assignee_id == current_user.id,
                db.and_(Ticket.assignee_id == None, Ticket.status == "open")
            )
        )
    # Admin sees all (no filter applied)

    status = request.args.get("status")
    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)

    priority = request.args.get("priority")
    if priority and priority in VALID_PRIORITIES:
        query = query.filter_by(priority=priority)

    tickets = db.session.scalars(query.order_by(Ticket.created_at.desc())).all()
    return jsonify(tickets=[t.to_dict() for t in tickets])


@tickets_bp.get("/tickets/<int:ticket_id>")
def get_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(error="Ticket not found."), 404

    if current_user.has_role("customer") and ticket.customer_id != current_user.id:
        return jsonify(error="Forbidden."), 403
        
    if current_user.has_role("agent") and not current_user.has_role("admin"):
        if ticket.assignee_id != current_user.id and ticket.assignee_id is not None:
            return jsonify(error="Forbidden."), 403

    return jsonify(ticket=ticket.to_dict())


@tickets_bp.patch("/tickets/<int:ticket_id>")
def update_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(error="Ticket not found."), 404

    # Customers can only update their own open tickets (subject/description)
    if current_user.has_role("customer"):
        if ticket.customer_id != current_user.id:
            return jsonify(error="Forbidden."), 403
        if ticket.status != "open":
            return jsonify(error="Customers can only edit open tickets."), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Invalid JSON payload."), 400

    if "subject" in data:
        ticket.subject = str(data["subject"]).strip()
    if "description" in data:
        ticket.description = str(data["description"]).strip()
        
    if "priority" in data and not current_user.has_role("customer"):
        priority = str(data["priority"]).strip().lower()
        if priority not in VALID_PRIORITIES:
            return jsonify(error=f"Invalid priority."), 400
        ticket.priority = priority
        
    if "category_id" in data and not current_user.has_role("customer"):
        category = db.session.get(Category, data["category_id"])
        if not category:
            return jsonify(error="Category not found."), 404
        ticket.category_id = category.id

    db.session.commit()
    return jsonify(message="Ticket updated.", ticket=ticket.to_dict())


@tickets_bp.delete("/tickets/<int:ticket_id>")
@roles_required("admin")
def delete_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(error="Ticket not found."), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify(message="Ticket deleted.")


@tickets_bp.post("/tickets/<int:ticket_id>/assign")
@roles_required("admin")
def assign_ticket(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(error="Ticket not found."), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "assignee_id" not in data:
        return jsonify(error="assignee_id is required."), 400

    assignee_id = data["assignee_id"]
    if assignee_id is None:
        ticket.assignee_id = None
    else:
        assignee = db.session.get(User, assignee_id)
        if not assignee or not assignee.has_role("agent"):
            return jsonify(error="Assignee must be a valid agent."), 400
        ticket.assignee_id = assignee.id

    db.session.commit()
    return jsonify(message="Ticket assigned.", ticket=ticket.to_dict())


@tickets_bp.post("/tickets/<int:ticket_id>/status")
@roles_required("agent", "admin")
def update_status(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify(error="Ticket not found."), 404

    # Agents can only update status of tickets assigned to them or unassigned
    if current_user.has_role("agent") and not current_user.has_role("admin"):
        if ticket.assignee_id != current_user.id and ticket.assignee_id is not None:
            return jsonify(error="Forbidden."), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "status" not in data:
        return jsonify(error="status is required."), 400

    status = str(data["status"]).strip().lower()
    if status not in VALID_STATUSES:
        return jsonify(error=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"), 400

    ticket.status = status
    now = datetime.now(timezone.utc)

    if status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = now
    elif status == "closed" and not ticket.closed_at:
        ticket.closed_at = now

    db.session.commit()
    return jsonify(message="Ticket status updated.", ticket=ticket.to_dict())