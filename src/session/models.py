"""Data models for session persistence and management."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReadingSession:
    """Represents a reading session for a page.

    Attributes:
        session_id: Unique identifier for the session
        page_url: URL or file path of the page being read
        title: Title of the page (from HTML <title> or filename)
        playback_position: Current position in text (character offset)
        created_at: Timestamp when session was created
        last_accessed: Timestamp of last access to this session
        extraction_settings: Settings used for text extraction (dict)
        tts_settings: Settings used for TTS synthesis (dict)
    """

    session_id: str
    page_url: str
    title: str
    playback_position: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    extraction_settings: dict = field(default_factory=dict)
    tts_settings: dict = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation of session."""
        return f"Session: {self.title} ({self.page_url})"

    def __repr__(self) -> str:
        """Detailed representation of session."""
        return (
            f"ReadingSession(id={self.session_id!r}, url={self.page_url!r}, "
            f"title={self.title!r}, position={self.playback_position})"
        )

    def is_valid(self) -> bool:
        """Check if session is valid.

        Returns:
            True if all required fields are present and non-empty
        """
        return all([self.session_id, self.page_url, self.title])

    def to_dict(self) -> dict:
        """Convert session to dictionary for serialization.

        Returns:
            Dictionary representation of the session
        """
        return {
            "session_id": self.session_id,
            "page_url": self.page_url,
            "title": self.title,
            "playback_position": self.playback_position,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "extraction_settings": self.extraction_settings,
            "tts_settings": self.tts_settings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReadingSession":
        """Create session from dictionary (deserialization).

        Args:
            data: Dictionary representation of a session

        Returns:
            ReadingSession instance
        """
        return cls(
            session_id=data["session_id"],
            page_url=data["page_url"],
            title=data["title"],
            playback_position=data.get("playback_position", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_accessed=datetime.fromisoformat(data.get("last_accessed", datetime.now().isoformat())),
            extraction_settings=data.get("extraction_settings", {}),
            tts_settings=data.get("tts_settings", {}),
        )
