#!/usr/bin/env python3
"""
Build verification script for Render deployment.
Checks that all critical components are properly configured.
"""

import sys
import os


def check_environment():
    """Verify critical environment variables are set."""
    required = ["DATABASE_URL", "GEMINI_API_KEY", "SECRET_KEY"]
    optional = ["GITHUB_TOKEN", "GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"]

    missing_required = []
    for key in required:
        if not os.getenv(key):
            missing_required.append(key)

    if missing_required:
        print(
            f"❌ Missing required environment variables: {', '.join(missing_required)}"
        )
        return False

    print("✅ All required environment variables are set")

    # Check optional
    for key in optional:
        if os.getenv(key):
            print(f"✅ {key} is configured")
        else:
            print(f"⚠️  {key} is not set (optional)")

    return True


def check_imports():
    """Verify all critical imports work."""
    try:
        print("Checking imports...")
        import fastapi

        print("✅ FastAPI")

        import sqlalchemy

        print("✅ SQLAlchemy")

        import asyncpg

        print("✅ asyncpg")

        import google.generativeai

        print("✅ Google Generative AI")

        import github

        print("✅ PyGithub")

        from playwright.async_api import async_playwright

        print("✅ Playwright")

        # Check app imports
        from app.core.config import settings

        print("✅ App config")

        from app.core.database import engine

        print("✅ Database engine")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def check_database():
    """Verify database connection."""
    try:
        import asyncio
        from app.core.database import engine

        async def test_connection():
            from sqlalchemy import text

            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.fetchone()

        asyncio.run(test_connection())
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("VibeAuditor Build Verification")
    print("=" * 60)

    checks = [
        ("Environment Variables", check_environment),
        ("Python Imports", check_imports),
        ("Database Connection", check_database),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        results.append(check_func())

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
