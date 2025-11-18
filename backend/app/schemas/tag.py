from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re


class TagBase(BaseModel):
    """Base tag schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=7)

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """Validate that color is a valid hex color code."""
        if v is not None:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('color must be a valid hex color code (e.g., #FF5733)')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate tag name."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError('name cannot be empty or whitespace only')
        return v


class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating an existing tag."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=7)

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """Validate that color is a valid hex color code."""
        if v is not None:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('color must be a valid hex color code (e.g., #FF5733)')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate tag name."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('name cannot be empty or whitespace only')
        return v


class TagResponse(TagBase):
    """Schema for tag responses."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagWithMedicationCount(TagResponse):
    """Schema for tag with medication count."""
    medication_count: int = 0


class TagList(BaseModel):
    """Schema for tag list responses."""
    tags: List[TagResponse]
    total: int
