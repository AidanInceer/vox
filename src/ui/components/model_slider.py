"""ModelSlider component for STT model selection.

This module provides a slider control that maps Whisper model values
to a user-friendly scale from "Faster" to "More Accurate".
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Final

import ttkbootstrap as ttk
from ttkbootstrap.constants import HORIZONTAL, LEFT, RIGHT, W, X

from src.ui.styles import FONTS, ICONS, SPACING

__all__ = ["ModelSlider"]

# Model mapping: index to model name
STT_MODELS: Final[list[str]] = [
    "tiny",
    "base",
    "small",
    "medium",
    "large",
    "large-v2",
    "large-v3",
]


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
        parent: Any,
        on_change: Callable[[str], None],
        **kwargs: Any,
    ) -> None:
        """Initialize the model slider.

        Args:
            parent: Parent widget
            on_change: Callback when model changes, receives model name
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        self._on_change = on_change
        self._current_index = 3  # Default to "medium"
        self._slider_var = ttk.IntVar(value=self._current_index)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the slider UI."""
        # Label row
        label_frame = ttk.Frame(self)
        label_frame.pack(fill=X, pady=(0, SPACING["xs"]))

        faster_label = ttk.Label(
            label_frame,
            text=f"{ICONS['faster']} Faster",
            font=FONTS["caption"],
        )
        faster_label.pack(side=LEFT)

        accurate_label = ttk.Label(
            label_frame,
            text=f"More Accurate {ICONS['accurate']}",
            font=FONTS["caption"],
        )
        accurate_label.pack(side=RIGHT)

        # Slider
        self._slider = ttk.Scale(
            self,
            from_=0,
            to=6,
            orient=HORIZONTAL,
            variable=self._slider_var,
            command=self._on_slider_change,
            length=200,
        )
        self._slider.pack(fill=X, pady=SPACING["xs"])

        # Current model display
        self._model_label = ttk.Label(
            self,
            text=f"Model: {self.get_model()}",
            font=FONTS["caption"],
        )
        self._model_label.pack(anchor=W, pady=(SPACING["xs"], 0))

    def _on_slider_change(self, value: str) -> None:
        """Handle slider value change.

        Args:
            value: Slider value as string
        """
        # Round to nearest integer for discrete steps
        index = round(float(value))
        if index != self._current_index:
            self._current_index = index
            self._slider_var.set(index)
            model = self.get_model()
            self._model_label.configure(text=f"Model: {model}")
            self._on_change(model)

    def get_model(self) -> str:
        """Get the currently selected model name."""
        return STT_MODELS[self._current_index]

    def set_model(self, model: str) -> None:
        """Set the slider to a specific model.

        Args:
            model: Model name (e.g., "medium", "large-v3")
        """
        if model in STT_MODELS:
            self._current_index = STT_MODELS.index(model)
            self._slider_var.set(self._current_index)
            self._model_label.configure(text=f"Model: {model}")
