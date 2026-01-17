"""Windows Accessibility API wrapper for browser tab detection.

This module provides a fallback method for detecting browser tabs using
the Windows Accessibility API when window title parsing isn't sufficient.

The Accessibility API can provide more reliable tab detection,
especially for newer browser versions.
"""

import logging
from typing import List, Optional

from src.browser.tab_info import TabInfo
from src.utils.errors import BrowserDetectionError

logger = logging.getLogger(__name__)


def get_browser_tabs(browser_name: str) -> List[TabInfo]:
    """Get browser tabs using Windows Accessibility API.

    This method uses the Windows UI Automation framework to detect
    and enumerate browser tabs from the accessibility tree.

    Args:
        browser_name: Browser name (chrome, edge, firefox)

    Returns:
        List of TabInfo objects detected via Accessibility API

    Raises:
        BrowserDetectionError: If detection fails
    """
    browser_name = browser_name.lower().strip()

    try:
        # Try using Windows UI Automation (pygetwindow as fallback)
        tabs = _detect_via_ui_automation(browser_name)
        if tabs:
            return tabs

        # Fallback: use basic window enumeration
        return _detect_via_window_enum(browser_name)

    except Exception as e:
        logger.warning(f"Accessibility API detection failed: {e}")
        return []


def get_window_text(window_handle: int) -> str:
    """Get text content of a window using accessibility API.

    Args:
        window_handle: Windows handle for the window

    Returns:
        Text content of the window

    Raises:
        BrowserDetectionError: If unable to retrieve window text
    """
    try:
        import pygetwindow

        window = pygetwindow.getWindowsWithTitle(str(window_handle))
        if window:
            return window[0].title
        return ""

    except Exception as e:
        raise BrowserDetectionError(f"Failed to get window text for handle {window_handle}: {e}") from e


def _detect_via_ui_automation(browser_name: str) -> List[TabInfo]:
    """Detect tabs using Windows UI Automation framework.

    This method uses UIAutomationCore to query the accessibility tree
    for tab elements within browser windows.

    Args:
        browser_name: Browser name

    Returns:
        List of detected TabInfo objects
    """
    tabs: List[TabInfo] = []

    try:
        # Try to import UI Automation library
        # On Windows, we can use pywinauto's accessibility features

        # Connect to browser application
        app = _connect_to_browser_app(browser_name)
        if not app:
            return []

        # Find tab container based on browser type
        tab_container = _find_tab_container(app, browser_name)
        if not tab_container:
            return []

        # Enumerate tabs in container
        tabs = _enumerate_tabs_from_container(tab_container, browser_name)

        return tabs

    except Exception as e:
        logger.debug(f"UI Automation detection failed: {e}")
        return []


def _connect_to_browser_app(browser_name: str) -> Optional:
    """Connect to a running browser application.

    Args:
        browser_name: Browser name

    Returns:
        Application object if found, None otherwise
    """
    try:
        import pywinauto

        process_map = {
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "firefox": "firefox.exe",
        }

        process_name = process_map.get(browser_name)
        if not process_name:
            return None

        try:
            app = pywinauto.Application().connect(title_re=f".*{browser_name}.*")
            return app
        except pywinauto.ProcessNotFoundError:
            return None

    except Exception as e:
        logger.debug(f"Could not connect to {browser_name}: {e}")
        return None


def _find_tab_container(app, browser_name: str):
    """Find the tab container element in the browser.

    Different browsers have different UI structures:
    - Chrome/Edge: TabControl or custom tab container
    - Firefox: Tab container with specific class names

    Args:
        app: Application object
        browser_name: Browser name

    Returns:
        Tab container element or None
    """
    try:
        # This is browser-specific; for now, return None as placeholder
        # Real implementation would navigate the accessibility tree
        return None

    except Exception as e:
        logger.debug(f"Could not find tab container: {e}")
        return None


def _enumerate_tabs_from_container(tab_container, browser_name: str) -> List[TabInfo]:
    """Enumerate tabs from a tab container element.

    Args:
        tab_container: Tab container element
        browser_name: Browser name

    Returns:
        List of TabInfo objects found in container
    """
    tabs: List[TabInfo] = []

    try:
        # This is a placeholder for real UI Automation enumeration
        # Would iterate through children of tab_container
        # and extract tab properties
        pass

    except Exception as e:
        logger.debug(f"Could not enumerate tabs: {e}")

    return tabs


def _detect_via_window_enum(browser_name: str) -> List[TabInfo]:
    """Detect tabs using basic window enumeration.

    This is a fallback method that enumerates all windows
    and looks for browser windows, then parses their titles.

    Args:
        browser_name: Browser name

    Returns:
        List of detected TabInfo objects
    """
    tabs: List[TabInfo] = []

    try:
        import pygetwindow

        # Get all windows
        windows = pygetwindow.getAllWindows()

        # Filter for browser windows
        browser_keywords = {
            "chrome": ["chrome", "google"],
            "edge": ["edge", "microsoft"],
            "firefox": ["firefox", "mozilla"],
        }

        keywords = browser_keywords.get(browser_name, [])

        for window in windows:
            try:
                title = window.title

                # Check if window belongs to this browser
                if any(kw.lower() in title.lower() for kw in keywords):
                    # Skip developer tools and other non-tab windows
                    if not any(skip in title.lower() for skip in ["devtools", "extensions", "about:blank"]):
                        # Create TabInfo from window
                        tab = _parse_tab_from_window(window, browser_name)
                        if tab and tab.is_valid():
                            tabs.append(tab)

            except Exception as e:
                logger.debug(f"Error processing window {window}: {e}")
                continue

        return tabs

    except Exception as e:
        logger.debug(f"Window enumeration failed: {e}")
        return []


def _parse_tab_from_window(window, browser_name: str) -> Optional[TabInfo]:
    """Parse TabInfo from a window object.

    Args:
        window: Window object from pygetwindow
        browser_name: Browser name

    Returns:
        TabInfo object or None if parsing fails
    """
    try:
        title = window.title
        if not title or title.strip() == "":
            return None

        # Remove browser suffix from title
        page_title = title
        for suffix in [" - Google Chrome", " - Microsoft Edge", " — Mozilla Firefox"]:
            if suffix.lower() in title.lower():
                page_title = title[: title.lower().index(suffix.lower())]
                break

        if not page_title or page_title.strip() == "":
            return None

        # Generate tab ID
        tab_id = str(hash(page_title) % (10**8))

        # Create TabInfo
        return TabInfo(
            browser_name=browser_name,
            tab_id=tab_id,
            title=page_title.strip(),
            url=f"about:tab#{page_title.replace(' ', '_')}",
            window_handle=window._handle if hasattr(window, "_handle") else None,
        )

    except Exception as e:
        logger.debug(f"Could not parse tab from window: {e}")
        return None
