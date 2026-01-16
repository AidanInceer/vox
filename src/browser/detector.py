"""Windows browser tab detection using pywinauto and Windows APIs.

This module provides functions to detect and enumerate browser tabs from
Chrome, Edge, Firefox, and other browsers running on Windows.

Key requirement: Detects inactive background tabs without switching focus.
"""

from typing import List, Dict, Optional
import psutil
import re
from src.browser.tab_info import TabInfo
from src.utils.errors import BrowserDetectionError
import logging

logger = logging.getLogger(__name__)


def detect_all_browser_tabs() -> List[TabInfo]:
    """Detect all browser tabs from all major browsers currently running.
    
    Returns:
        List of TabInfo objects representing all detected tabs
        across Chrome, Edge, and Firefox
        
    Raises:
        BrowserDetectionError: If tab detection fails
    """
    all_tabs: List[TabInfo] = []
    
    browsers = ['chrome', 'edge', 'firefox']
    for browser in browsers:
        try:
            tabs = get_browser_tabs(browser)
            all_tabs.extend(tabs)
        except (BrowserDetectionError, Exception) as e:
            logger.debug(f"Could not detect {browser} tabs: {e}")
            # Continue with other browsers even if one fails
            continue
    
    return all_tabs


def get_browser_tabs(browser_name: str) -> List[TabInfo]:
    """Get all tabs from a specific browser.
    
    Args:
        browser_name: Name of the browser ('chrome', 'edge', 'firefox')
        
    Returns:
        List of TabInfo objects for the specified browser
        
    Raises:
        BrowserDetectionError: If browser not found or detection fails
        ValueError: If invalid browser name provided
    """
    browser_name = browser_name.lower().strip()
    
    if browser_name not in ['chrome', 'edge', 'firefox']:
        raise ValueError(
            f"Unsupported browser: {browser_name}. "
            f"Supported: chrome, edge, firefox"
        )
    
    # Check if browser process is running
    process_names = _get_process_names(browser_name)
    if not _is_process_running(process_names):
        return []
    
    try:
        # Try to detect tabs using different methods
        tabs = _detect_tabs_by_window_title(browser_name, process_names)
        
        if tabs:
            return tabs
        
        # If window title method fails, try accessibility API
        tabs = _detect_tabs_by_accessibility(browser_name)
        return tabs
        
    except Exception as e:
        raise BrowserDetectionError(
            f"Failed to detect {browser_name} tabs: {str(e)}"
        ) from e


def _get_process_names(browser_name: str) -> List[str]:
    """Get process names for a given browser.
    
    Args:
        browser_name: Browser name (chrome, edge, firefox)
        
    Returns:
        List of process names to search for
    """
    process_map = {
        'chrome': ['chrome.exe', 'google chrome'],
        'edge': ['msedge.exe', 'microsoft edge'],
        'firefox': ['firefox.exe', 'firefox'],
    }
    return process_map.get(browser_name, [])


def _is_process_running(process_names: List[str]) -> bool:
    """Check if any of the given processes are running.
    
    Args:
        process_names: List of process names to check
        
    Returns:
        True if any process is found running
    """
    running_procs = [p.name() for p in psutil.process_iter(['name'])]
    
    for name in process_names:
        # Case-insensitive search
        if any(name.lower() in p.lower() for p in running_procs):
            return True
    
    return False


def _detect_tabs_by_window_title(browser_name: str, process_names: List[str]) -> List[TabInfo]:
    """Detect tabs by parsing window titles (most reliable for Chrome/Edge).
    
    Browser window titles typically follow patterns:
    - Chrome/Edge: "Page Title - Google Chrome" or "Page Title - Microsoft Edge"
    - Firefox: "Page Title — Mozilla Firefox"
    
    Args:
        browser_name: Browser name
        process_names: List of process names for this browser
        
    Returns:
        List of detected TabInfo objects
    """
    tabs: List[TabInfo] = []
    
    try:
        # Use pywinauto to find windows
        import pywinauto
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(proc.name().lower() in pname.lower() for pname in process_names):
                    # Found browser process
                    windows = pywinauto.findwindows.find_windows(
                        class_name_re='Chrome_WidgetWin_.*|ApplicationFrameWindow|MozillaWindowClass'
                    )
                    
                    for window in windows:
                        try:
                            title = window.window_text()
                            
                            # Skip window if it's not a tab (e.g., extensions, developer tools)
                            if title and not any(skip in title.lower() 
                                                 for skip in ['extensions', 'devtools', 'about']):
                                # Parse tab info from window title
                                tab = _parse_tab_from_title(browser_name, title, window.handle)
                                if tab and tab.is_valid():
                                    tabs.append(tab)
                        except Exception as e:
                            logger.debug(f"Could not get window text: {e}")
                            continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return tabs
        
    except ImportError:
        logger.debug("pywinauto not available, trying alternative detection method")
        return []
    except Exception as e:
        logger.debug(f"Window title detection failed: {e}")
        return []


def _detect_tabs_by_accessibility(browser_name: str) -> List[TabInfo]:
    """Detect tabs using Windows Accessibility API.
    
    This is a fallback method when window title parsing fails.
    
    Args:
        browser_name: Browser name
        
    Returns:
        List of detected TabInfo objects
    """
    tabs: List[TabInfo] = []
    
    try:
        # Import accessibility module
        from src.browser.accessibility import get_browser_tabs as get_tabs_accessibility
        
        tabs = get_tabs_accessibility(browser_name)
        return tabs
        
    except Exception as e:
        logger.debug(f"Accessibility detection failed: {e}")
        return []


def _parse_tab_from_title(browser_name: str, title: str, window_handle: int) -> Optional[TabInfo]:
    """Parse TabInfo from browser window title.
    
    Attempts to extract page title and URL from window title string.
    
    Args:
        browser_name: Browser name
        title: Window title string
        window_handle: Windows handle for the tab window
        
    Returns:
        TabInfo object if parsing successful, None otherwise
    """
    # Simple heuristic: try to extract meaningful info from title
    # For now, use title as page title and invent a basic URL
    # This is a simplified implementation; real implementation would use
    # Accessibility APIs to get actual URLs
    
    if not title:
        return None
    
    # Remove browser suffix from title
    page_title = title
    for suffix in [' - Google Chrome', ' - Microsoft Edge', ' — Mozilla Firefox', ' - Chromium']:
        if suffix.lower() in title.lower():
            page_title = title[:title.lower().index(suffix.lower())]
            break
    
    if not page_title or page_title.strip() == '':
        return None
    
    # Generate a basic URL (this should be improved with real URL detection)
    # For now, just use a placeholder
    url = f"about:tab#{page_title.replace(' ', '_')}"
    
    # Generate tab ID from title hash
    tab_id = str(hash(page_title) % (10**8))
    
    return TabInfo(
        browser_name=browser_name,
        tab_id=tab_id,
        title=page_title.strip(),
        url=url,
        window_handle=window_handle
    )
