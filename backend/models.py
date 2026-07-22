import uuid
from datetime import datetime

from extensions import db


def gen_uuid():
    return str(uuid.uuid4())


class Inquiry(db.Model):
    """A message submitted through the public 'Let's Connect' form."""

    __tablename__ = "inquiries"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    full_name = db.Column("fullName", db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, index=True)
    company = db.Column(db.String(150), nullable=True)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="NEW", index=True)
    created_at = db.Column(
        "createdAt", db.DateTime, default=datetime.utcnow, index=True
    )
    updated_at = db.Column(
        "updatedAt", db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self, full=False):
        data = {
            "id": self.id,
            "fullName": self.full_name,
            "email": self.email,
            "company": self.company,
            "subject": self.subject,
            "status": self.status,
            "createdAt": self.created_at.isoformat() + "Z",
            "updatedAt": self.updated_at.isoformat() + "Z",
        }
        if full:
            data["message"] = self.message
        else:
            # List views only need a short preview, not the full message.
            data["messagePreview"] = (
                (self.message[:80] + "…") if len(self.message) > 80 else self.message
            )
        return data
