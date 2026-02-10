"""
Gemini Service

Handles all AI/ML interactions with Google's Gemini API:
- Analyzing visual context (screenshots/video) against code
- Identifying bugs and discrepancies
- Generating code fixes
- Self-correcting based on CI/CD errors

Input: Visual media (images/video), code context, bug descriptions
Output: Analysis results, code fixes, error corrections
"""

import json
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import settings


# System prompt for the main analysis
SYSTEM_PROMPT_SENTINEL = """You are The Sentinel, an elite Design Engineer and QA Specialist.
You possess 'Vibe Intelligence'—the ability to map visual behavior in images/video to the underlying code logic.

**Your Task:**
1. Analyze the provided screenshots or video frames.
2. Read the provided Codebase Context and Bug Description (if any).
3. Identify where the Codebase implementation diverges from the visual behavior seen in the media (or where it conflicts with the bug description).
4. Generate the SPECIFIC code fix. Do not explain *how* to fix it; provide the *actual code block* to replace.

**Output Format (JSON Only):**
{
    "analysis": "Short description of the visual bug",
    "severity": "High/Medium/Low",
    "fix": {
        "file_path": "path/to/file",
        "code": "The full corrected code block"
    }
}

**Guidelines:**
- Be precise and specific about the issue
- Provide complete, working code in the fix.code field
- The code should be production-ready and follow best practices
- Match the style and conventions of the existing codebase"""


# System prompt for self-correction based on CI errors
SYSTEM_PROMPT_SELF_CORRECT = """You are The Sentinel in Self-Correction Mode.
Your previous code fix was submitted to CI/CD and FAILED.

**Your Task:**
1. Analyze the provided CI/CD error logs
2. Look at the code you previously suggested
3. Fix the errors and provide a corrected version

**Error Categories to Handle:**
- Syntax errors (missing brackets, typos)
- Type errors (TypeScript type mismatches)
- Import errors (missing or incorrect imports)
- Lint errors (ESLint/Prettier violations)
- Runtime errors (undefined variables, null references)

**Output Format (JSON Only):**
{
    "error_analysis": "Description of what went wrong",
    "corrected_code": "The fixed code block",
    "changes_made": "Brief explanation of the changes"
}

**Guidelines:**
- Fix ALL errors, not just the first one
- Maintain the original intent of the fix
- Ensure the code passes common lint rules
- Add any missing imports or type definitions"""


# System prompt for file scouting
SYSTEM_PROMPT_SCOUT = """You are The Sentinel in Scout Mode.
Your job is to identify which files in a codebase are likely relevant to a bug.

**Your Task:**
Given a file tree listing and a bug description, return ONLY the file paths
that are likely relevant to fix the bug.

**Output Format (JSON Only):**
{
    "relevant_files": ["path/to/file1", "path/to/file2"],
    "reasoning": "Brief explanation of why these files were selected"
}

**Guidelines:**
- Select files that likely contain the bug or need modification
- Focus on frontend files (JSX, TSX, CSS, styled-components)
- Include configuration files if relevant (tailwind.config, etc.)
- Limit to 5-10 most relevant files
- Be conservative - only select files you're confident about"""


