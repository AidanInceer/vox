"""Playback controller with interactive keyboard controls.

This module provides keyboard-driven playback controls including pause/resume,
seeking, speed adjustment, and graceful quit.
"""

import logging
import msvcrt
import queue
import threading
import time
from typing import List, Optional

from src.tts.playback import AudioPlayback, PlaybackState

logger = logging.getLogger(__name__)


class PlaybackController:
    """Manages interactive playback with keyboard controls.

    Keyboard Controls:
        SPACE: Pause/resume playback
        →: Seek forward 5 seconds
        ←: Seek backward 5 seconds
        ↑: Increase speed by 0.25x
        ↓: Decrease speed by 0.25x
        Q: Quit playback

    Attributes:
        audio_playback: AudioPlayback instance for controlling audio
        state: Current playback state
        command_queue: Queue for keyboard commands
        shutdown_event: Event to signal shutdown
    """

    DEBOUNCE_MS = 100  # Debounce window in milliseconds
    SEEK_DELTA_SEC = 5  # Seek amount in seconds
    SPEED_DELTA = 0.25  # Speed adjustment amount

    def __init__(self, audio_playback: AudioPlayback):
        """Initialize playback controller.

        Args:
            audio_playback: AudioPlayback instance to control
        """
        self.audio_playback = audio_playback
        # Use the audio_playback state directly, not a copy
        self.state = self.audio_playback.state
        self.command_queue: queue.Queue = queue.Queue()
        self.shutdown_event = threading.Event()
        self._keyboard_thread: Optional[threading.Thread] = None
        self._last_key_time: float = 0
        self._lock = threading.Lock()

    def start(self, audio_bytes: bytes, chunks: List[str]) -> None:
        """Start playback with keyboard control thread.

        Args:
            audio_bytes: Audio data to play
            chunks: List of text chunks for reference

        Raises:
            RuntimeError: If playback fails to start
        """
        try:
            # Store chunks for reference
            self.state.chunk_buffer = chunks

            # Start keyboard input thread
            self._keyboard_thread = threading.Thread(
                target=self._keyboard_input_thread, daemon=True
            )
            self._keyboard_thread.start()

            # Start audio playback
            self.audio_playback.play_audio(audio_bytes)

            # Process commands until shutdown
            self._process_commands()

        except Exception as e:
            logger.error(f"Failed to start playback: {e}")
            self.shutdown_event.set()
            raise RuntimeError(f"Playback failed: {e}") from e

    def pause(self) -> None:
        """Pause playback.

        Raises:
            RuntimeError: If not currently playing
        """
        with self._lock:
            if not self.state.is_playing:
                raise RuntimeError("Cannot pause: not playing")

            self.audio_playback.pause()
            logger.info("Playback paused")

    def resume(self) -> None:
        """Resume paused playback.

        Raises:
            RuntimeError: If not currently paused
        """
        with self._lock:
            if not self.state.is_paused:
                raise RuntimeError("Cannot resume: not paused")

            self.audio_playback.resume()
            logger.info("Playback resumed")

    def quit(self) -> None:
        """Gracefully quit playback and clean up."""
        with self._lock:
            logger.info("Quitting playback...")
            self.shutdown_event.set()

            # Stop audio
            if self.state.is_playing or self.state.is_paused:
                self.audio_playback.stop()

            logger.info("Playback quit")

    def seek(self, delta_seconds: int) -> None:
        """Seek forward or backward by delta seconds.

        Args:
            delta_seconds: Number of seconds to seek (positive=forward, negative=backward)

        Raises:
            RuntimeError: If not currently playing
        """
        with self._lock:
            if not (self.state.is_playing or self.state.is_paused):
                raise RuntimeError("Cannot seek: not playing")

            # Calculate new position from current state position
            current_pos = self.state.current_position_ms
            new_pos = max(0, current_pos + (delta_seconds * 1000))

            # Seek to new position
            self.audio_playback.seek(new_pos)
            logger.info(f"Seeked {delta_seconds}s to {new_pos}ms")

    def adjust_speed(self, delta: float) -> None:
        """Adjust playback speed.

        Args:
            delta: Speed adjustment amount (positive=faster, negative=slower)

        Raises:
            RuntimeError: If not currently playing
        """
        with self._lock:
            if not (self.state.is_playing or self.state.is_paused):
                raise RuntimeError("Cannot adjust speed: not playing")

            # Calculate new speed with clamping
            new_speed = self.state.playback_speed + delta
            new_speed = max(0.5, min(2.0, new_speed))

            self.audio_playback.set_speed(new_speed)
            logger.info(f"Speed adjusted to {new_speed}x")

    def _keyboard_input_thread(self) -> None:
        """Background thread for capturing keyboard input."""
        logger.debug("Keyboard input thread started")

        while not self.shutdown_event.is_set():
            try:
                # Check if key is available (non-blocking)
                if msvcrt.kbhit():
                    # Read the key
                    key = msvcrt.getch()

                    # Apply debouncing
                    current_time = time.time() * 1000  # Convert to milliseconds
                    if current_time - self._last_key_time < self.DEBOUNCE_MS:
                        continue  # Ignore key within debounce window

                    self._last_key_time = current_time

                    # Process key
                    if key == b' ':
                        # Toggle pause/resume
                        if self.state.is_playing:
                            self.command_queue.put(('pause', None))
                        elif self.state.is_paused:
                            self.command_queue.put(('resume', None))

                    elif key in (b'q', b'Q'):
                        # Quit
                        self.command_queue.put(('quit', None))

                    elif key == b'\xe0':  # Arrow key prefix
                        # Read second byte for arrow key
                        arrow = msvcrt.getch()
                        if arrow == b'M':  # Right arrow
                            self.command_queue.put(('seek', self.SEEK_DELTA_SEC))
                        elif arrow == b'K':  # Left arrow
                            self.command_queue.put(('seek', -self.SEEK_DELTA_SEC))
                        elif arrow == b'H':  # Up arrow
                            self.command_queue.put(('speed', self.SPEED_DELTA))
                        elif arrow == b'P':  # Down arrow
                            self.command_queue.put(('speed', -self.SPEED_DELTA))

                # Small sleep to prevent CPU spinning
                time.sleep(0.01)

            except Exception as e:
                logger.error(f"Error in keyboard input thread: {e}")
                break

        logger.debug("Keyboard input thread stopped")

    def _process_commands(self) -> None:
        """Process commands from the command queue."""
        logger.debug("Command processing started")

        while not self.shutdown_event.is_set():
            try:
                # Get command with timeout to allow checking shutdown event
                command, arg = self.command_queue.get(timeout=0.1)

                # Process command
                if command == 'pause':
                    try:
                        self.pause()
                    except RuntimeError as e:
                        logger.warning(f"Pause failed: {e}")

                elif command == 'resume':
                    try:
                        self.resume()
                    except RuntimeError as e:
                        logger.warning(f"Resume failed: {e}")

                elif command == 'quit':
                    self.quit()
                    break

                elif command == 'seek':
                    try:
                        self.seek(arg)
                    except RuntimeError as e:
                        logger.warning(f"Seek failed: {e}")

                elif command == 'speed':
                    try:
                        self.adjust_speed(arg)
                    except RuntimeError as e:
                        logger.warning(f"Speed adjust failed: {e}")

            except queue.Empty:
                # No command available, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing command: {e}")

        logger.debug("Command processing stopped")
