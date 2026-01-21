"""Unit tests for VoxDatabase class.

Tests cover:
- Database initialization and schema creation
- Settings operations (get/set)
- Transcription history operations (CRUD)
"""

from datetime import datetime
from pathlib import Path

from src.persistence.database import VoxDatabase, init_default_settings


class TestVoxDatabaseInit:
    """Tests for database initialization."""

    def test_creates_database_file(self, tmp_path: Path) -> None:
        """Database file should be created on initialization."""
        db_path = tmp_path / "test.db"
        assert not db_path.exists()

        db = VoxDatabase(db_path)
        try:
            assert db_path.exists()
        finally:
            db.close()

    def test_creates_schema_on_init(self, tmp_path: Path) -> None:
        """Settings and history tables should be created."""
        db_path = tmp_path / "test.db"
        db = VoxDatabase(db_path)

        try:
            # Check tables exist by querying them
            assert db.get_all_settings() == {}
            assert db.get_history() == []
        finally:
            db.close()

    def test_db_path_property(self, tmp_path: Path) -> None:
        """db_path property should return the database path."""
        db_path = tmp_path / "test.db"
        db = VoxDatabase(db_path)

        try:
            assert db.db_path == db_path
        finally:
            db.close()

    def test_context_manager(self, tmp_path: Path) -> None:
        """Database should work as context manager."""
        db_path = tmp_path / "test.db"

        with VoxDatabase(db_path) as db:
            db.set_setting("test", "value")
            assert db.get_setting("test") == "value"


