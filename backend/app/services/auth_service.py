"""
Authentication Service

Handles password hashing, JWT creation/validation, and user authentication.

Input: Credentials (email+password) or JWT token strings.
Output: Hashed passwords, JWT tokens, or validated user data.
"""

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import UserModel, get_user_by_email


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """
    Hash a plaintext password with bcrypt.

    Input: Plain-text password string.
    Output: Bcrypt hash string.
    """
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    Input: Plain-text password and its bcrypt hash.
    Output: True if they match, False otherwise.
    """
    return pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT Token management
# ---------------------------------------------------------------------------
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Input:
        data: Payload dict (must contain 'sub' key with user email).
        expires_delta: Optional custom expiration.
    Output:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    Input: JWT token string.
    Output: Decoded payload dict, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Current-user dependency helper
# ---------------------------------------------------------------------------
async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[UserModel]:
    """
    Validate email + password and return the user.

    Input:
        db: Database session
        email: User email
        password: Plain-text password
    Output: UserModel if valid, None otherwise.
    """
    user = await get_user_by_email(db, email)
    if user is None:
        return None
    if user.hashed_password is None:
        # OAuth-only user – cannot login with password
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
