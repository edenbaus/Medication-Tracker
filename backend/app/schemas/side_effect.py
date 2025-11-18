from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.side_effect import SeverityLevel


class SideEffectBase(BaseModel):
    """Base schema for side effect data."""
    medication_id: UUID
    severity: SeverityLevel
    description: str = Field(..., min_length=1, max_length=5000)
    occurred_at: datetime


class SideEffectCreate(SideEffectBase):
    """Schema for creating a side effect report."""
    pass


class SideEffectUpdate(BaseModel):
    """Schema for updating a side effect report."""
    severity: Optional[SeverityLevel] = None
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    occurred_at: Optional[datetime] = None


class SideEffectResponse(SideEffectBase):
    """Schema for side effect response."""
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SideEffectWithMedication(SideEffectResponse):
    """Schema for side effect with medication details."""
    medication: Optional[dict] = None

    class Config:
        from_attributes = True
