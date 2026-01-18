"""Playback controller with interactive keyboard controls.

This module provides keyboard-driven playback controls including pause/resume,
seeking, speed adjustment, and graceful quit.
"""

import logging
import msvcrt
import queue
import threading
import time
from typing import TYPE_CHECKING, List, Optional

from src.tts.playback import AudioPlayback

if TYPE_CHECKING:
    from src.tts.chunking import ChunkSynthesizer

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

    def start(
        self,
        audio_bytes: Optional[bytes] = None,
        chunks: Optional[List[str]] = None,
        chunk_synthesizer: Optional["ChunkSynthesizer"] = None,
    ) -> None:
        """Start playback with keyboard control thread.

        Can operate in two modes:
        1. Direct playback: Pass audio_bytes for immediate playback
        2. Streaming playback: Pass chunk_synthesizer for chunked streaming

        Args:
            audio_bytes: Audio data to play (for direct playback mode)
            chunks: List of text chunks for reference (for direct mode)
            chunk_synthesizer: ChunkSynthesizer for streaming playback (for streaming mode)

        Raises:
            RuntimeError: If playback fails to start
            ValueError: If neither audio_bytes nor chunk_synthesizer provided
        """
        if audio_bytes is None and chunk_synthesizer is None:
            raise ValueError("Either audio_bytes or chunk_synthesizer must be provided")

        try:
            # Store chunks for reference
            if chunks:
                self.state.chunk_buffer = chunks

            # Start keyboard input thread
            self._keyboard_thread = threading.Thread(target=self._keyboard_input_thread, daemon=True)
            self._keyboard_thread.start()

            # Start audio playback based on mode
            if chunk_synthesizer:
                # Streaming mode: consume chunks from synthesizer
                playback_thread = threading.Thread(
                    target=self._chunked_playback_thread, args=(chunk_synthesizer,), daemon=True
                )
            else:
                # Direct mode: play audio_bytes directly
                playback_thread = threading.Thread(target=self._playback_thread, args=(audio_bytes,), daemon=True)

            playback_thread.start()

            # Process commands in main thread (this blocks until quit)
            self._process_commands()

            # Wait for playback to complete or quit
            playback_thread.join(timeout=1.0)

        except Exception as e:
            logger.error(f"Failed to start playback: {e}")
            self.shutdown_event.set()
            raise RuntimeError(f"Playback failed: {e}") from e

    def _playback_thread(self, audio_bytes: bytes) -> None:
        """Background thread for audio playback.

        Args:
            audio_bytes: Audio data to play
        """
        try:
            self.audio_playback.play_audio(audio_bytes)
        except Exception as e:
            logger.error(f"Playback thread error: {e}")
            self.shutdown_event.set()

    def _chunked_playback_thread(self, chunk_synthesizer: "ChunkSynthesizer") -> None:
        """Background thread for chunked audio playback.

        Consumes chunks from ChunkSynthesizer and plays them sequentially.

        Args:
            chunk_synthesizer: ChunkSynthesizer instance to consume chunks from
        """
        from src.tts.chunking import SynthesisStatus

        try:
            logger.info("Starting chunked playback")
            chunk_index = 0
            total_chunks = chunk_synthesizer.get_chunk_count()

            while not self.shutdown_event.is_set() and chunk_index < total_chunks:
                # Get next chunk
                chunk = None

                # Try to get from synthesizer's chunks list
                if chunk_index < len(chunk_synthesizer.chunks):
                    chunk = chunk_synthesizer.chunks[chunk_index]

                if chunk is None:
                    logger.warning(f"Chunk {chunk_index} not found")
                    break

                # Wait for chunk to be synthesized
                while not self.shutdown_event.is_set():
                    if chunk.synthesis_status == SynthesisStatus.COMPLETED:
                        break
                    elif chunk.synthesis_status == SynthesisStatus.FAILED:
                        logger.error(f"Chunk {chunk_index} synthesis failed, skipping")
                        chunk_index += 1
                        continue

                    # Show buffering indicator if waiting
                    if chunk.synthesis_status in (SynthesisStatus.PENDING, SynthesisStatus.IN_PROGRESS):
                        print(f"\r⏳ Buffering chunk {chunk_index + 1}/{total_chunks}...", end="", flush=True)

                    time.sleep(0.1)

                # Clear buffering message
                print("\r" + " " * 60 + "\r", end="", flush=True)

                # Play the chunk
                if chunk.audio_data:
                    logger.debug(f"Playing chunk {chunk_index + 1}/{total_chunks}")
                    with self._lock:
                        self.state.current_chunk_index = chunk_index

                    try:
                        self.audio_playback.play_audio(chunk.audio_data)
                    except Exception as e:
                        logger.error(f"Failed to play chunk {chunk_index}: {e}")
                        # Continue to next chunk on error

                chunk_index += 1

            logger.info("Chunked playback complete")

        except Exception as e:
            logger.error(f"Chunked playback thread error: {e}")
            self.shutdown_event.set()

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

    def seek(self, delta_seconds: int, chunk_synthesizer: Optional["ChunkSynthesizer"] = None) -> None:
        """Seek forward or backward by delta seconds.

        Args:
            delta_seconds: Number of seconds to seek (positive=forward, negative=backward)
            chunk_synthesizer: Optional ChunkSynthesizer for on-demand synthesis

        Raises:
            RuntimeError: If not currently playing
        """
        with self._lock:
            if not (self.state.is_playing or self.state.is_paused):
                raise RuntimeError("Cannot seek: not playing")

            # In chunked mode, seeking between chunks is not fully supported yet
            # This is a limitation noted for future enhancement
            if chunk_synthesizer:
                logger.warning("Seeking in chunked mode is limited - seeking within current audio only")

            # Calculate new position from current state position
            current_pos = self.state.current_position_ms
            new_pos = max(0, current_pos + (delta_seconds * 1000))

            # Seek to new position
            self.audio_playback.seek(new_pos)
            logger.info(f"Seeked {delta_seconds}s to {new_pos}ms")

    def adjust_speed(self, delta: float) -> None:
        """Adjust playback speed.

        Note: Speed adjustment is not supported during playback.
        Speed must be set before playback starts using the --speed flag.

        Args:
            delta: Speed adjustment amount (positive=faster, negative=slower)

        Raises:
            RuntimeError: If not currently playing
            NotImplementedError: Speed control not supported during playback
        """
        with self._lock:
            if not (self.state.is_playing or self.state.is_paused):
                raise RuntimeError("Cannot adjust speed: not playing")

            # pygame.mixer doesn't support runtime speed control
            # Inform the user about the limitation
            logger.warning(
                "Speed adjustment during playback is not supported. Use --speed flag when starting playback."
            )
            print(
                "\n⚠️  Speed control not available during playback.\n"
                "   Use the --speed flag when starting (e.g., --speed 1.5)\n"
            )

            # Don't call set_speed as it will raise NotImplementedError

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
                    if key == b" ":
                        # Toggle pause/resume
                        if self.state.is_playing:
                            self.command_queue.put(("pause", None))
                        elif self.state.is_paused:
                            self.command_queue.put(("resume", None))

                    elif key in (b"q", b"Q"):
                        # Quit
                        self.command_queue.put(("quit", None))

                    elif key == b"\xe0":  # Arrow key prefix
                        # Read second byte for arrow key
                        arrow = msvcrt.getch()
                        if arrow == b"M":  # Right arrow
                            self.command_queue.put(("seek", self.SEEK_DELTA_SEC))
                        elif arrow == b"K":  # Left arrow
                            self.command_queue.put(("seek", -self.SEEK_DELTA_SEC))
                        elif arrow == b"H":  # Up arrow
                            self.command_queue.put(("speed", self.SPEED_DELTA))
                        elif arrow == b"P":  # Down arrow
                            self.command_queue.put(("speed", -self.SPEED_DELTA))

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
                if command == "pause":
                    try:
                        self.pause()
                    except RuntimeError as e:
                        logger.warning(f"Pause failed: {e}")

                elif command == "resume":
                    try:
                        self.resume()
                    except RuntimeError as e:
                        logger.warning(f"Resume failed: {e}")

                elif command == "quit":
                    self.quit()
                    break

                elif command == "seek":
                    try:
                        self.seek(arg)
                    except RuntimeError as e:
                        logger.warning(f"Seek failed: {e}")

                elif command == "speed":
                    try:
                        self.adjust_speed(arg)
                    except RuntimeError as e:
                        logger.warning(f"Speed adjust failed: {e}")

            except queue.Empty:
                # Check if playback has finished naturally
                if not self.state.is_playing and not self.state.is_paused:
                    logger.debug("Playback completed, stopping command processing")
                    break
                # No command available, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing command: {e}")

        logger.debug("Command processing stopped")
