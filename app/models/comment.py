from datetime import datetime, timezone
from ..extensions import db


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ticket = db.relationship("Ticket", backref=db.backref("comments", lazy="dynamic", cascade="all, delete-orphan"))
    author = db.relationship("User", backref="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "body": self.body,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author": self.author.to_dict() if self.author else None,
        }