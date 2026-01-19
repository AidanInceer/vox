"""Audio playback and control implementation for Windows.

This module provides audio playback functionality including pause/resume,
volume control, and speed adjustment using pygame.mixer.
"""

import io
import logging
import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Suppress pygame welcome message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    # Suppress pkg_resources deprecation warning from pygame
    warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")
except Exception:
    pass

import pygame  # noqa: E402

logger = logging.getLogger(__name__)


@dataclass
class PlaybackState:
    """Tracks playback state and position.

    Attributes:
        is_playing: Whether audio is currently playing
        is_paused: Whether playback is paused
        current_position_ms: Current position in milliseconds
        playback_speed: Playback speed multiplier (0.5 - 2.0)
        current_chunk_index: Index of the current audio chunk
        chunk_buffer: List of buffered audio chunks
    """

    is_playing: bool = False
    is_paused: bool = False
    current_position_ms: int = 0
    playback_speed: float = 1.0
    current_chunk_index: int = 0
    chunk_buffer: list = field(default_factory=list)


class AudioPlayback:
    """Manages audio playback with pause/resume and control support using pygame.mixer."""

    def __init__(self):
        """Initialize pygame.mixer for audio playback."""
        self.state = PlaybackState()
        self._audio_file: Optional[Path] = None
        self._initialized = False
        self._init_mixer()

    def _init_mixer(self) -> None:
        """Initialize pygame mixer if not already initialized."""
        if not self._initialized:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
                self._initialized = True
                logger.info("pygame.mixer initialized successfully")
            except pygame.error as e:
                raise RuntimeError(f"Failed to initialize pygame.mixer: {e}") from e

    def play_audio(self, audio_bytes: bytes, format: str = "wav") -> None:
        """Play audio from bytes using pygame.mixer.

        This method blocks until playback completes.

        Args:
            audio_bytes: Audio data to play
            format: Audio format ('wav', 'mp3', etc.)

        Raises:
            ValueError: If audio_bytes is empty or invalid
            RuntimeError: If playback fails
        """
        if not audio_bytes:
            raise ValueError("Audio bytes cannot be empty")

        try:
            # Load audio from bytes using pygame
            audio_stream = io.BytesIO(audio_bytes)
            pygame.mixer.music.load(audio_stream)

            # Start playback
            pygame.mixer.music.play()
            self.state.is_playing = True
            self.state.is_paused = False

            logger.info("Started audio playback with pygame.mixer")

            # Block until playback completes
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Check 10 times per second

            self.state.is_playing = False
            logger.info("Audio playback completed")

        except pygame.error as e:
            self.state.is_playing = False
            raise RuntimeError(f"Audio playback failed: {e}") from e
        except Exception as e:
            self.state.is_playing = False
            raise RuntimeError(f"Unexpected error during playback: {e}") from e

    def pause(self) -> None:
        """Pause audio playback.

        Raises:
            RuntimeError: If not currently playing or already paused
        """
        if not self.state.is_playing:
            raise RuntimeError("Cannot pause: no audio is playing")
        if self.state.is_paused:
            raise RuntimeError("Cannot pause: already paused")

        try:
            pygame.mixer.music.pause()
            self.state.is_paused = True
            self.state.is_playing = False
            logger.info("Audio paused")
        except pygame.error as e:
            raise RuntimeError(f"Failed to pause audio: {e}") from e

    def resume(self) -> None:
        """Resume paused audio playback.

        Raises:
            RuntimeError: If not currently paused
        """
        if not self.state.is_paused:
            raise RuntimeError("Cannot resume: audio is not paused")

        try:
            pygame.mixer.music.unpause()
            self.state.is_paused = False
            self.state.is_playing = True
            logger.info("Audio resumed")
        except pygame.error as e:
            raise RuntimeError(f"Failed to resume audio: {e}") from e

    def stop(self) -> None:
        """Stop audio playback completely."""
        if self.state.is_playing or self.state.is_paused:
            try:
                pygame.mixer.music.stop()
                self.state.is_playing = False
                self.state.is_paused = False
                self.state.current_position_ms = 0
                logger.info("Audio stopped")
            except pygame.error as e:
                logger.error(f"Failed to stop audio: {e}")

    def seek(self, position_ms: int) -> None:
        """Seek to a specific position in audio.

        Args:
            position_ms: Position in milliseconds

        Raises:
            ValueError: If position is invalid
            RuntimeError: If not currently playing
        """
        if position_ms < 0:
            raise ValueError(f"Position must be >= 0, got {position_ms}")

        if not (self.state.is_playing or self.state.is_paused):
            raise RuntimeError("Cannot seek: no audio is playing")

        try:
            # pygame.mixer.music.set_pos() takes position in seconds (float)
            position_sec = position_ms / 1000.0
            pygame.mixer.music.set_pos(position_sec)
            self.state.current_position_ms = position_ms
            logger.debug(f"Seeked to {position_ms}ms")
        except pygame.error as e:
            raise RuntimeError(f"Failed to seek: {e}") from e

    def get_position(self) -> int:
        """Get current playback position in milliseconds.

        Returns:
            Position in milliseconds
        """
        if self.state.is_playing or self.state.is_paused:
            try:
                # pygame.mixer.music.get_pos() returns milliseconds since play() started
                position_ms = pygame.mixer.music.get_pos()
                if position_ms >= 0:
                    self.state.current_position_ms = position_ms
            except pygame.error:
                pass  # Keep last known position

        return self.state.current_position_ms

    def set_speed(self, speed: float) -> None:
        """Set playback speed.

        Note: pygame.mixer.music does not support runtime speed adjustment.
        Speed must be set during audio synthesis, not during playback.
        This method updates the state for tracking purposes only.

        Args:
            speed: Speed multiplier (0.5 to 2.0)

        Raises:
            ValueError: If speed is out of range
            NotImplementedError: Always raised as pygame.mixer doesn't support speed control
        """
        if not 0.5 <= speed <= 2.0:
            raise ValueError(f"Speed must be 0.5-2.0, got {speed}")

        # pygame.mixer.music doesn't support runtime speed control
        # Speed must be set during synthesis, not during playback
        raise NotImplementedError(
            "Speed adjustment during playback is not supported. "
            "Use the --speed flag when starting playback to synthesize audio at the desired speed."
        )

    def is_playing(self) -> bool:
        """Check if audio is currently playing.

        Returns:
            True if audio is playing (not paused)
        """
        return self.state.is_playing and not self.state.is_paused

    def is_paused(self) -> bool:
        """Check if audio playback is paused.

        Returns:
            True if audio is paused
        """
        return self.state.is_paused

    def cleanup(self) -> None:
        """Clean up resources and shut down pygame mixer."""
        try:
            self.stop()

            if self._initialized:
                pygame.mixer.quit()
                self._initialized = False
                logger.debug("pygame.mixer shut down")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


# Global playback instance
_playback_instance: Optional[AudioPlayback] = None


def get_playback() -> AudioPlayback:
    """Get the global audio playback instance.

    Returns:
        AudioPlayback instance
    """
    global _playback_instance
    if _playback_instance is None:
        _playback_instance = AudioPlayback()
    return _playback_instance


def play_audio(audio_bytes: bytes) -> None:
    """Play audio from bytes using the global playback instance.

    Args:
        audio_bytes: Audio data to play
    """
    playback = get_playback()
    playback.play_audio(audio_bytes)
