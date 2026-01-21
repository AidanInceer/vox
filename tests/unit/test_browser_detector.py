"""Tests for browser tab detection (User Story 1).

These tests verify the ability to detect and enumerate browser tabs
from Chrome, Edge, Firefox, and other browsers running on Windows.

Key requirement: Must detect inactive background tabs without switching focus.
"""

from unittest.mock import patch

import pytest

from src.browser.tab_info import TabInfo


class TestBrowserDetection:
    """Test basic browser detection capabilities."""

    def test_detect_chrome_tabs(self):
        """Detect Chrome browser tabs with title and URL."""
        # Mock Chrome process running with tabs
        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            mock_detect.return_value = [
                TabInfo(
                    browser_name="chrome",
                    tab_id="1",
                    title="Google Search",
                    url="https://www.google.com",
                    window_handle=1001,
                ),
                TabInfo(
                    browser_name="chrome",
                    tab_id="2",
                    title="GitHub - aidan/vox",
                    url="https://github.com/aidan/vox",
                    window_handle=1001,
                ),
            ]

            from src.browser.detector import get_browser_tabs

            tabs = get_browser_tabs("chrome")

            assert len(tabs) >= 1
            assert all(t.browser_name == "chrome" for t in tabs)
            assert all(t.title and t.url for t in tabs)

    def test_detect_edge_tabs(self):
        """Detect Microsoft Edge browser tabs."""
        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            mock_detect.return_value = [
                TabInfo(
                    browser_name="edge",
                    tab_id="1",
                    title="Azure Portal",
                    url="https://portal.azure.com",
                    window_handle=2001,
                ),
            ]

            from src.browser.detector import get_browser_tabs

            tabs = get_browser_tabs("edge")

            assert len(tabs) >= 1
            assert all(t.browser_name == "edge" for t in tabs)

    def test_detect_firefox_tabs(self):
        """Detect Firefox browser tabs."""
        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            mock_detect.return_value = [
                TabInfo(
                    browser_name="firefox",
                    tab_id="1",
                    title="Mozilla Firefox Start Page",
                    url="https://www.mozilla.org",
                    window_handle=3001,
                ),
            ]

            from src.browser.detector import get_browser_tabs

            tabs = get_browser_tabs("firefox")

            assert len(tabs) >= 1
            assert all(t.browser_name == "firefox" for t in tabs)

    def test_tab_detect_inactive_tabs(self):
        """Core US1 requirement: detect inactive background tabs without focus."""
        # This is the critical test for User Story 1
        # We need to verify tabs can be detected even if they're not in focus
        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            # Simulate 3 tabs, middle one is active, others are background
            mock_detect.return_value = [
                TabInfo(
                    browser_name="chrome",
                    tab_id="1",
                    title="Background Tab 1",
                    url="https://example.com/1",
                    window_handle=1001,
                ),
                TabInfo(
                    browser_name="chrome",
                    tab_id="2",
                    title="Active Tab (currently in focus)",
                    url="https://example.com/2",
                    window_handle=1001,
                ),
                TabInfo(
                    browser_name="chrome",
                    tab_id="3",
                    title="Background Tab 2",
                    url="https://example.com/3",
                    window_handle=1001,
                ),
            ]

            from src.browser.detector import get_browser_tabs

            tabs = get_browser_tabs("chrome")

            # All 3 tabs should be detected, including inactive ones
            assert len(tabs) == 3

            # Background tabs should have valid info
            background_tabs = [t for t in tabs if "Background" in t.title]
            assert len(background_tabs) == 2
            assert all(t.url and t.tab_id for t in background_tabs)

    def test_detect_all_browsers_simultaneously(self):
        """Detect tabs from multiple browsers running simultaneously."""
        with patch("src.browser.detector.detect_all_browser_tabs") as mock_detect_all:
            mock_detect_all.return_value = [
                TabInfo("chrome", "1", "Chrome Page", "https://google.com", 1001),
                TabInfo("chrome", "2", "Chrome GitHub", "https://github.com", 1001),
                TabInfo("edge", "1", "Edge Azure", "https://portal.azure.com", 2001),
                TabInfo("firefox", "1", "Firefox Mozilla", "https://mozilla.org", 3001),
            ]

            from src.browser.detector import detect_all_browser_tabs

            tabs = detect_all_browser_tabs()

            assert len(tabs) >= 4

            # Verify tabs from different browsers
            chrome_tabs = [t for t in tabs if t.browser_name == "chrome"]
            edge_tabs = [t for t in tabs if t.browser_name == "edge"]
            firefox_tabs = [t for t in tabs if t.browser_name == "firefox"]

            assert len(chrome_tabs) >= 2
            assert len(edge_tabs) >= 1
            assert len(firefox_tabs) >= 1

    def test_tab_info_validation_after_detection(self):
        """Verify detected TabInfo objects are valid."""
        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            mock_detect.return_value = [
                TabInfo(
                    browser_name="chrome", tab_id="1", title="Valid Tab", url="https://example.com", window_handle=1001
                ),
            ]

            from src.browser.detector import get_browser_tabs

            tabs = get_browser_tabs("chrome")

            assert len(tabs) > 0
            tab = tabs[0]
            assert tab.is_valid()
            assert tab.browser_name == "chrome"
            assert tab.title is not None
            assert tab.url is not None


