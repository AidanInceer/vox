"""Unit tests for HotkeyManager class.

Tests cover:
- Hotkey registration and unregistration
- Listener start/stop lifecycle
- Hotkey parsing and validation
"""

from unittest.mock import MagicMock, patch

import pytest

from src.hotkey.manager import HotkeyManager, parse_hotkey
from src.utils.errors import (
    HotkeyAlreadyRegisteredError,
    HotkeyInvalidFormatError,
)


class TestParseHotkey:
    """Tests for hotkey string parsing."""

    def test_parse_simple_hotkey(self) -> None:
        """parse_hotkey should parse simple hotkey combinations."""
        keys = parse_hotkey("<ctrl>+<alt>+space")
        # Should have 3 keys
        assert len(keys) == 3

    def test_parse_without_angle_brackets(self) -> None:
        """parse_hotkey should work without angle brackets."""
        keys = parse_hotkey("ctrl+alt+space")
        assert len(keys) == 3

    def test_parse_case_insensitive(self) -> None:
        """parse_hotkey should be case insensitive."""
        keys1 = parse_hotkey("CTRL+ALT+SPACE")
        keys2 = parse_hotkey("ctrl+alt+space")
        assert keys1 == keys2

    def test_parse_single_character_key(self) -> None:
        """parse_hotkey should handle single character keys."""
        keys = parse_hotkey("ctrl+a")
        assert len(keys) == 2

    def test_parse_function_key(self) -> None:
        """parse_hotkey should handle function keys."""
        keys = parse_hotkey("ctrl+f1")
        assert len(keys) == 2

    def test_parse_empty_string_raises(self) -> None:
        """parse_hotkey should raise HotkeyInvalidFormatError for empty string."""
        with pytest.raises(HotkeyInvalidFormatError):
            parse_hotkey("")

    def test_parse_invalid_key_raises(self) -> None:
        """parse_hotkey should raise HotkeyInvalidFormatError for unknown keys."""
        with pytest.raises(HotkeyInvalidFormatError):
            parse_hotkey("ctrl+invalidkey")

    def test_parse_whitespace_only_raises(self) -> None:
        """parse_hotkey should raise HotkeyInvalidFormatError for whitespace."""
        with pytest.raises(HotkeyInvalidFormatError):
            parse_hotkey("   ")


class TestHotkeyManagerRegistration:
    """Tests for hotkey registration functionality."""

    def test_register_hotkey_stores_callback(self) -> None:
        """register_hotkey should store the callback for the hotkey."""
        manager = HotkeyManager()
        callback = MagicMock()

        manager.register_hotkey("<ctrl>+<alt>+space", callback)

        assert "<ctrl>+<alt>+space" in manager.get_registered_hotkeys()

    def test_register_hotkey_normalizes_format(self) -> None:
        """register_hotkey should normalize hotkey string."""
        manager = HotkeyManager()
        callback = MagicMock()

        manager.register_hotkey("CTRL+ALT+SPACE", callback)

        # Should be stored as lowercase
        assert "ctrl+alt+space" in manager.get_registered_hotkeys()

    def test_register_hotkey_raises_on_invalid_format(self) -> None:
        """register_hotkey should raise HotkeyInvalidFormatError for invalid format."""
        manager = HotkeyManager()
        callback = MagicMock()

        with pytest.raises(HotkeyInvalidFormatError):
            manager.register_hotkey("ctrl+unknownkey", callback)

    def test_register_hotkey_raises_on_duplicate(self) -> None:
        """register_hotkey should raise HotkeyAlreadyRegisteredError for duplicates."""
        manager = HotkeyManager()
        callback = MagicMock()

        manager.register_hotkey("<ctrl>+<alt>+space", callback)

        with pytest.raises(HotkeyAlreadyRegisteredError):
            manager.register_hotkey("<ctrl>+<alt>+space", callback)

    def test_unregister_hotkey_removes_callback(self) -> None:
        """unregister_hotkey should remove the callback."""
        manager = HotkeyManager()
        callback = MagicMock()

        manager.register_hotkey("<ctrl>+<alt>+space", callback)
        manager.unregister_hotkey("<ctrl>+<alt>+space")

        assert "<ctrl>+<alt>+space" not in manager.get_registered_hotkeys()

    def test_unregister_hotkey_raises_on_unknown(self) -> None:
        """unregister_hotkey should raise KeyError for unknown hotkey."""
        manager = HotkeyManager()

        with pytest.raises(KeyError):
            manager.unregister_hotkey("<ctrl>+<alt>+space")

    def test_can_reregister_after_unregister(self) -> None:
        """Should be able to register same hotkey after unregistering."""
        manager = HotkeyManager()
        callback = MagicMock()

        manager.register_hotkey("<ctrl>+<alt>+space", callback)
        manager.unregister_hotkey("<ctrl>+<alt>+space")
        manager.register_hotkey("<ctrl>+<alt>+space", callback)

        assert "<ctrl>+<alt>+space" in manager.get_registered_hotkeys()


