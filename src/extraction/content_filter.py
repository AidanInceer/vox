"""Content filtering module for extracting main content from webpages.

This module provides functions to filter out noise elements (navigation,
headers, footers, sidebars, ads) and extract the main article content.
"""

import re
import unicodedata
from typing import Optional

from bs4 import BeautifulSoup, NavigableString


# Common IDs and classes for navigation elements
NAV_SELECTORS = [
    "nav",
    "[role='navigation']",
    ".navbar",
    ".nav",
    ".menu",
    "#menu",
    "#nav",
]

# Common IDs and classes for header elements
HEADER_SELECTORS = [
    "header",
    "[role='banner']",
    ".header",
    "#header",
    ".page-header",
]

# Common IDs and classes for footer elements
FOOTER_SELECTORS = [
    "footer",
    "[role='contentinfo']",
    ".footer",
    "#footer",
    ".page-footer",
]

# Common IDs and classes for sidebar/aside elements
SIDEBAR_SELECTORS = [
    "aside",
    "[role='complementary']",
    ".sidebar",
    "#sidebar",
    ".widgets",
    ".related-posts",
]

# Common IDs and classes for advertisement elements
AD_SELECTORS = [
    ".ad",
    ".ads",
    ".advertisement",
    ".banner-ad",
    "[class*='ad-']",
    "[class*='advert']",
    "[class*='sponsor']",
]

# Elements that typically contain main content
MAIN_CONTENT_SELECTORS = [
    "main",
    "article",
    "[role='main']",
    ".main",
    ".content",
    ".post",
    ".entry",
]


