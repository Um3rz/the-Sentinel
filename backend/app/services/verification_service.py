"""
Verification Loop Service

Implements the "Marathon" self-correction loop:
- Monitors PR CI/CD status
- Detects build/lint failures
- Auto-corrects code using Gemini
- Iteratively commits fixes until CI passes

Input: PR number, repo URL, original code
Output: Final CI status, corrected code, iteration count
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.services.github_service import GitHubService
from app.services.gemini_service import GeminiService


@dataclass
class VerificationResult:
    """Result of the verification loop."""

    success: bool
    iterations: int
    final_status: str
    error_logs: List[Dict]
    corrected_code: Optional[str] = None
    error_message: Optional[str] = None


class VerificationLoopService:
    """
    Service that monitors PR CI/CD and auto-corrects code.

    The "Marathon Loop":
    1. Create PR with initial fix
    2. Poll CI/CD status
    3. If failed, fetch error logs
    4. Send to Gemini for self-correction
    5. Commit corrected code
    6. Repeat until success or max iterations
    """

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        gemini_service: Optional[GeminiService] = None,
    ):
        """
        Initialize the verification loop service.

        Args:
            github_service: GitHub service instance
            gemini_service: Gemini service instance
        """
        self.github = github_service or GitHubService()
        self.gemini = gemini_service or GeminiService()
        self.max_iterations = 3  # Prevent infinite loops
        self.poll_timeout = 300  # 5 minutes
        self.poll_interval = 15  # 15 seconds between polls

    async def run_verification_loop(
        self,
        repo_url: str,
        pr_number: int,
        branch: str,
        file_path: str,
        original_code: str,
    ) -> VerificationResult:
        """
        Run the full verification and self-correction loop.

        Args:
            repo_url: Full GitHub repository URL
            pr_number: PR number to monitor
            branch: Branch name with the fix
            file_path: Path to the file being fixed
            original_code: The code that was initially submitted

        Returns:
            VerificationResult with final status
        """
        iteration = 0
        current_code = original_code
        error_logs: List[Dict] = []

        while iteration < self.max_iterations:
            iteration += 1

            # Wait for CI to complete
            status = self.github.wait_for_ci_completion(
                repo_url=repo_url,
                pr_number=pr_number,
                timeout_seconds=self.poll_timeout,
                poll_interval=self.poll_interval,
            )

            # Check if CI passed
            if status["state"] == "success":
                return VerificationResult(
                    success=True,
                    iterations=iteration,
                    final_status="success",
                    error_logs=[],
                    corrected_code=current_code,
                )

            # CI failed - get error logs
            error_logs = self.github.get_check_logs(repo_url, pr_number)

            if not error_logs:
                # No specific errors found, but status is not success
                return VerificationResult(
                    success=False,
                    iterations=iteration,
                    final_status=status["state"],
                    error_logs=status["statuses"],
                    corrected_code=current_code,
                    error_message="CI failed but no specific error logs found",
                )

            # Use Gemini to self-correct
            correction = await self.gemini.self_correct(
                original_code=current_code, error_logs=error_logs, file_path=file_path
            )

            corrected_code = correction.get("corrected_code", current_code)

            # Commit the correction
            commit_message = f"fix: Auto-correct CI errors (iteration {iteration})\n\n"
            commit_message += (
                f"Error analysis: {correction.get('error_analysis', 'N/A')}\n"
            )
            commit_message += f"Changes: {correction.get('changes_made', 'N/A')}"

            self.github.commit_file_changes(
                repo_url=repo_url,
                branch=branch,
                file_path=file_path,
                new_content=corrected_code,
                commit_message=commit_message,
            )

            current_code = corrected_code

            # Small delay to let GitHub process the new commit
            await asyncio.sleep(5)

        # Max iterations reached
        return VerificationResult(
            success=False,
            iterations=iteration,
            final_status="timeout",
            error_logs=error_logs if "error_logs" in dir() else [],
            corrected_code=current_code,
            error_message=f"Maximum iterations ({self.max_iterations}) reached without CI success",
        )

    async def quick_check_status(self, repo_url: str, pr_number: int) -> Dict:
        """
        Quick check of PR status without waiting.

        Args:
            repo_url: Full GitHub repository URL
            pr_number: PR number

        Returns:
            Status dict with state and statuses
        """
        return self.github.get_pr_status(repo_url, pr_number)


# Singleton instance for dependency injection
_verification_service: Optional[VerificationLoopService] = None


def get_verification_service(
    github_service: Optional[GitHubService] = None,
    gemini_service: Optional[GeminiService] = None,
) -> VerificationLoopService:
    """
    Get or create the VerificationLoopService singleton.

    Args:
        github_service: Optional GitHub service
        gemini_service: Optional Gemini service

    Returns:
        VerificationLoopService instance
    """
    global _verification_service
    if _verification_service is None:
        _verification_service = VerificationLoopService(github_service, gemini_service)
    return _verification_service
