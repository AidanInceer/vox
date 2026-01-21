"""Integration tests for full session management workflow."""

import tempfile
from pathlib import Path

import pytest

from src.session.manager import SessionManager


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for session storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def session_manager(temp_storage_dir):
    """Create a SessionManager with temporary storage."""
    return SessionManager(storage_dir=temp_storage_dir)


class TestSessionWorkflow:
    """Integration tests for full session management workflow."""

    def test_full_session_lifecycle(self, session_manager):
        """Test complete workflow: save → list → resume → delete."""
        # Step 1: Save a new session
        session_id = session_manager.save_session(
            session_name="test-article",
            url="https://example.com/article",
            extracted_text="This is a long article about testing. " * 100,
            playback_position=0,
            tts_settings={"voice": "en_US", "speed": 1.0},
        )

        assert session_id is not None

        # Step 2: List sessions - verify it appears
        sessions = session_manager.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["session_name"] == "test-article"
        assert sessions[0]["session_id"] == session_id
        assert sessions[0]["url"] == "https://example.com/article"
        assert sessions[0]["progress_percent"] == 0.0

        # Step 3: Load the session
        loaded_session = session_manager.load_session("test-article")
        assert loaded_session.session_id == session_id
        assert loaded_session.session_name == "test-article"
        assert loaded_session.playback_position == 0

        # Step 4: Update position and save again (simulating resume)
        loaded_session.update_position(500)
        # In real usage, the manager would save this, but we'll test resume directly

        # Step 5: Resume session (get text and position)
        text, position = session_manager.resume_session("test-article")
        assert position == 0  # Original position since we didn't re-save
        assert "testing" in text

        # Step 6: Delete the session
        session_manager.delete_session("test-article")

        # Step 7: Verify it's gone
        sessions = session_manager.list_sessions()
        assert len(sessions) == 0

        # Verify can't load deleted session
        with pytest.raises(ValueError):
            session_manager.load_session("test-article")

    def test_multiple_sessions_workflow(self, session_manager):
        """Test managing multiple sessions concurrently."""
        # Create multiple sessions
        sessions_data = [
            ("article-1", "https://example.com/1", "Content for article one. " * 50, 0),
            ("article-2", "https://example.com/2", "Content for article two. " * 100, 50),
            ("article-3", "https://example.com/3", "Content for article three. " * 75, 100),
        ]

        session_ids = []
        for name, url, text, pos in sessions_data:
            sid = session_manager.save_session(name, url, text, pos)
            session_ids.append(sid)

        # List all sessions
        sessions = session_manager.list_sessions()
        assert len(sessions) == 3

        # Verify all session names present
        names = {s["session_name"] for s in sessions}
        assert names == {"article-1", "article-2", "article-3"}

        # Resume each session and verify content
        for name, url, text, pos in sessions_data:
            loaded_text, loaded_pos = session_manager.resume_session(name)
            assert loaded_pos == pos
            assert loaded_text == text

        # Delete middle session
        session_manager.delete_session("article-2")

        # Verify only 2 remain
        sessions = session_manager.list_sessions()
        assert len(sessions) == 2
        names = {s["session_name"] for s in sessions}
        assert names == {"article-1", "article-3"}

    def test_session_name_uniqueness_enforcement(self, session_manager):
        """Test that duplicate session names are prevented."""
        # Save first session
        session_manager.save_session(
            session_name="unique-name", url="https://example.com/1", extracted_text="First content"
        )

        # Try to save another with same name
        with pytest.raises(ValueError, match="already exists"):
            session_manager.save_session(
                session_name="unique-name", url="https://example.com/2", extracted_text="Second content"
            )

        # Verify only one session exists
        sessions = session_manager.list_sessions()
        assert len(sessions) == 1

    def test_session_persistence_across_manager_instances(self, temp_storage_dir):
        """Test that sessions persist across SessionManager instances."""
        # Create first manager and save session
        manager1 = SessionManager(storage_dir=temp_storage_dir)
        session_id = manager1.save_session(
            session_name="persistent-test", url="https://example.com", extracted_text="Test persistence"
        )

        # Create new manager instance with same storage dir
        manager2 = SessionManager(storage_dir=temp_storage_dir)

        # Verify session is accessible
        sessions = manager2.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["session_name"] == "persistent-test"

        # Load and verify data intact
        loaded = manager2.load_session("persistent-test")
        assert loaded.session_id == session_id
        assert loaded.page_url == "https://example.com"

    def test_resume_updates_last_accessed(self, session_manager):
        """Test that resuming a session updates its last_accessed timestamp."""
        # Save session
        session_manager.save_session(session_name="test", url="https://example.com", extracted_text="Test")

        # Get initial listing
        sessions1 = session_manager.list_sessions()
        first_accessed = sessions1[0]["last_accessed"]

        # Wait and resume
        import time

        time.sleep(0.1)
        session_manager.resume_session("test")

        # Check updated timestamp
        sessions2 = session_manager.list_sessions()
        second_accessed = sessions2[0]["last_accessed"]

        assert second_accessed > first_accessed
