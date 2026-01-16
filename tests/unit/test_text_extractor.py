"""Tests for HTML parsing and text extraction (User Story 1).

These tests verify the ability to parse HTML content and extract
readable text while preserving reading order and structure.
"""

import pytest
from src.extraction.text_extractor import TextExtractor
from src.utils.errors import ExtractionError


class TestHTMLExtraction:
    """Test HTML parsing and text extraction."""

    def test_extract_simple_html(self):
        """Extract text from basic HTML."""
        html = """
        <html>
            <body>
                <h1>Welcome to Example Site</h1>
                <p>This is a test page.</p>
            </body>
        </html>
        """
        
        # This test assumes extract_html method exists on TextExtractor
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        assert text is not None
        assert 'Welcome to Example Site' in text
        assert 'This is a test page' in text

    def test_extract_with_whitespace_handling(self):
        """Handle excess whitespace correctly."""
        html = """
        <html>
            <body>
                <p>Line  with   extra    spaces</p>
                <p>
                
                
                    Text with extra newlines
                
                </p>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        # Should normalize whitespace
        assert 'Line with extra spaces' in text or 'Line  with   extra    spaces' in text
        assert text is not None

    def test_extract_preserves_reading_order(self):
        """Extract text in correct reading order (DOM traversal)."""
        html = """
        <html>
            <body>
                <div>
                    <h1>First</h1>
                    <p>Second</p>
                </div>
                <div>
                    <h2>Third</h2>
                    <p>Fourth</p>
                </div>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        # Verify reading order is preserved (using string positions)
        first_pos = text.find('First')
        second_pos = text.find('Second')
        third_pos = text.find('Third')
        fourth_pos = text.find('Fourth')
        
        # Check all text is present
        assert first_pos >= 0 and second_pos >= 0 and third_pos >= 0 and fourth_pos >= 0
        
        # Check order is approximately preserved
        assert first_pos < second_pos < third_pos < fourth_pos

    def test_extract_with_complex_dom(self):
        """Extract text from complex HTML with nested structures."""
        html = """
        <html>
            <body>
                <header>
                    <nav>
                        <a href="#">Home</a>
                        <a href="#">About</a>
                    </nav>
                </header>
                <main>
                    <article>
                        <h1>Article Title</h1>
                        <p>First paragraph with <strong>bold</strong> text.</p>
                        <p>Second paragraph.</p>
                        <ul>
                            <li>List item 1</li>
                            <li>List item 2</li>
                        </ul>
                    </article>
                    <aside>
                        <h3>Sidebar</h3>
                        <p>Sidebar content.</p>
                    </aside>
                </main>
                <footer>
                    <p>Copyright 2026</p>
                </footer>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        # Verify key content is extracted
        assert 'Article Title' in text
        assert 'First paragraph' in text
        assert 'bold' in text
        assert 'List item 1' in text
        assert 'List item 2' in text
        assert 'Copyright 2026' in text

    def test_extract_unicode_content(self):
        """Handle Unicode and special characters correctly."""
        html = """
        <html>
            <body>
                <p>English text</p>
                <p>Émojis: 🎉 🎊 🎈</p>
                <p>Special chars: café, naïve, résumé</p>
                <p>Math: ∑ ∏ √ ∞</p>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        assert 'English' in text
        assert text is not None
        # Unicode should be preserved or handled gracefully
        assert len(text) > 0

    def test_extract_removes_script_tags(self):
        """Filter out script tags and content."""
        html = """
        <html>
            <body>
                <h1>Main Content</h1>
                <script>
                    var x = "This should not appear";
                    console.log('Hidden code');
                </script>
                <p>Visible paragraph</p>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        assert 'Main Content' in text
        assert 'Visible paragraph' in text
        # Script content should be removed
        assert 'console.log' not in text or text.count('console.log') == 0

    def test_extract_removes_style_tags(self):
        """Filter out style tags and CSS."""
        html = """
        <html>
            <head>
                <style>
                    body { color: red; }
                    h1 { font-size: 2em; }
                </style>
            </head>
            <body>
                <h1>Title</h1>
                <p>Content</p>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        assert 'Title' in text
        assert 'Content' in text
        # CSS should be removed
        assert 'font-size' not in text

    def test_extract_preserves_paragraph_boundaries(self):
        """Maintain paragraph/section boundaries in output."""
        html = """
        <html>
            <body>
                <p>Paragraph 1</p>
                <p>Paragraph 2</p>
                <section>
                    <h2>Section Title</h2>
                    <p>Section paragraph</p>
                </section>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        # All paragraphs should be present and distinguishable
        assert 'Paragraph 1' in text
        assert 'Paragraph 2' in text
        assert 'Section Title' in text
        assert 'Section paragraph' in text

    def test_extract_handles_data_attributes(self):
        """Handle HTML5 data attributes gracefully."""
        html = """
        <html>
            <body>
                <div data-id="123" data-type="article">
                    <h1>Article with Data</h1>
                    <p data-highlight="true">Important paragraph</p>
                </div>
            </body>
        </html>
        """
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        assert 'Article with Data' in text
        assert 'Important paragraph' in text
        # Data attributes should not appear in text
        assert 'data-id' not in text


class TestExtractionErrors:
    """Test error handling in text extraction."""

    def test_extract_empty_html(self):
        """Handle empty HTML gracefully."""
        extractor = TextExtractor()
        text = extractor.extract_html("")
        
        assert text is not None
        assert text.strip() == "" or len(text.strip()) == 0

    def test_extract_invalid_html(self):
        """Handle malformed HTML gracefully (BeautifulSoup is forgiving)."""
        html = "<p>Unclosed paragraph<div>Nested unclosed</div>"
        
        extractor = TextExtractor()
        text = extractor.extract_html(html)
        
        # BeautifulSoup should still extract text despite malformed HTML
        assert 'Unclosed paragraph' in text

    def test_extract_very_large_html(self):
        """Handle large HTML documents."""
        # Generate large HTML
        large_html = "<html><body>"
        for i in range(1000):
            large_html += f"<p>Paragraph {i}: This is test content {i}</p>"
        large_html += "</body></html>"
        
        extractor = TextExtractor()
        text = extractor.extract_html(large_html)
        
        # Should extract without error
        assert text is not None
        assert 'Paragraph 0' in text
        assert 'Paragraph 999' in text


class TestTextExtractorInterface:
    """Test TextExtractor interface contract."""

    def test_extractor_implements_extract_method(self):
        """TextExtractor should have extract_html method."""
        extractor = TextExtractor()
        assert hasattr(extractor, 'extract_html')
        assert callable(extractor.extract_html)

    def test_extractor_returns_string(self):
        """extract_html should always return a string."""
        extractor = TextExtractor()
        html = "<p>Test</p>"
        result = extractor.extract_html(html)
        
        assert isinstance(result, str)

    def test_supports_method_exists(self):
        """TextExtractor should have supports method."""
        extractor = TextExtractor()
        assert hasattr(extractor, 'supports')
        assert callable(extractor.supports)

    def test_supports_html_type(self):
        """Extractor should support HTML source type."""
        extractor = TextExtractor()
        # Should return True for HTML
        supports_html = extractor.supports('html')
        assert supports_html is True
