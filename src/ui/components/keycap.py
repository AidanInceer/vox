"""KeyCapLabel component for visual hotkey display.

This module provides a visual key cap representation for displaying
keyboard shortcuts in a style similar to Windows 11 key indicators.
"""

from __future__ import annotations

import re
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT

from src.ui.styles import FONTS

__all__ = ["KeyCapLabel"]


class KeyCapLabel(ttk.Frame):
    """Visual key cap representation for hotkey display.

    Displays hotkey combinations in a visual key cap style,
    similar to how keyboard shortcuts appear in Windows 11.

    Example:
        >>> keycap = KeyCapLabel(parent)
        >>> keycap.set_hotkey("<ctrl>+<alt>+space")
        # Displays: [Ctrl] + [Alt] + [Space]
    """

    # Key name mappings for display
    KEY_DISPLAY_MAP = {
        "ctrl": "Ctrl",
        "alt": "Alt",
        "shift": "Shift",
        "space": "Space",
        "enter": "Enter",
        "return": "Enter",
        "tab": "Tab",
        "escape": "Esc",
        "esc": "Esc",
        "backspace": "⌫",
        "delete": "Del",
        "up": "↑",
        "down": "↓",
        "left": "←",
        "right": "→",
    }

    def __init__(
        self,
        parent: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the key cap label.

        Args:
            parent: Parent widget
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        self._hotkey = ""
        self._key_labels: list[ttk.Label] = []

    def set_hotkey(self, hotkey: str) -> None:
        """Set the hotkey to display.

        Args:
            hotkey: Hotkey string (e.g., "<ctrl>+<alt>+space")
        """
        self._hotkey = hotkey
        self._build_keycaps()

    def _build_keycaps(self) -> None:
        """Build the visual keycap display."""
        # Clear existing labels
        for label in self._key_labels:
            label.destroy()
        self._key_labels.clear()

        if not self._hotkey:
            return

        # Parse hotkey string
        keys = self._parse_hotkey(self._hotkey)

        for i, key in enumerate(keys):
            if i > 0:
                # Add "+" separator
                sep = ttk.Label(
                    self,
                    text=" + ",
                    font=FONTS["mono"],
                )
                sep.pack(side=LEFT)
                self._key_labels.append(sep)

            # Create keycap-style label
            display_text = self._get_display_text(key)
            keycap = ttk.Label(
                self,
                text=f" {display_text} ",
                font=FONTS["mono"],
                bootstyle="info",  # type: ignore[arg-type]
                borderwidth=1,
                relief="raised",
            )
            keycap.pack(side=LEFT, padx=1)
            self._key_labels.append(keycap)

    def _parse_hotkey(self, hotkey: str) -> list[str]:
        """Parse hotkey string into individual keys.

        Args:
            hotkey: Hotkey string (e.g., "<ctrl>+<alt>+space")

        Returns:
            List of key names
        """
        # Extract keys from angle brackets and standalone words
        pattern = r"<([^>]+)>|([a-zA-Z0-9]+)"
        matches = re.findall(pattern, hotkey)
        keys = []
        for match in matches:
            key = match[0] if match[0] else match[1]
            if key:
                keys.append(key.lower())
        return keys

    def _get_display_text(self, key: str) -> str:
        """Get display text for a key.

        Args:
            key: Key name (lowercase)

        Returns:
            Display-friendly key name
        """
        key_lower = key.lower()
        if key_lower in self.KEY_DISPLAY_MAP:
            return self.KEY_DISPLAY_MAP[key_lower]
        # Capitalize single letters/numbers
        if len(key) == 1:
            return key.upper()
        return key.capitalize()
