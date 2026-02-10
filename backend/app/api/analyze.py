"""
Analyze Endpoint

Handles the core /analyze API that:
1. Accepts video/images/deployed_url + repo_url
2. Captures visual context if deployed_url is provided
3. Fetches relevant code from GitHub
4. Orchestrates the Gemini analysis pipeline
5. Creates a PR with the fix
6. Runs verification loop for self-correction

This is the main entry point for the Vibe Loop.
"""

import uuid
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    BackgroundTasks,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.schemas import AnalyzeResponse, AnalysisResult, AnalysisFix
from app.models.user import UserModel
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.services.url_capture_service import get_url_capture_service, URLCaptureService
from app.services.github_service import get_github_service, GitHubService
from app.services.gemini_service import get_gemini_service, GeminiService
from app.services.verification_service import (
    get_verification_service,
    VerificationLoopService,
)

router = APIRouter(prefix="/api/v1", tags=["Analysis"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("5/hour")
async def analyze_vibe(
    request: Request,
    background_tasks: BackgroundTasks,
    repo_url: str = Form(..., description="GitHub repository URL"),
    deployed_url: Optional[str] = Form(
        None, description="Deployed app URL for auto-capture"
    ),
    bug_description: Optional[str] = Form(None, description="Bug description"),
    github_token: Optional[str] = Form(
        None, description="GitHub token for private repos"
    ),
    video: Optional[UploadFile] = File(None, description="Video file (MP4/WebM)"),
    images: List[UploadFile] = File(default=[], description="Image files (PNG/JPG)"),
    url_capture_service: URLCaptureService = Depends(get_url_capture_service),
    current_user: UserModel = Depends(get_current_user),
) -> AnalyzeResponse:
    """
    Analyze visual context against a codebase and generate fixes.

    This is the main "Vibe Loop" endpoint that:
    1. Captures screenshots from deployed_url (if provided)
    2. Saves uploaded video/images temporarily
    3. Fetches relevant code from the repository
    4. Uses Gemini to analyze and generate fixes
    5. Creates a PR with the fix
    6. (Optional) Runs verification loop for CI self-correction

    Input:
        - repo_url: Required GitHub repository URL
        - deployed_url: Optional URL to capture screenshots from
        - bug_description: Optional text description of the issue
        - github_token: Optional GitHub token for private repos
        - video: Optional video file upload
        - images: Optional image file uploads

    Output:
        - AnalyzeResponse with analysis results and PR URL

    Raises:
        HTTPException: If no visual input provided or processing fails
    """
    job_id = str(uuid.uuid4())
    temp_dir: Optional[Path] = None
    screenshots_captured: Optional[List[str]] = None
    image_paths: List[str] = []
    video_path: Optional[str] = None

    try:
        # Validate: At least one visual input required
        has_visual_input = (
            video is not None or len(images) > 0 or deployed_url is not None
        )

        if not has_visual_input:
            raise HTTPException(
                status_code=400,
                detail="At least one visual input required: video, images, or deployed_url",
            )

        # Create temp directory for file storage
        temp_dir = Path(tempfile.mkdtemp(prefix=f"vibe_check_{job_id}_"))

        # Step 1: Capture screenshots if deployed_url provided
        if deployed_url:
            try:
                screenshots_captured = await url_capture_service.capture_visual_context(
                    url=str(deployed_url)
                )
                image_paths.extend(screenshots_captured)
            except Exception as e:
                import logging

                logging.warning(f"URL capture skipped: {e}")
                screenshots_captured = None

        # Step 2: Save uploaded images
        if images:
            for i, image in enumerate(images):
                if image and image.filename:
                    image_path = temp_dir / f"upload_{i}_{image.filename}"
                    with open(image_path, "wb") as f:
                        content = await image.read()
                        f.write(content)
                    image_paths.append(str(image_path))

        # Step 3: Save uploaded video
        if video and video.filename:
            video_path = str(temp_dir / f"video_{video.filename}")
            with open(video_path, "wb") as f:
                content = await video.read()
                f.write(content)

        # Initialize services
        # Priority: 1) Form token, 2) User's OAuth token, 3) Env token
        effective_github_token = (
            github_token or current_user.github_access_token or settings.GITHUB_TOKEN
        )

        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"Using GitHub token from: {'form' if github_token else 'oauth' if current_user.github_access_token else 'env' if settings.GITHUB_TOKEN else 'none'}"
        )
        logger.info(
            f"Token length: {len(effective_github_token) if effective_github_token else 0}"
        )

        if not effective_github_token:
            raise HTTPException(
                status_code=400,
                detail="No GitHub token available. Please provide a token or connect your GitHub account.",
            )

        try:
            github_service = get_github_service(effective_github_token)
        except ValueError as e:
            error_msg = str(e)
            if (
                "Invalid GitHub token" in error_msg
                or "401" in error_msg
                or "Bad credentials" in error_msg
            ):
                raise HTTPException(
                    status_code=401,
                    detail="Your GitHub token has expired or is invalid. Please re-authenticate with GitHub or provide a valid GitHub token.",
                )
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize GitHub service: {error_msg}",
            )
        gemini_service = get_gemini_service()

        # Step 4: Fetch repository file tree
        try:
            file_tree = github_service.get_file_tree(repo_url)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch repository: {str(e)}. Ensure the repo exists and is accessible.",
            )

        # Check if user has write access
        try:
            has_write_access = github_service.check_write_access(repo_url)
            logger.info(f"User has write access: {has_write_access}")
            if not has_write_access:
                raise HTTPException(
                    status_code=403,
                    detail=f"GitHub token for user '{github_service.user_login}' does not have write access to this repository. "
                    "Please ensure: 1) Your token has 'repo' scope (for private repos) or 'public_repo' scope (for public repos), "
                    "2) You are a collaborator on this repository or it's your own repository, "
                    "3) If it's someone else's repo, fork it first and analyze your fork.",
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Could not verify write access: {e}")

        # Step 5: Scout for relevant files
        file_paths = [f["path"] for f in file_tree if f["type"] == "blob"]
        relevant_files = await gemini_service.scout_files(
            file_tree=file_paths, bug_description=bug_description
        )

        # Step 6: Fetch content of relevant files
        code_context = {}
        for file_path in relevant_files[:10]:  # Limit to 10 files
            content = github_service.get_file_content(repo_url, file_path)
            if content:
                code_context[file_path] = content

        if not code_context:
            raise HTTPException(
                status_code=400,
                detail="Could not fetch any relevant code files from the repository",
            )

        # Step 7: Analyze with Gemini
        try:
            if video_path:
                analysis_result = await gemini_service.analyze_video_frames(
                    video_path=video_path,
                    code_context=code_context,
                    bug_description=bug_description,
                )
            else:
                analysis_result = await gemini_service.analyze_vibe(
                    code_context=code_context,
                    bug_description=bug_description,
                    image_paths=image_paths if image_paths else None,
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

        # Validate analysis result
        fix = analysis_result.get("fix", {})
        if not fix or not fix.get("file_path") or not fix.get("code"):
            return AnalyzeResponse(
                status="success",
                job_id=job_id,
                analysis=AnalysisResult(
                    analysis=analysis_result.get(
                        "analysis", "No specific issue identified"
                    ),
                    severity=analysis_result.get("severity", "Low"),
                    fix=AnalysisFix(file_path="", code=""),
                ),
                pr_url=None,
                screenshots_captured=screenshots_captured,
                error=None,
            )

        # Step 8: Create branch and commit fix
        branch_name = f"fix-vibe-{job_id[:8]}"
        try:
            github_service.create_branch(repo_url, "main", branch_name)
        except Exception as e:
            error_str = str(e).lower()
            # Check for permission errors
            if "403" in error_str or "forbidden" in error_str:
                raise HTTPException(
                    status_code=403,
                    detail="GitHub token doesn't have write access to this repository. Please ensure: 1) You're using a Personal Access Token with 'repo' scope, 2) You have push access to the repository, or 3) Connect your GitHub account via OAuth.",
                )
            # Try with master
            try:
                github_service.create_branch(repo_url, "master", branch_name)
            except Exception as e2:
                raise HTTPException(
                    status_code=500, detail=f"Failed to create branch: {str(e2)}"
                )

        # Commit the fix
        commit_message = (
            f"fix: {analysis_result.get('analysis', 'Automated vibe fix')[:50]}"
        )
        try:
            github_service.commit_file_changes(
                repo_url=repo_url,
                branch=branch_name,
                file_path=fix["file_path"],
                new_content=fix["code"],
                commit_message=commit_message,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to commit changes: {str(e)}"
            )

        # Step 9: Create PR
        try:
            pr_body = f"## Automated Vibe Fix\n\n"
            pr_body += f"**Issue:** {analysis_result.get('analysis', 'N/A')}\n\n"
            pr_body += f"**Severity:** {analysis_result.get('severity', 'N/A')}\n\n"
            pr_body += f"**File Modified:** `{fix['file_path']}`\n\n"
            pr_body += "---\n"
            pr_body += (
                "*This PR was automatically generated by The Sentinel (VibeChecker)*"
            )

            pr = github_service.create_pull_request(
                repo_url=repo_url,
                title=f"fix: {analysis_result.get('analysis', 'Vibe fix')[:50]}",
                body=pr_body,
                head_branch=branch_name,
                base_branch="main",
            )

            pr_url = pr.html_url
            pr_number = pr.number

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create pull request: {str(e)}"
            )

        # Step 10: Start background verification loop (optional, runs asynchronously)
        # This runs in the background and doesn't block the response
        # verification_service = get_verification_service(github_service, gemini_service)
        # background_tasks.add_task(
        #     verification_service.run_verification_loop,
        #     repo_url, pr_number, branch_name, fix["file_path"], fix["code"]
        # )

        # Build response
        return AnalyzeResponse(
            status="success",
            job_id=job_id,
            analysis=AnalysisResult(
                analysis=analysis_result.get("analysis", ""),
                severity=analysis_result.get("severity", "Medium"),
                fix=AnalysisFix(file_path=fix["file_path"], code=fix["code"]),
            ),
            pr_url=pr_url,
            screenshots_captured=screenshots_captured,
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        import logging

        logging.exception("Unexpected error in analyze_vibe")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        # Cleanup temp directory
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
