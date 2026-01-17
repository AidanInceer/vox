"""HTML parsing using BeautifulSoup for text extraction.

This module provides utilities for parsing HTML documents and
preparing them for text extraction while preserving document structure.
"""

import logging
from typing import Optional

from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)


def parse_html(html_content: str) -> Optional[BeautifulSoup]:
    """Parse HTML content into a BeautifulSoup object.

    Args:
        html_content: Raw HTML string to parse

    Returns:
        BeautifulSoup object representing the parsed DOM, or None if empty

    Raises:
        ValueError: If html_content is invalid (but not empty)
    """
    if not html_content or not isinstance(html_content, str):
        return None

    try:
        # Use 'html.parser' for fast, built-in parsing (no external deps)
        # lxml would be faster but adds dependency; html5lib is more lenient
        soup = BeautifulSoup(html_content, "html.parser")

        return soup

    except Exception as e:
        logger.error(f"Failed to parse HTML: {e}")
        raise ValueError(f"Invalid HTML content: {e}") from e


def clean_html(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove script, style, and other non-text elements from HTML.

    This prepares the HTML for text extraction by removing elements
    that don't contribute to the visible text content.

    Args:
        soup: BeautifulSoup object to clean

    Returns:
        Cleaned BeautifulSoup object (modifies in place)
    """
    # Elements to remove entirely (don't extract text from these)
    remove_tags = {"script", "style", "meta", "link", "noscript", "iframe"}

    # Remove these elements from the tree
    for tag in soup.find_all(remove_tags):
        tag.decompose()

    # Remove common ad/navigation containers
    remove_classes = {
        "ad",
        "advertisement",
        "banner",
        "navigation",
        "nav",
        "sidebar",
        "aside",
        "footer",
        "footer-content",
        "social-media",
        "share-buttons",
        "comments",
    }

    for tag in soup.find_all(
        class_=lambda x: x and any(cls in (x.lower() if isinstance(x, str) else "") for cls in remove_classes)
    ):
        tag.decompose()

    return soup


def extract_visible_text(soup: BeautifulSoup) -> str:
    """Extract visible text from parsed HTML, preserving structure.

    Extracts all visible text content from HTML while:
    - Preserving reading order (depth-first DOM traversal)
    - Maintaining paragraph/section boundaries
    - Removing hidden elements and decorative content

    Args:
        soup: BeautifulSoup object

    Returns:
        Extracted text with preserved structure (newlines between paragraphs)
    """
    if not soup:
        return ""

    # Start with the body element if available, otherwise use soup root
    root = soup.body if soup.body else soup

    # Extract text
    text_parts = []
    _extract_from_element(root, text_parts)

    # Join parts and clean up whitespace
    text = "\n".join(text_parts)

    # Clean up excessive whitespace
    # - Remove runs of 3+ newlines (replace with 2)
    # - Strip leading/trailing whitespace from each line
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]  # Remove empty lines

    text = "\n".join(lines)

    return text


def _extract_from_element(element: Tag, parts: list[str], depth: int = 0) -> None:
    """Recursively extract text from an element and its children.

    This performs a depth-first traversal of the DOM, extracting text
    from each element and maintaining structure with newlines.

    Args:
        element: BeautifulSoup Tag to extract from
        parts: List to accumulate text parts
        depth: Current recursion depth (for debugging)
    """
    if not isinstance(element, Tag):
        return

    # Block-level elements that should have newlines around them
    block_tags = {
        "p",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "blockquote",
        "pre",
        "section",
        "article",
        "aside",
        "nav",
        "header",
        "footer",
        "li",
        "tr",
        "td",
        "th",
        "ul",
        "ol",
        "dl",
        "dt",
        "dd",
    }

    # Check if this is a block element
    is_block = element.name in block_tags

    # Add newline before block elements (except first)
    if is_block and parts:
        parts.append("\n")

    # Extract text from this element
    for child in element.children:
        if isinstance(child, NavigableString):
            # Direct text content
            text = str(child).strip()
            if text:
                parts.append(text)
        elif isinstance(child, Tag):
            # Skip hidden elements
            if _is_hidden(child):
                continue

            # Recursively extract from child
            _extract_from_element(child, parts, depth + 1)

    # Add newline after block elements
    if is_block and parts and parts[-1] != "\n":
        parts.append("\n")


def _is_hidden(element: Tag) -> bool:
    """Check if an element is visually hidden.

    Args:
        element: BeautifulSoup Tag to check

    Returns:
        True if element should be skipped (is hidden)
    """
    # Check for display:none or visibility:hidden in style
    style = element.get("style", "")
    if "display" in style.lower() and "none" in style.lower():
        return True
    if "visibility" in style.lower() and "hidden" in style.lower():
        return True

    # Check for hidden attributes
    if element.get("hidden") is not None:
        return True
    if element.get("aria-hidden") == "true":
        return True

    # Check for display:none in class (common pattern)
    classes = element.get("class", [])
    hidden_classes = {"hidden", "d-none", "display-none", "no-display"}
    if any(cls in hidden_classes for cls in classes):
        return True

    return False


def get_element_text(element: Tag) -> str:
    """Get just the text content of an element (not children).

    Args:
        element: BeautifulSoup Tag

    Returns:
        Text content of the element (direct children only)
    """
    text_parts = []

    for child in element.children:
        if isinstance(child, NavigableString) and not isinstance(child, Tag):
            text = str(child).strip()
            if text:
                text_parts.append(text)

    return " ".join(text_parts)


def find_main_content(soup: BeautifulSoup) -> Optional[Tag]:
    """Find the main content area of a page.

    Attempts to identify the primary content area by looking for
    common patterns (main tag, article, div with main/content class).

    Args:
        soup: BeautifulSoup object

    Returns:
        The main content element, or None if not found
    """
    # Priority order of selectors
    selectors = [
        "main",
        "article",
        ("div", {"id": lambda x: x and "main" in x.lower() or "content" in x.lower()}),
        (
            "div",
            {"class": lambda x: x and ("main" in str(x).lower() or "content" in str(x).lower())},
        ),
    ]

    for selector in selectors:
        try:
            if isinstance(selector, str):
                # Simple tag name selector
                element = soup.find(selector)
            else:
                # Dict selector with name and attrs
                tag_name, attrs = selector
                element = soup.find(tag_name, attrs=attrs)

            if element:
                return element
        except Exception as e:
            logger.debug(f"Selector failed: {e}")
            continue

    # Fallback: use body if main content not found
    return soup.body if soup else None
