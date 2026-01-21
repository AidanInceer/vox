"""Unit tests for ClipboardPaster class.

Tests cover:
- Clipboard read/write operations
- Paste simulation via Ctrl+V
- Clipboard restoration after paste
"""

from unittest.mock import MagicMock, call, patch

import pytest

from src.clipboard.paster import ClipboardPaster
from src.utils.errors import PasteError


class TestClipboardPasterBasicOperations:
    """Tests for basic clipboard operations."""

    @patch("src.clipboard.paster.pyperclip")
    def test_copy_to_clipboard_stores_text(self, mock_pyperclip: MagicMock) -> None:
        """copy_to_clipboard should store text in system clipboard."""
        paster = ClipboardPaster()
        paster.copy_to_clipboard("Hello world")

        mock_pyperclip.copy.assert_called_once_with("Hello world")

    @patch("src.clipboard.paster.pyperclip")
    def test_copy_to_clipboard_handles_unicode(self, mock_pyperclip: MagicMock) -> None:
        """copy_to_clipboard should handle unicode characters."""
        paster = ClipboardPaster()
        paster.copy_to_clipboard("你好世界 🌍")

        mock_pyperclip.copy.assert_called_once_with("你好世界 🌍")

    @patch("src.clipboard.paster.pyperclip")
    def test_copy_to_clipboard_handles_empty_string(
        self, mock_pyperclip: MagicMock
    ) -> None:
        """copy_to_clipboard should handle empty strings."""
        paster = ClipboardPaster()
        paster.copy_to_clipboard("")

        mock_pyperclip.copy.assert_called_once_with("")

    @patch("src.clipboard.paster.pyperclip")
    def test_copy_to_clipboard_raises_on_error(
        self, mock_pyperclip: MagicMock
    ) -> None:
        """copy_to_clipboard should raise PasteError on failure."""
        mock_pyperclip.copy.side_effect = Exception("Clipboard error")

        paster = ClipboardPaster()

        with pytest.raises(PasteError):
            paster.copy_to_clipboard("test")

    @patch("src.clipboard.paster.pyperclip")
    def test_get_clipboard_returns_text(self, mock_pyperclip: MagicMock) -> None:
        """get_clipboard should return current clipboard text."""
        mock_pyperclip.paste.return_value = "clipboard content"

        paster = ClipboardPaster()
        result = paster.get_clipboard()

        assert result == "clipboard content"

    @patch("src.clipboard.paster.pyperclip")
    def test_get_clipboard_returns_empty_for_none(
        self, mock_pyperclip: MagicMock
    ) -> None:
        """get_clipboard should return empty string for None."""
        mock_pyperclip.paste.return_value = None

        paster = ClipboardPaster()
        result = paster.get_clipboard()

        assert result == ""

    @patch("src.clipboard.paster.pyperclip")
    def test_get_clipboard_returns_empty_on_error(
        self, mock_pyperclip: MagicMock
    ) -> None:
        """get_clipboard should return empty string on error."""
        mock_pyperclip.paste.side_effect = Exception("Clipboard error")

        paster = ClipboardPaster()
        result = paster.get_clipboard()

        assert result == ""


class TestClipboardPasterPaste:
    """Tests for paste simulation functionality."""

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_copies_to_clipboard(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should copy text to clipboard first."""
        mock_pyperclip.paste.return_value = ""

        paster = ClipboardPaster()
        paster.paste_text("Hello world", restore_clipboard=False)

        mock_pyperclip.copy.assert_called_with("Hello world")

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_simulates_ctrl_v(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should simulate Ctrl+V keystroke."""
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_pyperclip.paste.return_value = ""

        paster = ClipboardPaster()
        paster.paste_text("test", restore_clipboard=False)

        # Verify pressed context manager was used with ctrl key
        mock_controller.pressed.assert_called()
        mock_controller.tap.assert_called_with("v")

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_returns_true_on_success(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should return True when successful."""
        mock_pyperclip.paste.return_value = ""

        paster = ClipboardPaster()
        result = paster.paste_text("test", restore_clipboard=False)

        assert result is True

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_returns_false_for_empty(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should return False for empty text."""
        paster = ClipboardPaster()
        result = paster.paste_text("", restore_clipboard=False)

        assert result is False


class TestClipboardPasterRestore:
    """Tests for clipboard restoration functionality."""

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_saves_original_clipboard(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should save original clipboard when restore=True."""
        mock_pyperclip.paste.return_value = "original"

        paster = ClipboardPaster()
        paster.paste_text("new text", restore_clipboard=True)

        # First call should be to get original content
        mock_pyperclip.paste.assert_called()

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_restores_clipboard(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should restore original clipboard after paste."""
        mock_pyperclip.paste.return_value = "original content"

        paster = ClipboardPaster()
        paster.paste_text("new text", restore_clipboard=True)

        # Should have copy calls: one for paste, one for restore
        copy_calls = mock_pyperclip.copy.call_args_list
        assert len(copy_calls) >= 2
        # Last copy should restore original
        assert copy_calls[-1] == call("original content")

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_skips_restore_when_disabled(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should not restore when restore_clipboard=False."""
        mock_pyperclip.paste.return_value = "original"

        paster = ClipboardPaster()
        paster.paste_text("new text", restore_clipboard=False)

        # Should only have one copy call (for the paste)
        assert mock_pyperclip.copy.call_count == 1
        mock_pyperclip.copy.assert_called_with("new text")


class TestClipboardPasterErrorHandling:
    """Tests for error handling."""

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_raises_on_copy_error(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should raise PasteError on copy failure."""
        mock_pyperclip.paste.return_value = ""
        mock_pyperclip.copy.side_effect = Exception("Copy failed")

        paster = ClipboardPaster()

        with pytest.raises(PasteError):
            paster.paste_text("test")

    @patch("src.clipboard.paster.time.sleep")
    @patch("src.clipboard.paster.pyperclip")
    @patch("src.clipboard.paster.keyboard.Controller")
    def test_paste_text_raises_on_keystroke_error(
        self,
        mock_controller_class: MagicMock,
        mock_pyperclip: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """paste_text should raise PasteError on keystroke failure."""
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        mock_pyperclip.paste.return_value = ""

        # Make the pressed context manager raise an error
        mock_controller.pressed.side_effect = Exception("Keystroke failed")

        paster = ClipboardPaster()

        with pytest.raises(PasteError):
            paster.paste_text("test")
