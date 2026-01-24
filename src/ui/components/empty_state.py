"""EmptyState component for empty list placeholders.

This module provides a friendly empty state display with icon
and message for when lists or sections have no content.
"""

from __future__ import annotations

from typing import Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import CENTER

from src.ui.styles import FONTS, SPACING

__all__ = ["EmptyState"]


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
        parent: Any,
        icon: str,
        message: str,
        description: str = "",
        **kwargs: Any,
    ) -> None:
        """Initialize the empty state.

        Args:
            parent: Parent widget
            icon: Unicode icon to display
            message: Primary message text
            description: Optional secondary description
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        self._icon = icon
        self._message = message
        self._description = description

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the empty state UI."""
        # Center container
        container = ttk.Frame(self)
        container.pack(expand=True, pady=SPACING["xxl"])

        # Icon
        icon_label = ttk.Label(
            container,
            text=self._icon,
            font=FONTS["display"],
        )
        icon_label.pack(anchor=CENTER, pady=(0, SPACING["md"]))

        # Message
        message_label = ttk.Label(
            container,
            text=self._message,
            font=FONTS["subtitle"],
        )
        message_label.pack(anchor=CENTER, pady=(0, SPACING["sm"]))

        # Description (optional)
        if self._description:
            desc_label = ttk.Label(
                container,
                text=self._description,
                font=FONTS["caption"],
                bootstyle="secondary",  # type: ignore[arg-type]
            )
            desc_label.pack(anchor=CENTER)
