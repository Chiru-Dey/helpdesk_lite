from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models.ticket import Ticket


def get_dashboard_data():
    today_start = datetime.now(timezone.utc).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    # 1. High-level metrics
    total_tickets = db.session.scalar(db.select(func.count(Ticket.id)))
    open_tickets = db.session.scalar(
        db.select(func.count(Ticket.id)).filter_by(status="open")
    )
    in_progress_tickets = db.session.scalar(
        db.select(func.count(Ticket.id)).filter_by(status="in_progress")
    )
    resolved_today = db.session.scalar(
        db.select(func.count(Ticket.id)).filter(
            Ticket.status == "resolved",
            Ticket.resolved_at >= today_start,
        )
    )
    closed_tickets = db.session.scalar(
        db.select(func.count(Ticket.id)).filter_by(status="closed")
    )

    # 2. Group by Priority
    priority_rows = db.session.execute(
        db.select(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority)
    ).all()
    priority_map = dict(priority_rows)

    tickets_by_priority = {
        "low": priority_map.get("low", 0),
        "medium": priority_map.get("medium", 0),
        "high": priority_map.get("high", 0),
        "urgent": priority_map.get("urgent", 0),
    }

    # 3. Group by Status
    status_rows = db.session.execute(
        db.select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
    ).all()
    status_map = dict(status_rows)

    tickets_by_status = {
        "open": status_map.get("open", 0),
        "in_progress": status_map.get("in_progress", 0),
        "resolved": status_map.get("resolved", 0),
        "closed": status_map.get("closed", 0),
    }

    # 4. Recent Tickets (eager loading relationships to prevent N+1 queries)
    recent_tickets = db.session.scalars(
        db.select(Ticket)
        .options(
            selectinload(Ticket.customer),
            selectinload(Ticket.assignee),
            selectinload(Ticket.category),
        )
        .order_by(Ticket.created_at.desc())
        .limit(5)
    ).all()

    return {
        "total_tickets": total_tickets or 0,
        "open_tickets": open_tickets or 0,
        "in_progress_tickets": in_progress_tickets or 0,
        "resolved_today": resolved_today or 0,
        "closed_tickets": closed_tickets or 0,
        "tickets_by_priority": tickets_by_priority,
        "tickets_by_status": tickets_by_status,
        "recent_tickets": [t.to_dict() for t in recent_tickets],
    }