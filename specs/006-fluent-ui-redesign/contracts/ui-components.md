# UI Component Contracts: Fluent UI Redesign

**Branch**: `006-fluent-ui-redesign`
**Date**: January 24, 2026
**Spec**: [spec.md](../spec.md)

---

## Overview

This document defines the interface contracts for the Fluent UI components. These contracts specify the public API for each component without implementation details.

---

## Module: ui/styles.py (Modified)

### Constants

```python
# Theme names for light/dark modes
THEMES: Final[dict[str, str]] = {
    "light": "cosmo",
    "dark": "darkly",
}

# Fluent Design color palette
COLORS_LIGHT: Final[dict[str, str]]  # Light theme colors
COLORS_DARK: Final[dict[str, str]]   # Dark theme colors

# Type scale following Fluent Design
FONTS: Final[dict[str, tuple[str, int, str]]] = {
    "display": (FONT_FAMILY, 28, "bold"),
    "title": (FONT_FAMILY, 20, "bold"),
    "subtitle": (FONT_FAMILY, 14, "bold"),
    "body": (FONT_FAMILY, 14, "normal"),
    "caption": (FONT_FAMILY, 12, "normal"),
    "mono": ("Cascadia Code", 12, "normal"),
}

# 8px grid spacing
SPACING: Final[dict[str, int]] = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48,
}

# Unicode icons
ICONS: Final[dict[str, str]]
```

### Functions

```python
def get_colors(theme: str = "light") -> dict[str, str]:
    """Get color palette for specified theme.

    Args:
        theme: "light" or "dark"

    Returns:
        Dictionary of color name to hex value
    """
    pass

def configure_fluent_styles(style: ttk.Style, theme: str = "light") -> None:
    """Configure ttkbootstrap styles for Fluent Design appearance.

    Sets up custom styles for:
    - Tabs with rounded indicators
    - Buttons with rounded corners
    - Cards with elevated appearance
    - Focus indicators for accessibility

    Args:
        style: ttkbootstrap Style instance
        theme: "light" or "dark" theme name
    """
    pass

def switch_theme(root: ttk.Window, theme: str) -> None:
    """Switch the application theme at runtime.

    Args:
        root: Main window instance
        theme: "light" or "dark"
    """
    pass
```

---

## Module: ui/components/card.py (New)

### Class: FluentCard

```python
class FluentCard(ttk.Frame):
    """Elevated card container with drop shadow.

    A container widget that displays content with an elevated appearance
    using a simulated drop shadow effect. Supports optional title header.

    Attributes:
        title: Optional card header text

    Example:
        >>> card = FluentCard(parent, title="Settings")
        >>> label = ttk.Label(card.content, text="Content here")
        >>> label.pack()
    """

    def __init__(
        self,
        parent: ttk.Widget,
        title: str = "",
        padding: int = SPACING["md"],
        **kwargs
    ) -> None:
        """Initialize the card.

        Args:
            parent: Parent widget
            title: Optional header text
            padding: Internal padding (default: 16px)
            **kwargs: Additional Frame options
        """
        pass

    @property
    def content(self) -> ttk.Frame:
        """Get the content frame for adding child widgets."""
        pass

    def set_title(self, title: str) -> None:
        """Update the card title."""
        pass
```

---

## Module: ui/components/model_slider.py (New)

### Class: ModelSlider

```python
class ModelSlider(ttk.Frame):
    """STT model selection slider with Faster/More Accurate labels.

    A slider control that maps 7 discrete Whisper model values to a
    user-friendly scale from "Faster" to "More Accurate".

    Model mapping:
        0: tiny (Fastest)
        1: base
        2: small
        3: medium (default)
        4: large
        5: large-v2
        6: large-v3 (Most Accurate)

    Example:
        >>> slider = ModelSlider(parent, on_change=save_model)
        >>> slider.set_model("medium")  # Positions at 3
    """

    def __init__(
        self,
        parent: ttk.Widget,
        on_change: Callable[[str], None],
        **kwargs
    ) -> None:
        """Initialize the model slider.

        Args:
            parent: Parent widget
            on_change: Callback when model changes, receives model name
            **kwargs: Additional Frame options
        """
        pass

    def get_model(self) -> str:
        """Get the currently selected model name."""
        pass

    def set_model(self, model: str) -> None:
        """Set the slider to a specific model.

        Args:
            model: Model name (e.g., "medium", "large-v3")
        """
        pass
```

---

## Module: ui/components/theme_toggle.py (New)

### Class: ThemeToggle

```python
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
        parent: ttk.Widget,
        on_change: Callable[[str], None],
        **kwargs
    ) -> None:
        """Initialize the theme toggle.

        Args:
            parent: Parent widget
            on_change: Callback when theme changes, receives "light" or "dark"
            **kwargs: Additional Frame options
        """
        pass

    def get_theme(self) -> str:
        """Get the current theme selection."""
        pass

    def set_theme(self, theme: str) -> None:
        """Set the toggle to a specific theme.

        Args:
            theme: "light" or "dark"
        """
        pass
```

---

## Module: ui/components/speed_slider.py (New)

### Class: SpeedSlider

