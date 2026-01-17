"""Abstract interface and concrete implementations for text extraction from various sources."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from src.browser.tab_info import TabInfo
from src.extraction.html_parser import clean_html, extract_visible_text, parse_html
from src.utils.errors import ExtractionError

logger = logging.getLogger(__name__)


class TextExtractor(ABC):
    """Abstract base class for text extraction from different sources.

    Implementations:
        - ExtractFromTab: Extract text from browser tabs
        - ExtractFromURL: Extract text from web URLs
        - ExtractFromFile: Extract text from local HTML files
    """

    def extract_html(self, html_content: str) -> str:
        """Extract text from HTML content (concrete method for testing).

        Args:
            html_content: Raw HTML string

        Returns:
            Extracted text content (empty string if no content found)

        Raises:
            ExtractionError: If extraction fails unexpectedly
        """
        if not html_content or not html_content.strip():
            return ""

        try:
            # Parse HTML
            soup = parse_html(html_content)
            if not soup:
                # If parsing fails but no exception, return empty string
                return ""

            # Clean HTML (remove scripts, styles, ads)
            soup = clean_html(soup)

            # Extract text
            text = extract_visible_text(soup)
            return text.strip()

        except ExtractionError as e:
            # Re-raise extraction errors but handle gracefully for invalid HTML
            if "no body content" in str(e).lower():
                return ""
            raise
        except Exception as e:
            # Handle unexpected errors gracefully for malformed HTML
            logger.debug(f"HTML extraction error (continuing): {e}")
            return ""

    @abstractmethod
    def extract(self, source: str) -> str:
        """Extract text from the given source.

        Args:
            source: Source identifier (tab_id, URL, or file path)

        Returns:
            Extracted text content from the source

        Raises:
            ExtractionError: If text extraction fails
            TimeoutError: If extraction exceeds timeout
            ValidationError: If source is invalid
        """
        pass

    @abstractmethod
    def supports(self, source_type: str) -> bool:
        """Check if this extractor supports the given source type.

        Args:
            source_type: Type of source ('tab', 'url', 'file', etc.)

        Returns:
            True if this extractor can handle the source type
        """
        pass


class ConcreteTextExtractor(TextExtractor):
    """Concrete text extractor implementation for browser tabs.

    Implements text extraction from browser tabs using:
    1. Browser detection to get tab information
    2. HTML parsing with BeautifulSoup
    3. DOM walking to preserve reading order
    """

    def __init__(self):
        """Initialize the text extractor."""
        self.timeout = 10  # seconds

    def extract(self, source: str) -> str:
        """Extract text from the given source.

        For browser tabs, source is a tab_id or TabInfo object.

        Args:
            source: Source identifier (tab_id or TabInfo)

        Returns:
            Extracted text content from the source

        Raises:
            ExtractionError: If extraction fails
        """
        if not source:
            raise ExtractionError("Source cannot be empty")

        try:
            # Handle TabInfo object
            if isinstance(source, TabInfo):
                return self.extract_from_tab(source)

            # Handle string source (tab_id, URL, etc.)
            if isinstance(source, str):
                # For now, assume it's a tab_id
                # In a real implementation, would detect source type
                return self.extract_from_tab_id(source)

            raise ExtractionError(f"Unsupported source type: {type(source)}")

        except ExtractionError:
            raise
        except Exception as e:
            raise ExtractionError(f"Text extraction failed: {str(e)}") from e

    def extract_from_tab(self, tab_info: TabInfo) -> str:
        """Extract text from a browser tab.

        Args:
            tab_info: TabInfo object with tab metadata

        Returns:
            Extracted text content from the tab

        Raises:
            ExtractionError: If extraction fails
        """
        if not tab_info or not tab_info.is_valid():
            raise ExtractionError("Invalid tab information")

        try:
            # Step 1: Get HTML content from tab
            html_content = self._get_tab_html(tab_info)
            if not html_content:
                raise ExtractionError(f"Could not retrieve HTML from tab {tab_info.tab_id}")

            # Step 2: Parse HTML
            soup = parse_html(html_content)
            if not soup:
                raise ExtractionError("Failed to parse HTML")

            # Step 3: Clean HTML (remove scripts, styles, ads)
            soup = clean_html(soup)

            # Step 4: Extract text preserving structure
            text = extract_visible_text(soup)

            if not text or not text.strip():
                raise ExtractionError("No text content extracted from tab")

            return text.strip()

        except ExtractionError:
            raise
        except Exception as e:
            raise ExtractionError(f"Failed to extract text from tab {tab_info.tab_id}: {str(e)}") from e

    def extract_from_tab_id(self, tab_id: str) -> str:
        """Extract text from a tab by tab_id.

        Args:
            tab_id: Unique identifier for the tab

        Returns:
            Extracted text content

        Raises:
            ExtractionError: If extraction fails
        """
        # In a real implementation, would:
        # 1. Look up TabInfo by tab_id
        # 2. Call extract_from_tab()

        # For now, this is a placeholder
        raise ExtractionError(f"Tab lookup not yet implemented for {tab_id}")

    def _get_tab_html(self, tab_info: TabInfo) -> Optional[str]:
        """Get HTML content from a browser tab.

        This is a placeholder implementation.
        Real implementation would use accessibility APIs
        or inter-process communication to get tab content.

        Args:
            tab_info: Tab to get content from

        Returns:
            HTML content as string, or None if unable to retrieve
        """
        # TODO: Implement real tab content retrieval
        # Would use pywinauto or similar to get tab DOM
        logger.warning(f"Tab HTML retrieval not implemented for {tab_info.browser_name}")
        return None

    def supports(self, source_type: str) -> bool:
        """Check if this extractor supports the given source type.

        Args:
            source_type: Type of source ('tab', 'url', 'file', etc.)

        Returns:
            True if this extractor can handle the source type
        """
        # This implementation supports tabs primarily
        return source_type.lower() in ["tab", "browser", "tabs", "html"]
