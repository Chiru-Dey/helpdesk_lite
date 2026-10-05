from datetime import datetime, timezone
from ..extensions import db


class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False)
    priority = db.Column(db.String(20), default="medium", nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    resolved_at = db.Column(db.DateTime(timezone=True))
    closed_at = db.Column(db.DateTime(timezone=True))

    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    customer = db.relationship("User", foreign_keys=[customer_id], backref="created_tickets")
    assignee = db.relationship("User", foreign_keys=[assignee_id], backref="assigned_tickets")
    category = db.relationship("Category", backref="tickets")

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "customer": self.customer.to_dict() if self.customer else None,
            "assignee": self.assignee.to_dict() if self.assignee else None,
            "category": self.category.to_dict() if self.category else None,
        }