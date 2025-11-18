from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class MedicationBasicInfo(BaseModel):
    """Basic medication information for nested responses."""
    id: UUID
    drug_name: str
    standard_dose: str

    model_config = ConfigDict(from_attributes=True)


class RegimenBase(BaseModel):
    """Base regimen schema with common attributes."""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the regimen")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the regimen")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code (e.g., #FF5733)")


class RegimenCreate(RegimenBase):
    """Schema for creating a new regimen."""
    medication_ids: List[UUID] = Field(default_factory=list, description="List of medication IDs to include in regimen")


class RegimenUpdate(BaseModel):
    """Schema for updating a regimen."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')


class RegimenResponse(RegimenBase):
    """Schema for regimen response."""
    id: UUID
    user_id: UUID
    medications: List[MedicationBasicInfo] = []
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class RegimenList(BaseModel):
    """Schema for paginated list of regimens."""
    regimens: List[RegimenResponse]
    total: int
    page: int = 1
    page_size: int = 50
