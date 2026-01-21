"""User interface module for the desktop application.

This module provides the visual components including the main window,
settings panel, history view, and recording indicator overlay.

Note: Main exports are done via explicit imports to avoid circular dependency issues.
Use: from src.ui.indicator import RecordingIndicator
Use: from src.ui.main_window import VoxMainWindow
"""

from src.ui.styles import (
    COLORS,
    FONTS,
    PADDING,
    THEME_NAME,
    WINDOW_SIZE,
    configure_styles,
    create_themed_window,
)

__all__ = [
    "COLORS",
    "FONTS",
    "PADDING",
    "THEME_NAME",
    "WINDOW_SIZE",
    "configure_styles",
    "create_themed_window",
]
