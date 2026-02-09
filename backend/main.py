import sys
import asyncio

# Fix Playwright subprocess on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.analyze import router as analyze_router
from app.api.auth import router as auth_router
from app.core.database import create_tables

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="The VibeChecker API",
    description="Autonomous Vibe Engineering Agent Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS – allow frontend origins from env
import os
_frontend = os.getenv("FRONTEND_URL", "http://localhost:3000")
origins = [
    "http://localhost:3000",
    _frontend,
]
# Deduplicate
origins = list(set(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include Routers
app.include_router(analyze_router)
app.include_router(auth_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    import logging

    logger = logging.getLogger(__name__)
    try:
        await create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        logger.error("Make sure DATABASE_URL is configured correctly in .env")
        raise


@app.get("/api/v1/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint for monitoring."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/openapi.json")
async def get_openapi():
    """Return the OpenAPI schema as JSON."""
    from fastapi.openapi.utils import get_openapi

    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
