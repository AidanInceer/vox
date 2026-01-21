"""Theme configuration for the Vox desktop application.

This module provides ttkbootstrap theme configuration and style constants
for consistent visual appearance across all UI components.
"""

import logging
from typing import Final

import ttkbootstrap as ttk

logger = logging.getLogger(__name__)

# Theme configuration
THEME_NAME: Final[str] = "darkly"  # Modern dark theme

# Color palette (aligned with ttkbootstrap darkly theme)
COLORS: Final[dict[str, str]] = {
    "primary": "#375a7f",  # Blue-gray
    "secondary": "#444444",  # Dark gray
    "success": "#00bc8c",  # Green
    "info": "#3498db",  # Light blue
    "warning": "#f39c12",  # Orange
    "danger": "#e74c3c",  # Red
    "background": "#222222",  # Dark background
    "foreground": "#ffffff",  # White text
    "muted": "#888888",  # Muted gray text
}

# Font configuration
FONTS: Final[dict[str, tuple[str, int]]] = {
    "heading": ("Segoe UI", 14),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10),
}

# Spacing constants (pixels)
PADDING: Final[dict[str, int]] = {
    "small": 5,
    "medium": 10,
    "large": 15,
    "xlarge": 20,
}

# Window dimensions
WINDOW_SIZE: Final[dict[str, int]] = {
    "width": 600,
    "height": 500,
    "min_width": 400,
    "min_height": 350,
}


def create_themed_window(title: str = "Vox") -> ttk.Window:
    """Create a new themed ttkbootstrap window.

    Args:
        title: Window title

    Returns:
        Configured ttkbootstrap Window instance
    """
    window = ttk.Window(
        title=title,
        themename=THEME_NAME,
        size=(WINDOW_SIZE["width"], WINDOW_SIZE["height"]),
        minsize=(WINDOW_SIZE["min_width"], WINDOW_SIZE["min_height"]),
    )

    # Center window on screen
    window.place_window_center()

    logger.debug(f"Created themed window: {title}")
    return window


def configure_styles(style: ttk.Style) -> None:
    """Configure custom styles for the application.

    Args:
        style: ttkbootstrap Style instance to configure
    """
    # Custom style for history list items
    style.configure(
        "History.TFrame",
        background=COLORS["background"],
    )

    # Custom style for section headers
    style.configure(
        "Header.TLabel",
        font=FONTS["heading"],
        foreground=COLORS["foreground"],
    )

    # Custom style for muted/secondary text
    style.configure(
        "Muted.TLabel",
        font=FONTS["small"],
        foreground=COLORS["muted"],
    )

    # Custom style for monospace text (hotkey display)
    style.configure(
        "Mono.TLabel",
        font=FONTS["mono"],
        foreground=COLORS["info"],
    )

    logger.debug("Custom styles configured")
