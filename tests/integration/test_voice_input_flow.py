"""Integration tests for the voice input flow.

Tests the end-to-end voice input workflow:
- Hotkey → Recording → Transcription → Paste

Note: These tests use mocked hardware/external services to allow
running in CI/CD environments without actual microphones or Whisper models.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.persistence.models import AppState
from src.voice_input.controller import VoiceInputController


@pytest.fixture
def temp_db_path() -> Path:
    """Create a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        return Path(f.name)


@pytest.fixture
def mock_components():
    """Fixture to mock all external components."""
    import numpy as np

    with (
        patch("src.voice_input.controller.HotkeyManager") as mock_hotkey_class,
        patch("src.voice_input.controller.ClipboardPaster") as mock_paster_class,
        patch("src.voice_input.controller.MicrophoneRecorder") as mock_recorder_class,
        patch("src.voice_input.controller.STTEngine") as mock_stt_class,
        patch("src.voice_input.controller.check_microphone_available") as mock_check_mic,
    ):
        # Configure microphone check mock
        mock_check_mic.return_value = (True, None)

        # Configure HotkeyManager mock
        mock_hotkey = MagicMock()
        mock_hotkey_class.return_value = mock_hotkey

        # Configure ClipboardPaster mock
        mock_paster = MagicMock()
        mock_paster.paste_text.return_value = True
        mock_paster_class.return_value = mock_paster

        # Configure MicrophoneRecorder mock
        mock_recorder = MagicMock()
        mock_recorder.stop_recording.return_value = np.zeros(16000, dtype=np.int16)
        mock_recorder.sample_rate = 16000
        mock_recorder_class.return_value = mock_recorder

        # Configure STTEngine mock
        mock_stt = MagicMock()
        mock_stt.transcribe_audio.return_value = "Hello world"
        mock_stt_class.return_value = mock_stt

        yield {
            "hotkey_manager": mock_hotkey,
            "paster": mock_paster,
            "recorder": mock_recorder,
            "stt_engine": mock_stt,
        }


class TestVoiceInputEndToEnd:
    """Integration tests for the complete voice input flow."""

    def test_complete_voice_input_flow(
        self, temp_db_path: Path, mock_components: dict
    ) -> None:
        """Test complete flow: hotkey → record → transcribe → paste."""
        from src.persistence.database import VoxDatabase

        # Create real database for integration test
        db = VoxDatabase(db_path=temp_db_path)

        state_changes: list[AppState] = []

        def track_state(state: AppState) -> None:
            state_changes.append(state)

        controller = VoiceInputController(database=db, on_state_change=track_state)
        controller.start()

        # Verify initial state
        assert controller.state == AppState.IDLE

        # Step 1: Trigger recording (first hotkey press)
        controller.trigger_recording()
        assert controller.state == AppState.RECORDING

        # Step 2: Stop recording and process (second hotkey press)
        controller.trigger_recording()

        # Should have gone through all states and ended in IDLE
        assert controller.state == AppState.IDLE

        # Verify state transitions occurred
        assert AppState.RECORDING in state_changes
        assert AppState.TRANSCRIBING in state_changes
        assert AppState.PASTING in state_changes

        # Verify paste was called
        mock_components["paster"].paste_text.assert_called_once()
        paste_text = mock_components["paster"].paste_text.call_args[0][0]
        assert paste_text == "Hello world"

        # Verify transcription was saved to database
        history = db.get_history(limit=1)
        assert len(history) == 1
        assert history[0].text == "Hello world"

        controller.stop()
        db.close()

    def test_cancel_recording_flow(
        self, temp_db_path: Path, mock_components: dict
    ) -> None:
        """Test cancel flow: hotkey → record → cancel (no transcription)."""
        from src.persistence.database import VoxDatabase

        db = VoxDatabase(db_path=temp_db_path)

        controller = VoiceInputController(database=db)
        controller.start()

        # Start recording
        controller.trigger_recording()
        assert controller.state == AppState.RECORDING

        # Cancel
        controller.cancel_recording()
        assert controller.state == AppState.IDLE

        # Verify recorder was stopped
        mock_components["recorder"].stop_recording.assert_called_once()

        # Verify NO transcription was saved
        history = db.get_history(limit=10)
        assert len(history) == 0

        controller.stop()
        db.close()

    def test_hotkey_callback_integration(
        self, temp_db_path: Path, mock_components: dict
    ) -> None:
        """Test that hotkey callback is properly registered and wired."""
        from src.persistence.database import VoxDatabase

        db = VoxDatabase(db_path=temp_db_path)

        controller = VoiceInputController(database=db)
        controller.start()

        # Verify hotkey was registered
        mock_components["hotkey_manager"].register_hotkey.assert_called_once()

        # Get the registered callback
        callback = mock_components["hotkey_manager"].register_hotkey.call_args[0][1]

        # Trigger callback directly (simulating hotkey press)
        callback()

        # Should have started recording
        assert controller.state == AppState.RECORDING

        controller.stop()
        db.close()

    def test_settings_persistence(
        self, temp_db_path: Path, mock_components: dict
    ) -> None:
        """Test that settings are loaded and persisted correctly."""
        from src.persistence.database import VoxDatabase

        # First run - should set defaults
        db = VoxDatabase(db_path=temp_db_path)
        controller = VoiceInputController(database=db)
        controller.start()
        controller.stop()
        db.close()

        # Second run - should load persisted settings
        db = VoxDatabase(db_path=temp_db_path)
        hotkey = db.get_setting("hotkey")
        assert hotkey is not None
        db.close()

    def test_hotkey_update_integration(
        self, temp_db_path: Path, mock_components: dict
    ) -> None:
        """Test hotkey update with re-registration."""
        from src.persistence.database import VoxDatabase

        db = VoxDatabase(db_path=temp_db_path)

        controller = VoiceInputController(database=db)
        controller.start()

        # Update hotkey
        controller.update_hotkey("ctrl+shift+a")

        # Verify unregister and re-register were called
        mock_components["hotkey_manager"].unregister_hotkey.assert_called()
        assert mock_components["hotkey_manager"].register_hotkey.call_count == 2

        # Verify persisted
        assert db.get_setting("hotkey") == "ctrl+shift+a"

        controller.stop()
        db.close()


