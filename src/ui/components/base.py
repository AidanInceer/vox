"""Base component protocol and interfaces for Vox UI.

Defines the TabComponent protocol that all tab components must implement,
ensuring consistent API across StatusTab, SettingsTab, and HistoryTab.
"""

from typing import Any, Callable, Protocol, runtime_checkable

import ttkbootstrap as ttk


@runtime_checkable
class TabComponent(Protocol):
    """Protocol defining the interface for tab components.

    All tab components (StatusTab, SettingsTab, HistoryTab) must implement
    this protocol to ensure consistent integration with the main window.
    """

    @property
    def frame(self) -> ttk.Frame:
        """Get the root frame of this tab component.

        Returns:
            The ttk.Frame that contains this tab's UI elements.
        """
        ...

    def on_action(self, action: str, data: dict[str, Any] | None = None) -> None:
        """Handle an action from the parent or other components.

        Args:
            action: The action identifier (e.g., "refresh", "reset").
            data: Optional data associated with the action.
        """
        ...


ActionCallback = Callable[[str, dict[str, Any] | None], None]
"""Type alias for action callback functions.

Action callbacks receive:
- action: str - The action identifier
- data: dict | None - Optional action data
"""


class BaseTabComponent:
    """Base implementation for tab components.

    Provides common functionality for tab components. Subclasses
    should override _build() to create their specific UI.

    Attributes:
        _parent: The parent widget.
        _on_action: Optional callback for emitting actions to parent.
        _frame: The root frame of this component.
    """

    def __init__(self, parent: ttk.Frame, on_action: ActionCallback | None = None) -> None:
        """Initialize the tab component.

        Args:
            parent: The parent widget to attach to.
            on_action: Optional callback for emitting actions.
        """
        self._parent = parent
        self._on_action = on_action
        self._frame = self._build()

    @property
    def frame(self) -> ttk.Frame:
        """Get the root frame of this tab component."""
        return self._frame

    def _build(self) -> ttk.Frame:
        """Build and return the component's UI.

        Subclasses must override this method.

        Returns:
            The root frame containing the component's UI.
        """
        raise NotImplementedError("Subclasses must implement _build()")

    def on_action(self, action: str, data: dict[str, Any] | None = None) -> None:
        """Handle an action from parent or emit to parent.

        Override in subclasses to handle specific actions.

        Args:
            action: The action identifier.
            data: Optional action data.
        """
        pass

    def emit_action(self, action: str, data: dict[str, Any] | None = None) -> None:
        """Emit an action to the parent component.

        Args:
            action: The action identifier.
            data: Optional action data.
        """
        if self._on_action:
            self._on_action(action, data)
