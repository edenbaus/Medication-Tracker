from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User
from app.schemas.user import UserAdminResponse, UserUpdate, UserList

router = APIRouter()


@router.get("/users", response_model=UserList)
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_admin: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only).

    Supports pagination and filtering by admin status.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_admin: Filter by admin status (optional)
        current_admin: Current authenticated admin user
        db: Database session

    Returns:
        UserList: Paginated list of users
    """
    query = db.query(User)

    # Filter by admin status if specified
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    return UserList(
        users=users,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit
    )


@router.get("/users/{user_id}", response_model=UserAdminResponse)
def get_user_by_id(
    user_id: UUID,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID (admin only).

    Args:
        user_id: ID of the user to retrieve
        current_admin: Current authenticated admin user
        db: Database session

    Returns:
        UserAdminResponse: User details

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/users/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's details (admin only).

    Allows updating username, email, and admin status.

    Args:
        user_id: ID of the user to update
        user_update: Updated user data
        current_admin: Current authenticated admin user
        db: Database session

    Returns:
        UserAdminResponse: Updated user details

    Raises:
        HTTPException: If user not found or username/email already exists
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if updating to a username that already exists
    if user_update.username and user_update.username != user.username:
        existing_user = db.query(User).filter(
            and_(
                User.username == user_update.username,
                User.id != user_id
            )
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{user_update.username}' already exists"
            )

    # Check if updating to an email that already exists
    if user_update.email and user_update.email != user.email:
        existing_user = db.query(User).filter(
            and_(
                User.email == user_update.email,
                User.id != user_id
            )
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_update.email}' already exists"
            )

    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).

    This will CASCADE delete all user's medications, tags, logs, etc.
    Admins cannot delete themselves.

    Args:
        user_id: ID of the user to delete
        current_admin: Current authenticated admin user
        db: Database session

    Returns:
        None

    Raises:
        HTTPException: If user not found or admin tries to delete themselves
    """
    # Prevent admin from deleting themselves
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return None