class TestVoxDatabaseSettings:
    """Tests for settings operations."""

    def test_set_setting_creates_new(self, tmp_path: Path) -> None:
        """set_setting should insert new setting."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.set_setting("hotkey", "<ctrl>+<alt>+space")
            assert db.get_setting("hotkey") == "<ctrl>+<alt>+space"
        finally:
            db.close()

    def test_set_setting_updates_existing(self, tmp_path: Path) -> None:
        """set_setting should update existing setting."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.set_setting("hotkey", "<ctrl>+<alt>+space")
            db.set_setting("hotkey", "<ctrl>+<shift>+v")
            assert db.get_setting("hotkey") == "<ctrl>+<shift>+v"
        finally:
            db.close()

    def test_get_setting_returns_value(self, tmp_path: Path) -> None:
        """get_setting should return stored value."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.set_setting("restore_clipboard", "true")
            assert db.get_setting("restore_clipboard") == "true"
        finally:
            db.close()

    def test_get_setting_returns_default_when_missing(self, tmp_path: Path) -> None:
        """get_setting should return default for missing key."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            assert db.get_setting("nonexistent") is None
            assert db.get_setting("nonexistent", "default") == "default"
        finally:
            db.close()

    def test_get_all_settings(self, tmp_path: Path) -> None:
        """get_all_settings should return all settings as dict."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.set_setting("key1", "value1")
            db.set_setting("key2", "value2")

            settings = db.get_all_settings()
            assert settings == {"key1": "value1", "key2": "value2"}
        finally:
            db.close()


class TestVoxDatabaseHistory:
    """Tests for transcription history operations."""

    def test_add_transcription_returns_id(self, tmp_path: Path) -> None:
        """add_transcription should return inserted record ID."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            record_id = db.add_transcription("Hello world")
            assert record_id == 1

            record_id2 = db.add_transcription("Second transcription")
            assert record_id2 == 2
        finally:
            db.close()

    def test_add_transcription_stores_text(self, tmp_path: Path) -> None:
        """add_transcription should store text content."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            record_id = db.add_transcription("Hello world")
            record = db.get_transcription(record_id)

            assert record is not None
            assert record.text == "Hello world"
        finally:
            db.close()

    def test_add_transcription_stores_duration(self, tmp_path: Path) -> None:
        """add_transcription should store duration if provided."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            record_id = db.add_transcription("Hello world", duration_seconds=1.5)
            record = db.get_transcription(record_id)

            assert record is not None
            assert record.duration_seconds == 1.5
        finally:
            db.close()

    def test_add_transcription_computes_word_count(self, tmp_path: Path) -> None:
        """add_transcription should compute word count."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            record_id = db.add_transcription("Hello world how are you")
            record = db.get_transcription(record_id)

            assert record is not None
            assert record.word_count == 5
        finally:
            db.close()

    def test_get_history_returns_newest_first(self, tmp_path: Path) -> None:
        """get_history should return records ordered by created_at DESC."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            # Add records with different IDs - higher IDs are added later
            db.add_transcription("First")
            db.add_transcription("Second")
            db.add_transcription("Third")

            history = db.get_history()
            assert len(history) == 3
            # Newest (highest ID) should be first
            assert history[0].id == 3
            assert history[1].id == 2
            assert history[2].id == 1
        finally:
            db.close()

    def test_get_history_respects_limit(self, tmp_path: Path) -> None:
        """get_history should limit results."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            for i in range(5):
                db.add_transcription(f"Transcription {i}")

            history = db.get_history(limit=2)
            assert len(history) == 2
        finally:
            db.close()

    def test_get_history_respects_offset(self, tmp_path: Path) -> None:
        """get_history should skip records based on offset."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.add_transcription("First")  # ID 1
            db.add_transcription("Second")  # ID 2
            db.add_transcription("Third")  # ID 3

            # Offset 1 should skip the newest (ID 3)
            history = db.get_history(offset=1)
            assert len(history) == 2
            assert history[0].id == 2  # Second newest
            assert history[1].id == 1  # Oldest
        finally:
            db.close()

    def test_get_transcription_by_id(self, tmp_path: Path) -> None:
        """get_transcription should return specific record."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            record_id = db.add_transcription("Target text", duration_seconds=2.0)
            record = db.get_transcription(record_id)

            assert record is not None
            assert record.id == record_id
            assert record.text == "Target text"
            assert record.duration_seconds == 2.0
            assert isinstance(record.created_at, datetime)
        finally:
            db.close()

    def test_get_transcription_returns_none_for_missing(self, tmp_path: Path) -> None:
        """get_transcription should return None for invalid ID."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            assert db.get_transcription(999) is None
        finally:
            db.close()

    def test_delete_transcription_removes_record(self, tmp_path: Path) -> None:
        """delete_transcription should remove record."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            record_id = db.add_transcription("To be deleted")
            assert db.get_transcription(record_id) is not None

            result = db.delete_transcription(record_id)
            assert result is True
            assert db.get_transcription(record_id) is None
        finally:
            db.close()

    def test_delete_transcription_returns_false_for_missing(self, tmp_path: Path) -> None:
        """delete_transcription should return False for invalid ID."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            result = db.delete_transcription(999)
            assert result is False
        finally:
            db.close()

    def test_clear_history_removes_all(self, tmp_path: Path) -> None:
        """clear_history should remove all records."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.add_transcription("One")
            db.add_transcription("Two")
            db.add_transcription("Three")

            db.clear_history()
            assert db.get_history() == []
        finally:
            db.close()

    def test_clear_history_returns_count(self, tmp_path: Path) -> None:
        """clear_history should return number of deleted records."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.add_transcription("One")
            db.add_transcription("Two")
            db.add_transcription("Three")

            count = db.clear_history()
            assert count == 3
        finally:
            db.close()

    def test_count_history(self, tmp_path: Path) -> None:
        """count_history should return total record count."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            assert db.count_history() == 0

            db.add_transcription("One")
            db.add_transcription("Two")

            assert db.count_history() == 2
        finally:
            db.close()


class TestInitDefaultSettings:
    """Tests for init_default_settings helper."""

    def test_initializes_default_hotkey(self, tmp_path: Path) -> None:
        """Should initialize default hotkey setting."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            init_default_settings(db)
            assert db.get_setting("hotkey") == "<ctrl>+<alt>+space"
        finally:
            db.close()

    def test_initializes_default_restore_clipboard(self, tmp_path: Path) -> None:
        """Should initialize default restore_clipboard setting."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            init_default_settings(db)
            assert db.get_setting("restore_clipboard") == "true"
        finally:
            db.close()

    def test_does_not_overwrite_existing(self, tmp_path: Path) -> None:
        """Should not overwrite existing settings."""
        db = VoxDatabase(tmp_path / "test.db")

        try:
            db.set_setting("hotkey", "<ctrl>+<shift>+v")
            init_default_settings(db)
            assert db.get_setting("hotkey") == "<ctrl>+<shift>+v"
        finally:
            db.close()
