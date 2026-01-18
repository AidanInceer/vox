"""Unit tests for PlaybackController class."""

import threading
import time
from queue import Queue
from unittest.mock import Mock, MagicMock, patch

import pytest

from src.tts.controller import PlaybackController
from src.tts.playback import AudioPlayback, PlaybackState


@pytest.fixture
def mock_audio_playback():
    """Create a mock AudioPlayback instance with state simulation."""
    playback = Mock(spec=AudioPlayback)
    playback.state = PlaybackState()
    
    # Make pause() update state like real implementation
    def pause_side_effect():
        playback.state.is_paused = True
        playback.state.is_playing = False
    playback.pause.side_effect = pause_side_effect
    
    # Make resume() update state like real implementation
    def resume_side_effect():
        playback.state.is_paused = False
        playback.state.is_playing = True
    playback.resume.side_effect = resume_side_effect
    
    # Make stop() update state like real implementation
    def stop_side_effect():
        playback.state.is_playing = False
        playback.state.is_paused = False
    playback.stop.side_effect = stop_side_effect
    
    # Make get_position() return current position from state
    def get_position_side_effect():
        return playback.state.current_position_ms
    playback.get_position.side_effect = get_position_side_effect
    
    # Make seek() update state
    def seek_side_effect(pos):
        playback.state.current_position_ms = pos
    playback.seek.side_effect = seek_side_effect
    
    # Make set_speed() update state
    def set_speed_side_effect(speed):
        playback.state.playback_speed = speed
    playback.set_speed.side_effect = set_speed_side_effect
    
    return playback


@pytest.fixture
def controller(mock_audio_playback):
    """Create a PlaybackController with mocked audio playback."""
    return PlaybackController(mock_audio_playback)


class TestPlaybackControllerInit:
    """Tests for PlaybackController.__init__()"""

    def test_init_creates_controller(self, mock_audio_playback):
        """Test that __init__ creates controller with required attributes."""
        controller = PlaybackController(mock_audio_playback)
        
        assert controller.audio_playback == mock_audio_playback
        assert isinstance(controller.state, PlaybackState)
        assert isinstance(controller.command_queue, Queue)
        assert isinstance(controller.shutdown_event, threading.Event)
        assert not controller.shutdown_event.is_set()

    def test_init_sets_initial_state(self, controller):
        """Test that initial PlaybackState is correct."""
        assert controller.state.is_playing is False
        assert controller.state.is_paused is False
        assert controller.state.current_position_ms == 0
        assert controller.state.playback_speed == 1.0


class TestPlaybackControllerPause:
    """Tests for PlaybackController.pause()"""

    def test_pause_sets_state(self, controller, mock_audio_playback):
        """Test that pause() updates state correctly."""
        # Set up playing state
        controller.state.is_playing = True
        controller.state.is_paused = False
        
        controller.pause()
        
        assert controller.state.is_paused is True
        assert controller.state.is_playing is False
        mock_audio_playback.pause.assert_called_once()

    def test_pause_calls_audio_playback(self, controller, mock_audio_playback):
        """Test that pause() calls AudioPlayback.pause()."""
        controller.state.is_playing = True
        
        controller.pause()
        
        mock_audio_playback.pause.assert_called_once()

    def test_pause_when_not_playing_raises_error(self, controller):
        """Test that pause() raises error when not playing."""
        controller.state.is_playing = False
        
        with pytest.raises(RuntimeError, match="Cannot pause: not playing"):
            controller.pause()

    def test_pause_is_idempotent(self, controller, mock_audio_playback):
        """Test that second pause() call raises error since already paused."""
        controller.state.is_playing = True
        
        controller.pause()
        # After pause, is_playing is False, so another pause should raise error
        with pytest.raises(RuntimeError, match="Cannot pause: not playing"):
            controller.pause()


class TestPlaybackControllerResume:
    """Tests for PlaybackController.resume()"""

    def test_resume_sets_state(self, controller, mock_audio_playback):
        """Test that resume() updates state correctly."""
        # Set up paused state
        controller.state.is_playing = False
        controller.state.is_paused = True
        
        controller.resume()
        
        assert controller.state.is_playing is True
        assert controller.state.is_paused is False
        mock_audio_playback.resume.assert_called_once()

    def test_resume_calls_audio_playback(self, controller, mock_audio_playback):
        """Test that resume() calls AudioPlayback.resume()."""
        controller.state.is_paused = True
        
        controller.resume()
        
        mock_audio_playback.resume.assert_called_once()

    def test_resume_when_not_paused_raises_error(self, controller):
        """Test that resume() raises error when not paused."""
        controller.state.is_paused = False
        
        with pytest.raises(RuntimeError, match="Cannot resume: not paused"):
            controller.resume()


class TestPlaybackControllerQuit:
    """Tests for PlaybackController.quit()"""

    def test_quit_sets_shutdown_event(self, controller):
        """Test that quit() sets shutdown event."""
        controller.quit()
        
        assert controller.shutdown_event.is_set()

    def test_quit_stops_playback(self, controller, mock_audio_playback):
        """Test that quit() stops audio playback."""
        controller.state.is_playing = True
        
        controller.quit()
        
        mock_audio_playback.stop.assert_called_once()
        assert controller.state.is_playing is False

    def test_quit_is_graceful(self, controller):
        """Test that quit() doesn't raise exceptions."""
        # Should not raise even if not playing
        controller.quit()
        
        # Should not raise on second call
        controller.quit()


