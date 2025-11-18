import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


# Junction table for many-to-many relationship between medications and tags
medication_tags = Table(
    'medication_tags',
    Base.metadata,
    Column('medication_id', UUID(as_uuid=True), ForeignKey('medications.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False)
)


class Tag(Base):
    """
    Tag model for organizing and categorizing medications.

    Tags allow users to create custom categories with colors for easy
    filtering and visual organization of medications.
    """
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String, nullable=False)
    color = Column(String, nullable=True)  # Hex color code for UI display (e.g., "#FF5733")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tags")
    medications = relationship("Medication", secondary=medication_tags, back_populates="tags")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uix_user_tag_name'),
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', user_id={self.user_id})>"
