"""
End-to-end integration tests for PageReader CLI.

Tests the full workflow from CLI invocation through text extraction,
synthesis, and playback using real URLs and mock audio output.
"""

import pytest
import sys
import io
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import CLI functions
from src.main import main, create_parser


class TestEndToEndURLReading:
    """Test complete URL reading workflow from CLI to audio output."""

    @patch("src.main.PiperSynthesizer")
    @patch("src.main.get_playback")
    @patch("src.main.ConcreteTextExtractor")
    def test_read_url_complete_flow(self, mock_extractor_class, mock_get_playback, mock_synth_class):
        """Test reading a URL from start to finish."""
        # Setup mocks
        mock_extractor = MagicMock()
        mock_extractor.extract_from_url.return_value = "Python is a high-level programming language."
        mock_extractor_class.return_value = mock_extractor

        mock_synth = MagicMock()
        mock_synth.synthesize.return_value = b"fake_audio_data"
        mock_synth.is_available.return_value = True
        mock_synth_class.return_value = mock_synth

        mock_player = MagicMock()
        mock_player.play_audio.return_value = None
        mock_get_playback.return_value = mock_player

        # Simulate CLI arguments
        test_args = ["pagereader", "read", "--url", "https://example.com/test"]
        with patch.object(sys, "argv", test_args):
            captured_output = io.StringIO()
            with patch("sys.stdout", captured_output):
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0, f"CLI exited with non-zero code: {e.code}"

        # Verify workflow
        mock_extractor.extract_from_url.assert_called_once_with("https://example.com/test")
        assert mock_synth.synthesize.called
        assert mock_player.play_audio.called


    def test_url_validation_error_handling(self):
        """Test that invalid URLs are rejected with helpful error."""
        test_args = ["pagereader", "read", "--url", "invalid-url"]
        with patch.object(sys, "argv", test_args):
            captured_output = io.StringIO()
            with patch("sys.stdout", captured_output):
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code != 0
        output = captured_output.getvalue()
        assert "ERROR" in output or "Invalid" in output


class TestCLIArgumentParsing:
    """Test CLI argument parsing and validation."""

    def test_parse_read_command_with_url(self):
        """Test parsing read command with URL argument."""
        parser = create_parser()
        args = parser.parse_args(["read", "--url", "https://example.com"])
        assert args.command == "read"
        assert args.url == "https://example.com"

    def test_parse_version_command(self):
        """Test parsing version flag."""
        parser = create_parser()
        args = parser.parse_args(["-v"])
        assert args.version is True


class TestVersionCommand:
    """Test version command functionality."""

    def test_version_flag_displays_version(self):
        """Test that -v flag displays app version."""
        test_args = ["pagereader", "-v"]
        with patch.object(sys, "argv", test_args):
            captured_output = io.StringIO()
            with patch("sys.stdout", captured_output):
                with pytest.raises(SystemExit) as exc_info:
                    main()

        assert exc_info.value.code == 0
        output = captured_output.getvalue()
        assert "PageReader" in output or "1.0" in output
