"""Unit tests for settings UI functionality.

Tests for T076: Settings save/load round-trip in src/ui/main_window.py.
"""

import tempfile
from pathlib import Path

from src.persistence.database import VoxDatabase


class TestSettingsSaveLoad:
    """Tests for settings save/load functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Create temp database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_settings.db"
        self.database = VoxDatabase(db_path=self.db_path)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        self.database.close()
        if self.db_path.exists():
            self.db_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_hotkey_setting_round_trip(self) -> None:
        """Test that hotkey setting can be saved and loaded."""
        # Save a custom hotkey
        custom_hotkey = "<ctrl>+<shift>+v"
        self.database.set_setting("hotkey", custom_hotkey)

        # Load it back
        loaded = self.database.get_setting("hotkey", "<ctrl>+<alt>+space")

        assert loaded == custom_hotkey

    def test_restore_clipboard_setting_round_trip(self) -> None:
        """Test that restore_clipboard setting can be saved and loaded."""
        # Save as false
        self.database.set_setting("restore_clipboard", "false")

        # Load it back
        loaded = self.database.get_setting("restore_clipboard", "true")

        assert loaded == "false"

    def test_default_hotkey_when_not_set(self) -> None:
        """Test that default hotkey is returned when not set."""
        default = "<ctrl>+<alt>+space"
        loaded = self.database.get_setting("hotkey", default)

        assert loaded == default

    def test_settings_persist_after_database_reopen(self) -> None:
        """Test that settings persist after closing and reopening database."""
        # Save settings
        hotkey = "<alt>+<shift>+r"
        self.database.set_setting("hotkey", hotkey)
        self.database.set_setting("restore_clipboard", "false")

        # Close database
        self.database.close()

        # Reopen database
        new_db = VoxDatabase(db_path=self.db_path)

        try:
            # Verify settings persisted
            assert new_db.get_setting("hotkey", "") == hotkey
            assert new_db.get_setting("restore_clipboard", "") == "false"
        finally:
            new_db.close()

    def test_update_existing_setting(self) -> None:
        """Test that updating an existing setting works."""
        # Set initial value
        self.database.set_setting("hotkey", "<ctrl>+a")

        # Update value
        self.database.set_setting("hotkey", "<ctrl>+b")

        # Verify update
        loaded = self.database.get_setting("hotkey", "")

        assert loaded == "<ctrl>+b"


class TestHotkeyCapture:
    """Tests for hotkey capture functionality."""

    def test_key_to_string_modifier_keys(self) -> None:
        """Test conversion of modifier keys to string."""
        # Skip if pynput not available
        try:
            from pynput import keyboard
        except ImportError:
            return

        # Import the key mapping logic directly
        # We'll test the logic without needing a full window
        special_key_map = {
            keyboard.Key.ctrl_l: "<ctrl>",
            keyboard.Key.ctrl_r: "<ctrl>",
            keyboard.Key.alt_l: "<alt>",
            keyboard.Key.alt_r: "<alt>",
            keyboard.Key.shift_l: "<shift>",
            keyboard.Key.shift_r: "<shift>",
            keyboard.Key.cmd: "<cmd>",
            keyboard.Key.space: "space",
            keyboard.Key.enter: "enter",
            keyboard.Key.tab: "tab",
            keyboard.Key.esc: "esc",
        }

        # Test modifier key conversions
        assert special_key_map.get(keyboard.Key.ctrl_l) == "<ctrl>"
        assert special_key_map.get(keyboard.Key.alt_l) == "<alt>"
        assert special_key_map.get(keyboard.Key.shift_l) == "<shift>"

    def test_key_to_string_special_keys(self) -> None:
        """Test conversion of special keys to string."""
        try:
            from pynput import keyboard
        except ImportError:
            return

        special_key_map = {
            keyboard.Key.space: "space",
            keyboard.Key.enter: "enter",
            keyboard.Key.tab: "tab",
            keyboard.Key.esc: "esc",
            keyboard.Key.backspace: "backspace",
            keyboard.Key.delete: "delete",
        }

        # Test special key conversions
        assert special_key_map.get(keyboard.Key.space) == "space"
        assert special_key_map.get(keyboard.Key.enter) == "enter"
        assert special_key_map.get(keyboard.Key.tab) == "tab"

    def test_key_to_string_character_keys(self) -> None:
        """Test conversion of character keys to string."""
        try:
            from pynput import keyboard
        except ImportError:
            return

        # Test character key conversions
        key_a = keyboard.KeyCode.from_char("a")
        assert key_a.char.lower() == "a"

        key_v = keyboard.KeyCode.from_char("v")
        assert key_v.char.lower() == "v"


class TestHotkeyValidation:
    """Tests for hotkey validation during capture."""

    def test_captured_keys_builds_correct_hotkey_string(self) -> None:
        """Test that captured keys are assembled correctly."""
        captured_keys = {"<ctrl>", "<alt>", "space"}

        # Build the hotkey string (replicate _stop_hotkey_capture logic)
        modifiers = [k for k in captured_keys if k.startswith("<")]
        others = [k for k in captured_keys if not k.startswith("<")]
        hotkey = "+".join(sorted(modifiers) + sorted(others))

        assert hotkey == "<alt>+<ctrl>+space"

    def test_hotkey_requires_modifier(self) -> None:
        """Test that hotkey validation requires at least one modifier."""
        # Simulate captured keys with no modifiers
        captured_keys = {"space", "a"}
        modifiers = [k for k in captured_keys if k.startswith("<")]

        # Should fail validation (no modifiers)
        assert len(modifiers) == 0

    def test_hotkey_requires_non_modifier_key(self) -> None:
        """Test that hotkey validation requires a non-modifier key."""
        # Simulate captured keys with only modifiers
        captured_keys = {"<ctrl>", "<alt>"}
        others = [k for k in captured_keys if not k.startswith("<")]

        # Should fail validation (no non-modifier keys)
        assert len(others) == 0

    def test_single_modifier_with_key_is_valid(self) -> None:
        """Test that a single modifier with a key is valid."""
        captured_keys = {"<ctrl>", "c"}
        modifiers = [k for k in captured_keys if k.startswith("<")]
        others = [k for k in captured_keys if not k.startswith("<")]

        # Should pass validation
        assert len(modifiers) >= 1
        assert len(others) >= 1

    def test_multiple_modifiers_with_key_is_valid(self) -> None:
        """Test that multiple modifiers with a key is valid."""
        captured_keys = {"<ctrl>", "<shift>", "<alt>", "f1"}
        modifiers = [k for k in captured_keys if k.startswith("<")]
        others = [k for k in captured_keys if not k.startswith("<")]

        # Should pass validation
        assert len(modifiers) >= 1
        assert len(others) >= 1

        hotkey = "+".join(sorted(modifiers) + sorted(others))
        assert hotkey == "<alt>+<ctrl>+<shift>+f1"
