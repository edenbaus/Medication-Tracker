import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SeverityLevel(str, enum.Enum):
    """Enum for side effect severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class SideEffect(Base):
    """
    Side effect model for tracking medication side effects.

    Records side effects experienced by users, their severity, and when they occurred.
    """
    __tablename__ = "side_effects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    medication_id = Column(UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    severity = Column(Enum(SeverityLevel, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    description = Column(Text, nullable=False)
    occurred_at = Column(DateTime, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="side_effects")
    medication = relationship("Medication", back_populates="side_effects")

    def __repr__(self):
        return f"<SideEffect(id={self.id}, medication_id={self.medication_id}, severity={self.severity})>"
