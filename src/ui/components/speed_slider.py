"""SpeedSlider component for TTS playback speed adjustment.

This module provides a slider control for adjusting text-to-speech
playback speed from 0.5x to 2.0x.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import HORIZONTAL, LEFT, RIGHT, W, X

from src.ui.styles import FONTS, SPACING

__all__ = ["SpeedSlider"]


class SpeedSlider(ttk.Frame):
    """TTS speed adjustment slider.

    A slider control for adjusting text-to-speech playback speed
    from 0.5x to 2.0x with visual labels.

    Example:
        >>> slider = SpeedSlider(parent, on_change=set_tts_speed)
        >>> slider.set_speed(1.5)
    """

    # Speed range constants
    MIN_SPEED = 0.5
    MAX_SPEED = 2.0
    DEFAULT_SPEED = 1.0

    def __init__(
        self,
        parent: Any,
        on_change: Callable[[float], None],
        **kwargs: Any,
    ) -> None:
        """Initialize the speed slider.

        Args:
            parent: Parent widget
            on_change: Callback when speed changes, receives speed value
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        self._on_change = on_change
        self._current_speed = self.DEFAULT_SPEED
        self._slider_var = ttk.DoubleVar(value=self._current_speed)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the slider UI."""
        # Label row
        label_frame = ttk.Frame(self)
        label_frame.pack(fill=X, pady=(0, SPACING["xs"]))

        slow_label = ttk.Label(
            label_frame,
            text="0.5x",
            font=FONTS["caption"],
        )
        slow_label.pack(side=LEFT)

        fast_label = ttk.Label(
            label_frame,
            text="2.0x",
            font=FONTS["caption"],
        )
        fast_label.pack(side=RIGHT)

        # Slider
        self._slider = ttk.Scale(
            self,
            from_=self.MIN_SPEED,
            to=self.MAX_SPEED,
            orient=HORIZONTAL,
            variable=self._slider_var,
            command=self._on_slider_change,
            length=200,
        )
        self._slider.pack(fill=X, pady=SPACING["xs"])

        # Current speed display
        self._speed_label = ttk.Label(
            self,
            text=f"Speed: {self._current_speed:.1f}x",
            font=FONTS["caption"],
        )
        self._speed_label.pack(anchor=W, pady=(SPACING["xs"], 0))

    def _on_slider_change(self, value: str) -> None:
        """Handle slider value change.

        Args:
            value: Slider value as string
        """
        # Round to 1 decimal place for cleaner values
        speed = round(float(value), 1)
        if speed != self._current_speed:
            self._current_speed = speed
            self._speed_label.configure(text=f"Speed: {speed:.1f}x")
            self._on_change(speed)

    def get_speed(self) -> float:
        """Get the current speed value."""
        return self._current_speed

    def set_speed(self, speed: float) -> None:
        """Set the slider to a specific speed.

        Args:
            speed: Speed value from 0.5 to 2.0
        """
        clamped = max(self.MIN_SPEED, min(self.MAX_SPEED, speed))
        self._current_speed = clamped
        self._slider_var.set(clamped)
        self._speed_label.configure(text=f"Speed: {clamped:.1f}x")
