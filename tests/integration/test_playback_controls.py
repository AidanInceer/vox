"""Integration tests for playback control workflow."""

import threading
import time
from unittest.mock import Mock, patch

import pytest

from src.tts.controller import PlaybackController
from src.tts.playback import AudioPlayback, PlaybackState


@pytest.fixture
def sample_audio_bytes():
    """Create sample WAV audio bytes for testing."""
    # Minimal valid WAV file (44-byte header + 8 bytes of data)
    wav_header = (
        b"RIFF"
        b"\x24\x00\x00\x00"  # File size - 8
        b"WAVE"
        b"fmt "
        b"\x10\x00\x00\x00"  # fmt chunk size (16)
        b"\x01\x00"  # Audio format (1 = PCM)
        b"\x01\x00"  # Number of channels (1 = mono)
        b"\x22\x56\x00\x00"  # Sample rate (22050 Hz)
        b"\x44\xac\x00\x00"  # Byte rate
        b"\x02\x00"  # Block align
        b"\x10\x00"  # Bits per sample (16)
        b"data"
        b"\x08\x00\x00\x00"  # Data chunk size (8 bytes)
        b"\x00\x00\x00\x00\x00\x00\x00\x00"  # 8 bytes of silence
    )
    return wav_header


class TestPlaybackControlWorkflow:
    """Integration tests for full playback control workflow."""

    @patch("src.tts.controller.msvcrt")
    def test_full_playback_lifecycle(self, mock_msvcrt, sample_audio_bytes):
        """Test complete workflow: start → pause → resume → quit."""
        # Mock audio playback with state
        audio_playback = Mock(spec=AudioPlayback)
        audio_playback.state = PlaybackState()
        audio_playback.play_audio = Mock(
            side_effect=lambda audio_bytes: setattr(audio_playback.state, "is_playing", True)
            or setattr(audio_playback.state, "is_paused", False)
        )
        audio_playback.pause = Mock(
            side_effect=lambda: setattr(audio_playback.state, "is_paused", True)
            or setattr(audio_playback.state, "is_playing", False)
        )
        audio_playback.resume = Mock(
            side_effect=lambda: setattr(audio_playback.state, "is_paused", False)
            or setattr(audio_playback.state, "is_playing", True)
        )
        audio_playback.stop = Mock()

        controller = PlaybackController(audio_playback)

        # Simulate keyboard inputs: spacebar (pause), spacebar (resume), Q (quit)
        mock_msvcrt.kbhit.side_effect = [
            True,
            True,
            True,
            False,  # Three key presses, then stop
        ]
        mock_msvcrt.getch.side_effect = [
            b" ",  # Pause
            b" ",  # Resume
            b"q",  # Quit
        ]

        # Start playback in a thread (since it's blocking)
        def run_playback():
            try:
                controller.start(sample_audio_bytes, ["Test chunk"])
            except Exception:
                pass  # Expected when we quit

        playback_thread = threading.Thread(target=run_playback, daemon=True)
        playback_thread.start()

        # Wait a bit for playback to start
        time.sleep(0.2)

        # Verify state transitions
        assert controller.state.is_playing is True or controller.state.is_paused is True

        # Wait for quit
        playback_thread.join(timeout=2)

    @patch("src.tts.controller.msvcrt")
    def test_seek_operations(self, mock_msvcrt, sample_audio_bytes):
        """Test seeking forward and backward."""
        audio_playback = Mock(spec=AudioPlayback)
        audio_playback.state = PlaybackState()
        audio_playback.seek = Mock()
        audio_playback.get_position = Mock(return_value=10000)  # 10 seconds

        controller = PlaybackController(audio_playback)
        controller.state.is_playing = True
        controller.state.current_position_ms = 10000

        # Seek forward
        controller.seek(5)
        audio_playback.seek.assert_called_with(15000)

        # Seek backward
        controller.state.current_position_ms = 20000
        controller.seek(-5)
        audio_playback.seek.assert_called_with(15000)

    @patch("src.tts.controller.msvcrt")
    def test_speed_adjustment_operations(self, mock_msvcrt, sample_audio_bytes, capsys):
        """Test that speed adjustment warns user it's not supported during playback."""
        audio_playback = Mock(spec=AudioPlayback)
        audio_playback.state = PlaybackState(is_playing=True)
        # Note: pygame.mixer doesn't support runtime speed control
        # Speed must be set before playback with --speed flag

        controller = PlaybackController(audio_playback)

        # Attempt to adjust speed during playback
        # Should warn user but not raise exception
        controller.adjust_speed(0.25)

        # Verify state hasn't changed (speed control not supported)
        assert controller.state.playback_speed == 1.0

        # Verify warning message was displayed
        captured = capsys.readouterr()
        assert "Speed control not available during playback" in captured.out
        assert "--speed flag" in captured.out

    def test_graceful_shutdown(self, sample_audio_bytes):
        """Test that quit provides clean shutdown."""
        audio_playback = Mock(spec=AudioPlayback)
        audio_playback.state = PlaybackState(is_playing=True)

        # Mock stop to update state like real implementation
        def stop_side_effect():
            audio_playback.state.is_playing = False
            audio_playback.state.is_paused = False

        audio_playback.stop = Mock(side_effect=stop_side_effect)

        controller = PlaybackController(audio_playback)

        # Quit should not raise exception
        controller.quit()

        # Verify shutdown event is set
        assert controller.shutdown_event.is_set()

        # Verify audio stopped
        audio_playback.stop.assert_called_once()

        # Verify state updated
        assert controller.state.is_playing is False

    @patch("src.tts.controller.msvcrt")
    def test_pause_resume_toggle(self, mock_msvcrt, sample_audio_bytes):
        """Test toggling between pause and resume with spacebar."""
        audio_playback = Mock(spec=AudioPlayback)
        audio_playback.state = PlaybackState(is_playing=True)

        # Mock pause to update state like real implementation
        def pause_side_effect():
            audio_playback.state.is_paused = True
            audio_playback.state.is_playing = False

        audio_playback.pause = Mock(side_effect=pause_side_effect)

        # Mock resume to update state like real implementation
        def resume_side_effect():
            audio_playback.state.is_paused = False
            audio_playback.state.is_playing = True

        audio_playback.resume = Mock(side_effect=resume_side_effect)

        controller = PlaybackController(audio_playback)

        # First spacebar: pause
        controller.pause()
        assert controller.state.is_paused is True
        assert controller.state.is_playing is False
        audio_playback.pause.assert_called_once()

        # Second spacebar: resume
        controller.resume()
        assert controller.state.is_playing is True
        assert controller.state.is_paused is False
        audio_playback.resume.assert_called_once()

    def test_state_consistency_during_operations(self, sample_audio_bytes):
        """Test that PlaybackState remains consistent during operations."""
        audio_playback = Mock(spec=AudioPlayback)
        audio_playback.state = PlaybackState()

        # Mock pause to update state like real implementation
        def pause_side_effect():
            audio_playback.state.is_paused = True
            audio_playback.state.is_playing = False

        audio_playback.pause = Mock(side_effect=pause_side_effect)

        # Mock resume to update state like real implementation
        def resume_side_effect():
            audio_playback.state.is_paused = False
            audio_playback.state.is_playing = True

        audio_playback.resume = Mock(side_effect=resume_side_effect)

        # Mock stop to update state like real implementation
        def stop_side_effect():
            audio_playback.state.is_playing = False
            audio_playback.state.is_paused = False

        audio_playback.stop = Mock(side_effect=stop_side_effect)

        controller = PlaybackController(audio_playback)

        # Initial state
        assert controller.state.is_playing is False
        assert controller.state.is_paused is False
        assert controller.state.playback_speed == 1.0
        assert controller.state.current_position_ms == 0

        # After starting (simulate by updating the shared state)
        audio_playback.state.is_playing = True
        assert controller.state.is_playing is True
        assert controller.state.is_paused is False

        # After pausing
        controller.pause()
        assert controller.state.is_playing is False
        assert controller.state.is_paused is True

        # After resuming
        controller.resume()
        assert controller.state.is_playing is True
        assert controller.state.is_paused is False

        # After quitting
        controller.quit()
        assert controller.state.is_playing is False
