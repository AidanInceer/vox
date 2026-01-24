"""User interface module for the desktop application.

This module provides the visual components including the main window,
settings panel, history view, and recording indicator overlay.

Note: Main exports are done via explicit imports to avoid circular dependency issues.
Use: from src.ui.indicator import RecordingIndicator
Use: from src.ui.main_window import VoxMainWindow
"""

from src.ui.components import (
    EmptyState,
    FluentCard,
    HistoryItemCard,
    KeyCapLabel,
    ModelSlider,
    SpeedSlider,
    ThemeToggle,
)
from src.ui.styles import (
    COLORS,
    COLORS_DARK,
    COLORS_LIGHT,
    FONTS,
    ICONS,
    PADDING,
    SPACING,
    THEME_NAME,
    WINDOW_SIZE,
    configure_styles,
    create_themed_window,
    switch_theme,
)

__all__ = [
    # Style constants
    "COLORS",
    "COLORS_DARK",
    "COLORS_LIGHT",
    "FONTS",
    "ICONS",
    "PADDING",
    "SPACING",
    "THEME_NAME",
    "WINDOW_SIZE",
    # Style functions
    "configure_styles",
    "create_themed_window",
    "switch_theme",
    # Components
    "EmptyState",
    "FluentCard",
    "HistoryItemCard",
    "KeyCapLabel",
    "ModelSlider",
    "SpeedSlider",
    "ThemeToggle",
]
