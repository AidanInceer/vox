"""ThemeToggle component for light/dark theme switching.

This module provides a toggle control for switching between light
and dark themes with sun/moon icons.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, X

from src.ui.styles import FONTS, ICONS, SPACING

__all__ = ["ThemeToggle"]


class ThemeToggle(ttk.Frame):
    """Light/Dark theme toggle switch with icons.

    A toggle control for switching between light and dark themes,
    displaying sun/moon icons and triggering theme switch callback.

    Example:
        >>> toggle = ThemeToggle(parent, on_change=switch_theme)
        >>> toggle.set_theme("dark")
    """

    def __init__(
        self,
        parent: Any,
        on_change: Callable[[str], None],
        **kwargs: Any,
    ) -> None:
        """Initialize the theme toggle.

        Args:
            parent: Parent widget
            on_change: Callback when theme changes, receives "light" or "dark"
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        self._on_change = on_change
        self._current_theme = "light"
        self._toggle_var = ttk.BooleanVar(value=False)  # False = light, True = dark

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the toggle UI."""
        # Container row
        row = ttk.Frame(self)
        row.pack(fill=X, pady=SPACING["sm"])

        # Light icon
        light_label = ttk.Label(
            row,
            text=ICONS["theme_light"],
            font=FONTS["body"],
        )
        light_label.pack(side=LEFT, padx=(0, SPACING["sm"]))

        # Toggle switch
        self._toggle = ttk.Checkbutton(
            row,
            variable=self._toggle_var,
            command=self._on_toggle_change,
            bootstyle="round-toggle",  # type: ignore[arg-type]
        )
        self._toggle.pack(side=LEFT, padx=SPACING["sm"])

        # Dark icon
        dark_label = ttk.Label(
            row,
            text=ICONS["theme_dark"],
            font=FONTS["body"],
        )
        dark_label.pack(side=LEFT, padx=(SPACING["sm"], 0))

        # Theme label
        self._theme_label = ttk.Label(
            self,
            text="Light theme",
            font=FONTS["caption"],
        )
        self._theme_label.pack(anchor="w", pady=(SPACING["xs"], 0))

    def _on_toggle_change(self) -> None:
        """Handle toggle state change."""
        is_dark = self._toggle_var.get()
        self._current_theme = "dark" if is_dark else "light"
        self._theme_label.configure(text="Dark theme" if is_dark else "Light theme")
        self._on_change(self._current_theme)

    def get_theme(self) -> str:
        """Get the current theme selection."""
        return self._current_theme

    def set_theme(self, theme: str) -> None:
        """Set the toggle to a specific theme.

        Args:
            theme: "light" or "dark"
        """
        if theme in ("light", "dark"):
            self._current_theme = theme
            is_dark = theme == "dark"
            self._toggle_var.set(is_dark)
            self._theme_label.configure(text="Dark theme" if is_dark else "Light theme")