class GeminiService:
    """
    Service for AI-powered code analysis and generation using Google's Gemini API.

    Handles:
    - Visual bug detection from screenshots/video
    - Code analysis and fix generation
    - Self-correction based on CI/CD feedback
    - Smart file scouting in repositories
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini service.

        Args:
            api_key: Gemini API key. Uses settings.GEMINI_API_KEY if not provided.
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in .env")

        genai.configure(api_key=self.api_key)

        # Configure safety settings to allow code generation
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        # Initialize model instances for different tasks
        self.analysis_model = genai.GenerativeModel(
            model_name="gemini-3-pro-preview", safety_settings=self.safety_settings
        )

    def _encode_image(self, image_path: str) -> Dict[str, str]:
        """
        Encode an image file for the Gemini API.

        Args:
            image_path: Path to the image file

        Returns:
            Dict with mime_type and data for Gemini
        """
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Determine MIME type from extension
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        mime_type = mime_types.get(ext, "image/png")

        return {"mime_type": mime_type, "data": image_data}

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from Gemini response, handling various formats.

        Args:
            text: Raw response text from Gemini

        Returns:
            Parsed JSON as dict

        Raises:
            ValueError: If JSON cannot be parsed
        """
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to find JSON in the text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except:
                    pass
            raise ValueError(
                f"Failed to parse JSON response: {e}\nResponse: {text[:200]}"
            )

    async def scout_files(
        self, file_tree: List[str], bug_description: Optional[str] = None
    ) -> List[str]:
        """
        Identify relevant files for a bug fix.

        Args:
            file_tree: List of file paths in the repository
            bug_description: Description of the bug

        Returns:
            List of file paths that are likely relevant
        """
        # Build the prompt
        prompt = SYSTEM_PROMPT_SCOUT + "\n\n"
        prompt += "**File Tree:**\n"
        for path in file_tree[:100]:  # Limit to first 100 files
            prompt += f"- {path}\n"

        if bug_description:
            prompt += f"\n**Bug Description:** {bug_description}\n"

        prompt += "\nIdentify the most relevant files for fixing this bug."

        # Call Gemini
        response = await self.analysis_model.generate_content_async(prompt)

        try:
            result = self._parse_json_response(response.text)
            return result.get("relevant_files", [])
        except Exception as e:
            # Fallback: return files with common web extensions
            return [
                path
                for path in file_tree
                if any(
                    ext in path.lower()
                    for ext in [
                        ".tsx",
                        ".jsx",
                        ".ts",
                        ".js",
                        ".css",
                        ".scss",
                        ".styled",
                        "component",
                        "button",
                        "modal",
                        "page",
                    ]
                )
                and not "node_modules" in path
            ][:10]

    async def analyze_vibe(
        self,
        code_context: Dict[str, str],
        bug_description: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze visual context against code to identify bugs.

        Args:
            code_context: Dict mapping file paths to their contents
            bug_description: Optional text description of the bug
            image_paths: Optional list of screenshot paths

        Returns:
            Analysis result with fix details:
                - analysis: Description of the bug
                - severity: High/Medium/Low
                - fix: Dict with file_path and code
        """
        # Build the content parts
        content_parts = []

        # Add system prompt
        prompt = SYSTEM_PROMPT_SENTINEL + "\n\n"

        # Add code context
        prompt += "**Codebase Context:**\n\n"
        for file_path, file_content in code_context.items():
            prompt += f"### {file_path}\n```\n{file_content[:2000]}\n```\n\n"

        if bug_description:
            prompt += f"**Bug Description:** {bug_description}\n\n"

        prompt += "Analyze the provided visual context and code. Identify discrepancies and provide the fix."

        content_parts.append(prompt)

        # Add images if provided
        if image_paths:
            for image_path in image_paths:
                try:
                    image_data = self._encode_image(image_path)
                    content_parts.append(image_data)
                except Exception as e:
                    print(f"Warning: Could not encode image {image_path}: {e}")

        # Call Gemini
        response = await self.analysis_model.generate_content_async(content_parts)

        # Parse response
        result = self._parse_json_response(response.text)

        # Validate required fields
        required_fields = ["analysis", "severity", "fix"]
        for field in required_fields:
            if field not in result:
                result[field] = (
                    "Unknown" if field != "fix" else {"file_path": "", "code": ""}
                )

        return result

    async def self_correct(
        self, original_code: str, error_logs: List[Dict[str, str]], file_path: str
    ) -> Dict[str, str]:
        """
        Self-correct code based on CI/CD error logs.

        Args:
            original_code: The code that failed CI
            error_logs: List of error log dicts from CI/CD
            file_path: Path to the file being fixed

        Returns:
            Correction result:
                - error_analysis: Description of errors
                - corrected_code: Fixed code
                - changes_made: Explanation of changes
        """
        # Build error log text
        error_text = "\n\n".join(
            [
                f"Check: {log['name']}\nConclusion: {log['conclusion']}\n"
                f"Title: {log.get('output_title', 'N/A')}\n"
                f"Summary: {log.get('output_summary', 'N/A')}"
                for log in error_logs
            ]
        )

        prompt = SYSTEM_PROMPT_SELF_CORRECT + "\n\n"
        prompt += f"**File:** {file_path}\n\n"
        prompt += f"**Original Code:**\n```\n{original_code}\n```\n\n"
        prompt += f"**CI/CD Error Logs:**\n{error_text}\n\n"
        prompt += "Please provide the corrected code that fixes all errors."

        # Call Gemini
        response = await self.analysis_model.generate_content_async(prompt)

        # Parse response
        result = self._parse_json_response(response.text)

        # Validate required fields
        required_fields = ["error_analysis", "corrected_code", "changes_made"]
        for field in required_fields:
            if field not in result:
                result[field] = "" if field != "error_analysis" else "Unknown error"

        return result

    async def analyze_video_frames(
        self,
        video_path: str,
        code_context: Dict[str, str],
        bug_description: Optional[str] = None,
        frame_interval: int = 5,
    ) -> Dict[str, Any]:
        """
        Extract frames from video and analyze them.

        Args:
            video_path: Path to the video file
            code_context: Dict mapping file paths to their contents
            bug_description: Optional bug description
            frame_interval: Extract frame every N seconds

        Returns:
            Analysis result with timestamps of issues found
        """
        # Note: Video frame extraction would require cv2 or similar
        # For now, we'll use the video file as-is if Gemini supports it
        # or extract key frames as images

        # For simplicity, treat it as a single analysis for now
        # In production, you'd extract frames and analyze multiple
        desc = bug_description or ""
        return await self.analyze_vibe(
            code_context=code_context,
            bug_description=desc + f" (Video: {video_path})",
        )


# Singleton instance for dependency injection
_gemini_service: Optional[GeminiService] = None


def get_gemini_service(api_key: Optional[str] = None) -> GeminiService:
    """
    Get or create the GeminiService singleton.

    Args:
        api_key: Optional API key to override default

    Returns:
        GeminiService instance
    """
    global _gemini_service
    if _gemini_service is None or api_key:
        _gemini_service = GeminiService(api_key)
    return _gemini_service