class TestVoiceInputErrorRecovery:
    """Tests for error handling and recovery."""

    def test_microphone_error_recovery(
        self, temp_db_path: Path, mock_components: dict
    ) -> None:
        """Test that microphone errors are handled gracefully."""
        from src.persistence.database import VoxDatabase
        from src.utils.errors import MicrophoneError

        db = VoxDatabase(db_path=temp_db_path)

        error_messages: list[str] = []

        def track_error(msg: str) -> None:
            error_messages.append(msg)

        controller = VoiceInputController(database=db, on_error=track_error)
        controller.start()

        # Make recorder raise error
        with patch(
            "src.voice_input.controller.MicrophoneRecorder"
        ) as mock_recorder_class:
            mock_recorder_class.side_effect = MicrophoneError(
                "No microphone", error_code="NO_MIC"
            )

            controller.trigger_recording()

        # Should have notified error and returned to IDLE
        assert controller.state == AppState.IDLE
        assert len(error_messages) == 1
        assert "microphone" in error_messages[0].lower()

        controller.stop()
        db.close()

    def test_transcription_error_recovery(
        self, temp_db_path: Path, mock_components: dict
    ) -> None:
        """Test that transcription errors are handled gracefully."""
        from src.persistence.database import VoxDatabase
        from src.utils.errors import TranscriptionError

        db = VoxDatabase(db_path=temp_db_path)

        error_messages: list[str] = []

        def track_error(msg: str) -> None:
            error_messages.append(msg)

        controller = VoiceInputController(database=db, on_error=track_error)
        controller.start()

        # Start recording
        controller.trigger_recording()

        # Make STT raise error during stop
        mock_components["stt_engine"].transcribe_audio.side_effect = TranscriptionError(
            "Model error", error_code="MODEL_ERROR"
        )

        # Stop recording (triggers transcription)
        controller.trigger_recording()

        # Should have notified error and returned to IDLE
        assert controller.state == AppState.IDLE
        assert len(error_messages) == 1

        controller.stop()
        db.close()
