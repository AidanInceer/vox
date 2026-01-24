"""FluentCard component with elevated drop shadow effect.

This module provides a card container widget that displays content
with a Windows 11 Fluent Design elevated appearance using simulated
drop shadow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, HORIZONTAL, W, X

from src.ui.styles import FONTS, SPACING, get_colors, get_current_theme

if TYPE_CHECKING:
    from typing import Optional

__all__ = ["FluentCard"]


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

    SHADOW_OFFSET = 4
    CORNER_RADIUS = 8

    def __init__(
        self,
        parent: Any,
        title: str = "",
        padding: int = SPACING["md"],
        **kwargs: Any,
    ) -> None:
        """Initialize the card.

        Args:
            parent: Parent widget
            title: Optional header text
            padding: Internal padding (default: 16px)
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        self._title = title
        self._padding = padding
        self._title_label: "Optional[ttk.Label]" = None

        # Create shadow effect using a Canvas
        self._shadow_canvas = ttk.Canvas(
            self,
            highlightthickness=0,
        )
        self._shadow_canvas.pack(fill=BOTH, expand=True)

        # Create the main card frame on top of shadow
        self._card_frame = ttk.Frame(
            self._shadow_canvas,
            bootstyle="light",  # type: ignore[arg-type]
        )

        # Create content area
        self._content_frame = ttk.Frame(self._card_frame)

        # Build the card structure
        self._build_card()

        # Bind resize to redraw shadow
        self.bind("<Configure>", self._on_configure)

    def _build_card(self) -> None:
        """Build the card internal structure."""
        # Add title if provided
        if self._title:
            self._title_label = ttk.Label(
                self._card_frame,
                text=self._title,
                font=FONTS["subtitle"],
                bootstyle="default",  # type: ignore[arg-type]
            )
            self._title_label.pack(
                anchor=W,
                padx=self._padding,
                pady=(self._padding, SPACING["sm"]),
            )

            # Add separator under title
            separator = ttk.Separator(self._card_frame, orient=HORIZONTAL)
            separator.pack(fill=X, padx=self._padding)

        # Pack content frame
        self._content_frame.pack(
            fill=BOTH,
            expand=True,
            padx=self._padding,
            pady=self._padding,
        )

    def _on_configure(
        self,
        event: "ttk.tk.Event",  # type: ignore[name-defined]
    ) -> None:
        """Handle resize events to redraw shadow."""
        self._draw_shadow()

    def _draw_shadow(self) -> None:
        """Draw the shadow effect on the canvas."""
        self._shadow_canvas.delete("shadow")

        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        colors = get_colors(get_current_theme())

        # Draw shadow rectangle (offset down and right)
        shadow_color = colors["shadow"]
        self._shadow_canvas.create_rectangle(
            self.SHADOW_OFFSET,
            self.SHADOW_OFFSET,
            width,
            height,
            fill=shadow_color,
            outline="",
            tags="shadow",
        )

        # Position the card frame above the shadow
        card_width = width - self.SHADOW_OFFSET
        card_height = height - self.SHADOW_OFFSET

        self._shadow_canvas.create_window(
            0,
            0,
            window=self._card_frame,
            anchor="nw",
            width=card_width,
            height=card_height,
            tags="card",
        )

    @property
    def content(self) -> ttk.Frame:
        """Get the content frame for adding child widgets."""
        return self._content_frame

    def set_title(self, title: str) -> None:
        """Update the card title.

        Args:
            title: New title text
        """
        self._title = title
        if self._title_label is not None:
            self._title_label.configure(text=title)
