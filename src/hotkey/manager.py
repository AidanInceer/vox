"""Global hotkey registration and management for vox voice input.

This module provides global hotkey registration using pynput, with support
for toggle state tracking (press to start, press again to stop).
"""

import logging
import threading
from typing import Callable, Optional

from pynput import keyboard

from src.utils.errors import (
    HotkeyAlreadyRegisteredError,
    HotkeyInvalidFormatError,
)

logger = logging.getLogger(__name__)


def parse_hotkey(hotkey_str: str) -> frozenset[keyboard.Key | keyboard.KeyCode]:
    """Parse a hotkey string into a set of pynput keys.

    Args:
        hotkey_str: Hotkey in format '<ctrl>+<alt>+space' or 'ctrl+alt+space'

    Returns:
        Frozen set of pynput Key/KeyCode objects

    Raises:
        HotkeyInvalidFormatError: If hotkey format is invalid
    """
    # Normalize the string: lowercase and handle angle brackets
    normalized = hotkey_str.lower().strip()

    # Split by + and process each part
    parts = [p.strip() for p in normalized.split("+") if p.strip()]

    if not parts:
        raise HotkeyInvalidFormatError(
            f"Empty hotkey string: '{hotkey_str}'",
            error_code="HOTKEY_EMPTY",
        )

    keys: set[keyboard.Key | keyboard.KeyCode] = set()

    for part in parts:
        # Remove angle brackets if present
        clean = part.strip("<>")

        # Map common names to pynput keys
        key = _parse_key_part(clean, hotkey_str)
        keys.add(key)

    return frozenset(keys)


def _parse_key_part(part: str, original: str) -> keyboard.Key | keyboard.KeyCode:
    """Parse a single key part into a pynput key.

    Args:
        part: Single key name (e.g., 'ctrl', 'space', 'a')
        original: Original hotkey string for error messages

    Returns:
        pynput Key or KeyCode

    Raises:
        HotkeyInvalidFormatError: If key name is unrecognized
    """
    # Modifier key mappings
    modifier_map = {
        "ctrl": keyboard.Key.ctrl_l,
        "ctrl_l": keyboard.Key.ctrl_l,
        "ctrl_r": keyboard.Key.ctrl_r,
        "control": keyboard.Key.ctrl_l,
        "alt": keyboard.Key.alt_l,
        "alt_l": keyboard.Key.alt_l,
        "alt_r": keyboard.Key.alt_r,
        "shift": keyboard.Key.shift_l,
        "shift_l": keyboard.Key.shift_l,
        "shift_r": keyboard.Key.shift_r,
        "cmd": keyboard.Key.cmd,
        "win": keyboard.Key.cmd,
        "super": keyboard.Key.cmd,
    }

    # Special key mappings
    special_map = {
        "space": keyboard.Key.space,
        "enter": keyboard.Key.enter,
        "return": keyboard.Key.enter,
        "tab": keyboard.Key.tab,
        "esc": keyboard.Key.esc,
        "escape": keyboard.Key.esc,
        "backspace": keyboard.Key.backspace,
        "delete": keyboard.Key.delete,
        "home": keyboard.Key.home,
        "end": keyboard.Key.end,
        "pageup": keyboard.Key.page_up,
        "page_up": keyboard.Key.page_up,
        "pagedown": keyboard.Key.page_down,
        "page_down": keyboard.Key.page_down,
        "up": keyboard.Key.up,
        "down": keyboard.Key.down,
        "left": keyboard.Key.left,
        "right": keyboard.Key.right,
        "f1": keyboard.Key.f1,
        "f2": keyboard.Key.f2,
        "f3": keyboard.Key.f3,
        "f4": keyboard.Key.f4,
        "f5": keyboard.Key.f5,
        "f6": keyboard.Key.f6,
        "f7": keyboard.Key.f7,
        "f8": keyboard.Key.f8,
        "f9": keyboard.Key.f9,
        "f10": keyboard.Key.f10,
        "f11": keyboard.Key.f11,
        "f12": keyboard.Key.f12,
    }

    # Check modifiers first
    if part in modifier_map:
        return modifier_map[part]

    # Check special keys
    if part in special_map:
        return special_map[part]

    # Single character key
    if len(part) == 1:
        return keyboard.KeyCode.from_char(part)

    # Unknown key
    raise HotkeyInvalidFormatError(
        f"Unknown key '{part}' in hotkey: '{original}'",
        error_code="HOTKEY_UNKNOWN_KEY",
        context={"key": part, "hotkey": original},
    )


