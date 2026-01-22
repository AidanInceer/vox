"""Unit tests for VoiceInputController class.

Tests cover:
- State machine transitions (IDLE → RECORDING → TRANSCRIBING → PASTING → IDLE)
- Toggle behavior (hotkey press to start, press again to stop)
- Cancel functionality (Escape key)
- Integration callbacks
"""

from unittest.mock import MagicMock, patch

import pytest

from src.persistence.models import AppState
from src.voice_input.controller import VoiceInputController


@pytest.fixture
def mock_database() -> MagicMock:
    """Create a mock database."""
    db = MagicMock()
    db.get_setting.return_value = None
    return db


@pytest.fixture
def controller(mock_database: MagicMock) -> VoiceInputController:
    """Create a VoiceInputController with mocked dependencies."""
    return VoiceInputController(database=mock_database)


class TestVoiceInputControllerInit:
    """Tests for controller initialization."""

    def test_init_sets_idle_state(self, mock_database: MagicMock) -> None:
        """Controller should initialize in IDLE state."""
        controller = VoiceInputController(database=mock_database)
        assert controller.state == AppState.IDLE

    def test_init_accepts_database(self, mock_database: MagicMock) -> None:
        """Controller should accept database instance."""
        controller = VoiceInputController(database=mock_database)
        assert controller._database is mock_database

    def test_init_accepts_callbacks(self, mock_database: MagicMock) -> None:
        """Controller should accept on_state_change and on_error callbacks."""
        state_callback = MagicMock()
        error_callback = MagicMock()

        controller = VoiceInputController(
            database=mock_database,
            on_state_change=state_callback,
            on_error=error_callback,
        )

        assert controller._on_state_change is state_callback
        assert controller._on_error is error_callback

    def test_is_recording_false_initially(self, mock_database: MagicMock) -> None:
        """is_recording should be False initially."""
        controller = VoiceInputController(database=mock_database)
        assert controller.is_recording is False


