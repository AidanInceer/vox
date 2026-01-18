"""Unit tests for SessionManager class."""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest

from src.session.manager import SessionManager
from src.session.models import ReadingSession


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for session storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def session_manager(temp_storage_dir):
    """Create a SessionManager with temporary storage."""
    return SessionManager(storage_dir=temp_storage_dir)


class TestSessionManagerInit:
    """Tests for SessionManager.__init__()"""

    def test_init_creates_storage_dir(self, temp_storage_dir):
        """Test that __init__ creates storage directory if it doesn't exist."""
        storage_path = temp_storage_dir / "sessions"
        assert not storage_path.exists()
        
        manager = SessionManager(storage_dir=storage_path)
        
        assert storage_path.exists()
        assert storage_path.is_dir()

    def test_init_creates_index_file(self, temp_storage_dir):
        """Test that __init__ creates sessions.json index file."""
        manager = SessionManager(storage_dir=temp_storage_dir)
        
        index_file = temp_storage_dir / "sessions.json"
        assert index_file.exists()
        
        # Verify it's valid JSON with empty list
        with open(index_file, "r") as f:
            data = json.load(f)
        assert data == []

    def test_init_uses_default_dir_when_none(self):
        """Test that __init__ uses default APPDATA dir when storage_dir is None."""
        manager = SessionManager(storage_dir=None)
        
        # Should use %APPDATA%/vox/sessions
        expected_path = Path(os.getenv("APPDATA")) / "vox" / "sessions"
        assert manager.storage_dir == expected_path


