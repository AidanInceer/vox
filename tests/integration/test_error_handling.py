"""Integration tests for error handling and recovery flow.

Tests for T085: Error recovery flow in the voice input system.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.persistence.database import VoxDatabase
from src.persistence.models import AppState
from src.voice_input.controller import VoiceInputController


class TestErrorRecoveryFlow:
    """Integration tests for error recovery scenarios."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_error.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    def test_full_error_recovery_cycle(
        self,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test complete error recovery cycle: error -> recovery -> ready."""
        mock_check_mic.return_value = (False, "No microphone detected")

        states: list[AppState] = []
        errors: list[str] = []

        controller = VoiceInputController(
            database=self.database,
            on_state_change=lambda s: states.append(s),
            on_error=lambda e: errors.append(e),
        )
        controller.start()

        # Trigger recording (will fail due to no mic)
        controller.trigger_recording()

        # Verify error flow
        assert AppState.ERROR in states
        assert len(errors) == 1
        assert "microphone" in errors[0].lower()

        # Verify recovery to IDLE
        assert controller.state == AppState.IDLE

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    def test_error_does_not_block_subsequent_recordings(
        self,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test that error recovery allows new recording attempts."""
        # First call fails, second succeeds
        mock_check_mic.side_effect = [
            (False, "No microphone"),
            (True, None),
        ]

        mock_recorder = MagicMock()
        mock_recorder_class.return_value = mock_recorder

        controller = VoiceInputController(database=self.database)
        controller.start()

        # First attempt fails
        controller.trigger_recording()
        assert controller.state == AppState.IDLE

        # Second attempt should start recording
        controller.trigger_recording()
        assert controller.state == AppState.RECORDING

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    def test_multiple_errors_handled_gracefully(
        self,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test that multiple consecutive errors are handled gracefully."""
        mock_check_mic.return_value = (False, "No microphone")

        error_count = 0

        def count_error(msg: str) -> None:
            nonlocal error_count
            error_count += 1

        controller = VoiceInputController(
            database=self.database, on_error=count_error
        )
        controller.start()

        # Multiple failed attempts
        for _ in range(3):
            controller.trigger_recording()
            assert controller.state == AppState.IDLE

        assert error_count == 3

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    def test_error_callback_exception_does_not_crash(
        self,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test that exception in error callback doesn't crash controller."""
        mock_check_mic.return_value = (False, "No microphone")

        def bad_callback(msg: str) -> None:
            raise ValueError("Callback error!")

        controller = VoiceInputController(
            database=self.database, on_error=bad_callback
        )
        controller.start()

        # Should not crash despite callback exception
        controller.trigger_recording()
        assert controller.state == AppState.IDLE


class TestErrorIndicatorIntegration:
    """Integration tests for error indicator display."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_indicator.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    def test_indicator_shows_error_then_hides(
        self,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test that indicator shows error state then hides on recovery."""
        mock_check_mic.return_value = (False, "No microphone")

        mock_indicator = MagicMock()
        mock_indicator.is_visible = False

        controller = VoiceInputController(
            database=self.database, indicator=mock_indicator
        )
        controller.start()

        controller.trigger_recording()

        # Should have shown error
        mock_indicator.show.assert_called()
        call_args = [call[0][0] for call in mock_indicator.show.call_args_list]
        assert "error" in call_args

        # Should hide when returning to IDLE
        mock_indicator.hide.assert_called()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    def test_indicator_cycles_through_states_on_error(
        self,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test indicator state transitions during error flow."""
        mock_check_mic.return_value = (False, "No microphone")

        indicator_states: list[str] = []
        mock_indicator = MagicMock()
        mock_indicator.is_visible = True

        def track_update_state(state: str) -> None:
            indicator_states.append(state)

        mock_indicator.update_state.side_effect = track_update_state

        controller = VoiceInputController(
            database=self.database, indicator=mock_indicator
        )
        controller.start()

        controller.trigger_recording()

        # Should have transitioned through error state
        assert "error" in indicator_states


class TestTranscriptionErrorHandling:
    """Integration tests for transcription-related errors."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_transcription.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.STTEngine")
    def test_empty_audio_triggers_error(
        self,
        mock_stt_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test that empty audio data triggers appropriate error."""
        mock_check_mic.return_value = (True, None)

        mock_recorder = MagicMock()
        mock_recorder.get_audio_data.return_value = None  # No audio
        mock_recorder_class.return_value = mock_recorder

        errors: list[str] = []

        controller = VoiceInputController(
            database=self.database, on_error=lambda e: errors.append(e)
        )
        controller.start()

        # Start and stop recording
        controller._start_recording()
        controller._stop_recording_and_process()

        assert len(errors) >= 1
        assert "audio" in errors[-1].lower() or "recorded" in errors[-1].lower()

    @patch("src.voice_input.controller.HotkeyManager")
    @patch("src.voice_input.controller.ClipboardPaster")
    @patch("src.voice_input.controller.check_microphone_available")
    @patch("src.voice_input.controller.MicrophoneRecorder")
    @patch("src.voice_input.controller.STTEngine")
    def test_stt_exception_triggers_error(
        self,
        mock_stt_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_check_mic: MagicMock,
        mock_paster_class: MagicMock,
        mock_hotkey_class: MagicMock,
    ) -> None:
        """Test that STT engine exception triggers error notification."""
        import numpy as np

        from src.utils.errors import TranscriptionError

        mock_check_mic.return_value = (True, None)

        mock_recorder = MagicMock()
        mock_recorder.get_audio_data.return_value = np.zeros(1000)
        mock_recorder.save_to_file.return_value = None
        mock_recorder_class.return_value = mock_recorder

        mock_stt = MagicMock()
        mock_stt.transcribe_audio.side_effect = TranscriptionError(
            "Model failed", error_code="MODEL_ERROR"
        )
        mock_stt_class.return_value = mock_stt

        errors: list[str] = []

        controller = VoiceInputController(
            database=self.database, on_error=lambda e: errors.append(e)
        )
        controller.start()

        controller._start_recording()
        controller._stop_recording_and_process()

        assert len(errors) >= 1
        # Should have recovered to IDLE
        assert controller.state == AppState.IDLE