class TestHotkeyManagerLifecycle:
    """Tests for listener start/stop lifecycle."""

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_start_creates_listener(self, mock_listener_class: MagicMock) -> None:
        """start should create and start a keyboard listener."""
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener

        manager = HotkeyManager()
        manager.start()

        mock_listener_class.assert_called_once()
        mock_listener.start.assert_called_once()

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_start_sets_is_listening(self, mock_listener_class: MagicMock) -> None:
        """start should set is_listening to True."""
        manager = HotkeyManager()

        assert not manager.is_listening

        manager.start()

        assert manager.is_listening

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_start_raises_when_already_listening(self, mock_listener_class: MagicMock) -> None:
        """start should raise RuntimeError if already listening."""
        manager = HotkeyManager()
        manager.start()

        with pytest.raises(RuntimeError):
            manager.start()

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_stop_stops_listener(self, mock_listener_class: MagicMock) -> None:
        """stop should stop the keyboard listener."""
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener

        manager = HotkeyManager()
        manager.start()
        manager.stop()

        mock_listener.stop.assert_called_once()

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_stop_clears_is_listening(self, mock_listener_class: MagicMock) -> None:
        """stop should set is_listening to False."""
        manager = HotkeyManager()
        manager.start()

        assert manager.is_listening

        manager.stop()

        assert not manager.is_listening

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_stop_is_safe_to_call_multiple_times(self, mock_listener_class: MagicMock) -> None:
        """stop should be safe to call multiple times."""
        manager = HotkeyManager()
        manager.start()

        manager.stop()
        manager.stop()  # Should not raise

    def test_stop_is_safe_when_not_started(self) -> None:
        """stop should be safe to call when not started."""
        manager = HotkeyManager()
        manager.stop()  # Should not raise


class TestHotkeyManagerCallback:
    """Tests for hotkey callback triggering."""

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_callback_invoked_when_hotkey_pressed(self, mock_listener_class: MagicMock) -> None:
        """Callback should be invoked when hotkey combination is pressed."""
        from pynput import keyboard

        manager = HotkeyManager()
        callback = MagicMock()
        manager.register_hotkey("ctrl+a", callback)

        # Capture the on_press callback
        manager.start()
        on_press = mock_listener_class.call_args[1]["on_press"]

        # Simulate pressing ctrl
        on_press(keyboard.Key.ctrl_l)
        callback.assert_not_called()

        # Simulate pressing 'a' while ctrl is held
        on_press(keyboard.KeyCode.from_char("a"))

        # Give thread time to execute callback
        import time

        time.sleep(0.1)

        callback.assert_called_once()

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_callback_not_invoked_for_partial_match(self, mock_listener_class: MagicMock) -> None:
        """Callback should not be invoked for partial hotkey match."""
        from pynput import keyboard

        manager = HotkeyManager()
        callback = MagicMock()
        manager.register_hotkey("ctrl+alt+a", callback)

        manager.start()
        on_press = mock_listener_class.call_args[1]["on_press"]

        # Only press ctrl+a (missing alt)
        on_press(keyboard.Key.ctrl_l)
        on_press(keyboard.KeyCode.from_char("a"))

        import time

        time.sleep(0.1)

        callback.assert_not_called()

    @patch("src.hotkey.manager.keyboard.Listener")
    def test_key_release_clears_pressed_keys(self, mock_listener_class: MagicMock) -> None:
        """Key release should clear the key from pressed set."""
        from pynput import keyboard

        manager = HotkeyManager()
        callback = MagicMock()
        manager.register_hotkey("ctrl+a", callback)

        manager.start()
        on_press = mock_listener_class.call_args[1]["on_press"]
        on_release = mock_listener_class.call_args[1]["on_release"]

        # Press ctrl
        on_press(keyboard.Key.ctrl_l)
        # Release ctrl
        on_release(keyboard.Key.ctrl_l)
        # Press 'a' after ctrl released (should not trigger)
        on_press(keyboard.KeyCode.from_char("a"))

        import time

        time.sleep(0.1)

        callback.assert_not_called()


class TestHotkeyManagerGetRegisteredHotkeys:
    """Tests for get_registered_hotkeys method."""

    def test_returns_empty_list_initially(self) -> None:
        """get_registered_hotkeys should return empty list initially."""
        manager = HotkeyManager()
        assert manager.get_registered_hotkeys() == []

    def test_returns_registered_hotkeys(self) -> None:
        """get_registered_hotkeys should return all registered hotkeys."""
        manager = HotkeyManager()
        manager.register_hotkey("ctrl+a", MagicMock())
        manager.register_hotkey("ctrl+b", MagicMock())

        hotkeys = manager.get_registered_hotkeys()

        assert "ctrl+a" in hotkeys
        assert "ctrl+b" in hotkeys
        assert len(hotkeys) == 2
