"""
GitHub Service

Handles all GitHub API interactions for the VibeChecker:
- Fetching repository file trees and content
- Creating branches and commits
- Opening Pull Requests
- Polling CI/CD status for the verification loop

Input: Repository URLs, file paths, code changes
Output: File contents, PR URLs, CI status
"""

import base64
import re
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from github import Github, GithubException
from github.Repository import Repository
from github.Branch import Branch
from github.PullRequest import PullRequest
from github.Commit import Commit

from app.core.config import settings


class GitHubService:
    """
    Service for interacting with GitHub repositories.

    Handles fetching code, creating branches, committing changes,
    opening PRs, and monitoring CI/CD status.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub service.

        Args:
            token: GitHub personal access token. Uses settings.GITHUB_TOKEN if not provided.
        """
        self.token = token or settings.GITHUB_TOKEN
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN in .env")

        self.github = Github(self.token)

        # Verify token and get user info
        try:
            self.user = self.github.get_user()
            self.user_login = self.user.login
        except Exception as e:
            raise ValueError(f"Invalid GitHub token: {str(e)}")

    def parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
        """
        Parse a GitHub repository URL into owner and repo name.

        Args:
            repo_url: Full GitHub URL (e.g., https://github.com/user/repo)

        Returns:
            Tuple of (owner, repo_name)

        Raises:
            ValueError: If URL is not a valid GitHub repo URL
        """
        # Handle various GitHub URL formats
        patterns = [
            r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/\.]+)",
            r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/\.]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group("owner"), match.group("repo")

        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

    def get_repository(self, repo_url: str) -> Repository:
        """
        Get a GitHub repository object.

        Args:
            repo_url: Full GitHub repository URL

        Returns:
            PyGithub Repository object

        Raises:
            GithubException: If repository not found or no access
        """
        owner, repo_name = self.parse_repo_url(repo_url)
        return self.github.get_repo(f"{owner}/{repo_name}")

    def check_write_access(self, repo_url: str) -> bool:
        """
        Check if the authenticated user has write access to a repository.

        Args:
            repo_url: Full GitHub repository URL

        Returns:
            True if user has write access, False otherwise
        """
        try:
            repo = self.get_repository(repo_url)
            # Check if user is a collaborator with push access
            return repo.has_in_collaborators(self.user_login)
        except Exception:
            return False

    def get_file_tree(self, repo_url: str, branch: str = "main") -> List[Dict]:
        """
        Fetch the file tree of a repository.

        Args:
            repo_url: Full GitHub repository URL
            branch: Branch to fetch tree from (default: main)

        Returns:
            List of dicts with file info: path, type, size
        """
        repo = self.get_repository(repo_url)

        # Try main, fallback to master
        try:
            tree = repo.get_git_tree(branch, recursive=True)
        except GithubException:
            branch = "master"
            tree = repo.get_git_tree(branch, recursive=True)

        files = []
        for item in tree.tree:
            files.append(
                {
                    "path": item.path,
                    "type": item.type,
                    "size": item.size if hasattr(item, "size") else None,
                    "sha": item.sha,
                }
            )

        return files

    def get_file_content(
        self, repo_url: str, file_path: str, branch: str = "main"
    ) -> Optional[str]:
        """
        Fetch the content of a specific file.

        Args:
            repo_url: Full GitHub repository URL
            file_path: Path to file within the repo
            branch: Branch to fetch from

        Returns:
            File content as string, or None if not found
        """
        repo = self.get_repository(repo_url)

        try:
            from github.ContentFile import ContentFile

            content = repo.get_contents(file_path, ref=branch)
            # Handle case where content might be a list (directory)
            if isinstance(content, list):
                return None
            # Type check for ContentFile
            if not isinstance(content, ContentFile):
                return None
            if content.encoding == "base64":
                return base64.b64decode(content.content).decode("utf-8")
            return content.content
        except GithubException:
            return None

    def get_files_by_extensions(
        self,
        repo_url: str,
        extensions: List[str],
        max_files: int = 50,
        branch: str = "main",
    ) -> Dict[str, str]:
        """
        Fetch all files with specific extensions.

        Args:
            repo_url: Full GitHub repository URL
            extensions: List of file extensions (e.g., [".tsx", ".css"])
            max_files: Maximum number of files to fetch
            branch: Branch to fetch from

        Returns:
            Dict mapping file paths to their contents
        """
        tree = self.get_file_tree(repo_url, branch)
        files_content = {}

        for item in tree:
            if item["type"] == "blob":
                # Check if file has one of the desired extensions
                if any(item["path"].endswith(ext) for ext in extensions):
                    content = self.get_file_content(repo_url, item["path"], branch)
                    if content:
                        files_content[item["path"]] = content

                    if len(files_content) >= max_files:
                        break

        return files_content

    def create_branch(
        self, repo_url: str, base_branch: str, new_branch_name: str
    ) -> str:
        """
        Create a new branch from an existing branch.

        Args:
            repo_url: Full GitHub repository URL
            base_branch: Branch to base from (e.g., main)
            new_branch_name: Name for the new branch

        Returns:
            Name of the created branch
        """
        repo = self.get_repository(repo_url)

        # Get the base branch reference
        try:
            base_ref = repo.get_git_ref(f"heads/{base_branch}")
        except GithubException:
            # Fallback to master
            base_branch = "master"
            base_ref = repo.get_git_ref(f"heads/{base_branch}")

        # Create new branch from base
        repo.create_git_ref(
            ref=f"refs/heads/{new_branch_name}", sha=base_ref.object.sha
        )

        return new_branch_name

    def commit_file_changes(
        self,
        repo_url: str,
        branch: str,
        file_path: str,
        new_content: str,
        commit_message: str,
    ) -> Commit:
        """
        Commit changes to a file.

        Args:
            repo_url: Full GitHub repository URL
            branch: Branch to commit to
            file_path: Path to file to update
            new_content: New file content
            commit_message: Commit message

        Returns:
            The created Commit object
        """
        repo = self.get_repository(repo_url)

        # Get current file (if it exists)
        try:
            from github.ContentFile import ContentFile

            contents = repo.get_contents(file_path, ref=branch)
            # Check if contents is a single file (not a list)
            if isinstance(contents, ContentFile):
                # Update existing file
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=new_content,
                    sha=contents.sha,  # type: ignore
                    branch=branch,
                )
                return result["commit"]  # type: ignore
            else:
                raise GithubException(404, "Path is a directory, not a file", None)
        except GithubException:
            # Create new file
            result = repo.create_file(
                path=file_path,
                message=commit_message,
                content=new_content,
                branch=branch,
            )
            return result["commit"]  # type: ignore

    def create_pull_request(
        self,
        repo_url: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
    ) -> PullRequest:
        """
        Create a pull request.

        Args:
            repo_url: Full GitHub repository URL
            title: PR title
            body: PR description
            head_branch: Branch with changes
            base_branch: Branch to merge into

        Returns:
            Created PullRequest object
        """
        repo = self.get_repository(repo_url)

        try:
            pr = repo.create_pull(
                title=title, body=body, head=head_branch, base=base_branch
            )
        except GithubException:
            # Try with master as base
            pr = repo.create_pull(
                title=title, body=body, head=head_branch, base="master"
            )

        return pr

    def get_pr_status(self, repo_url: str, pr_number: int) -> Dict:
        """
        Get the CI/CD status of a pull request.

        Args:
            repo_url: Full GitHub repository URL
            pr_number: PR number

        Returns:
            Dict with status info:
                - state: pending, success, failure, error
                - statuses: List of individual check statuses
                - total_count: Total number of checks
        """
        repo = self.get_repository(repo_url)
        pr = repo.get_pull(pr_number)

        # Get combined status
        head_sha = pr.head.sha
        commit = repo.get_commit(head_sha)
        combined_status = commit.get_status()  # type: ignore

        statuses = []
        for status in combined_status.statuses:  # type: ignore
            statuses.append(
                {
                    "context": status.context,
                    "state": status.state,
                    "description": status.description,
                    "target_url": status.target_url,
                }
            )

        # Also check check runs (GitHub Actions, etc.)
        check_runs = commit.get_check_runs()  # type: ignore
        for run in check_runs:
            output_title = ""
            if run.output:
                # Handle CheckRunOutput properly
                try:
                    output_title = getattr(run.output, "title", "") or ""
                except:
                    output_title = ""
            statuses.append(
                {
                    "context": run.name,
                    "state": self._map_conclusion_to_state(run.conclusion),
                    "description": output_title,
                    "target_url": run.html_url,
                }
            )

        return {
            "state": combined_status.state,  # type: ignore
            "statuses": statuses,
            "total_count": len(statuses),
        }

    def _map_conclusion_to_state(self, conclusion: Optional[str]) -> str:
        """Map check run conclusion to status state."""
        if conclusion is None:
            return "pending"
        if conclusion == "success":
            return "success"
        if conclusion == "failure":
            return "failure"
        return "error"

    def wait_for_ci_completion(
        self,
        repo_url: str,
        pr_number: int,
        timeout_seconds: int = 300,
        poll_interval: int = 10,
    ) -> Dict:
        """
        Poll CI/CD status until completion or timeout.

        Args:
            repo_url: Full GitHub repository URL
            pr_number: PR number
            timeout_seconds: Maximum time to wait
            poll_interval: Seconds between polls

        Returns:
            Final status dict with 'state' and 'statuses'
        """
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < timeout_seconds:
            status = self.get_pr_status(repo_url, pr_number)

            # Check if all checks have completed
            if status["state"] != "pending":
                return status

            time.sleep(poll_interval)

        # Timeout reached, return current status
        return self.get_pr_status(repo_url, pr_number)

    def get_check_logs(self, repo_url: str, pr_number: int) -> List[Dict]:
        """
        Get detailed logs from failed checks.

        Args:
            repo_url: Full GitHub repository URL
            pr_number: PR number

        Returns:
            List of dicts with check name, conclusion, and logs
        """
        repo = self.get_repository(repo_url)
        pr = repo.get_pull(pr_number)
        head_sha = pr.head.sha

        logs = []
        check_runs = repo.get_commit(head_sha).get_check_runs()  # type: ignore

        for run in check_runs:
            if run.conclusion in ["failure", "error"]:
                # Safely extract output fields
                output_title = ""
                output_summary = ""
                if run.output:
                    output_title = getattr(run.output, "title", "") or ""
                    output_summary = getattr(run.output, "summary", "") or ""

                logs.append(
                    {
                        "name": run.name,
                        "conclusion": run.conclusion,
                        "output_title": output_title,
                        "output_summary": output_summary,
                        "html_url": run.html_url,
                    }
                )

        return logs

    def close_pr(self, repo_url: str, pr_number: int) -> None:
        """
        Close a pull request without merging.

        Args:
            repo_url: Full GitHub repository URL
            pr_number: PR number to close
        """
        repo = self.get_repository(repo_url)
        pr = repo.get_pull(pr_number)
        pr.edit(state="closed")


# Singleton instance for dependency injection
_github_service: Optional[GitHubService] = None


def get_github_service(token: Optional[str] = None) -> GitHubService:
    """
    Get or create the GitHubService singleton.

    Args:
        token: Optional GitHub token to override default

    Returns:
        GitHubService instance
    """
    global _github_service
    if _github_service is None or token:
        _github_service = GitHubService(token)
    return _github_service
