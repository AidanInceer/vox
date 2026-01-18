"""Text chunking and streaming synthesis for faster TTS feedback.

This module provides chunking functionality to split text into
manageable pieces, synthesize audio incrementally, and enable
streaming playback.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SynthesisStatus(Enum):
    """Status of audio chunk synthesis."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AudioChunk:
    """Represents a chunk of text and its synthesized audio.

    Attributes:
        chunk_index: Sequential index of this chunk (0-based)
        text_content: The text content for this chunk
        audio_data: Synthesized audio bytes (None if not yet synthesized)
        duration_ms: Duration of the audio in milliseconds
        synthesis_status: Current status of synthesis for this chunk
    """

    chunk_index: int
    text_content: str
    audio_data: Optional[bytes] = None
    duration_ms: int = 0
    synthesis_status: SynthesisStatus = SynthesisStatus.PENDING