class TestPlaybackControllerSeek:
    """Tests for PlaybackController.seek()"""

    def test_seek_forward_updates_position(self, controller, mock_audio_playback):
        """Test seeking forward updates position."""
        controller.state.is_playing = True
        controller.state.current_position_ms = 10000  # 10 seconds
        
        controller.seek(5)  # Seek forward 5 seconds
        
        expected_position = 15000  # 15 seconds
        mock_audio_playback.seek.assert_called_once_with(expected_position)

    def test_seek_backward_updates_position(self, controller, mock_audio_playback):
        """Test seeking backward updates position."""
        controller.state.is_playing = True
        controller.state.current_position_ms = 20000  # 20 seconds
        
        controller.seek(-10)  # Seek backward 10 seconds
        
        expected_position = 10000  # 10 seconds
        mock_audio_playback.seek.assert_called_once_with(expected_position)

    def test_seek_backward_beyond_start_clamps_to_zero(self, controller, mock_audio_playback):
        """Test seeking before start clamps to 0."""
        controller.state.is_playing = True
        controller.state.current_position_ms = 5000  # 5 seconds
        
        controller.seek(-10)  # Try to seek to -5 seconds
        
        mock_audio_playback.seek.assert_called_once_with(0)

    def test_seek_when_not_playing_raises_error(self, controller):
        """Test that seek() raises error when not playing."""
        controller.state.is_playing = False
        
        with pytest.raises(RuntimeError, match="Cannot seek: not playing"):
            controller.seek(10)


class TestPlaybackControllerAdjustSpeed:
    """Tests for PlaybackController.adjust_speed()"""

    def test_adjust_speed_displays_warning(self, controller, mock_audio_playback, capsys):
        """Test that adjust_speed displays a warning about lack of runtime support."""
        controller.state.is_playing = True
        controller.state.playback_speed = 1.0
        
        # Speed adjustment during playback is not supported
        controller.adjust_speed(0.25)
        
        # State should not change
        assert controller.state.playback_speed == 1.0
        
        # Should display warning message
        captured = capsys.readouterr()
        assert "Speed control not available during playback" in captured.out
        assert "--speed flag" in captured.out
        
        # set_speed should not be called
        mock_audio_playback.set_speed.assert_not_called()

    def test_adjust_speed_does_not_crash(self, controller, mock_audio_playback):
        """Test that adjust_speed does not crash or raise exception."""
        controller.state.is_playing = True
        controller.state.playback_speed = 1.5
        
        # Should not raise exception, just warn
        controller.adjust_speed(-0.25)
        
        # State unchanged
        assert controller.state.playback_speed == 1.5

    def test_adjust_speed_when_not_playing_raises_error(self, controller):
        """Test that adjust_speed() raises error when not playing."""
        controller.state.is_playing = False
        
        with pytest.raises(RuntimeError, match="Cannot adjust speed: not playing"):
            controller.adjust_speed(0.25)


class TestPlaybackControllerKeyboardProcessing:
    """Tests for keyboard command processing"""

    @patch('src.tts.controller.msvcrt')
    def test_keyboard_thread_processes_space_key(self, mock_msvcrt, controller):
        """Test keyboard thread processes spacebar for pause/resume."""
        # Mock kbhit to return True once, then False
        mock_msvcrt.kbhit.side_effect = [True, False]
        mock_msvcrt.getch.return_value = b' '  # Spacebar
        
        controller.state.is_playing = True
        
        # Start keyboard thread
        controller._keyboard_input_thread()
        
        # Command should be in queue
        assert not controller.command_queue.empty()
        command, arg = controller.command_queue.get()
        assert command == 'pause'  # When playing, spacebar triggers pause

    @patch('src.tts.controller.msvcrt')
    def test_keyboard_thread_processes_q_key(self, mock_msvcrt, controller):
        """Test keyboard thread processes Q key for quit."""
        mock_msvcrt.kbhit.side_effect = [True, False]
        mock_msvcrt.getch.return_value = b'q'
        
        controller._keyboard_input_thread()
        
        assert not controller.command_queue.empty()
        command, arg = controller.command_queue.get()
        assert command == 'quit'

    @patch('src.tts.controller.msvcrt')
    def test_keyboard_thread_processes_arrow_keys(self, mock_msvcrt, controller):
        """Test keyboard thread processes arrow keys."""
        # Arrow keys send two bytes: 0xe0 followed by direction code
        mock_msvcrt.kbhit.side_effect = [True, True, False]
        mock_msvcrt.getch.side_effect = [b'\xe0', b'M']  # Right arrow
        
        controller.state.is_playing = True
        controller._keyboard_input_thread()
        
        assert not controller.command_queue.empty()
        command, arg = controller.command_queue.get()
        assert command == 'seek'
        assert arg == 5  # SEEK_DELTA_SEC


class TestPlaybackControllerDebouncing:
    """Tests for debouncing rapid key presses"""

    @patch('src.tts.controller.msvcrt')
    def test_debouncing_prevents_rapid_commands(self, mock_msvcrt, controller):
        """Test that rapid key presses within debounce window are ignored."""
        import time
        
        # Mock rapid spacebar presses (3 presses within 50ms)
        mock_msvcrt.kbhit.side_effect = [True, True, True, False]
        mock_msvcrt.getch.side_effect = [b' ', b' ', b' ']
        
        controller.state.is_playing = True
        controller._last_key_time = 0
        
        # Start keyboard thread (this will process keys with debouncing)
        controller._keyboard_input_thread()
        
        # Only first and possibly last command should be in queue (debouncing)
        # With 100ms debounce, rapid presses should be filtered
        commands_received = []
        while not controller.command_queue.empty():
            commands_received.append(controller.command_queue.get())
        
        # Should have fewer commands than key presses due to debouncing
        assert len(commands_received) < 3
