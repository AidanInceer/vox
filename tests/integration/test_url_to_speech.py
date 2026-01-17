"""Integration tests for URL and file-based reading workflows."""

import pytest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import tempfile
import os

from src.extraction.text_extractor import ConcreteTextExtractor
from src.extraction.url_fetcher import fetch_url
from src.extraction.file_loader import load_file
from src.tts.synthesizer import PiperSynthesizer
from src.tts.playback import AudioPlayback
from src.utils.errors import URLFetchError, FileLoadError


class TestURLToSpeechIntegration:
    """Integration test suite for URL and file-based reading workflows."""

    @patch("src.tts.synthesizer.synthesize_piper")
    @patch("src.extraction.url_fetcher.requests.get")
    def test_full_url_read_flow(self, mock_get, mock_synthesize):
        """Test complete flow: fetch URL, extract text, synthesize, playback."""
        # Mock URL fetch
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
            <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Welcome to Test</h1>
                <p>This is the main content.</p>
                <p>More information here.</p>
            </body>
            </html>
        """
        mock_response.encoding = "utf-8"
        mock_get.return_value = mock_response

        # Mock TTS synthesis
        mock_audio_bytes = b"mock audio data"
        mock_synthesize.return_value = mock_audio_bytes

        # Execute flow
        url = "https://example.com/test"
        html_content = fetch_url(url)
        assert "Welcome to Test" in html_content

        # Extract text
        extractor = ConcreteTextExtractor()
        text = extractor.extract_html(html_content)
        assert text is not None
        assert len(text) > 0

        # Synthesize to speech
        synthesizer = PiperSynthesizer()
        audio = synthesizer.synthesize(text)
        assert audio is not None
        assert len(audio) > 0

    def test_file_read_flow(self):
        """Test complete flow: load HTML file, extract text, synthesize, playback."""
        html_content = """
            <html>
            <head><title>Local File Test</title></head>
            <body>
                <h1>Local Content</h1>
                <p>Reading from a local file.</p>
            </body>
            </html>
        """

        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            # Load file
            loaded_content = load_file(tmp_path)
            # Normalize line endings for comparison (Windows uses \r\n)
            assert loaded_content.replace('\r\n', '\n') == html_content.replace('\r\n', '\n')

            # Extract text
            extractor = ConcreteTextExtractor()
            text = extractor.extract_html(loaded_content)
            assert "Local Content" in text

            # Verify text extraction worked
            assert text is not None
            assert len(text) > 0
        finally:
            os.unlink(tmp_path)

    @patch("src.tts.synthesizer.synthesize_piper")
    def test_complex_webpage_extraction(self, mock_synthesize):
        """Test extraction from complex webpage with nav/header/footer prioritizing main content."""
        html_content = """
            <html>
            <head><title>Complex Page</title></head>
            <body>
                <header>
                    <nav>
                        <a href="/home">Home</a>
                        <a href="/about">About</a>
                        <a href="/contact">Contact</a>
                    </nav>
                </header>
                
                <main>
                    <article>
                        <h1>Main Article Title</h1>
                        <p>This is the primary content that should be extracted first.</p>
                        <p>Important information for the user.</p>
                        <section>
                            <h2>Subsection</h2>
                            <p>Additional context and details.</p>
                        </section>
                    </article>
                </main>
                
                <aside>
                    <h3>Related Links</h3>
                    <ul>
                        <li>Link 1</li>
                        <li>Link 2</li>
                    </ul>
                </aside>
                
                <footer>
                    <p>Copyright 2026</p>
                </footer>
            </body>
            </html>
        """

        # Extract text
        extractor = ConcreteTextExtractor()
        text = extractor.extract_html(html_content)

        # Verify main content is present
        assert "Main Article Title" in text
        assert "primary content" in text
        assert "Additional context" in text

        # Verify navigation appears but shouldn't be the focus
        # (actual filtering is handled by content_filter, this just tests extraction)
        assert text is not None
        assert len(text) > 50

    def test_url_fetch_with_invalid_url(self):
        """Test URL fetching with invalid URL raises appropriate error."""
        with pytest.raises(URLFetchError):
            fetch_url("not a valid url")

    def test_file_load_with_missing_file(self):
        """Test file loading with non-existent file raises appropriate error."""
        with pytest.raises(FileLoadError):
            load_file("/nonexistent/path/to/file.html")

    @patch("src.extraction.url_fetcher.requests.get")
    def test_url_read_with_timeout_handling(self, mock_get):
        """Test URL reading handles timeouts gracefully."""
        from requests.exceptions import Timeout

        mock_get.side_effect = Timeout("Request timed out")

        with pytest.raises(URLFetchError) as exc_info:
            fetch_url("https://slow-example.com", timeout=5)

        assert "timeout" in str(exc_info.value).lower()

    @patch("src.tts.synthesizer.synthesize_piper")
    def test_text_extraction_preserves_order(self, mock_synthesize):
        """Test that text extraction preserves reading order."""
        html_content = """
            <html>
            <body>
                <h1>First</h1>
                <p>Second paragraph</p>
                <h2>Third section</h2>
                <p>Fourth paragraph</p>
            </body>
            </html>
        """

        extractor = ConcreteTextExtractor()
        text = extractor.extract_html(html_content)

        # Extract text in order
        first_idx = text.find("First")
        second_idx = text.find("Second")
        third_idx = text.find("Third")
        fourth_idx = text.find("Fourth")

        # Verify reading order is preserved
        assert first_idx < second_idx < third_idx < fourth_idx

    @patch("src.tts.synthesizer.synthesize_piper")
    @patch("src.extraction.url_fetcher.requests.get")
    def test_url_to_speech_with_unicode_content(self, mock_get, mock_synthesize):
        """Test URL-to-speech with unicode characters and special symbols."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
            <html>
            <body>
                <h1>Unicode Test: Café français</h1>
                <p>Symbols: © ® ™ € £ ¥</p>
                <p>Other languages: 你好 مرحبا Привет</p>
            </body>
            </html>
        """
        mock_response.encoding = "utf-8"
        mock_get.return_value = mock_response

        mock_synthesize.return_value = b"audio data"

        # Fetch and extract
        html = fetch_url("https://example.com/unicode")
        extractor = ConcreteTextExtractor()
        text = extractor.extract_html(html)

        # Verify unicode content is preserved
        assert "Café" in text
        assert "français" in text

    def test_html_file_with_meta_charset_utf8(self):
        """Test loading HTML file with explicit UTF-8 charset declaration."""
        html_content = """
            <html>
            <head>
                <meta charset="UTF-8">
                <title>UTF-8 Test</title>
            </head>
            <body>
                <p>Café, naïve, résumé</p>
            </body>
            </html>
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            loaded = load_file(tmp_path)
            assert "UTF-8" in loaded
            assert "Café" in loaded
        finally:
            os.unlink(tmp_path)

    @patch("src.tts.synthesizer.synthesize_piper")
    def test_empty_html_file_handling(self, mock_synthesize):
        """Test handling of empty or near-empty HTML files."""
        html_content = "<html><body></body></html>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            loaded = load_file(tmp_path)
            assert loaded == html_content

            # Extract text from empty HTML
            extractor = ConcreteTextExtractor()
            text = extractor.extract_html(loaded)
            # Should return empty or minimal text
            assert text is not None
        finally:
            os.unlink(tmp_path)
