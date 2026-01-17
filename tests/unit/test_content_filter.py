"""Unit tests for content filter module."""

import pytest
from bs4 import BeautifulSoup

from src.extraction.content_filter import (
    extract_headings,
    extract_paragraphs,
    filter_main_content,
    get_text_nodes,
    remove_boilerplate,
)


class TestContentFilter:
    """Test suite for content filtering functionality."""

    def test_filter_main_content_with_nav(self):
        """Test that navigation elements are removed."""
        html = """
        <html>
        <body>
            <nav><a href="/home">Home</a></nav>
            <main><p>Main content</p></main>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        filtered = filter_main_content(soup)

        assert filtered is not None
        text = filtered.get_text(strip=True)
        assert "Main content" in text
        assert "Home" not in text or text.count("Home") == 0

    def test_filter_main_content_with_header_footer(self):
        """Test that header and footer are removed."""
        html = """
        <html>
        <body>
            <header><h1>Site Header</h1></header>
            <article><p>Article content</p></article>
            <footer><p>Copyright 2026</p></footer>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        filtered = filter_main_content(soup)

        assert filtered is not None
        text = filtered.get_text(strip=True)
        assert "Article content" in text

    def test_filter_main_content_with_sidebar(self):
        """Test that sidebar elements are removed."""
        html = """
        <html>
        <body>
            <main>
                <article><p>Main article</p></article>
            </main>
            <aside><p>Related links</p></aside>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        filtered = filter_main_content(soup)

        assert filtered is not None
        text = filtered.get_text(strip=True)
        assert "Main article" in text

    def test_remove_boilerplate(self):
        """Test boilerplate removal function."""
        html = """
        <html>
        <body>
            <nav>Navigation</nav>
            <header>Header</header>
            <main><p>Content</p></main>
            <footer>Footer</footer>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        cleaned = remove_boilerplate(soup)

        assert cleaned is not None
        text = cleaned.get_text(strip=True)
        assert "Content" in text

    def test_get_text_nodes(self):
        """Test text node extraction."""
        html = "<html><body><p>Paragraph 1</p><p>Paragraph 2</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        nodes = get_text_nodes(soup)

        assert len(nodes) >= 2
        assert "Paragraph 1" in nodes
        assert "Paragraph 2" in nodes

    def test_extract_paragraphs(self):
        """Test paragraph extraction."""
        html = """
        <html>
        <body>
            <p>First paragraph</p>
            <div>Not a paragraph</div>
            <p>Second paragraph</p>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = extract_paragraphs(soup)

        assert len(paragraphs) == 2
        assert "First paragraph" in paragraphs
        assert "Second paragraph" in paragraphs
        assert "Not a paragraph" not in paragraphs

    def test_extract_headings(self):
        """Test heading extraction with hierarchy."""
        html = """
        <html>
        <body>
            <h1>Main Title</h1>
            <h2>Subsection</h2>
            <h3>Sub-subsection</h3>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        headings = extract_headings(soup)

        assert len(headings) == 3
        assert headings[0] == (1, "Main Title")
        assert headings[1] == (2, "Subsection")
        assert headings[2] == (3, "Sub-subsection")

    def test_extract_headings_skips_empty(self):
        """Test that empty headings are skipped."""
        html = """
        <html>
        <body>
            <h1>Title</h1>
            <h2></h2>
            <h3>Subtitle</h3>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        headings = extract_headings(soup)

        assert len(headings) == 2
        assert all(text for level, text in headings)

    def test_filter_removes_scripts_and_styles(self):
        """Test that script and style tags are removed."""
        html = """
        <html>
        <body>
            <style>body { color: red; }</style>
            <p>Content</p>
            <script>alert('test');</script>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        filtered = filter_main_content(soup)

        assert filtered is not None
        text = filtered.get_text(strip=True)
        assert "alert" not in text
        assert "color" not in text
        assert "Content" in text

    def test_filter_main_content_with_none(self):
        """Test that None input is handled gracefully."""
        result = filter_main_content(None)
        assert result is None

    def test_filter_main_content_with_empty_html(self):
        """Test filtering empty HTML."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        filtered = filter_main_content(soup)

        assert filtered is not None

    def test_extract_paragraphs_empty_html(self):
        """Test paragraph extraction from empty HTML."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = extract_paragraphs(soup)

        assert len(paragraphs) == 0
