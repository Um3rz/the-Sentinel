"""
User Model

SQLAlchemy model for user data storage in PostgreSQL (Neon).
Replaces the in-memory dictionary with persistent database storage.

Input: User registration/authentication data
Output: Persistent user records in PostgreSQL
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserModel(Base):
    """
    SQLAlchemy model for user storage.

    Maps to 'users' table in PostgreSQL.
    """

    __tablename__ = "users"

    # Primary key - UUID for security and flexibility
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Email is unique and indexed for fast lookups
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Password (nullable for OAuth-only users)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Profile info
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # GitHub OAuth fields
    github_id: Mapped[Optional[int]] = mapped_column(
        Integer, unique=True, index=True, nullable=True
    )
    github_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_access_token: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    # Verification status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=datetime.utcnow, nullable=True
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, github_username={self.github_username})>"


# ---------------------------------------------------------------------------
# CRUD Operations
# ---------------------------------------------------------------------------


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserModel]:
    """
    Lookup user by email.

    Args:
        db: Database session
        email: User email address

    Returns:
        UserModel if found, None otherwise
    """
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    return result.scalar_one_or_none()


async def get_user_by_github_id(
    db: AsyncSession, github_id: int
) -> Optional[UserModel]:
    """
    Lookup user by GitHub ID.

    Args:
        db: Database session
        github_id: GitHub user ID

    Returns:
        UserModel if found, None otherwise
    """
    result = await db.execute(select(UserModel).where(UserModel.github_id == github_id))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[UserModel]:
    """
    Lookup user by ID.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        UserModel if found, None otherwise
    """
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserModel) -> UserModel:
    """
    Create a new user in the database.

    Args:
        db: Database session
        user: UserModel instance to create

    Returns:
        Created UserModel

    Raises:
        IntegrityError: If email or github_id already exists
    """
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: UserModel) -> UserModel:
    """
    Update an existing user.

    Args:
        db: Database session
        user: UserModel with updated fields

    Returns:
        Updated UserModel
    """
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: UserModel) -> None:
    """
    Delete a user from the database.

    Args:
        db: Database session
        user: UserModel to delete
    """
    await db.delete(user)
    await db.commit()


# ---------------------------------------------------------------------------
# UserRecord compatibility layer (for existing code)
# ---------------------------------------------------------------------------


class UserRecord:
    """
    Compatibility layer to maintain existing code structure.

    This class wraps UserModel to provide the same interface as the
    old in-memory UserRecord for backward compatibility.

    Note: New code should use UserModel directly with async operations.
    """

    def __init__(
        self,
        email: str,
        hashed_password: Optional[str] = None,
        full_name: Optional[str] = None,
        github_id: Optional[int] = None,
        github_username: Optional[str] = None,
        github_access_token: Optional[str] = None,
        is_verified: bool = False,
    ):
        self.id: str = str(uuid.uuid4())
        self.email: str = email
        self.hashed_password: Optional[str] = hashed_password
        self.full_name: Optional[str] = full_name
        self.github_id: Optional[int] = github_id
        self.github_username: Optional[str] = github_username
        self.github_access_token: Optional[str] = github_access_token
        self.is_verified: bool = is_verified
        self.created_at: datetime = datetime.utcnow()

    @classmethod
    def from_model(cls, model: UserModel) -> "UserRecord":
        """Create UserRecord from UserModel."""
        record = cls.__new__(cls)
        record.id = model.id
        record.email = model.email
        record.hashed_password = model.hashed_password
        record.full_name = model.full_name
        record.github_id = model.github_id
        record.github_username = model.github_username
        record.github_access_token = model.github_access_token
        record.is_verified = model.is_verified
        record.created_at = model.created_at
        return record

    def to_model(self) -> UserModel:
        """Convert UserRecord to UserModel."""
        return UserModel(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            github_id=self.github_id,
            github_username=self.github_username,
            github_access_token=self.github_access_token,
            is_verified=self.is_verified,
            created_at=self.created_at,
        )


# Legacy functions for backward compatibility
# These will use the in-memory fallback if db is not provided
# but should be replaced with async versions above

# In-memory fallback for development/testing
_users_db: dict = {}


def get_user_by_email_sync(email: str) -> Optional[UserRecord]:
    """Synchronous version - uses in-memory fallback."""
    return _users_db.get(email)


def get_user_by_github_id_sync(github_id: int) -> Optional[UserRecord]:
    """Synchronous version - uses in-memory fallback."""
    for user in _users_db.values():
        if user.github_id == github_id:
            return user
    return None


def create_user_sync(user: UserRecord) -> UserRecord:
    """Synchronous version - uses in-memory fallback."""
    if user.email in _users_db:
        raise ValueError("User with this email already exists")
    _users_db[user.email] = user
    return user


def update_user_sync(user: UserRecord) -> UserRecord:
    """Synchronous version - uses in-memory fallback."""
    _users_db[user.email] = user
    return user