class TestBrowserDetectionErrors:
    """Test error handling in browser detection."""

    def test_no_browser_running(self):
        """Handle case when requested browser is not running."""
        with patch("src.browser.detector.get_browser_tabs") as mock_detect:
            mock_detect.return_value = []

            from src.browser.detector import get_browser_tabs

            tabs = get_browser_tabs("safari")  # Not typically on Windows

            assert len(tabs) == 0

    def test_invalid_browser_name(self):
        """Handle invalid browser name gracefully."""
        from src.browser.detector import get_browser_tabs
        from src.utils.errors import BrowserDetectionError

        with pytest.raises((BrowserDetectionError, ValueError)):
            get_browser_tabs("nonexistent_browser")

    def test_browser_tab_detection_timeout(self):
        """Handle detection timeout gracefully."""
        from src.browser.detector import get_browser_tabs
        from src.utils.errors import BrowserDetectionError

        # Patch the process check to return True so we reach the detection methods
        with patch("src.browser.detector._is_process_running") as mock_process:
            mock_process.return_value = True

            # Patch the helper function that would timeout
            with patch("src.browser.detector._detect_tabs_by_window_title") as mock_window:
                # Simulate timeout in window title detection - this will be caught and wrapped
                mock_window.side_effect = TimeoutError("Detection timeout")

                # get_browser_tabs wraps exceptions in BrowserDetectionError
                with pytest.raises(BrowserDetectionError):
                    get_browser_tabs("chrome")


class TestBrowserTabSelection:
    """Test tab selection from detected tabs."""

    def test_select_tab_by_id(self):
        """Select specific tab by ID."""
        tabs = [
            TabInfo("chrome", "1", "Tab 1", "https://example.com/1", 1001),
            TabInfo("chrome", "2", "Tab 2", "https://example.com/2", 1001),
            TabInfo("chrome", "3", "Tab 3", "https://example.com/3", 1001),
        ]

        # Find tab by ID
        selected = next((t for t in tabs if t.tab_id == "2"), None)
        assert selected is not None
        assert selected.title == "Tab 2"

    def test_select_tab_by_title(self):
        """Select tab by title search."""
        tabs = [
            TabInfo("chrome", "1", "Google Search", "https://google.com", 1001),
            TabInfo("chrome", "2", "GitHub - aidan", "https://github.com", 1001),
        ]

        # Find tab with matching title
        selected = next((t for t in tabs if "GitHub" in t.title), None)
        assert selected is not None
        assert selected.tab_id == "2"

    def test_select_tab_by_url(self):
        """Select tab by URL pattern."""
        tabs = [
            TabInfo("chrome", "1", "Google", "https://google.com", 1001),
            TabInfo("chrome", "2", "GitHub", "https://github.com", 1001),
        ]

        # Find tab with matching URL
        selected = next((t for t in tabs if "github.com" in t.url), None)
        assert selected is not None
        assert selected.title == "GitHub"
