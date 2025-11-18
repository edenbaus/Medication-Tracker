from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date


class ThirdPartyBase(BaseModel):
    """Base schema for third party."""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the third party")
    relationship_type: Optional[str] = Field(None, max_length=100, description="Relationship to user (e.g., Child, Parent, Spouse)")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    notes: Optional[str] = Field(None, description="Additional notes")


class ThirdPartyCreate(ThirdPartyBase):
    """Schema for creating a third party."""
    pass


class ThirdPartyUpdate(BaseModel):
    """Schema for updating a third party."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    relationship_type: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    notes: Optional[str] = None


class ThirdPartyResponse(ThirdPartyBase):
    """Schema for third party response."""
    id: UUID
    user_id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
