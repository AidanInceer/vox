"""SQLite database wrapper for settings and transcription history.

This module provides persistent storage for user settings and transcription
history using SQLite. The database is stored in %APPDATA%/vox/vox.db by default.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.persistence.models import TranscriptionRecord, UserSettings
from src.utils.errors import DatabaseError

logger = logging.getLogger(__name__)

# SQL Schema
_SCHEMA_SQL = """
-- Settings table (key-value store)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transcription history table
CREATE TABLE IF NOT EXISTS transcription_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL,
    word_count INTEGER
);

-- Index for efficient history queries (newest first)
CREATE INDEX IF NOT EXISTS idx_history_created
    ON transcription_history(created_at DESC);
"""


def _get_default_db_path() -> Path:
    """Get default database path in APPDATA.

    Returns:
        Path to vox.db in %APPDATA%/vox/
    """
    # Import here to avoid circular import
    from src.config import get_vox_database_path

    return get_vox_database_path()


class VoxDatabase:
    """SQLite database for settings and transcription history.

    Provides a simple key-value store for user settings and a structured
    table for transcription history. The database file is stored in the
    user's application data directory (%APPDATA%/vox/vox.db on Windows).

    Thread Safety:
        Uses `check_same_thread=False` for safe multi-threaded access.
        Individual operations are atomic but not grouped transactions.

    Attributes:
        db_path: Path to the SQLite database file.

    Example:
        >>> db = VoxDatabase()
        >>> db.set_setting("hotkey", "<ctrl>+<alt>+space")
        >>> db.get_setting("hotkey")
        '<ctrl>+<alt>+space'
        >>> db.add_transcription("Hello world", duration_seconds=1.5)
        1
        >>> db.close()

        # Using context manager:
        >>> with VoxDatabase() as db:
        ...     db.set_setting("key", "value")
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize database connection.

        Args:
            db_path: Path to database file, or None for default
                     Default: %APPDATA%/vox/vox.db

        Creates database and schema if not exists.

        Raises:
            DatabaseError: If database initialization fails
        """
        self._db_path = db_path or _get_default_db_path()
        self._conn: Optional[sqlite3.Connection] = None

        try:
            # Ensure parent directory exists
            self._db_path.parent.mkdir(parents=True, exist_ok=True)

            # Connect with thread safety disabled for multi-thread access
            self._conn = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            self._conn.row_factory = sqlite3.Row

            # Initialize schema
            self._init_schema()

            logger.info(f"Database initialized at {self._db_path}")

        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to initialize database: {e}",
                error_code="DATABASE_INIT_FAILED",
                context={"path": str(self._db_path)},
            ) from e

    def _init_schema(self) -> None:
        """Initialize database schema."""
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        self._conn.executescript(_SCHEMA_SQL)
        self._conn.commit()

    @property
    def db_path(self) -> Path:
        """Get the database file path.

        Returns:
            Path object pointing to the SQLite database file.
        """
        return self._db_path

    # =========================================================================
    # Settings Operations
    # =========================================================================

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a setting value by key.

        Args:
            key: Setting key to retrieve
            default: Default value if key not found

        Returns:
            Setting value, or default if not found
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        cursor = self._conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        )
        row = cursor.fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        """Set a setting value (insert or update).

        Args:
            key: Setting key
            value: Setting value
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        self._conn.execute(
            """INSERT OR REPLACE INTO settings (key, value, updated_at)
               VALUES (?, ?, CURRENT_TIMESTAMP)""",
            (key, value),
        )
        self._conn.commit()
        logger.debug(f"Setting '{key}' updated")

    def get_all_settings(self) -> dict[str, str]:
        """Get all settings as a dictionary.

        Returns:
            Dictionary of all settings {key: value}
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        cursor = self._conn.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cursor.fetchall()}

    # =========================================================================
    # History Operations
    # =========================================================================

    def add_transcription(
        self,
        text: str,
        duration_seconds: Optional[float] = None,
    ) -> int:
        """Add a transcription to history.

        Args:
            text: Transcribed text
            duration_seconds: Recording duration

        Returns:
            ID of inserted record

        Raises:
            DatabaseError: If insertion fails
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        word_count = len(text.split()) if text else 0

        cursor = self._conn.execute(
            """INSERT INTO transcription_history (text, duration_seconds, word_count)
               VALUES (?, ?, ?)""",
            (text, duration_seconds, word_count),
        )
        self._conn.commit()

        record_id = cursor.lastrowid
        logger.debug(f"Transcription added with ID {record_id}")
        return record_id if record_id is not None else 0

    def get_history(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TranscriptionRecord]:
        """Get transcription history (newest first).

        Args:
            limit: Maximum records to return
            offset: Records to skip (for pagination)

        Returns:
            List of TranscriptionRecord objects
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        cursor = self._conn.execute(
            """SELECT id, text, created_at, duration_seconds, word_count
               FROM transcription_history
               ORDER BY id DESC
               LIMIT ? OFFSET ?""",
            (limit, offset),
        )

        records = []
        for row in cursor.fetchall():
            # Parse created_at timestamp
            created_at = row["created_at"]
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)

            records.append(
                TranscriptionRecord(
                    id=row["id"],
                    text=row["text"],
                    created_at=created_at,
                    duration_seconds=row["duration_seconds"],
                    word_count=row["word_count"],
                )
            )

        return records

    def get_transcription(self, record_id: int) -> Optional[TranscriptionRecord]:
        """Get a specific transcription by ID.

        Args:
            record_id: ID of the transcription to retrieve

        Returns:
            TranscriptionRecord if found, None otherwise
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        cursor = self._conn.execute(
            """SELECT id, text, created_at, duration_seconds, word_count
               FROM transcription_history
               WHERE id = ?""",
            (record_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        created_at = row["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return TranscriptionRecord(
            id=row["id"],
            text=row["text"],
            created_at=created_at,
            duration_seconds=row["duration_seconds"],
            word_count=row["word_count"],
        )

    def delete_transcription(self, record_id: int) -> bool:
        """Delete a transcription.

        Args:
            record_id: ID of the transcription to delete

        Returns:
            True if deleted, False if not found
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        cursor = self._conn.execute(
            "DELETE FROM transcription_history WHERE id = ?",
            (record_id,),
        )
        self._conn.commit()

        deleted = cursor.rowcount > 0
        if deleted:
            logger.debug(f"Transcription {record_id} deleted")
        return deleted

    def clear_history(self) -> int:
        """Delete all transcription history.

        Returns:
            Number of records deleted
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        cursor = self._conn.execute("DELETE FROM transcription_history")
        self._conn.commit()

        count = cursor.rowcount
        logger.info(f"Cleared {count} transcription records")
        return count

    def count_history(self) -> int:
        """Get total number of transcription records.

        Returns:
            Count of transcription records
        """
        if self._conn is None:
            raise DatabaseError("Database connection not established")

        cursor = self._conn.execute("SELECT COUNT(*) as count FROM transcription_history")
        row = cursor.fetchone()
        return row["count"] if row else 0

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def close(self) -> None:
        """Close the database connection.

        Releases the SQLite connection. Safe to call multiple times.
        After closing, all database operations will raise DatabaseError.
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.debug("Database connection closed")

    def __enter__(self) -> "VoxDatabase":
        """Context manager entry.

        Returns:
            The VoxDatabase instance for use in a with statement.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit.

        Automatically closes the database connection when exiting the context.

        Args:
            exc_type: Exception type if raised, None otherwise.
            exc_val: Exception value if raised, None otherwise.
            exc_tb: Exception traceback if raised, None otherwise.
        """
        self.close()


def init_default_settings(db: VoxDatabase) -> None:
    """Initialize default settings if not already present in the database.

    Populates the settings table with default values from UserSettings
    for any keys that don't already exist. Existing settings are preserved.

    Args:
        db: VoxDatabase instance to initialize settings in.
    """
    defaults = UserSettings()
    for key, value in defaults.to_dict().items():
        if db.get_setting(key) is None:
            db.set_setting(key, value)
            logger.debug(f"Initialized default setting: {key}={value}")
