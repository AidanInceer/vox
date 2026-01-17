"""DOM traversal utilities for maintaining reading order during text extraction.

This module provides functions to walk the DOM tree in reading order,
preserving document structure and section boundaries.
"""

import logging
from typing import List, Optional, Tuple

from bs4 import NavigableString, Tag

logger = logging.getLogger(__name__)


class TextSection:
    """Represents a section of text with metadata about its structure."""

    def __init__(self, text: str, element: Optional[Tag] = None, level: int = 0, is_heading: bool = False):
        """Initialize a text section.

        Args:
            text: The text content of this section
            element: The HTML element this section came from
            level: Heading level if this is a heading (1-6), 0 otherwise
            is_heading: Whether this is a heading/title
        """
        self.text = text
        self.element = element
        self.level = level
        self.is_heading = is_heading

    def __repr__(self) -> str:
        return f"TextSection(text={self.text[:50]!r}, level={self.level}, heading={self.is_heading})"


def walk_dom(soup: Tag, preserve_structure: bool = True) -> List[str]:
    """Walk the DOM tree in reading order and extract text segments.

    Performs a depth-first traversal of the DOM, extracting text while
    respecting document structure (paragraphs, headings, etc.).

    Args:
        soup: The root element to start traversal from
        preserve_structure: If True, includes section markers in output

    Returns:
        List of text segments in reading order, each segment representing
        a logical unit (paragraph, heading, etc.)
    """
    if not soup:
        return []

    sections: List[TextSection] = []
    _walk_element(soup, sections)

    # Convert sections to strings
    text_parts = []
    for section in sections:
        if section.text.strip():  # Skip empty sections
            text_parts.append(section.text.strip())

    return text_parts


def _walk_element(element: Tag, sections: List[TextSection], depth: int = 0) -> None:
    """Recursively walk an element and its children, extracting text.

    Depth-first traversal that respects document structure.

    Args:
        element: Current element in traversal
        sections: List to accumulate text sections
        depth: Current nesting depth
    """
    if not isinstance(element, Tag):
        return

    # Skip hidden elements
    if _is_element_hidden(element):
        return

    # Block elements that represent logical sections
    block_elements = {"p", "div", "section", "article", "blockquote", "li", "td", "th"}

    # Heading elements
    heading_levels = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}

    # Check if this is a container element
    is_container = element.name in block_elements or element.name in heading_levels

    # Extract text from this element and children
    if element.name in heading_levels:
        # Heading element
        heading_text = _get_element_text(element)
        if heading_text:
            level = heading_levels[element.name]
            sections.append(TextSection(heading_text, element=element, level=level, is_heading=True))
    elif is_container:
        # Block element - create a new section
        text_parts = []
        for child in element.children:
            if isinstance(child, NavigableString) and not isinstance(child, Tag):
                # Direct text content
                text = str(child).strip()
                if text:
                    text_parts.append(text)
            elif isinstance(child, Tag):
                # Recursively process child
                # For nested block elements, they'll create their own sections
                child_is_block = child.name in block_elements or child.name in heading_levels
                if child_is_block:
                    # Let child create its own section
                    _walk_element(child, sections, depth + 1)
                else:
                    # Inline element - extract text inline
                    child_text = _get_element_text(child)
                    if child_text:
                        text_parts.append(child_text)

        # Create section if we have text content
        text = " ".join(text_parts)
        if text.strip():
            sections.append(TextSection(text, element=element, level=0))
    else:
        # Inline element - extract text from children
        for child in element.children:
            if isinstance(child, NavigableString) and not isinstance(child, Tag):
                text = str(child).strip()
                if text:
                    sections.append(TextSection(text, element=element))
            elif isinstance(child, Tag):
                _walk_element(child, sections, depth + 1)


def _get_element_text(element: Tag) -> str:
    """Get the text content of an element.

    Args:
        element: Element to extract text from

    Returns:
        Combined text from all descendants
    """
    text_parts = []

    for child in element.descendants:
        if isinstance(child, NavigableString) and not isinstance(child, Tag):
            text = str(child).strip()
            if text:
                text_parts.append(text)

    return " ".join(text_parts)


def _is_element_hidden(element: Tag) -> bool:
    """Check if an element is visually hidden.

    Args:
        element: Element to check

    Returns:
        True if element is hidden and should be skipped
    """
    # Check style attribute
    style = element.get("style", "")
    if "display:none" in style.replace(" ", ""):
        return True
    if "visibility:hidden" in style.replace(" ", ""):
        return True

    # Check hidden attribute
    if element.get("hidden") is not None:
        return True

    # Check aria-hidden
    if element.get("aria-hidden") == "true":
        return True

    # Check class for common hidden patterns
    classes = element.get("class", [])
    hidden_patterns = {"hidden", "d-none", "no-display", "display-none", "sr-only"}
    for cls in classes:
        if cls in hidden_patterns:
            return True

    return False


def extract_sections(soup: Tag) -> List[TextSection]:
    """Extract text sections with metadata about structure.

    Returns a list of TextSection objects that preserve information about
    the document structure (headings, nesting, etc.).

    Args:
        soup: Root element to process

    Returns:
        List of TextSection objects with structure preserved
    """
    sections: List[TextSection] = []
    _walk_element(soup, sections)
    return sections


def get_heading_hierarchy(soup: Tag) -> List[Tuple[int, str]]:
    """Extract heading hierarchy from document.

    Returns a list of (level, text) tuples representing the document's
    heading structure.

    Args:
        soup: Root element to process

    Returns:
        List of (level, heading_text) tuples
    """
    headings: List[Tuple[int, str]] = []

    # Find all heading elements
    for level in range(1, 7):
        tag_name = f"h{level}"
        for heading in soup.find_all(tag_name):
            if not _is_element_hidden(heading):
                text = _get_element_text(heading).strip()
                if text:
                    headings.append((level, text))

    return headings


def reorder_by_importance(sections: List[TextSection]) -> List[TextSection]:
    """Reorder sections by importance (optional, for summarization).

    This could be used to prioritize main content over sidebars.
    For now, preserves original order.

    Args:
        sections: List of text sections

    Returns:
        Reordered sections (currently returns as-is)
    """
    # TODO: Implement importance scoring based on:
    # - Heading level (higher = more important)
    # - Section type (article > aside)
    # - Position on page

    return sections
