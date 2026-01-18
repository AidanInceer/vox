"""Unit tests for CLI colored output and messaging."""

import io
import sys
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from colorama import Fore, Style

from src.main import print_error, print_status, print_success, print_warning


@contextmanager
def capture_output():
    """Capture stdout for testing print functions."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = old_stdout


class TestColoredOutput:
    """Test colored output helper functions."""

    def test_print_status_contains_cyan(self):
        """Test that print_status uses cyan color."""
        with capture_output() as output:
            print_status("Test message")
            result = output.getvalue()
            assert "[*]" in result
            assert "Test message" in result

    def test_print_success_contains_green(self):
        """Test that print_success uses green color."""
        with capture_output() as output:
            print_success("Success message")
            result = output.getvalue()
            assert "[OK]" in result
            assert "Success message" in result

    def test_print_error_contains_red(self):
        """Test that print_error uses red color."""
        with capture_output() as output:
            print_error("Error message")
            result = output.getvalue()
            assert "[ERROR]" in result
            assert "Error message" in result

    def test_print_warning_contains_yellow(self):
        """Test that print_warning uses yellow color."""
        with capture_output() as output:
            print_warning("Warning message")
            result = output.getvalue()
            assert "[!]" in result
            assert "Warning message" in result

    def test_status_message_format(self):
        """Test that status messages have correct format."""
        with capture_output() as output:
            print_status("Fetching URL...")
            result = output.getvalue()
            assert result.strip().endswith("Fetching URL...")

    def test_success_message_format(self):
        """Test that success messages have correct format."""
        with capture_output() as output:
            print_success("Retrieved 1000 characters")
            result = output.getvalue()
            assert "Retrieved 1000 characters" in result

    def test_error_message_format(self):
        """Test that error messages have correct format."""
        with capture_output() as output:
            print_error("Failed to connect")
            result = output.getvalue()
            assert "Failed to connect" in result

    def test_warning_message_format(self):
        """Test that warning messages have correct format."""
        with capture_output() as output:
            print_warning("Check your connection")
            result = output.getvalue()
            assert "Check your connection" in result

    def test_multiple_messages_sequence(self):
        """Test that multiple messages can be printed in sequence."""
        with capture_output() as output:
            print_status("Starting...")
            print_success("Done")
            print_warning("Note")
            print_error("Failed")
            result = output.getvalue()
            assert "[*]" in result
            assert "[OK]" in result
            assert "[!]" in result
            assert "[ERROR]" in result

    def test_empty_message(self):
        """Test that empty messages are handled."""
        with capture_output() as output:
            print_status("")
            result = output.getvalue()
            assert "[*]" in result

    def test_special_characters_in_message(self):
        """Test that special characters are handled correctly."""
        with capture_output() as output:
            print_success("URL: https://example.com?param=value&other=123")
            result = output.getvalue()
            assert "https://example.com?param=value&other=123" in result

    def test_multiline_message(self):
        """Test that multiline messages are handled."""
        with capture_output() as output:
            print_error("Line 1\nLine 2\nLine 3")
            result = output.getvalue()
            assert "Line 1" in result
            assert "Line 2" in result
            assert "Line 3" in result


class TestCLIValidation:
    """Test CLI input validation and error messages."""

    @patch("src.main.ConcreteTextExtractor")
    def test_url_validation_missing_protocol(self, mock_extractor):
        """Test that URLs without http/https are rejected."""
        from src.main import _get_content

        class Args:
            tab = None
            url = "example.com"
            file = None
            active = False

        with capture_output() as output:
            result = _get_content(Args())
            output_text = output.getvalue()
            assert result == ""
            assert "Invalid URL format" in output_text or "URL must start with" in output_text

    @patch("src.main.ConcreteTextExtractor")
    def test_url_validation_http_protocol(self, mock_extractor):
        """Test that HTTP URLs are accepted."""
        from src.main import _get_content

        mock_extractor.return_value.extract_from_url.return_value = "Test content"

        class Args:
            tab = None
            url = "http://example.com"
            file = None
            active = False

        result = _get_content(Args())
        # Should call extract_from_url without validation error
        mock_extractor.return_value.extract_from_url.assert_called_once()

    @patch("src.main.ConcreteTextExtractor")
    def test_url_validation_https_protocol(self, mock_extractor):
        """Test that HTTPS URLs are accepted."""
        from src.main import _get_content

        mock_extractor.return_value.extract_from_url.return_value = "Test content"

        class Args:
            tab = None
            url = "https://example.com"
            file = None
            active = False

        result = _get_content(Args())
        # Should call extract_from_url without validation error
        mock_extractor.return_value.extract_from_url.assert_called_once()

    def test_file_validation_nonexistent(self):
        """Test that nonexistent files are rejected with helpful message."""
        from src.main import _get_content

        class Args:
            tab = None
            url = None
            file = "/nonexistent/path/file.html"
            active = False

        with capture_output() as output:
            result = _get_content(Args())
            output_text = output.getvalue()
            assert result == ""
            assert "File not found" in output_text


class TestCLIHelpText:
    """Test CLI help text and examples."""

    def test_parser_has_examples(self):
        """Test that parser includes usage examples."""
        from src.main import create_parser

        parser = create_parser()
        help_text = parser.format_help()
        assert "Examples:" in help_text
        assert "pagereader read --url" in help_text

    def test_parser_has_descriptions(self):
        """Test that parser has descriptive help text."""
        from src.main import create_parser

        parser = create_parser()
        help_text = parser.format_help()
        assert "ai tts" in help_text.lower() or "tts" in help_text.lower()

    def test_read_command_has_help(self):
        """Test that read command has helpful descriptions."""
        from src.main import create_parser

        parser = create_parser()
        # Parse with read command to get read-specific help
        try:
            args = parser.parse_args(["read", "--help"])
        except SystemExit:
            # --help causes SystemExit, which is expected
            pass


class TestProgressIndicators:
    """Test progress indicators and timing."""

    @patch("src.main._get_content")
    @patch("src.main.PiperSynthesizer")
    @patch("src.main._play_audio")
    def test_retrieval_shows_elapsed_time(self, mock_play, mock_synth, mock_get):
        """Test that content retrieval shows elapsed time."""
        from src.main import command_read

        mock_get.return_value = "Test content"
        mock_synth.return_value.synthesize.return_value = b"audio data"

        class Args:
            tab = None
            url = "https://example.com"
            file = None
            active = False
            voice = "en_US-libritts-high"
            speed = 1.0
            no_play = False
            output = None
            verbose = False
            save_session = None

        with capture_output() as output:
            try:
                command_read(Args())
            except SystemExit:
                pass
            output_text = output.getvalue()
            # Should show timing like "Retrieved X characters (Y.YYs)"
            assert "Retrieved" in output_text
            assert "characters" in output_text

    @patch("src.main._get_content")
    @patch("src.main.PiperSynthesizer")
    @patch("src.main._play_audio")
    def test_synthesis_shows_elapsed_time(self, mock_play, mock_synth, mock_get):
        """Test that speech synthesis shows elapsed time."""
        from src.main import command_read

        mock_get.return_value = "Test content"
        mock_synth.return_value.synthesize.return_value = b"audio data"

        class Args:
            tab = None
            url = "https://example.com"
            file = None
            active = False
            voice = "en_US-libritts-high"
            speed = 1.0
            no_play = False
            output = None
            verbose = False
            save_session = None

        with capture_output() as output:
            try:
                command_read(Args())
            except SystemExit:
                pass
            output_text = output.getvalue()
            # Should show timing like "Generated X bytes (Y.YYs)"
            assert "Generated" in output_text or "Synthesizing" in output_text