class TestVoiceInputControllerStartStop:
    """Tests for start/stop lifecycle."""

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_start_initializes_hotkey_manager(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """start should initialize and start HotkeyManager."""
        mock_hotkey = MagicMock()
        mock_hotkey_class.return_value = mock_hotkey

        controller = VoiceInputController(database=mock_database)
        controller.start()

        mock_hotkey_class.assert_called_once()
        mock_hotkey.register_hotkey.assert_called_once()
        mock_hotkey.start.assert_called_once()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_start_raises_if_already_started(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """start should raise RuntimeError if already started."""
        controller = VoiceInputController(database=mock_database)
        controller.start()

        with pytest.raises(RuntimeError):
            controller.start()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_stop_stops_hotkey_manager(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """stop should stop HotkeyManager."""
        mock_hotkey = MagicMock()
        mock_hotkey_class.return_value = mock_hotkey

        controller = VoiceInputController(database=mock_database)
        controller.start()
        controller.stop()

        mock_hotkey.stop.assert_called_once()

    def test_stop_is_safe_when_not_started(self, mock_database: MagicMock) -> None:
        """stop should be safe to call when not started."""
        controller = VoiceInputController(database=mock_database)
        controller.stop()  # Should not raise


class TestVoiceInputControllerStateTransitions:
    """Tests for state machine transitions."""

    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_trigger_recording_transitions_to_recording(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """trigger_recording should transition from IDLE to RECORDING."""
        # Mock microphone availability
        mock_check_mic.return_value = (True, None)

        controller = VoiceInputController(database=mock_database)
        controller.start()

        assert controller.state == AppState.IDLE

        controller.trigger_recording()

        assert controller.state == AppState.RECORDING

    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_state_change_callback_invoked(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """State change callback should be invoked on transitions."""
        # Mock microphone availability
        mock_check_mic.return_value = (True, None)

        state_callback = MagicMock()

        controller = VoiceInputController(database=mock_database, on_state_change=state_callback)
        controller.start()

        controller.trigger_recording()

        state_callback.assert_called_with(AppState.RECORDING)


class TestVoiceInputControllerToggle:
    """Tests for toggle behavior (hotkey press to start/stop)."""

    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_trigger_recording_starts_from_idle(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """trigger_recording from IDLE should start recording."""
        # Mock microphone availability
        mock_check_mic.return_value = (True, None)

        mock_recorder = MagicMock()
        mock_recorder_class.return_value = mock_recorder

        controller = VoiceInputController(database=mock_database)
        controller.start()

        controller.trigger_recording()

        assert controller.state == AppState.RECORDING
        mock_recorder.start_recording.assert_called_once()

    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.STTEngine")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_trigger_recording_stops_and_transcribes(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_stt_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """trigger_recording from RECORDING should stop and transcribe."""
        import numpy as np

        # Mock microphone availability
        mock_check_mic.return_value = (True, None)

        mock_recorder = MagicMock()
        mock_recorder.get_audio_data.return_value = np.zeros(1000, dtype=np.int16)
        mock_recorder.get_recording_duration.return_value = 1.5
        mock_recorder_class.return_value = mock_recorder

        mock_stt = MagicMock()
        mock_stt.transcribe_audio.return_value = "Hello world"
        mock_stt_class.return_value = mock_stt

        mock_paster = MagicMock()
        mock_paster_class.return_value = mock_paster

        controller = VoiceInputController(database=mock_database)
        controller.start()

        # Start recording
        controller.trigger_recording()
        assert controller.state == AppState.RECORDING

        # Stop recording (second trigger)
        controller.trigger_recording()

        # Should end in IDLE after processing
        assert controller.state == AppState.IDLE
        mock_recorder.stop_recording.assert_called()


class TestVoiceInputControllerCancel:
    """Tests for cancel functionality."""

    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_cancel_recording_returns_to_idle(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """cancel_recording should return to IDLE without transcribing."""
        # Mock microphone availability
        mock_check_mic.return_value = (True, None)

        mock_recorder = MagicMock()
        mock_recorder_class.return_value = mock_recorder

        controller = VoiceInputController(database=mock_database)
        controller.start()

        # Start recording
        controller.trigger_recording()
        assert controller.state == AppState.RECORDING

        # Cancel
        controller.cancel_recording()

        assert controller.state == AppState.IDLE
        mock_recorder.stop_recording.assert_called_once()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_cancel_recording_noop_from_idle(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """cancel_recording should be no-op from IDLE state."""
        controller = VoiceInputController(database=mock_database)
        controller.start()

        # Cancel from IDLE should not raise
        controller.cancel_recording()

        assert controller.state == AppState.IDLE


class TestVoiceInputControllerHotkeyUpdate:
    """Tests for hotkey update functionality."""

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_update_hotkey_persists_to_database(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """update_hotkey should persist new hotkey to database."""
        controller = VoiceInputController(database=mock_database)
        controller.start()

        controller.update_hotkey("ctrl+shift+a")

        mock_database.set_setting.assert_called_with("hotkey", "ctrl+shift+a")

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_update_hotkey_reregisters(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """update_hotkey should unregister old and register new hotkey."""
        mock_hotkey = MagicMock()
        mock_hotkey_class.return_value = mock_hotkey

        controller = VoiceInputController(database=mock_database)
        controller.start()

        controller.update_hotkey("ctrl+shift+a")

        mock_hotkey.unregister_hotkey.assert_called()
        # Should have 2 register calls: initial + update
        assert mock_hotkey.register_hotkey.call_count == 2


class TestVoiceInputControllerErrorHandling:
    """Tests for error handling."""

    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_microphone_error_notifies_callback(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Microphone error should trigger error callback."""
        from src.utils.errors import MicrophoneError

        mock_recorder_class.side_effect = MicrophoneError("No microphone", error_code="NO_MIC")

        error_callback = MagicMock()
        controller = VoiceInputController(database=mock_database, on_error=error_callback)
        controller.start()

        controller.trigger_recording()

        error_callback.assert_called()
        assert controller.state == AppState.IDLE


class TestVoiceInputControllerIndicatorIntegration:
    """Tests for RecordingIndicator integration."""

    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_indicator_shown_on_recording_start(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Indicator should show with recording state when recording starts."""
        # Mock microphone availability
        mock_check_mic.return_value = (True, None)

        mock_indicator = MagicMock()
        mock_indicator.is_visible = False

        controller = VoiceInputController(database=mock_database, indicator=mock_indicator)
        controller.start()
        controller.trigger_recording()

        mock_indicator.show.assert_called_with("recording")

    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.STTEngine")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_indicator_updates_to_processing(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_stt_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Indicator should update to processing during transcription."""
        import numpy as np

        # Mock microphone availability
        mock_check_mic.return_value = (True, None)

        mock_recorder = MagicMock()
        mock_recorder.stop_recording.return_value = np.zeros(1000, dtype=np.int16)
        mock_recorder.sample_rate = 16000
        mock_recorder_class.return_value = mock_recorder

        mock_stt = MagicMock()
        mock_stt.transcribe_audio.return_value = "Hello"
        mock_stt_class.return_value = mock_stt

        mock_paster = MagicMock()
        mock_paster_class.return_value = mock_paster

        mock_indicator = MagicMock()
        mock_indicator.is_visible = True

        controller = VoiceInputController(database=mock_database, indicator=mock_indicator)
        controller.start()
        controller.trigger_recording()  # Start
        controller.trigger_recording()  # Stop and process

        # Should have updated to processing
        mock_indicator.update_state.assert_any_call("processing")

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_indicator_hidden_when_idle(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Indicator should be hidden when returning to IDLE state."""
        mock_indicator = MagicMock()

        controller = VoiceInputController(database=mock_database, indicator=mock_indicator)
        controller.start()

        # Force a state change to IDLE
        controller._set_state(AppState.IDLE)

        mock_indicator.hide.assert_called()

    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_indicator_shows_error_on_failure(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Indicator should show error state on failure."""
        from src.utils.errors import MicrophoneError

        mock_recorder_class.side_effect = MicrophoneError("No microphone", error_code="NO_MIC")

        mock_indicator = MagicMock()
        mock_indicator.is_visible = False

        controller = VoiceInputController(database=mock_database, indicator=mock_indicator)
        controller.start()
        controller.trigger_recording()

        # Should show error state
        mock_indicator.show.assert_called_with("error")

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_indicator_hidden_on_stop(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Indicator should be hidden when controller is stopped."""
        mock_indicator = MagicMock()

        controller = VoiceInputController(database=mock_database, indicator=mock_indicator)
        controller.start()
        controller.stop()

        mock_indicator.hide.assert_called()

    def test_controller_works_without_indicator(self, mock_database: MagicMock) -> None:
        """Controller should work correctly without an indicator."""
        controller = VoiceInputController(database=mock_database)
        # Should not raise even without indicator
        controller._set_state(AppState.RECORDING)
        controller._set_state(AppState.IDLE)


class TestErrorStateTransitions:
    """Tests for error handling state transitions (T084)."""

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    def test_error_state_on_no_microphone(
        self,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Controller should transition to ERROR state when no microphone."""
        mock_check_mic.return_value = (False, "No microphone detected")

        states_captured: list[AppState] = []

        def capture_state(state: AppState) -> None:
            states_captured.append(state)

        controller = VoiceInputController(database=mock_database, on_state_change=capture_state)
        controller.start()
        controller.trigger_recording()

        # Should have transitioned to ERROR then IDLE
        assert AppState.ERROR in states_captured
        assert states_captured[-1] == AppState.IDLE

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    def test_error_callback_invoked_on_mic_error(
        self,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """on_error callback should be invoked with error message."""
        mock_check_mic.return_value = (False, "Microphone unavailable")

        error_messages: list[str] = []

        def capture_error(message: str) -> None:
            error_messages.append(message)

        controller = VoiceInputController(database=mock_database, on_error=capture_error)
        controller.start()
        controller.trigger_recording()

        assert len(error_messages) == 1
        assert "unavailable" in error_messages[0].lower()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    def test_error_recovery_to_idle(
        self,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Controller should automatically recover to IDLE after error."""
        from src.utils.errors import MicrophoneError

        mock_check_mic.return_value = (True, None)
        mock_recorder_class.side_effect = MicrophoneError("Device disconnected", error_code="DEVICE_ERROR")

        controller = VoiceInputController(database=mock_database)
        controller.start()
        controller.trigger_recording()

        # Should be back in IDLE after error
        assert controller.state == AppState.IDLE

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.STTEngine")
    def test_transcription_failure_shows_error(
        self,
        mock_stt_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Empty transcription result should trigger error notification."""
        import numpy as np

        mock_check_mic.return_value = (True, None)

        mock_recorder = MagicMock()
        mock_recorder.stop_recording.return_value = np.zeros(1000, dtype=np.int16)
        mock_recorder.sample_rate = 16000
        mock_recorder_class.return_value = mock_recorder

        mock_stt = MagicMock()
        mock_stt.transcribe_audio.return_value = ""  # Empty result
        mock_stt_class.return_value = mock_stt

        error_messages: list[str] = []

        def capture_error(msg: str) -> None:
            error_messages.append(msg)

        controller = VoiceInputController(database=mock_database, on_error=capture_error)
        controller.start()

        # Start recording
        controller._start_recording()
        # Stop and process
        controller._stop_recording_and_process()

        assert len(error_messages) >= 1
        assert "transcribe" in error_messages[-1].lower()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    def test_error_indicator_state_shown(
        self,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Indicator should display error state on error notification."""
        mock_indicator = MagicMock()
        mock_indicator.is_visible = True

        controller = VoiceInputController(database=mock_database, indicator=mock_indicator)
        controller.start()

        # Manually trigger error notification
        controller._notify_error("Test error")

        # Should have called update_state with "error"
        mock_indicator.update_state.assert_any_call("error")

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    def test_controller_ready_after_error_recovery(
        self,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
        mock_database: MagicMock,
    ) -> None:
        """Controller should be ready for new recording after error recovery."""
        # First call fails, second succeeds
        mock_check_mic.side_effect = [
            (False, "No microphone"),
            (True, None),
        ]

        controller = VoiceInputController(database=mock_database)
        controller.start()

        # First attempt fails
        controller.trigger_recording()
        assert controller.state == AppState.IDLE

        # Restore successful microphone check
        mock_check_mic.side_effect = None
        mock_check_mic.return_value = (True, None)

        # Controller should be able to accept new recording
        assert controller.state == AppState.IDLE
        assert controller.is_recording is False
