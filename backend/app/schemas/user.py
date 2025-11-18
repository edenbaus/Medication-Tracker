from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (without password)."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[str] = None
    email: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user details (admin only)."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None


class UserAdminResponse(UserBase):
    """Schema for user response including admin status."""
    id: UUID
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    """Schema for paginated list of users."""
    users: List[UserAdminResponse]
    total: int
    page: int = 1
    page_size: int = 50
