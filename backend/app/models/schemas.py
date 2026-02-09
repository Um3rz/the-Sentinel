"""
Pydantic Models for API Request/Response schemas.

These models define the structure of data flowing through the API,
ensuring type safety and automatic validation.
"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class AnalyzeRequest(BaseModel):
    """
    Request model for the /analyze endpoint.
    
    At least one of: video, images, or deployed_url must be provided
    for visual context. repo_url is always required.
    """
    repo_url: HttpUrl = Field(
        ...,
        description="GitHub repository URL (e.g., https://github.com/user/repo)"
    )
    deployed_url: Optional[HttpUrl] = Field(
        None,
        description="Deployed application URL for automatic screenshot capture"
    )
    bug_description: Optional[str] = Field(
        None,
        description="Optional text description of the bug or desired UI change"
    )
    github_token: Optional[str] = Field(
        None,
        description="GitHub token for private repos (optional)"
    )


class AnalysisFix(BaseModel):
    """Model for a single code fix."""
    file_path: str = Field(..., description="Path to file that needs changes")
    code: str = Field(..., description="The corrected code block")


class AnalysisResult(BaseModel):
    """Model for the analysis result from Gemini."""
    analysis: str = Field(..., description="Description of the visual bug")
    severity: str = Field(..., description="High/Medium/Low severity rating")
    fix: AnalysisFix = Field(..., description="The code fix details")


class AnalyzeResponse(BaseModel):
    """
    Response model for the /analyze endpoint.
    """
    status: str = Field(..., description="success or error")
    job_id: str = Field(..., description="Unique identifier for this analysis job")
    analysis: Optional[AnalysisResult] = Field(
        None,
        description="Analysis result with fix details"
    )
    pr_url: Optional[str] = Field(
        None,
        description="URL to the created Pull Request"
    )
    screenshots_captured: Optional[List[str]] = Field(
        None,
        description="List of screenshot paths captured from deployed_url"
    )
    error: Optional[str] = Field(None, description="Error message if status is error")


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str
    version: str


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Request body for user registration."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: Optional[str] = Field(None, description="Display name")


class UserLogin(BaseModel):
    """Request body for email/password login."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserOut(BaseModel):
    """Public user profile returned by API."""
    id: str
    email: str
    full_name: Optional[str] = None
    github_username: Optional[str] = None
    is_verified: bool = False


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
