"""Theme configuration for the Vox desktop application.

This module provides ttkbootstrap theme configuration and style constants
for consistent visual appearance across all UI components following
Windows 11 Fluent Design principles.
"""

import logging
from typing import Final

import ttkbootstrap as ttk

logger = logging.getLogger(__name__)

# Theme configuration - Fluent Design themes
THEMES: Final[dict[str, str]] = {
    "light": "cosmo",
    "dark": "darkly",
}

# Default theme for legacy compatibility
THEME_NAME: Final[str] = THEMES["light"]

# Font family - Windows 11 native look
FONT_FAMILY: Final[str] = "Segoe UI Variable"

# 8px grid spacing system (Fluent Design)
SPACING: Final[dict[str, int]] = {
    "xs": 4,  # Tight internal padding
    "sm": 8,  # Default internal padding
    "md": 16,  # Section margins
    "lg": 24,  # Card margins
    "xl": 32,  # Page margins
    "xxl": 48,  # Major section gaps
}

# Legacy padding (deprecated - use SPACING instead)
PADDING: Final[dict[str, int]] = {
    "small": SPACING["xs"],
    "medium": SPACING["sm"],
    "large": SPACING["md"],
    "xlarge": SPACING["lg"],
}

# Fluent type scale
FONTS: Final[dict[str, tuple[str, int, str]]] = {
    "display": (FONT_FAMILY, 28, "bold"),  # App title, hero text
    "title": (FONT_FAMILY, 20, "bold"),  # Section headers
    "subtitle": (FONT_FAMILY, 14, "bold"),  # Card headers
    "body": (FONT_FAMILY, 14, "normal"),  # Primary content
    "caption": (FONT_FAMILY, 12, "normal"),  # Helper text
    "mono": ("Cascadia Code", 12, "normal"),  # Hotkey display
}

# Unicode icons for Fluent Design
ICONS: Final[dict[str, str]] = {
    "status": "🏠",
    "settings": "⚙️",
    "history": "📋",
    "record": "🎤",
    "stop": "⏹️",
    "refresh": "🔄",
    "delete": "🗑️",
    "copy": "📄",
    "check": "✅",
    "warning": "⚠️",
    "error": "❌",
    "theme_light": "☀️",
    "theme_dark": "🌙",
    "faster": "⚡",
    "accurate": "🎯",
}

# Light theme color palette (Fluent Design)
# WCAG AA Contrast Ratios (minimum 4.5:1 for normal text, 3:1 for large text):
#   - foreground (#1a1a1a) on surface (#ffffff): 16.1:1 ✓
#   - foreground (#1a1a1a) on background (#f3f3f3): 13.5:1 ✓
#   - muted (#6e6e6e) on surface (#ffffff): 5.3:1 ✓
#   - primary (#0078d4) on surface (#ffffff): 4.5:1 ✓
#   - success (#107c10) on surface (#ffffff): 4.6:1 ✓
#   - danger (#d13438) on surface (#ffffff): 4.5:1 ✓
#   - warning_text (#8a6914) on surface (#ffffff): 4.6:1 ✓
#   - on_accent (#ffffff) on primary (#0078d4): 4.5:1 ✓
COLORS_LIGHT: Final[dict[str, str]] = {
    "primary": "#0078d4",  # Windows 11 accent blue
    "secondary": "#6c757d",  # Gray (secondary actions)
    "success": "#107c10",  # Green (success states)
    "info": "#0078d4",  # Blue (informational)
    "warning": "#8a6914",  # Dark gold (warnings) - WCAG AA compliant on white
    "danger": "#d13438",  # Red (errors, recording indicator)
    "background": "#f3f3f3",  # Light gray (main background)
    "surface": "#ffffff",  # White (cards, panels)
    "foreground": "#1a1a1a",  # Near black (primary text)
    "muted": "#6e6e6e",  # Gray (secondary text)
    "border": "#e1e1e1",  # Light border color
    "shadow": "#00000020",  # Shadow color with alpha
    "accent": "#0078d4",  # Accent color for focus
    "on_accent": "#ffffff",  # Text on accent color
    "disabled": "#a0a0a0",  # Disabled state foreground
    "disabled_bg": "#e8e8e8",  # Disabled state background
}

