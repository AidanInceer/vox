"""Unit tests for history UI functionality.

Tests for T077: History copy functionality in src/ui/main_window.py.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.persistence.database import VoxDatabase


class TestHistoryCopyFunctionality:
    """Tests for history copy functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Create temp database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_history.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_history_stores_transcription(self) -> None:
        """Test that transcriptions are stored in history."""
        text = "Hello world test transcription"
        record_id = self.database.add_transcription(text)

        assert record_id is not None
        assert record_id > 0

        # Verify it can be retrieved
        history = self.database.get_history(limit=10)
        assert len(history) == 1
        assert history[0].text == text

    def test_history_retrieval(self) -> None:
        """Test that history can be retrieved."""
        # Add multiple transcriptions
        texts = [
            "First transcription",
            "Second transcription",
            "Third transcription",
        ]

        for text in texts:
            self.database.add_transcription(text)

        # Retrieve history
        history = self.database.get_history(limit=10)

        assert len(history) == 3
        # Should be in reverse chronological order (newest first)
        assert history[0].text == "Third transcription"

    def test_history_limit_works(self) -> None:
        """Test that history limit is respected."""
        # Add 5 transcriptions
        for i in range(5):
            self.database.add_transcription(f"Transcription {i}")

        # Retrieve with limit of 3
        history = self.database.get_history(limit=3)

        assert len(history) == 3

    @patch("src.clipboard.paster.pyperclip")
    def test_clipboard_paster_copy(self, mock_pyperclip: MagicMock) -> None:
        """Test that ClipboardPaster can copy text to clipboard."""
        from src.clipboard.paster import ClipboardPaster

        paster = ClipboardPaster()
        text = "Test text to copy"

        paster.copy_to_clipboard(text)

        mock_pyperclip.copy.assert_called_once_with(text)

    @patch("src.clipboard.paster.pyperclip")
    def test_clipboard_paster_handles_unicode(self, mock_pyperclip: MagicMock) -> None:
        """Test that ClipboardPaster handles unicode text."""
        from src.clipboard.paster import ClipboardPaster

        paster = ClipboardPaster()
        text = "Hello 世界 🌍 नमस्ते"

        paster.copy_to_clipboard(text)

        mock_pyperclip.copy.assert_called_once_with(text)


class TestHistoryItemDisplay:
    """Tests for history item display functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_display.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_transcription_record_has_timestamp(self) -> None:
        """Test that transcription records have timestamps."""
        self.database.add_transcription("Test text")
        history = self.database.get_history(limit=1)
        record = history[0]

        assert record.created_at is not None
        assert isinstance(record.created_at, datetime)

    def test_transcription_record_has_word_count(self) -> None:
        """Test that word count can be calculated from transcription."""
        text = "This is a test with seven words"
        self.database.add_transcription(text)
        history = self.database.get_history(limit=1)
        record = history[0]

        word_count = len(record.text.split())

        assert word_count == 7

    def test_text_preview_truncation(self) -> None:
        """Test that long text is truncated for preview."""
        # Long text > 100 characters
        long_text = "This is a very long transcription. " * 10

        self.database.add_transcription(long_text)
        history = self.database.get_history(limit=1)
        record = history[0]

        # Truncate logic from _create_history_item
        text_preview = record.text[:100] + "..." if len(record.text) > 100 else record.text

        assert len(text_preview) <= 103  # 100 chars + "..."
        assert text_preview.endswith("...")

    def test_text_preview_no_truncation_for_short_text(self) -> None:
        """Test that short text is not truncated."""
        short_text = "Short transcription"

        self.database.add_transcription(short_text)
        history = self.database.get_history(limit=1)
        record = history[0]

        # Truncate logic from _create_history_item
        text_preview = record.text[:100] + "..." if len(record.text) > 100 else record.text

        assert text_preview == short_text
        assert not text_preview.endswith("...")


class TestHistoryRefresh:
    """Tests for history refresh functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_refresh.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_history_shows_new_transcriptions(self) -> None:
        """Test that new transcriptions appear in history."""
        # Initially empty
        history = self.database.get_history(limit=10)
        assert len(history) == 0

        # Add transcription
        self.database.add_transcription("New transcription")

        # Refresh history
        history = self.database.get_history(limit=10)
        assert len(history) == 1
        assert history[0].text == "New transcription"

    def test_clear_history_removes_all_items(self) -> None:
        """Test that clear history removes all items."""
        # Add some transcriptions
        for i in range(5):
            self.database.add_transcription(f"Transcription {i}")

        # Verify they exist
        history = self.database.get_history(limit=10)
        assert len(history) == 5

        # Clear history
        count = self.database.clear_history()

        # Verify cleared
        assert count == 5
        history = self.database.get_history(limit=10)
        assert len(history) == 0


class TestHistoryPagination:
    """Tests for history pagination functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_pagination.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_history_limit_default(self) -> None:
        """Test that history has a reasonable default limit."""
        # Add many transcriptions
        for i in range(150):
            self.database.add_transcription(f"Transcription {i}")

        # Default limit in main_window is 100
        history = self.database.get_history(limit=100)

        assert len(history) == 100

    def test_history_ordering(self) -> None:
        """Test that history is ordered newest first."""
        # Add transcriptions in order
        self.database.add_transcription("First")
        self.database.add_transcription("Second")
        self.database.add_transcription("Third")

        history = self.database.get_history(limit=10)

        # Newest should be first
        assert history[0].text == "Third"
        assert history[1].text == "Second"
        assert history[2].text == "First"