class HotkeyManager:
    """Global hotkey registration and management using pynput.

    Provides global hotkey registration with support for modifier keys
    (Ctrl, Alt, Shift) and toggle state tracking. Hotkeys are registered
    as key combinations and callbacks are executed when all keys in the
    combination are pressed simultaneously.

    Thread Safety:
        Callbacks execute in the pynput listener thread, not the main thread.
        Use a queue or `root.after()` for GUI updates from callbacks.

    Attributes:
        is_listening: Whether the manager is currently listening for hotkeys.

    Example:
        >>> manager = HotkeyManager()
        >>> manager.register_hotkey('<ctrl>+<alt>+space', my_callback)
        >>> manager.start()
        >>> # ... hotkey is now active
        >>> manager.stop()
    """

    def __init__(self) -> None:
        """Initialize the hotkey manager.

        Creates an empty hotkey registry and prepares the keyboard listener.
        The listener is not started until `start()` is called.
        """
        self._hotkeys: dict[str, tuple[frozenset[keyboard.Key | keyboard.KeyCode], Callable[[], None]]] = {}
        self._listener: Optional[keyboard.Listener] = None
        self._pressed_keys: set[keyboard.Key | keyboard.KeyCode] = set()
        self._lock = threading.Lock()
        self._is_listening = False

        logger.debug("HotkeyManager initialized")

    def register_hotkey(self, hotkey: str, callback: Callable[[], None]) -> None:
        """Register a global hotkey.

        Args:
            hotkey: Hotkey string in pynput format (e.g., '<ctrl>+<alt>+space')
            callback: Function to call when hotkey is pressed (no args)

        Raises:
            HotkeyInvalidFormatError: If hotkey format is invalid
            HotkeyAlreadyRegisteredError: If hotkey already registered
        """
        # Normalize for storage
        normalized = hotkey.lower().strip()

        with self._lock:
            if normalized in self._hotkeys:
                raise HotkeyAlreadyRegisteredError(
                    f"Hotkey '{hotkey}' is already registered",
                    error_code="HOTKEY_ALREADY_REGISTERED",
                    context={"hotkey": hotkey},
                )

            # Parse the hotkey
            keys = parse_hotkey(hotkey)
            self._hotkeys[normalized] = (keys, callback)

            logger.info(f"Hotkey registered: {hotkey}")

    def unregister_hotkey(self, hotkey: str) -> None:
        """Unregister a previously registered hotkey.

        Args:
            hotkey: Hotkey string to unregister

        Raises:
            KeyError: If hotkey not registered
        """
        normalized = hotkey.lower().strip()

        with self._lock:
            if normalized not in self._hotkeys:
                raise KeyError(f"Hotkey '{hotkey}' is not registered")

            del self._hotkeys[normalized]
            logger.info(f"Hotkey unregistered: {hotkey}")

    def start(self) -> None:
        """Start listening for registered hotkeys.

        Begins the pynput keyboard listener in a background thread.
        Once started, all registered hotkey callbacks will be triggered
        when their key combinations are pressed.

        Raises:
            RuntimeError: If the manager is already listening.
        """
        with self._lock:
            if self._is_listening:
                raise RuntimeError("HotkeyManager is already listening")

            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.start()
            self._is_listening = True

            logger.info("Hotkey listener started")

    def stop(self) -> None:
        """Stop listening for hotkeys and release resources.

        Stops the pynput keyboard listener and clears the pressed keys state.
        Safe to call multiple times; subsequent calls are no-ops.
        """
        with self._lock:
            if self._listener is not None:
                self._listener.stop()
                self._listener = None
                self._is_listening = False
                self._pressed_keys.clear()

                logger.info("Hotkey listener stopped")

    @property
    def is_listening(self) -> bool:
        """Check if the manager is currently listening for hotkeys.

        Returns:
            True if the keyboard listener is active, False otherwise.
        """
        with self._lock:
            return self._is_listening

    def _normalize_key(self, key: keyboard.Key | keyboard.KeyCode | None) -> keyboard.Key | keyboard.KeyCode | None:
        """Normalize a key for comparison (handle left/right variants).

        Args:
            key: The key to normalize

        Returns:
            Normalized key for comparison
        """
        if key is None:
            return None

        # Map right variants to left variants for matching
        if key == keyboard.Key.ctrl_r:
            return keyboard.Key.ctrl_l
        if key == keyboard.Key.alt_r:
            return keyboard.Key.alt_l
        if key == keyboard.Key.shift_r:
            return keyboard.Key.shift_l

        return key

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        """Handle key press event.

        Args:
            key: The key that was pressed
        """
        if key is None:
            return

        normalized_key = self._normalize_key(key)
        if normalized_key is None:
            return

        with self._lock:
            self._pressed_keys.add(normalized_key)
            self._check_hotkeys()

    def _on_release(self, key: keyboard.Key | keyboard.KeyCode | None) -> None:
        """Handle key release event.

        Args:
            key: The key that was released
        """
        if key is None:
            return

        normalized_key = self._normalize_key(key)
        if normalized_key is None:
            return

        with self._lock:
            self._pressed_keys.discard(normalized_key)

    def _check_hotkeys(self) -> None:
        """Check if any registered hotkey combination is currently pressed."""
        for hotkey_str, (keys, callback) in self._hotkeys.items():
            # Normalize pressed keys for comparison
            normalized_pressed = {self._normalize_key(k) for k in self._pressed_keys}

            if keys <= normalized_pressed:
                logger.debug(f"Hotkey triggered: {hotkey_str}")
                # Execute callback in a separate thread to avoid blocking listener
                threading.Thread(target=callback, daemon=True).start()
                # Clear pressed keys to avoid repeated triggers
                self._pressed_keys.clear()
                return

    def get_registered_hotkeys(self) -> list[str]:
        """Get list of currently registered hotkey strings.

        Returns:
            List of normalized hotkey strings that are currently registered.
            Format matches registration (e.g., '<ctrl>+<alt>+space').
        """
        with self._lock:
            return list(self._hotkeys.keys())
