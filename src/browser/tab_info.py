"""Data structures and models for browser tab information."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TabInfo:
    """Information about a browser tab.
    
    Attributes:
        browser_name: Name of the browser (chrome, edge, firefox, etc.)
        tab_id: Unique identifier for the tab within the browser
        title: Browser tab title (from page <title> or tab label)
        url: URL of the page in the tab
        window_handle: Windows process handle or window handle for the tab
    """
    
    browser_name: str
    tab_id: str
    title: str
    url: str
    window_handle: Optional[int] = None
    
    def __str__(self) -> str:
        """String representation of tab info."""
        return f"{self.browser_name}: {self.title} ({self.url})"
    
    def __repr__(self) -> str:
        """Detailed representation of tab info."""
        return (
            f"TabInfo(browser={self.browser_name}, tab_id={self.tab_id}, "
            f"title={self.title!r}, url={self.url!r})"
        )
    
    def is_valid(self) -> bool:
        """Check if tab info is valid (has required fields).
        
        Returns:
            True if all required fields are present and non-empty
        """
        return all([self.browser_name, self.tab_id, self.title, self.url])