# Dark theme color palette (Fluent Design)
# WCAG AA Contrast Ratios (minimum 4.5:1 for normal text, 3:1 for large text):
#   - foreground (#ffffff) on surface (#2d2d2d): 12.6:1 ✓
#   - foreground (#ffffff) on background (#202020): 15.1:1 ✓
#   - muted (#a0a0a0) on surface (#2d2d2d): 6.3:1 ✓
#   - primary (#60cdff) on surface (#2d2d2d): 9.2:1 ✓
#   - success (#6ccb5f) on surface (#2d2d2d): 7.3:1 ✓
#   - danger (#ff6b6b) on surface (#2d2d2d): 6.4:1 ✓
#   - warning (#fce100) on surface (#2d2d2d): 12.1:1 ✓
#   - on_accent (#000000) on primary (#60cdff): 9.2:1 ✓
COLORS_DARK: Final[dict[str, str]] = {
    "primary": "#60cdff",  # Light blue for dark mode
    "secondary": "#9e9e9e",  # Gray (secondary actions)
    "success": "#6ccb5f",  # Light green
    "info": "#60cdff",  # Light blue
    "warning": "#fce100",  # Bright yellow
    "danger": "#ff6b6b",  # Light red
    "background": "#202020",  # Dark background
    "surface": "#2d2d2d",  # Elevated surface
    "foreground": "#ffffff",  # White text
    "muted": "#a0a0a0",  # Muted text
    "border": "#404040",  # Dark border
    "shadow": "#00000040",  # Darker shadow
    "accent": "#60cdff",  # Accent color
    "on_accent": "#000000",  # Text on accent
    "disabled": "#6e6e6e",  # Disabled state foreground
    "disabled_bg": "#3a3a3a",  # Disabled state background
}

# Legacy COLORS for backward compatibility (defaults to light)
COLORS: Final[dict[str, str]] = COLORS_LIGHT

# Window dimensions
WINDOW_SIZE: Final[dict[str, int]] = {
    "width": 600,
    "height": 500,
    "min_width": 400,
    "min_height": 350,
}

# Current theme state (mutable)
_current_theme: str = "light"


def get_colors(theme: str = "light") -> dict[str, str]:
    """Get color palette for specified theme.

    Args:
        theme: "light" or "dark"

    Returns:
        Dictionary of color name to hex value
    """
    return COLORS_DARK if theme == "dark" else COLORS_LIGHT


def get_current_theme() -> str:
    """Get the current theme name.

    Returns:
        "light" or "dark"
    """
    return _current_theme


def switch_theme(root: ttk.Window, theme: str) -> None:
    """Switch the application theme at runtime.

    Args:
        root: Main window instance
        theme: "light" or "dark"
    """
    global _current_theme

    if theme not in THEMES:
        logger.warning(f"Invalid theme '{theme}', defaulting to 'light'")
        theme = "light"

    _current_theme = theme
    theme_name = THEMES[theme]

    # Switch ttkbootstrap theme
    root.style.theme_use(theme_name)

    # Apply Fluent style overrides for the new theme
    configure_fluent_overrides(root.style, theme)

    logger.info(f"Switched to {theme} theme ({theme_name})")


def configure_fluent_overrides(style: ttk.Style, theme: str = "light") -> None:
    """Configure Fluent Design style overrides.

    Sets up custom styles for:
    - Tabs with rounded indicators and hover/focus states
    - Buttons with rounded corners
    - Cards with elevated appearance
    - Focus indicators for accessibility

    Args:
        style: ttkbootstrap Style instance
        theme: "light" or "dark" theme name
    """
    colors = get_colors(theme)

    # Tab styling - rounded pill selection indicator with hover/focus states
    style.configure(
        "TNotebook",
        tabmargins=[SPACING["xs"], SPACING["xs"], SPACING["xs"], 0],
    )

    style.configure(
        "TNotebook.Tab",
        padding=[SPACING["md"], SPACING["sm"]],
        font=(FONT_FAMILY, 11, "normal"),
        focuscolor=colors["accent"],
    )

    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", colors["surface"]),
            ("active", colors["border"]),  # Hover state
            ("!selected", colors["background"]),
        ],
        foreground=[
            ("selected", colors["primary"]),
            ("active", colors["foreground"]),  # Hover state
            ("!selected", colors["muted"]),
        ],
        padding=[
            ("selected", [SPACING["md"], SPACING["sm"]]),
            ("active", [SPACING["md"], SPACING["sm"]]),  # Pressed state
        ],
    )

    # Button styling - rounded corners, focus states
    style.configure(
        "TButton",
        padding=[SPACING["md"], SPACING["sm"]],
        font=(FONT_FAMILY, 11, "normal"),
        focuscolor=colors["accent"],
    )

    style.map(
        "TButton",
        background=[
            ("active", colors["primary"]),
            ("pressed", colors["accent"]),
        ],
    )

    # Primary accent button style
    style.configure(
        "Accent.TButton",
        background=colors["primary"],
        foreground=colors["on_accent"],
        padding=[SPACING["lg"], SPACING["md"]],
        font=(FONT_FAMILY, 12, "bold"),
    )

    # Focus ring styling for accessibility
    style.map(
        "TButton",
        focuscolor=[("focus", colors["accent"])],
    )

    style.map(
        "TScale",
        focuscolor=[("focus", colors["accent"])],
    )

    # Entry field focus styling
    style.map(
        "TEntry",
        focuscolor=[("focus", colors["accent"])],
        bordercolor=[("focus", colors["primary"])],
    )

    # Checkbutton focus styling
    style.map(
        "TCheckbutton",
        focuscolor=[("focus", colors["accent"])],
    )

    # Combobox focus styling
    style.map(
        "TCombobox",
        focuscolor=[("focus", colors["accent"])],
        bordercolor=[("focus", colors["primary"])],
    )

    # Spinbox focus styling
    style.map(
        "TSpinbox",
        focuscolor=[("focus", colors["accent"])],
        bordercolor=[("focus", colors["primary"])],
    )

    # Disabled state styling for buttons - visually distinguishable
    style.map(
        "TButton",
        foreground=[
            ("disabled", colors["disabled"]),
            ("!disabled", colors["foreground"]),
        ],
        background=[
            ("disabled", colors["disabled_bg"]),
        ],
    )

    # Disabled state styling for entry fields
    style.map(
        "TEntry",
        foreground=[
            ("disabled", colors["disabled"]),
        ],
        fieldbackground=[
            ("disabled", colors["disabled_bg"]),
        ],
    )

    # Disabled state styling for checkbuttons
    style.map(
        "TCheckbutton",
        foreground=[
            ("disabled", colors["disabled"]),
        ],
    )

    # Disabled state styling for scales/sliders
    style.map(
        "TScale",
        troughcolor=[
            ("disabled", colors["disabled_bg"]),
        ],
    )

    # Disabled state styling for combobox
    style.map(
        "TCombobox",
        foreground=[
            ("disabled", colors["disabled"]),
        ],
        fieldbackground=[
            ("disabled", colors["disabled_bg"]),
        ],
    )

    logger.debug(f"Fluent style overrides configured for {theme} theme")


