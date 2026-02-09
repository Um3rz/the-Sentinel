"""
Authentication API Endpoints

Provides:
  POST /api/v1/auth/register  – Email/password registration
  POST /api/v1/auth/login     – Email/password login (returns JWT)
  GET  /api/v1/auth/github    – Redirect to GitHub OAuth
  GET  /api/v1/auth/github/callback – Exchange code for token, create/auth user
  GET  /api/v1/auth/me        – Return current authenticated user
"""

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from fastapi import Depends
from fastapi.responses import RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.schemas import (
    UserCreate,
    UserLogin,
    UserOut,
    TokenResponse,
)
from app.models.user import (
    UserModel,
    create_user,
    get_user_by_email,
    get_user_by_github_id,
    update_user,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    hash_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Email / Password Auth
# ---------------------------------------------------------------------------

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_USER_EMAILS_URL = "https://api.github.com/user/emails"


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(
    request: Request, body: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserOut:
    """
    Register a new user with email and password.

    Input: UserCreate body (email, password, optional full_name).
    Output: UserOut with the new user profile.
    Logic:
      1. Check if email already exists.
      2. Hash the password.
      3. Store the user.
      4. Return the user profile.
    """
    existing = await get_user_by_email(db, body.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = UserModel(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        is_verified=False,
    )

    try:
        await create_user(db, user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        github_username=None,
        is_verified=user.is_verified,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request, body: UserLogin, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Login with email and password and receive a JWT.

    Input: UserLogin body (email, password).
    Output: TokenResponse with access_token and token_type.
    Logic:
      1. Authenticate credentials.
      2. Generate JWT containing the user's email in 'sub'.
    """
    user = await authenticate_user(db, body.email, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.email, "uid": user.id})
    return TokenResponse(access_token=token, token_type="bearer")


# ---------------------------------------------------------------------------
# GitHub OAuth
# ---------------------------------------------------------------------------


@router.get("/github")
async def github_login():
    """
    Redirect the user to GitHub's OAuth authorization page.

    Input: None.
    Output: 302 redirect to GitHub.
    Logic: Constructs the OAuth authorize URL with required scopes.
    """
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured. Set GITHUB_CLIENT_ID in .env",
        )

    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": f"{settings.FRONTEND_URL}/auth/github/callback",
        "scope": "read:user user:email repo",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"{GITHUB_AUTHORIZE_URL}?{query}")


@router.get("/github/callback", response_model=TokenResponse)
@limiter.limit("10/minute")
async def github_callback(
    request: Request, code: str, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Exchange the GitHub OAuth code for an access token and create/login user.

    Input: 'code' query parameter from GitHub redirect.
    Output: TokenResponse with a JWT for the authenticated user.
    Logic:
      1. Exchange code → GitHub access token.
      2. Fetch GitHub user profile + email.
      3. Find or create local UserModel.
      4. Issue our own JWT.
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured",
        )

    # Step 1 – Exchange code for GitHub token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

    if token_resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange GitHub code for token",
        )

    token_data = token_resp.json()
    gh_access_token = token_data.get("access_token")
    if not gh_access_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GitHub OAuth error: {token_data.get('error_description', 'unknown')}",
        )

    # Step 2 – Fetch GitHub user profile
    headers = {
        "Authorization": f"Bearer {gh_access_token}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        user_resp = await client.get(GITHUB_USER_URL, headers=headers)
        emails_resp = await client.get(GITHUB_USER_EMAILS_URL, headers=headers)

    if user_resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch GitHub user profile",
        )

    gh_user = user_resp.json()
    gh_id: int = gh_user["id"]
    gh_username: str = gh_user.get("login", "")
    gh_name: str = gh_user.get("name") or gh_username

    # Get primary email
    primary_email = gh_user.get("email")
    if not primary_email and emails_resp.status_code == 200:
        for em in emails_resp.json():
            if em.get("primary"):
                primary_email = em["email"]
                break
    if not primary_email:
        primary_email = f"{gh_username}@users.noreply.github.com"

    # Step 3 – Find or create user
    user = await get_user_by_github_id(db, gh_id)
    if user is None:
        user = await get_user_by_email(db, primary_email)

    if user is None:
        # Brand-new user via GitHub
        user = UserModel(
            email=primary_email,
            github_id=gh_id,
            github_username=gh_username,
            github_access_token=gh_access_token,
            full_name=gh_name,
            is_verified=True,  # GitHub email is trusted
        )
        await create_user(db, user)
    else:
        # Existing user – update GitHub fields
        user.github_id = gh_id
        user.github_username = gh_username
        user.github_access_token = gh_access_token
        if not user.full_name:
            user.full_name = gh_name
        await update_user(db, user)

    # Step 4 – Issue JWT
    token = create_access_token(data={"sub": user.email, "uid": user.id})
    return TokenResponse(access_token=token, token_type="bearer")


# ---------------------------------------------------------------------------
# Current user endpoint
# ---------------------------------------------------------------------------


@router.get("/me", response_model=UserOut)
async def get_me(current_user: UserModel = Depends(get_current_user)) -> UserOut:
    """
    Return the currently authenticated user's profile.

    Input: Bearer token (via dependency).
    Output: UserOut.
    """
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        github_username=current_user.github_username,
        is_verified=current_user.is_verified,
    )
