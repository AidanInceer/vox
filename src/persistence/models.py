"""Data models for the hotkey voice input feature.

This module defines the core data structures used across the voice input
feature, providing type-safe containers for application state, transcription
records, and user preferences.

Classes:
    AppState: Enumeration of application states for the state machine.
    TranscriptionRecord: Dataclass for a completed voice transcription.
    UserSettings: Dataclass containing user preference settings.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional


class AppState(Enum):
    """Application state enumeration for the voice input state machine.

    Defines all possible states for the voice input feature. The controller
    uses these states to track the current operation and determine valid
    transitions.

    State Transitions:
        IDLE → RECORDING (hotkey pressed)
        RECORDING → TRANSCRIBING (hotkey pressed again to stop)
        RECORDING → IDLE (cancelled via Escape)
        TRANSCRIBING → PASTING (transcription successful)
        TRANSCRIBING → ERROR (transcription failed)
        PASTING → IDLE (paste complete)
        ERROR → IDLE (error acknowledged)

    Attributes:
        IDLE: Waiting for user input, no active operation.
        RECORDING: Actively recording audio from microphone.
        TRANSCRIBING: Processing recorded audio through STT engine.
        PASTING: Inserting transcribed text at cursor position.
        ERROR: An error occurred during processing.
    """

    IDLE = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    PASTING = auto()
    ERROR = auto()


@dataclass
class TranscriptionRecord:
    """Represents a completed voice transcription.

    Attributes:
        id: Unique identifier (None for unsaved records)
        text: Transcribed text content
        created_at: When transcription occurred
        duration_seconds: Audio recording duration (optional)
        word_count: Number of words in transcription (computed if not provided)
    """

    id: Optional[int]
    text: str
    created_at: datetime
    duration_seconds: Optional[float] = None
    word_count: Optional[int] = None

    def __post_init__(self) -> None:
        """Compute word count if not provided."""
        if self.word_count is None and self.text:
            self.word_count = len(self.text.split())


@dataclass
class UserSettings:
    """User preferences container for the voice input feature.

    Attributes:
        hotkey: Activation hotkey in pynput format (e.g., '<ctrl>+<alt>+space')
        restore_clipboard: Whether to restore clipboard after paste operation
    """

    hotkey: str = "<ctrl>+<alt>+space"
    restore_clipboard: bool = True

    def to_dict(self) -> dict[str, str]:
        """Convert settings to dictionary for database storage.

        Serializes all settings to string values suitable for storage
        in a key-value database table.

        Returns:
            Dictionary mapping setting names to their string representations.
            Boolean values are converted to lowercase 'true' or 'false'.
        """
        return {
            "hotkey": self.hotkey,
            "restore_clipboard": str(self.restore_clipboard).lower(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "UserSettings":
        """Create UserSettings from dictionary.

        Args:
            data: Dictionary with setting keys and string values

        Returns:
            UserSettings instance with parsed values
        """
        restore_clipboard_str = data.get("restore_clipboard", "true")
        # Handle both string "true"/"false" and actual bool values
        if isinstance(restore_clipboard_str, bool):
            restore_clipboard = restore_clipboard_str
        else:
            restore_clipboard = restore_clipboard_str.lower() == "true"

        return cls(
            hotkey=data.get("hotkey", "<ctrl>+<alt>+space"),
            restore_clipboard=restore_clipboard,
        )