```python
class SpeedSlider(ttk.Frame):
    """TTS speed adjustment slider.

    A slider control for adjusting text-to-speech playback speed
    from 0.5x to 2.0x with visual labels.

    Example:
        >>> slider = SpeedSlider(parent, on_change=set_tts_speed)
        >>> slider.set_speed(1.5)
    """

    def __init__(
        self,
        parent: ttk.Widget,
        on_change: Callable[[float], None],
        **kwargs
    ) -> None:
        """Initialize the speed slider.

        Args:
            parent: Parent widget
            on_change: Callback when speed changes, receives float value
            **kwargs: Additional Frame options
        """
        pass

    def get_speed(self) -> float:
        """Get the current speed value (0.5 to 2.0)."""
        pass

    def set_speed(self, speed: float) -> None:
        """Set the slider to a specific speed.

        Args:
            speed: Speed value from 0.5 to 2.0
        """
        pass
```

---

## Module: ui/components/keycap.py (New)

### Class: KeyCapLabel

```python
class KeyCapLabel(ttk.Frame):
    """Visual key cap representation for hotkey display.

    Displays hotkey combinations in a visual key cap style,
    similar to how keyboard shortcuts appear in Windows 11.

    Example:
        >>> keycap = KeyCapLabel(parent)
        >>> keycap.set_hotkey("<ctrl>+<alt>+space")
        # Displays: [Ctrl] + [Alt] + [Space]
    """

    def __init__(
        self,
        parent: ttk.Widget,
        **kwargs
    ) -> None:
        """Initialize the key cap label.

        Args:
            parent: Parent widget
            **kwargs: Additional Frame options
        """
        pass

    def set_hotkey(self, hotkey: str) -> None:
        """Set the hotkey to display.

        Args:
            hotkey: Hotkey string (e.g., "<ctrl>+<alt>+space")
        """
        pass
```

---

## Module: ui/components/history_item.py (New)

### Class: HistoryItemCard

```python
class HistoryItemCard(FluentCard):
    """History entry card with hover-reveal actions.

    Displays a transcription history entry with timestamp, preview text,
    and action buttons that appear on hover.

    Example:
        >>> item = HistoryItemCard(
        ...     parent,
        ...     record=transcription,
        ...     on_copy=copy_handler,
        ...     on_delete=delete_handler
        ... )
    """

    def __init__(
        self,
        parent: ttk.Widget,
        record: TranscriptionRecord,
        on_copy: Callable[[int], None],
        on_delete: Callable[[int], None],
        **kwargs
    ) -> None:
        """Initialize the history item card.

        Args:
            parent: Parent widget
            record: TranscriptionRecord with id, text, timestamp
            on_copy: Callback for copy action, receives record id
            on_delete: Callback for delete action, receives record id
            **kwargs: Additional FluentCard options
        """
        pass
```

---

## Module: ui/components/empty_state.py (New)

### Class: EmptyState

```python
class EmptyState(ttk.Frame):
    """Empty state placeholder with icon and message.

    Displays a friendly message when a list or section has no content.

    Example:
        >>> empty = EmptyState(
        ...     parent,
        ...     icon="📋",
        ...     message="No transcriptions yet",
        ...     description="Your voice recordings will appear here"
        ... )
    """

    def __init__(
        self,
        parent: ttk.Widget,
        icon: str,
        message: str,
        description: str = "",
        **kwargs
    ) -> None:
        """Initialize the empty state.

        Args:
            parent: Parent widget
            icon: Unicode icon to display
            message: Primary message text
            description: Optional secondary description
            **kwargs: Additional Frame options
        """
        pass
```

---

## Module: ui/main_window.py (Modified)

### Class: VoxMainWindow (Updated methods)

```python
class VoxMainWindow:
    """Main application window - updated for Fluent Design."""

    # Existing methods unchanged...

    def _build_status_tab(self) -> None:
        """Build the status tab with Fluent styling.

        Changes from current:
        - Centered content layout
        - FluentCard containers instead of LabelFrame
        - KeyCapLabel for hotkey display
        - Larger, pill-style status indicator
        - Accent-colored Record button as focal point
        """
        pass

    def _build_settings_tab(self) -> None:
        """Build the settings tab with Fluent styling.

        Changes from current:
        - FluentCard containers for each settings group
        - Auto-save on change (no Save button)
        - ThemeToggle for Appearance card
        - ModelSlider for STT selection
        - SpeedSlider for TTS speed
        - Visual confirmation on save
        """
        pass

    def _build_history_tab(self) -> None:
        """Build the history tab with Fluent styling.

        Changes from current:
        - HistoryItemCard for each entry
        - Hover-reveal action buttons
        - EmptyState when no history
        - Consistent item heights
        """
        pass

    def _on_theme_change(self, theme: str) -> None:
        """Handle theme toggle change.

        Args:
            theme: "light" or "dark"
        """
        pass

    def _on_stt_model_change(self, model: str) -> None:
        """Handle STT model slider change.

        Args:
            model: Model name (e.g., "medium")
        """
        pass

    def _on_tts_speed_change(self, speed: float) -> None:
        """Handle TTS speed slider change.

        Args:
            speed: Speed value (0.5 to 2.0)
        """
        pass

    def _show_save_confirmation(self) -> None:
        """Show brief visual confirmation that settings were saved."""
        pass
```