class TestSessionManagerSaveSession:
    """Tests for SessionManager.save_session()"""

    def test_save_session_with_valid_inputs(self, session_manager, temp_storage_dir):
        """Test saving a session with valid inputs."""
        session_id = session_manager.save_session(
            session_name="test-article",
            url="https://example.com/article",
            extracted_text="This is a test article content.",
            playback_position=0,
            tts_settings={"voice": "en_US", "speed": 1.0}
        )
        
        # Verify session_id is valid UUID
        assert UUID(session_id)
        
        # Verify session file exists
        session_file = temp_storage_dir / "test-article.json"
        assert session_file.exists()
        
        # Verify file contents
        with open(session_file, "r") as f:
            data = json.load(f)
        
        assert data["session_id"] == session_id
        assert data["session_name"] == "test-article"
        assert data["url"] == "https://example.com/article"
        assert data["extracted_text"] == "This is a test article content."
        assert data["playback_position"] == 0
        assert data["tts_settings"] == {"voice": "en_US", "speed": 1.0}
        assert "created_at" in data
        assert "last_accessed" in data

    def test_save_session_updates_index(self, session_manager, temp_storage_dir):
        """Test that save_session updates the sessions.json index."""
        session_manager.save_session(
            session_name="test-article",
            url="https://example.com/article",
            extracted_text="Test content."
        )
        
        # Read index
        index_file = temp_storage_dir / "sessions.json"
        with open(index_file, "r") as f:
            index = json.load(f)
        
        assert len(index) == 1
        assert index[0]["session_name"] == "test-article"
        assert index[0]["url"] == "https://example.com/article"

    def test_save_session_with_invalid_name_empty(self, session_manager):
        """Test that save_session raises ValueError for empty session_name."""
        with pytest.raises(ValueError, match="session_name cannot be empty"):
            session_manager.save_session(
                session_name="",
                url="https://example.com",
                extracted_text="Test"
            )

    def test_save_session_with_invalid_name_too_long(self, session_manager):
        """Test that save_session raises ValueError for session_name >64 chars."""
        with pytest.raises(ValueError, match="session_name must be 1-64 characters"):
            session_manager.save_session(
                session_name="a" * 65,
                url="https://example.com",
                extracted_text="Test"
            )

    def test_save_session_with_invalid_name_bad_chars(self, session_manager):
        """Test that save_session raises ValueError for invalid characters."""
        with pytest.raises(ValueError, match="Invalid characters in session_name"):
            session_manager.save_session(
                session_name="test article!",
                url="https://example.com",
                extracted_text="Test"
            )

    def test_save_session_with_duplicate_name(self, session_manager):
        """Test that save_session raises ValueError for duplicate session_name."""
        # Save first session
        session_manager.save_session(
            session_name="test-article",
            url="https://example.com",
            extracted_text="Test"
        )
        
        # Try to save with same name
        with pytest.raises(ValueError, match="Session with name 'test-article' already exists"):
            session_manager.save_session(
                session_name="test-article",
                url="https://example.com/other",
                extracted_text="Other"
            )

    def test_save_session_with_invalid_url(self, session_manager):
        """Test that save_session raises ValueError for invalid URL."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            session_manager.save_session(
                session_name="test",
                url="not-a-url",
                extracted_text="Test"
            )

    def test_save_session_with_empty_text(self, session_manager):
        """Test that save_session raises ValueError for empty extracted_text."""
        with pytest.raises(ValueError, match="extracted_text cannot be empty"):
            session_manager.save_session(
                session_name="test",
                url="https://example.com",
                extracted_text=""
            )

    def test_save_session_with_invalid_position(self, session_manager):
        """Test that save_session raises ValueError for out-of-bounds position."""
        with pytest.raises(ValueError, match="playback_position out of bounds"):
            session_manager.save_session(
                session_name="test",
                url="https://example.com",
                extracted_text="Short text",
                playback_position=999
            )


class TestSessionManagerLoadSession:
    """Tests for SessionManager.load_session()"""

    def test_load_session_existing(self, session_manager):
        """Test loading an existing session."""
        # Save a session first
        session_id = session_manager.save_session(
            session_name="test-article",
            url="https://example.com",
            extracted_text="Test content",
            playback_position=5
        )
        
        # Load it
        session = session_manager.load_session("test-article")
        
        assert session.session_id == session_id
        assert session.session_name == "test-article"
        assert session.page_url == "https://example.com"
        assert session.playback_position == 5

    def test_load_session_updates_last_accessed(self, session_manager, temp_storage_dir):
        """Test that load_session updates last_accessed timestamp."""
        session_manager.save_session(
            session_name="test",
            url="https://example.com",
            extracted_text="Test"
        )
        
        # Read original timestamp
        session_file = temp_storage_dir / "test.json"
        with open(session_file, "r") as f:
            data = json.load(f)
        original_accessed = data["last_accessed"]
        
        # Wait a bit and load
        import time
        time.sleep(0.1)
        
        session = session_manager.load_session("test")
        
        # Verify timestamp updated
        with open(session_file, "r") as f:
            data = json.load(f)
        new_accessed = data["last_accessed"]
        
        assert new_accessed > original_accessed

    def test_load_session_non_existent(self, session_manager):
        """Test that load_session raises ValueError for non-existent session."""
        with pytest.raises(ValueError, match="Session 'nonexistent' not found"):
            session_manager.load_session("nonexistent")


class TestSessionManagerListSessions:
    """Tests for SessionManager.list_sessions()"""

    def test_list_sessions_empty(self, session_manager):
        """Test listing sessions when none exist."""
        sessions = session_manager.list_sessions()
        assert sessions == []

    def test_list_sessions_multiple(self, session_manager):
        """Test listing multiple sessions."""
        # Save multiple sessions
        session_manager.save_session("article-1", "https://example.com/1", "Content 1")
        session_manager.save_session("article-2", "https://example.com/2", "Content 2" * 50)
        session_manager.save_session("article-3", "https://example.com/3", "Content 3")
        
        sessions = session_manager.list_sessions()
        
        assert len(sessions) == 3
        
        # Verify each session has required fields
        for session in sessions:
            assert "session_name" in session
            assert "session_id" in session
            assert "url" in session
            assert "created_at" in session
            assert "last_accessed" in session
            assert "playback_position" in session
            assert "total_characters" in session
            assert "progress_percent" in session
        
        # Verify names
        names = [s["session_name"] for s in sessions]
        assert "article-1" in names
        assert "article-2" in names
        assert "article-3" in names

    def test_list_sessions_progress_calculation(self, session_manager):
        """Test that progress_percent is calculated correctly."""
        session_manager.save_session(
            session_name="test",
            url="https://example.com",
            extracted_text="A" * 100,
            playback_position=25
        )
        
        sessions = session_manager.list_sessions()
        
        assert sessions[0]["progress_percent"] == 25.0
        assert sessions[0]["total_characters"] == 100


class TestSessionManagerDeleteSession:
    """Tests for SessionManager.delete_session()"""

    def test_delete_session_existing(self, session_manager, temp_storage_dir):
        """Test deleting an existing session."""
        session_manager.save_session("test", "https://example.com", "Test")
        
        # Verify it exists
        session_file = temp_storage_dir / "test.json"
        assert session_file.exists()
        
        # Delete it
        session_manager.delete_session("test")
        
        # Verify file removed
        assert not session_file.exists()
        
        # Verify not in index
        sessions = session_manager.list_sessions()
        assert len(sessions) == 0

    def test_delete_session_non_existent(self, session_manager):
        """Test that delete_session raises ValueError for non-existent session."""
        with pytest.raises(ValueError, match="Session 'nonexistent' not found"):
            session_manager.delete_session("nonexistent")


class TestSessionManagerSessionExists:
    """Tests for SessionManager.session_exists()"""

    def test_session_exists_true(self, session_manager):
        """Test session_exists returns True for existing session."""
        session_manager.save_session("test", "https://example.com", "Test")
        
        assert session_manager.session_exists("test") is True

    def test_session_exists_false(self, session_manager):
        """Test session_exists returns False for non-existent session."""
        assert session_manager.session_exists("nonexistent") is False
