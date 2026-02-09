"""
Application Configuration

Loads environment variables via pydantic-settings.
Input: .env file or OS environment variables.
Output: A validated Settings singleton.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Central configuration object loaded from .env.

    Input: Environment variables or .env file.
    Output: Typed, validated settings.
    """

    # --- General ---
    APP_ENV: str = "development"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/vibechecker"

    # --- AI ---
    GEMINI_API_KEY: str = ""

    # --- GitHub ---
    GITHUB_TOKEN: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # --- Auth ---
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"

    # --- Rate Limiting ---
    RATE_LIMIT_PER_MINUTE: int = 60

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Frontend URL (for OAuth redirect) ---
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
