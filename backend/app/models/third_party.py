from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime


class ThirdParty(Base):
    """
    Model for third parties (e.g., family members, children, patients)
    that a user can manage medications for.
    """
    __tablename__ = "third_parties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Third party information
    name = Column(String(200), nullable=False)
    relationship_type = Column(String(100))  # e.g., "Child", "Parent", "Spouse", "Patient"
    date_of_birth = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("User", back_populates="third_parties")
    medications = relationship("Medication", back_populates="third_party", cascade="all, delete-orphan")
