"""Voice input controller coordinating hotkey, recording, and transcription.

This module provides the main integration controller that orchestrates all
voice input components: hotkey listening, audio recording, speech-to-text
transcription, and clipboard paste operations.
"""

import logging
import tempfile
import threading
from pathlib import Path
from typing import Callable, Literal, Optional

from src.clipboard.paster import ClipboardPaster
from src.hotkey.manager import HotkeyManager
from src.persistence.database import VoxDatabase
from src.persistence.models import AppState
from src.stt.engine import STTEngine
from src.stt.recorder import MicrophoneRecorder, check_microphone_available
from src.ui.indicator import RecordingIndicator
from src.utils.errors import (
    MicrophoneError,
    TranscriptionError,
    VoxError,
)

logger = logging.getLogger(__name__)

# Default hotkey for voice input
DEFAULT_HOTKEY = "<ctrl>+<alt>+space"


class VoiceInputController:
    """Central coordinator for hotkey-triggered voice input operations.

    This is the main orchestrator for the voice input feature. It manages
    the complete voice-to-text pipeline including:
    - Global hotkey registration (toggle mode: press to start, press to stop)
    - Audio recording via MicrophoneRecorder
    - Speech-to-text transcription via STTEngine
    - Clipboard paste operations via ClipboardPaster
    - State machine transitions with callback notifications
    - Transcription history persistence

    The controller uses a state machine to track the current operation and
    ensure valid transitions between states.

    State Machine:
        IDLE ─────[hotkey]────→ RECORDING
          ↑                         │
          │                         │ [hotkey]
          │                         ↓
          │                    TRANSCRIBING
          │                         │
          │                         │ [success]
          │                         ↓
          └────────────────────  PASTING ────→ IDLE

        RECORDING ───[Escape/cancel]───→ IDLE (no paste)

    Attributes:
        state: Current application state (read-only).
        is_recording: Whether currently recording audio (read-only).

    Example:
        >>> db = VoxDatabase()
        >>> controller = VoiceInputController(database=db)
        >>> controller.start()
        >>> # User presses Ctrl+Alt+Space to toggle recording
        >>> controller.stop()
    """

    def __init__(
        self,
        database: VoxDatabase,
        on_state_change: Optional[Callable[[AppState], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        indicator: Optional[RecordingIndicator] = None,
    ) -> None:
        """Initialize the voice input controller.

        Creates the controller with all necessary dependencies. Components
        (hotkey manager, recorder, STT engine, paster) are lazily initialized
        when `start()` is called.

        Args:
            database: VoxDatabase instance for loading settings and storing
                transcription history.
            on_state_change: Optional callback invoked when the application
                state changes. Receives the new AppState as argument.
            on_error: Optional callback invoked when an error occurs.
                Receives the error message as argument.
            indicator: Optional RecordingIndicator instance for visual
                feedback during recording and processing.
        """
        self._database = database
        self._on_state_change = on_state_change
        self._on_error = on_error
        self._indicator = indicator

        # Initialize state
        self._state = AppState.IDLE
        self._state_lock = threading.Lock()

        # Components (lazy initialized)
        self._hotkey_manager: Optional[HotkeyManager] = None
        self._recorder: Optional[MicrophoneRecorder] = None
        self._stt_engine: Optional[STTEngine] = None
        self._paster: Optional[ClipboardPaster] = None

        # Current hotkey configuration
        self._current_hotkey: str = DEFAULT_HOTKEY

        # Recording state
        self._is_started = False

        logger.debug("VoiceInputController initialized")

    @property
    def state(self) -> AppState:
        """Get the current application state.

        Returns:
            Current AppState (IDLE, RECORDING, TRANSCRIBING, PASTING, ERROR).
        """
        with self._state_lock:
            return self._state

    @property
    def is_recording(self) -> bool:
        """Check if currently recording audio.

        Returns:
            True if the controller is in RECORDING state, False otherwise.
        """
        return self.state == AppState.RECORDING

    def _set_state(self, new_state: AppState) -> None:
        """Set the application state and notify callback.

        Args:
            new_state: The new state to transition to
        """
        with self._state_lock:
            old_state = self._state
            self._state = new_state

        logger.info(f"State transition: {old_state.name} → {new_state.name}")

        # Update indicator based on state
        self._update_indicator(new_state)

        if self._on_state_change:
            try:
                self._on_state_change(new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")

    def _update_indicator(self, state: AppState) -> None:
        """Update the recording indicator based on application state.

        Args:
            state: The current application state
        """
        if self._indicator is None:
            return

        # Map AppState to indicator state
        indicator_state_map: dict[AppState, Literal["recording", "processing", "success", "error"]] = {
            AppState.RECORDING: "recording",
            AppState.TRANSCRIBING: "processing",
            AppState.PASTING: "success",
            AppState.ERROR: "error",
        }

        if state == AppState.IDLE:
            # Hide indicator when idle
            self._indicator.hide()
        elif state in indicator_state_map:
            indicator_state = indicator_state_map[state]
            if not self._indicator.is_visible:
                self._indicator.show(indicator_state)
            else:
                self._indicator.update_state(indicator_state)

    def _notify_error(self, message: str) -> None:
        """Notify error callback and transition to ERROR state.

        Args:
            message: Error message to pass to callback
        """
        logger.error(f"Error: {message}")
        self._set_state(AppState.ERROR)

        if self._on_error:
            try:
                self._on_error(message)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

        # Auto-recover to IDLE after error notification
        self._set_state(AppState.IDLE)

    def start(self) -> None:
        """Start the voice input controller.

        Initializes all components and begins listening for the activation
        hotkey. Loads settings from the database and registers the configured
        hotkey for toggle recording.

        Raises:
            RuntimeError: If the controller is already started.
        """
        if self._is_started:
            raise RuntimeError("VoiceInputController is already started")

        # Load hotkey from database
        stored_hotkey = self._database.get_setting("hotkey")
        if stored_hotkey:
            self._current_hotkey = stored_hotkey
        else:
            # Initialize default settings
            self._database.set_setting("hotkey", DEFAULT_HOTKEY)
            self._database.set_setting("restore_clipboard", "true")

        # Initialize components
        self._hotkey_manager = HotkeyManager()
        self._paster = ClipboardPaster()

        # Register hotkey for toggle
        self._hotkey_manager.register_hotkey(self._current_hotkey, self._on_hotkey_pressed)

        # Start listening
        self._hotkey_manager.start()
        self._is_started = True

        logger.info(f"VoiceInputController started with hotkey: {self._current_hotkey}")

    def stop(self) -> None:
        """Stop the controller and release all resources.

        Cancels any in-progress recording, stops the hotkey listener,
        hides the indicator, and cleans up all components.
        Safe to call multiple times; subsequent calls are no-ops.
        """
        if not self._is_started:
            return

        # Cancel any in-progress recording
        if self.state == AppState.RECORDING:
            self.cancel_recording()

        # Stop hotkey listener
        if self._hotkey_manager:
            self._hotkey_manager.stop()
            self._hotkey_manager = None

        # Hide indicator (don't destroy - may be shared)
        if self._indicator:
            self._indicator.hide()

        # Cleanup components
        self._recorder = None
        self._stt_engine = None
        self._paster = None

        self._is_started = False
        self._set_state(AppState.IDLE)

        logger.info("VoiceInputController stopped")

    def trigger_recording(self) -> None:
        """Manually trigger a recording session.

        Programmatic equivalent of pressing the activation hotkey.
        Uses toggle behavior:
        - If IDLE: starts recording
        - If RECORDING: stops recording and begins transcription
        - Other states: ignored (busy)
        """
        self._on_hotkey_pressed()

    def cancel_recording(self) -> None:
        """Cancel an in-progress recording without transcribing.

        Stops the recorder and returns to IDLE state without processing
        the recorded audio. No-op if not currently recording.
        """
        if self.state != AppState.RECORDING:
            return

        logger.info("Recording cancelled by user")

        # Stop the recorder
        if self._recorder:
            self._recorder.stop_recording()
            self._recorder = None

        self._set_state(AppState.IDLE)

    def update_hotkey(self, new_hotkey: str) -> None:
        """Update the activation hotkey.

        Changes the hotkey used to trigger voice input. If the controller
        is running, the old hotkey is unregistered and the new one is
        registered immediately. The change is persisted to the database.

        Args:
            new_hotkey: New hotkey string in pynput format
                (e.g., '<ctrl>+<alt>+space').

        Raises:
            HotkeyInvalidFormatError: If the hotkey format is invalid.
            HotkeyAlreadyRegisteredError: If the hotkey is already registered.
        """
        if not self._is_started:
            # Just update the stored value
            self._database.set_setting("hotkey", new_hotkey)
            self._current_hotkey = new_hotkey
            return

        # Unregister old hotkey
        if self._hotkey_manager:
            try:
                self._hotkey_manager.unregister_hotkey(self._current_hotkey)
            except KeyError:
                pass  # Already unregistered

            # Register new hotkey (this will validate the format)
            self._hotkey_manager.register_hotkey(new_hotkey, self._on_hotkey_pressed)

        # Persist to database
        self._database.set_setting("hotkey", new_hotkey)
        self._current_hotkey = new_hotkey

        logger.info(f"Hotkey updated to: {new_hotkey}")

    def _on_hotkey_pressed(self) -> None:
        """Handle hotkey press - toggle recording state."""
        current_state = self.state

        if current_state == AppState.IDLE:
            # Start recording
            self._start_recording()
        elif current_state == AppState.RECORDING:
            # Stop recording and process
            self._stop_recording_and_process()
        else:
            # Busy with transcription or pasting, ignore
            logger.debug(f"Hotkey ignored in state: {current_state.name}")

    def _start_recording(self) -> None:
        """Start audio recording."""
        try:
            # Check microphone availability first
            is_available, error_msg = check_microphone_available()
            if not is_available:
                self._notify_error(error_msg or "No microphone available")
                return

            self._set_state(AppState.RECORDING)

            # Create a new recorder for this session
            self._recorder = MicrophoneRecorder()
            self._recorder.start_recording()

            logger.info("Recording started")

        except MicrophoneError as e:
            self._notify_error(f"Microphone error: {e.message}")
        except Exception as e:
            self._notify_error(f"Failed to start recording: {str(e)}")

    def _stop_recording_and_process(self) -> None:
        """Stop recording, transcribe, and paste result."""
        if not self._recorder:
            self._set_state(AppState.IDLE)
            return

        try:
            # Stop recording - returns the audio data directly
            audio_data = self._recorder.stop_recording()

            if audio_data is None or len(audio_data) == 0:
                logger.warning("No audio data recorded")
                self._notify_error("No audio recorded")
                return

            self._set_state(AppState.TRANSCRIBING)

            # Save to temp file for transcription
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                self._recorder.save_wav(audio_data, temp_path)

            # Lazy load STT engine
            if self._stt_engine is None:
                self._stt_engine = STTEngine()

            # Transcribe
            transcribed_text = self._stt_engine.transcribe_audio(temp_path)

            # Cleanup temp file
            try:
                temp_path.unlink()
            except Exception:
                pass

            if not transcribed_text or not transcribed_text.strip():
                logger.warning("Empty transcription result")
                self._notify_error("Could not transcribe audio")
                return

            # Calculate duration from audio data
            sample_rate = self._recorder.sample_rate
            duration = len(audio_data) / sample_rate

            # Paste the transcribed text
            self._set_state(AppState.PASTING)

            restore_clipboard = self._database.get_setting("restore_clipboard", "true") == "true"

            if self._paster:
                self._paster.paste_text(transcribed_text.strip(), restore_clipboard=restore_clipboard)

            # Save to history
            self._database.add_transcription(text=transcribed_text.strip(), duration_seconds=duration)

            logger.info(f"Transcription complete: {len(transcribed_text)} chars, {duration:.1f}s recording")

            self._set_state(AppState.IDLE)

        except TranscriptionError as e:
            self._notify_error(f"Transcription error: {e.message}")
        except VoxError as e:
            self._notify_error(f"Error: {e.message}")
        except Exception as e:
            self._notify_error(f"Processing failed: {str(e)}")
        finally:
            self._recorder = None
