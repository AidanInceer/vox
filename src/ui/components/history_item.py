"""HistoryItemCard component for transcription history display.

This module provides a card component for displaying individual
transcription history entries with hover-reveal actions.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, RIGHT, W, X

from src.ui.styles import FONTS, ICONS, SPACING

if TYPE_CHECKING:
    pass

__all__ = ["HistoryItemCard"]

# Fixed item height for consistent list appearance
ITEM_HEIGHT = 80


class HistoryItemCard(ttk.Frame):
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
        parent: Any,
        record: Any,  # TranscriptionRecord
        on_copy: Callable[[int], None],
        on_delete: Callable[[int], None],
        **kwargs: Any,
    ) -> None:
        """Initialize the history item card.

        Args:
            parent: Parent widget
            record: TranscriptionRecord with id, text, timestamp
            on_copy: Callback for copy action, receives record id
            on_delete: Callback for delete action, receives record id
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)
        self._record = record
        self._on_copy = on_copy
        self._on_delete = on_delete
        self._buttons_visible = False

        self._build_ui()
        self._bind_hover_events()

    def _build_ui(self) -> None:
        """Build the history item UI."""
        # Main container with fixed height
        self.configure(height=ITEM_HEIGHT)
        self.pack_propagate(False)

        # Content frame
        content = ttk.Frame(self, padding=SPACING["sm"])
        content.pack(fill=X, expand=True)

        # Header row: timestamp + action buttons
        header = ttk.Frame(content)
        header.pack(fill=X)

        # Timestamp
        timestamp_str = self._record.created_at.strftime("%Y-%m-%d %H:%M")
        timestamp_label = ttk.Label(
            header,
            text=timestamp_str,
            font=FONTS["caption"],
            bootstyle="secondary",  # type: ignore[arg-type]
        )
        timestamp_label.pack(side=LEFT)

        # Action buttons container (hidden by default)
        self._actions_frame = ttk.Frame(header)
        self._actions_frame.pack(side=RIGHT)

        # Copy button
        self._copy_btn = ttk.Button(
            self._actions_frame,
            text=f"{ICONS['copy']}",
            command=self._handle_copy,
            bootstyle="info-outline",  # type: ignore[arg-type]
            width=3,
        )
        self._copy_btn.pack(side=LEFT, padx=(0, SPACING["xs"]))

        # Delete button
        self._delete_btn = ttk.Button(
            self._actions_frame,
            text=f"{ICONS['delete']}",
            command=self._handle_delete,
            bootstyle="danger-outline",  # type: ignore[arg-type]
            width=3,
        )
        self._delete_btn.pack(side=LEFT)

        # Hide buttons initially
        self._actions_frame.pack_forget()

        # Text preview
        preview_text = self._record.text[:80] + "..." if len(self._record.text) > 80 else self._record.text
        preview_label = ttk.Label(
            content,
            text=preview_text,
            font=FONTS["body"],
            wraplength=400,
        )
        preview_label.pack(anchor=W, pady=(SPACING["xs"], 0))

        # Word count
        word_count = len(self._record.text.split())
        word_label = ttk.Label(
            content,
            text=f"{word_count} words",
            font=FONTS["caption"],
            bootstyle="secondary",  # type: ignore[arg-type]
        )
        word_label.pack(anchor=W)

    def _bind_hover_events(self) -> None:
        """Bind hover events for button reveal."""
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        # Also bind to children
        for child in self.winfo_children():
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)
            for grandchild in child.winfo_children():
                grandchild.bind("<Enter>", self._on_enter)
                grandchild.bind("<Leave>", self._on_leave)

    def _on_enter(self, event: Any) -> None:
        """Show action buttons on hover."""
        if not self._buttons_visible:
            self._actions_frame.pack(side=RIGHT)
            self._buttons_visible = True

    def _on_leave(self, event: Any) -> None:
        """Hide action buttons when leaving."""
        # Check if mouse is still within the card
        x, y = self.winfo_pointerxy()
        widget_x = self.winfo_rootx()
        widget_y = self.winfo_rooty()
        widget_w = self.winfo_width()
        widget_h = self.winfo_height()

        if not (widget_x <= x <= widget_x + widget_w and widget_y <= y <= widget_y + widget_h):
            self._actions_frame.pack_forget()
            self._buttons_visible = False

    def _handle_copy(self) -> None:
        """Handle copy button click."""
        self._on_copy(self._record.id)

    def _handle_delete(self) -> None:
        """Handle delete button click."""
        self._on_delete(self._record.id)