def create_themed_window(title: str = "Vox", theme: str = "light") -> ttk.Window:
    """Create a new themed ttkbootstrap window.

    Args:
        title: Window title
        theme: "light" or "dark" theme

    Returns:
        Configured ttkbootstrap Window instance
    """
    global _current_theme
    _current_theme = theme
    theme_name = THEMES.get(theme, THEMES["light"])

    window = ttk.Window(
        title=title,
        themename=theme_name,
        size=(WINDOW_SIZE["width"], WINDOW_SIZE["height"]),
        minsize=(WINDOW_SIZE["min_width"], WINDOW_SIZE["min_height"]),
    )

    # Center window on screen
    window.place_window_center()

    # Apply Fluent style overrides
    configure_fluent_overrides(window.style, theme)

    logger.debug(f"Created themed window: {title} with {theme} theme")
    return window


def configure_styles(style: ttk.Style, theme: str = "light") -> None:
    """Configure custom styles for the application.

    Args:
        style: ttkbootstrap Style instance to configure
        theme: "light" or "dark" theme name
    """
    colors = get_colors(theme)

    # Custom style for history list items
    style.configure(
        "History.TFrame",
        background=colors["surface"],
    )

    # Custom style for section headers
    # Legacy - use FONTS["title"] for new code
    style.configure(
        "Header.TLabel",
        font=FONTS["subtitle"],
        foreground=colors["foreground"],
    )

    # Fluent Design type scale styles
    style.configure(
        "Display.TLabel",
        font=FONTS["display"],
        foreground=colors["foreground"],
    )

    style.configure(
        "Title.TLabel",
        font=FONTS["title"],
        foreground=colors["foreground"],
    )

    style.configure(
        "Subtitle.TLabel",
        font=FONTS["subtitle"],
        foreground=colors["foreground"],
    )

    style.configure(
        "Body.TLabel",
        font=FONTS["body"],
        foreground=colors["foreground"],
    )

    style.configure(
        "Caption.TLabel",
        font=FONTS["caption"],
        foreground=colors["muted"],
    )

    # Custom style for muted/secondary text
    # Legacy - use Caption.TLabel for new code
    style.configure(
        "Muted.TLabel",
        font=FONTS["caption"],
        foreground=colors["muted"],
    )

    # Custom style for monospace text (hotkey display)
    style.configure(
        "Mono.TLabel",
        font=FONTS["mono"],
        foreground=colors["primary"],
    )

    # Status indicator styles
    style.configure(
        "Success.TLabel",
        foreground=colors["success"],
    )

    style.configure(
        "Danger.TLabel",
        foreground=colors["danger"],
    )

    style.configure(
        "Primary.TLabel",
        foreground=colors["primary"],
    )

    # Pill-style status indicator
    style.configure(
        "StatusPill.TLabel",
        font=FONTS["body"],
        padding=[SPACING["md"], SPACING["sm"]],
    )

    logger.debug(f"Custom styles configured for {theme} theme")
