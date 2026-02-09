"""
URL Capture Service

Uses Playwright to capture screenshots from deployed URLs
for visual analysis by the Gemini API.

Input: A deployed URL (e.g., https://myapp.vercel.app)
Output: List of file paths to captured screenshots
Logic: Launches headless browser, navigates to URL, captures full-page screenshot
"""

import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


class URLCaptureService:
    """
    Service for capturing visual context from deployed URLs.
    
    Uses Playwright headless browser to capture high-fidelity screenshots
    that can be fed into the Gemini analysis pipeline.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the URL Capture Service.
        
        Args:
            output_dir: Directory to save screenshots. Defaults to system temp.
        """
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_visual_context(
        self,
        url: str,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        wait_for_network_idle: bool = True,
        timeout_ms: int = 30000
    ) -> List[str]:
        """
        Capture screenshots from a deployed URL.
        
        Args:
            url: The URL to capture (e.g., https://myapp.vercel.app)
            viewport_width: Browser viewport width in pixels
            viewport_height: Browser viewport height in pixels
            wait_for_network_idle: Whether to wait for network to be idle
            timeout_ms: Maximum time to wait for page load in milliseconds
            
        Returns:
            List of absolute paths to captured screenshot files (PNG format)
            
        Raises:
            PlaywrightTimeout: If page fails to load within timeout
            Exception: For other browser/network errors
        """
        screenshots: List[str] = []
        capture_id = str(uuid.uuid4())[:8]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                device_scale_factor=2  # High-DPI for better quality
            )
            page = await context.new_page()
            
            try:
                # Navigate to URL
                await page.goto(
                    url,
                    wait_until="networkidle" if wait_for_network_idle else "load",
                    timeout=timeout_ms
                )
                
                # Capture full-page screenshot
                full_page_path = self.output_dir / f"capture_{capture_id}_full.png"
                await page.screenshot(
                    path=str(full_page_path),
                    full_page=True
                )
                screenshots.append(str(full_page_path))
                
                # Capture above-the-fold (viewport) screenshot
                viewport_path = self.output_dir / f"capture_{capture_id}_viewport.png"
                await page.screenshot(
                    path=str(viewport_path),
                    full_page=False
                )
                screenshots.append(str(viewport_path))
                
            except PlaywrightTimeout as e:
                raise PlaywrightTimeout(f"Timeout loading URL {url}: {e}")
            except Exception as e:
                raise Exception(f"Failed to capture URL {url}: {e}")
            finally:
                await browser.close()
        
        return screenshots
    
    async def capture_with_interactions(
        self,
        url: str,
        interactions: Optional[List[dict]] = None
    ) -> List[str]:
        """
        Capture screenshots after performing interactions (clicks, scrolls).
        
        This is useful for capturing multi-state UI (modals, dropdowns, etc.)
        
        Args:
            url: The URL to capture
            interactions: List of interaction dicts with keys:
                - type: 'click' | 'scroll' | 'wait'
                - selector: CSS selector (for click)
                - scroll_y: pixels to scroll (for scroll)
                - duration_ms: time to wait (for wait)
                
        Returns:
            List of screenshot paths captured after each interaction
        """
        screenshots: List[str] = []
        capture_id = str(uuid.uuid4())[:8]
        
        if interactions is None:
            interactions = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle")
                
                # Initial capture
                initial_path = self.output_dir / f"capture_{capture_id}_initial.png"
                await page.screenshot(path=str(initial_path), full_page=True)
                screenshots.append(str(initial_path))
                
                # Perform interactions and capture
                for i, action in enumerate(interactions):
                    if action.get("type") == "click" and action.get("selector"):
                        await page.click(action["selector"])
                    elif action.get("type") == "scroll":
                        await page.evaluate(f"window.scrollBy(0, {action.get('scroll_y', 500)})")
                    elif action.get("type") == "wait":
                        await asyncio.sleep(action.get("duration_ms", 1000) / 1000)
                    
                    # Capture after interaction
                    path = self.output_dir / f"capture_{capture_id}_step{i+1}.png"
                    await page.screenshot(path=str(path), full_page=True)
                    screenshots.append(str(path))
                    
            finally:
                await browser.close()
        
        return screenshots


# Singleton instance for dependency injection
_url_capture_service: Optional[URLCaptureService] = None


def get_url_capture_service() -> URLCaptureService:
    """
    Get or create the URLCaptureService singleton.
    
    Returns:
        URLCaptureService instance
    """
    global _url_capture_service
    if _url_capture_service is None:
        _url_capture_service = URLCaptureService()
    return _url_capture_service
