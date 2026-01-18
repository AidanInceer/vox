"""Session persistence and management.

This module provides the SessionManager class for saving, loading, listing,
and managing reading sessions.
"""

import json
import logging
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from src.session.models import ReadingSession

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session persistence - save, load, list, resume, and delete sessions.

    Attributes:
        storage_dir: Directory where session files are stored
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize SessionManager with storage directory.

        Args:
            storage_dir: Directory for session storage. If None, defaults to
                %APPDATA%/PageReader/sessions/

        Raises:
            OSError: If unable to create storage directory or index file
        """
        if storage_dir is None:
            storage_dir = Path(os.getenv("APPDATA")) / "PageReader" / "sessions"

        self.storage_dir = Path(storage_dir)

        # Create storage directory if it doesn't exist
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Session storage directory: {self.storage_dir}")
        except OSError as e:
            logger.error(f"Failed to create storage directory: {e}")
            raise

        # Create index file if it doesn't exist
        self.index_file = self.storage_dir / "sessions.json"
        if not self.index_file.exists():
            try:
                self._write_index([])
                logger.info("Created new session index")
            except OSError as e:
                logger.error(f"Failed to create index file: {e}")
                raise

    def _validate_session_name(self, session_name: str) -> None:
        """Validate session name format.

        Args:
            session_name: Session name to validate

        Raises:
            ValueError: If session_name is invalid
        """
        if not session_name:
            raise ValueError("session_name cannot be empty")

        if len(session_name) > 64:
            raise ValueError("session_name must be 1-64 characters")

        # Must be alphanumeric, hyphen, or underscore only
        if not re.match(r"^[a-zA-Z0-9_-]+$", session_name):
            raise ValueError(
                "Invalid characters in session_name. "
                "Use only letters, numbers, hyphens, and underscores."
            )

    def _slugify(self, session_name: str) -> str:
        """Convert session name to filename-safe slug.

        Args:
            session_name: Session name to convert

        Returns:
            Filename-safe version of session_name
        """
        # For now, session names are already restricted to safe characters
        # Just ensure lowercase for consistency
        return session_name.lower()

    def _write_session_file(self, session_name: str, data: dict) -> None:
        """Write session data to file atomically.

        Args:
            session_name: Session name (used for filename)
            data: Session data dictionary to write

        Raises:
            OSError: If unable to write file
        """
        slug = self._slugify(session_name)
        session_file = self.storage_dir / f"{slug}.json"

        # Write atomically using temp file + rename
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=self.storage_dir,
                delete=False,
                suffix=".tmp",
            ) as tmp:
                json.dump(data, tmp, indent=2)
                tmp_path = tmp.name

            # Atomic rename
            Path(tmp_path).replace(session_file)
            logger.debug(f"Wrote session file: {session_file}")

        except Exception as e:
            # Clean up temp file if it exists
            if "tmp_path" in locals():
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except:
                    pass
            raise OSError(f"Failed to write session file: {e}") from e

    def _read_index(self) -> list[dict]:
        """Read session index from disk.

        Returns:
            List of session metadata dictionaries

        Raises:
            OSError: If unable to read index file
            json.JSONDecodeError: If index file corrupted
        """
        try:
            with open(self.index_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted session index: {e}")
            raise
        except OSError as e:
            logger.error(f"Failed to read session index: {e}")
            raise

    def _write_index(self, index: list[dict]) -> None:
        """Write session index to disk atomically.

        Args:
            index: List of session metadata dictionaries

        Raises:
            OSError: If unable to write index file
        """
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=self.storage_dir,
                delete=False,
                suffix=".tmp",
            ) as tmp:
                json.dump(index, tmp, indent=2)
                tmp_path = tmp.name

            # Atomic rename
            Path(tmp_path).replace(self.index_file)
            logger.debug("Updated session index")

        except Exception as e:
            # Clean up temp file if it exists
            if "tmp_path" in locals():
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except:
                    pass
            raise OSError(f"Failed to write index file: {e}") from e

    def save_session(
        self,
        session_name: str,
        url: str,
        extracted_text: str,
        playback_position: int = 0,
        tts_settings: Optional[dict] = None,
    ) -> str:
        """Save a new reading session to disk.

        Args:
            session_name: User-provided session name (1-64 chars, alphanumeric+hyphen/underscore)
            url: Source URL of the content
            extracted_text: Full extracted text from the page
            playback_position: Current playback position in characters (default: 0)
            tts_settings: TTS settings (voice, speed) for consistent playback

        Returns:
            Generated session_id (UUID v4)

        Raises:
            ValueError: If session_name invalid or already exists
            ValueError: If url invalid format
            ValueError: If extracted_text is empty
            ValueError: If playback_position out of bounds
            OSError: If unable to write session file
        """
        # Validate session name
        self._validate_session_name(session_name)

        # Check for duplicate name
        if self.session_exists(session_name):
            raise ValueError(f"Session with name '{session_name}' already exists")

        # Validate URL
        if not url.startswith(("http://", "https://", "file://")):
            # Check if it's a file path
            if not Path(url).exists():
                raise ValueError("Invalid URL format")

        # Validate extracted text
        if not extracted_text:
            raise ValueError("extracted_text cannot be empty")

        # Validate playback position
        if playback_position < 0 or playback_position > len(extracted_text):
            raise ValueError("playback_position out of bounds")

        # Generate session ID and timestamps
        session_id = str(uuid4())
        now = datetime.now()

        # Create session data
        session_data = {
            "session_id": session_id,
            "session_name": session_name,
            "url": url,
            "title": session_name,  # Use session name as title for now
            "extracted_text": extracted_text,
            "playback_position": playback_position,
            "created_at": now.isoformat(),
            "last_accessed": now.isoformat(),
            "tts_settings": tts_settings or {},
            "extraction_settings": {},
        }

        # Write session file
        self._write_session_file(session_name, session_data)

        # Update index
        index = self._read_index()
        index.append({
            "session_name": session_name,
            "session_id": session_id,
            "url": url,
            "title": session_name,
            "created_at": now.isoformat(),
            "last_accessed": now.isoformat(),
            "playback_position": playback_position,
            "total_characters": len(extracted_text),
        })
        self._write_index(index)

        logger.info(f"Saved session '{session_name}' (ID: {session_id})")
        return session_id

    def load_session(self, session_name: str) -> ReadingSession:
        """Load an existing session from disk.

        Args:
            session_name: Name of the session to load

        Returns:
            Loaded ReadingSession object

        Raises:
            ValueError: If session_name not found
            OSError: If unable to read session file
            json.JSONDecodeError: If session file corrupted
            KeyError: If required fields missing from session file
        """
        # Check if session exists
        if not self.session_exists(session_name):
            raise ValueError(f"Session '{session_name}' not found")

        # Read session file
        slug = self._slugify(session_name)
        session_file = self.storage_dir / f"{slug}.json"

        try:
            with open(session_file, "r") as f:
                data = json.load(f)
        except OSError as e:
            logger.error(f"Failed to read session file: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted session file: {e}")
            raise

        # Update last_accessed timestamp
        now = datetime.now()
        data["last_accessed"] = now.isoformat()

        # Write back to file
        self._write_session_file(session_name, data)

        # Update index
        index = self._read_index()
        for entry in index:
            if entry["session_name"] == session_name:
                entry["last_accessed"] = now.isoformat()
                break
        self._write_index(index)

        # Create ReadingSession object
        session = ReadingSession(
            session_id=data["session_id"],
            session_name=data["session_name"],
            page_url=data["url"],
            title=data.get("title", session_name),
            playback_position=data.get("playback_position", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=now,
            extraction_settings=data.get("extraction_settings", {}),
            tts_settings=data.get("tts_settings", {}),
        )

        logger.info(f"Loaded session '{session_name}'")
        return session

    def list_sessions(self) -> list[dict]:
        """List all saved sessions with metadata.

        Returns:
            List of session metadata dicts, each containing:
                - session_name: User-facing session name
                - session_id: Internal UUID
                - url: Source URL
                - title: Page title
                - created_at: ISO 8601 timestamp
                - last_accessed: ISO 8601 timestamp
                - playback_position: Current character offset
                - total_characters: Total text length
                - progress_percent: Playback progress as percentage

        Raises:
            OSError: If unable to read index file
            json.JSONDecodeError: If index corrupted
        """
        index = self._read_index()

        # Calculate progress percentage for each session
        for entry in index:
            total = entry.get("total_characters", 1)
            position = entry.get("playback_position", 0)
            entry["progress_percent"] = (position / total) * 100 if total > 0 else 0.0

        logger.debug(f"Listed {len(index)} sessions")
        return index

    def resume_session(self, session_name: str) -> tuple[str, int]:
        """Resume playback from a saved session.

        Args:
            session_name: Name of the session to resume

        Returns:
            Tuple of (extracted_text, playback_position) for resuming playback

        Raises:
            Same as load_session()
        """
        session = self.load_session(session_name)

        # Read session file to get extracted text
        slug = self._slugify(session_name)
        session_file = self.storage_dir / f"{slug}.json"

        with open(session_file, "r") as f:
            data = json.load(f)

        extracted_text = data.get("extracted_text", "")

        logger.info(f"Resuming session '{session_name}' at position {session.playback_position}")
        return extracted_text, session.playback_position

    def delete_session(self, session_name: str) -> None:
        """Delete a saved session from disk.

        Args:
            session_name: Name of the session to delete

        Raises:
            ValueError: If session_name not found
            OSError: If unable to delete session file
        """
        # Check if session exists
        if not self.session_exists(session_name):
            raise ValueError(f"Session '{session_name}' not found")

        # Delete session file
        slug = self._slugify(session_name)
        session_file = self.storage_dir / f"{slug}.json"

        try:
            session_file.unlink()
            logger.info(f"Deleted session file: {session_file}")
        except OSError as e:
            logger.error(f"Failed to delete session file: {e}")
            raise

        # Update index
        index = self._read_index()
        index = [entry for entry in index if entry["session_name"] != session_name]
        self._write_index(index)

        logger.info(f"Deleted session '{session_name}'")

    def session_exists(self, session_name: str) -> bool:
        """Check if a session exists.

        Args:
            session_name: Name of the session to check

        Returns:
            True if session exists, False otherwise
        """
        try:
            index = self._read_index()
            return any(entry["session_name"] == session_name for entry in index)
        except Exception as e:
            logger.error(f"Failed to check session existence: {e}")
            return False

    def _read_session_data(self, session_name: str) -> dict:
        """Read raw session data from disk.

        Args:
            session_name: Name of the session to read

        Returns:
            Session data dictionary

        Raises:
            ValueError: If session not found
            OSError: If unable to read session file
            json.JSONDecodeError: If session file corrupted
        """
        if not self.session_exists(session_name):
            raise ValueError(f"Session '{session_name}' not found")

        slug = self._slugify(session_name)
        session_file = self.storage_dir / f"{slug}.json"

        try:
            with open(session_file, "r") as f:
                return json.load(f)
        except OSError as e:
            logger.error(f"Failed to read session file: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted session file: {e}")
            raise

    def update_session_position(self, session_name: str, playback_position: int) -> None:
        """Update the playback position for a session.

        Args:
            session_name: Name of the session to update
            playback_position: New playback position in characters

        Raises:
            ValueError: If session not found or position out of bounds
            OSError: If unable to update session file
        """
        # Read current session data
        data = self._read_session_data(session_name)

        # Validate position
        text_length = len(data.get("extracted_text", ""))
        if playback_position < 0 or playback_position > text_length:
            raise ValueError(f"Playback position {playback_position} out of bounds (0-{text_length})")

        # Update position and timestamp
        now = datetime.now()
        data["playback_position"] = playback_position
        data["last_accessed"] = now.isoformat()

        # Write updated data
        self._write_session_file(session_name, data)

        # Update index
        index = self._read_index()
        for entry in index:
            if entry["session_name"] == session_name:
                entry["playback_position"] = playback_position
                entry["last_accessed"] = now.isoformat()
                break
        self._write_index(index)

        logger.info(f"Updated session '{session_name}' position to {playback_position}")