def filter_main_content(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    """Filter HTML to extract main content, removing noise elements.

    This function attempts to identify and extract the main article content
    from a webpage by removing navigation, headers, footers, sidebars, and ads.

    Args:
        soup: BeautifulSoup object of the parsed HTML

    Returns:
        BeautifulSoup object with filtered content, or None if extraction fails

    Example:
        >>> soup = BeautifulSoup("<html>...</html>")
        >>> filtered = filter_main_content(soup)
        >>> if filtered:
        >>>     print(filtered.get_text())
    """
    if not soup:
        return None

    # Create a copy to avoid modifying original
    soup_copy = BeautifulSoup(str(soup), "html.parser")

    # Step 1: Remove navigation elements
    for selector in NAV_SELECTORS:
        for element in soup_copy.select(selector):
            element.decompose()

    # Step 2: Remove header elements
    for selector in HEADER_SELECTORS:
        for element in soup_copy.select(selector):
            element.decompose()

    # Step 3: Remove footer elements
    for selector in FOOTER_SELECTORS:
        for element in soup_copy.select(selector):
            element.decompose()

    # Step 4: Remove sidebar/aside elements
    for selector in SIDEBAR_SELECTORS:
        for element in soup_copy.select(selector):
            element.decompose()

    # Step 5: Remove advertisement elements
    for selector in AD_SELECTORS:
        for element in soup_copy.select(selector):
            element.decompose()

    # Step 6: Remove script and style tags
    for element in soup_copy.find_all(["script", "style"]):
        element.decompose()

    # Step 7: Try to find and extract main content
    main_content = _extract_main_content(soup_copy)

    return main_content if main_content else soup_copy


def _extract_main_content(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    """Extract main content area from filtered HTML.

    This function looks for common main content indicators like <main>,
    <article>, or divs with semantic role="main" attributes.

    Args:
        soup: BeautifulSoup object to search

    Returns:
        BeautifulSoup containing main content, or None if not found
    """
    # Try to find main content by selector
    for selector in MAIN_CONTENT_SELECTORS:
        main_element = soup.select_one(selector)
        if main_element:
            return BeautifulSoup(str(main_element), "html.parser")

    # Fallback: Look for the largest block of text (likely main content)
    body = soup.find("body")
    if body:
        return BeautifulSoup(str(body), "html.parser")

    return None


def remove_boilerplate(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove common boilerplate elements from HTML.

    This is a lighter version of filter_main_content that removes noise
    but keeps the overall structure intact.

    Args:
        soup: BeautifulSoup object to clean

    Returns:
        BeautifulSoup with boilerplate removed
    """
    soup_copy = BeautifulSoup(str(soup), "html.parser")

    # Remove common boilerplate selectors
    boilerplate_selectors = NAV_SELECTORS + HEADER_SELECTORS + FOOTER_SELECTORS + SIDEBAR_SELECTORS + AD_SELECTORS

    for selector in boilerplate_selectors:
        for element in soup_copy.select(selector):
            try:
                element.decompose()
            except Exception:
                # Element may have already been decomposed
                pass

    # Remove script and style tags
    for element in soup_copy.find_all(["script", "style"]):
        try:
            element.decompose()
        except Exception:
            pass

    return soup_copy


def get_text_nodes(soup: BeautifulSoup, skip_whitespace: bool = True) -> list[str]:
    """Extract all text nodes from HTML.

    Args:
        soup: BeautifulSoup object
        skip_whitespace: If True, skip nodes that are only whitespace

    Returns:
        List of text strings extracted from the HTML
    """
    text_nodes = []

    for element in soup.descendants:
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text and (not skip_whitespace or text.strip()):
                text_nodes.append(text)

    return text_nodes


def extract_paragraphs(soup: BeautifulSoup) -> list[str]:
    """Extract paragraph content from HTML.

    Args:
        soup: BeautifulSoup object

    Returns:
        List of paragraph text content
    """
    paragraphs = []

    for p_tag in soup.find_all("p"):
        text = p_tag.get_text(strip=True)
        if text:
            paragraphs.append(text)

    return paragraphs


def extract_headings(soup: BeautifulSoup) -> list[tuple[int, str]]:
    """Extract heading hierarchy from HTML.

    Args:
        soup: BeautifulSoup object

    Returns:
        List of tuples (heading_level, heading_text)
        Where heading_level is 1-6 (h1-h6)
    """
    headings = []

    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(heading.name[1])
        text = heading.get_text(strip=True)
        if text:
            headings.append((level, text))

    return headings


def clean_text_for_tts(text: str) -> str:
    """Clean text for text-to-speech synthesis.

    Removes or normalizes problematic characters and formatting
    that can cause issues with TTS engines like Piper.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text suitable for TTS

    """
    if not text:
        return ""

    # First, try to encode and decode as UTF-8 to catch surrogates
    try:
        text = text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        pass

    # Normalize Unicode characters (decompose special characters)
    try:
        text = unicodedata.normalize("NFKD", text)
    except Exception:
        pass

    # Remove control characters and invalid surrogates
    try:
        text = "".join(
            char
            for char in text
            if unicodedata.category(char)[0] != "C" or char in "\n\t\r"
        )
    except Exception:
        pass

    # Replace common HTML entities and symbols with text equivalents
    replacements = {
        "&nbsp;": " ",
        "&mdash;": " - ",
        "&ndash;": " - ",
        "&ldquo;": '"',
        "&rdquo;": '"',
        "&lsquo;": "'",
        "&rsquo;": "'",
        "©": "(c)",
        "®": "(R)",
        "™": "(TM)",
        "…": "...",
        "–": "-",
        "—": "-",
        """: '"',
        """: '"',
        "'": "'",
        "'": "'",
    }

    for entity, replacement in replacements.items():
        text = text.replace(entity, replacement)

    # Remove multiple consecutive spaces
    text = re.sub(r" +", " ", text)

    # Remove multiple consecutive newlines
    text = re.sub(r"\n\n+", "\n", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Final safety: encode to ASCII and replace unencoded chars
    try:
        # Try to encode as ASCII, replacing non-ASCII with "?"
        text = text.encode("ascii", errors="ignore").decode("ascii")
    except Exception:
        # If that fails, just ensure it's valid UTF-8
        text = text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

    return text
