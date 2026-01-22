"""Base component mixin for Vox UI components.

Provides common functionality for validation and state management
that can be mixed into UI component classes.
"""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


class ValidationMixin:
    """Mixin providing input validation helpers for UI components."""

    def validate_not_empty(self, value: str, field_name: str) -> bool:
        """Validate that a string value is not empty.

        Args:
            value: The string to validate.
            field_name: Name of the field for error messages.

        Returns:
            True if valid, False otherwise.
        """
        if not value or not value.strip():
            self._show_validation_error(f"{field_name} cannot be empty")
            return False
        return True

    def validate_in_range(self, value: float, min_val: float, max_val: float, field_name: str) -> bool:
        """Validate that a numeric value is within range.

        Args:
            value: The number to validate.
            min_val: Minimum allowed value (inclusive).
            max_val: Maximum allowed value (inclusive).
            field_name: Name of the field for error messages.

        Returns:
            True if valid, False otherwise.
        """
        if value < min_val or value > max_val:
            self._show_validation_error(f"{field_name} must be between {min_val} and {max_val}")
            return False
        return True

    def _show_validation_error(self, message: str) -> None:
        """Show a validation error to the user.

        Override this method in subclasses to customize error display.

        Args:
            message: The error message to display.
        """
        # Default implementation - subclasses should override
        pass


class StateMixin:
    """Mixin providing state management helpers for UI components."""

    _state: dict[str, Any]
    _state_listeners: dict[str, list[Callable[[Any], None]]]

    def init_state(self, initial_state: dict[str, Any] | None = None) -> None:
        """Initialize the component state.

        Args:
            initial_state: Optional initial state dictionary.
        """
        self._state = initial_state or {}
        self._state_listeners = {}

    def get_state(self, key: str, default: T = None) -> T:
        """Get a state value.

        Args:
            key: The state key.
            default: Default value if key doesn't exist.

        Returns:
            The state value or default.
        """
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Set a state value and notify listeners.

        Args:
            key: The state key.
            value: The new value.
        """
        old_value = self._state.get(key)
        self._state[key] = value

        if old_value != value and key in self._state_listeners:
            for listener in self._state_listeners[key]:
                listener(value)

    def on_state_change(self, key: str, listener: Callable[[Any], None]) -> None:
        """Register a listener for state changes.

        Args:
            key: The state key to listen for.
            listener: Callback function receiving the new value.
        """
        if key not in self._state_listeners:
            self._state_listeners[key] = []
        self._state_listeners[key].append(listener)


class BaseComponent(ValidationMixin, StateMixin):
    """Base mixin combining validation and state management.

    UI components can inherit from this to get common functionality.

    Example:
        class MyTab(BaseComponent):
            def __init__(self, parent):
                self.init_state({"loading": False})
                # ... build UI
    """

    def __init__(self) -> None:
        """Initialize the base component."""
        self.init_state()
