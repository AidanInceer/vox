"""Recording indicator overlay for visual feedback during voice input.

This module provides a translucent pill-shaped indicator that appears
above the Windows taskbar to show recording state feedback.
"""

import logging
import threading
import tkinter as tk
from typing import Literal, Optional

logger = logging.getLogger(__name__)

# Type alias for indicator states
IndicatorState = Literal["recording", "processing", "success", "error"]

# Visual state configurations
STATE_COLORS = {
    "recording": {"bg": "#FF4444", "fg": "#FFFFFF", "text": "● Recording..."},
    "processing": {"bg": "#4488FF", "fg": "#FFFFFF", "text": "⟳ Processing..."},
    "success": {"bg": "#44CC44", "fg": "#FFFFFF", "text": "✓ Done"},
    "error": {"bg": "#FF8844", "fg": "#FFFFFF", "text": "⚠ Error"},
}

# Default indicator dimensions
DEFAULT_WIDTH = 200
DEFAULT_HEIGHT = 40

# Auto-hide delay for success state (milliseconds)
SUCCESS_AUTO_HIDE_MS = 500

# Taskbar height estimate (Windows 11 default)
TASKBAR_HEIGHT = 48


class RecordingIndicator:
    """Translucent pill-shaped overlay for visual recording feedback.

    Displays a small floating indicator above the Windows taskbar to provide
    visual feedback during voice input operations. The indicator changes
    color and text based on the current state (recording, processing, etc).

    Thread Safety:
        All methods must be called from the main GUI thread or scheduled
        via `root.after()`. The indicator uses tkinter (not thread-safe).

    Attributes:
        is_visible: Whether the indicator is currently displayed.
        current_state: The current visual state, or None if hidden.

    Example:
        >>> indicator = RecordingIndicator()
        >>> indicator.show("recording")  # Red pulsing indicator
        >>> indicator.update_state("processing")  # Blue indicator
        >>> indicator.update_state("success")  # Green, auto-hides
        >>> indicator.destroy()  # Cleanup on application exit
    """

    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> None:
        """Initialize the recording indicator.

        Creates the indicator instance but does not create the tkinter window
        until `show()` is called. This allows lazy initialization.

        Args:
            width: Width of the indicator pill in pixels. Defaults to 200.
            height: Height of the indicator pill in pixels. Defaults to 40.
        """
        self._width = width
        self._height = height
        self._root: Optional[tk.Tk] = None
        self._main_root: Optional[tk.Tk] = None  # Reference to main app's root for thread-safe scheduling
        self._canvas: Optional[tk.Canvas] = None
        self._label: Optional[tk.Label] = None
        self._current_state: Optional[IndicatorState] = None
        self._is_visible = False
        self._auto_hide_id: Optional[str] = None
        self._pulse_id: Optional[str] = None
        self._pulse_state = False
        self._main_thread_id = threading.current_thread().ident

        logger.debug(f"RecordingIndicator initialized with dimensions {width}x{height}")

    def set_main_root(self, root: tk.Tk) -> None:
        """Set reference to main application's root window for thread-safe scheduling.
        
        This allows the indicator to schedule operations on the main thread's
        event loop even when called from background threads.
        
        Args:
            root: Main application's tkinter root window
        """
        self._main_root = root
        logger.debug("Main root reference set for thread-safe scheduling")

    def _schedule_on_main_thread(self, func: callable) -> None:
        """Schedule a function to run on the main thread.
        
        If already on the main thread, executes immediately.
        Otherwise, schedules via after() using either the main app root
        or the indicator's own root.
        
        Args:
            func: Function to execute on main thread
        """
        if threading.current_thread().ident == self._main_thread_id:
            # Already on main thread, execute directly
            func()
        else:
            # Try to schedule on main thread
            scheduler_root = self._main_root or self._root
            if scheduler_root:
                try:
                    scheduler_root.after(0, func)
                except tk.TclError:
                    pass  # Window may have been destroyed
            else:
                logger.warning("Cannot schedule on main thread: no root available")

    def _create_window(self) -> None:
        """Create the tkinter window with translucent pill appearance."""
        if self._root is not None:
            return  # Already created

        # Create root window
        self._root = tk.Tk()
        self._root.withdraw()  # Hide initially

        # Configure window properties
        self._root.overrideredirect(True)  # Remove window decorations
        self._root.attributes("-topmost", True)  # Always on top
        self._root.attributes("-alpha", 0.9)  # Slight transparency

        # Set window to be transparent for clicks (pass-through)
        # This makes the window non-blocking for mouse events
        try:
            self._root.attributes("-transparentcolor", "")
        except tk.TclError:
            pass  # Not all systems support this

        # Configure window size
        self._root.geometry(f"{self._width}x{self._height}")

        # Create pill-shaped appearance with rounded corners via a frame
        # Using a canvas for better visual control
        self._canvas = tk.Canvas(
            self._root,
            width=self._width,
            height=self._height,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

        # Create the pill shape background
        self._pill_bg = self._canvas.create_oval(
            0,
            0,
            self._width,
            self._height,
            fill=STATE_COLORS["recording"]["bg"],
            outline="",
        )

        # Create text label
        self._text_id = self._canvas.create_text(
            self._width // 2,
            self._height // 2,
            text=STATE_COLORS["recording"]["text"],
            fill=STATE_COLORS["recording"]["fg"],
            font=("Segoe UI", 11, "bold"),
        )

        logger.debug("Indicator window created")

    def _calculate_position(self) -> tuple[int, int]:
        """Calculate window position centered above taskbar.

        Returns:
            Tuple of (x, y) coordinates for window placement
        """
        if self._root is None:
            return (0, 0)

        # Get screen dimensions
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()

        # Calculate centered position
        x = (screen_width - self._width) // 2

        # Position above taskbar with small margin
        margin = 10
        y = screen_height - TASKBAR_HEIGHT - self._height - margin

        return (x, y)

    def _update_visuals(self, state: IndicatorState) -> None:
        """Update the visual appearance based on state.

        Args:
            state: The visual state to display
        """
        if self._canvas is None:
            return

        colors = STATE_COLORS[state]

        # Update pill background color
        self._canvas.itemconfig(self._pill_bg, fill=colors["bg"])

        # Update text
        self._canvas.itemconfig(
            self._text_id,
            text=colors["text"],
            fill=colors["fg"],
        )

        # Start or stop pulsing animation for recording state
        if state == "recording":
            self._start_pulse()
        else:
            self._stop_pulse()

    def _start_pulse(self) -> None:
        """Start the pulsing animation for recording state."""
        if self._root is None:
            return

        def pulse() -> None:
            if not self._is_visible or self._current_state != "recording":
                return
            if not self._root:
                return

            # Toggle between normal and dimmed
            self._pulse_state = not self._pulse_state
            alpha = 0.7 if self._pulse_state else 0.9

            try:
                self._root.attributes("-alpha", alpha)
            except tk.TclError:
                return  # Window may have been destroyed

            # Schedule next pulse
            self._pulse_id = self._root.after(500, pulse)

        if not self._root:
            return
        # Start pulsing
        self._pulse_id = self._root.after(500, pulse)

    def _stop_pulse(self) -> None:
        """Stop the pulsing animation."""
        if self._pulse_id and self._root:
            try:
                self._root.after_cancel(self._pulse_id)
            except tk.TclError:
                pass
            self._pulse_id = None

        # Reset alpha
        if self._root:
            try:
                self._root.attributes("-alpha", 0.9)
            except tk.TclError:
                pass

    def show(self, state: IndicatorState = "recording") -> None:
        """Show the indicator with the specified state.

        Thread-safe: Can be called from any thread.

        Args:
            state: Visual state to display
                - "recording": Red pulsing indicator
                - "processing": Blue indicator with spinner
                - "success": Green checkmark, auto-hides after 0.5s
                - "error": Orange warning indicator

        Creates window if not already created.
        """
        self._schedule_on_main_thread(lambda: self._show_impl(state))

    def _show_impl(self, state: IndicatorState) -> None:
        """Internal implementation of show() - must run on main thread."""
        # Create window if needed
        self._create_window()

        if self._root is None:
            return

        # Cancel any pending auto-hide
        if self._auto_hide_id:
            try:
                self._root.after_cancel(self._auto_hide_id)
            except tk.TclError:
                pass
            self._auto_hide_id = None

        # Update state and visuals
        self._current_state = state
        self._update_visuals(state)

        # Position and show window
        x, y = self._calculate_position()
        self._root.geometry(f"{self._width}x{self._height}+{x}+{y}")
        self._root.deiconify()  # Show window
        self._root.lift()  # Bring to front
        self._is_visible = True

        # Set up auto-hide for success state
        if state == "success":
            self._auto_hide_id = self._root.after(SUCCESS_AUTO_HIDE_MS, self.hide)

        logger.debug(f"Indicator shown with state: {state}")

    def hide(self) -> None:
        """Hide the indicator window.

        Thread-safe: Can be called from any thread.

        Withdraws the tkinter window from display and cancels any pending
        animations. Safe to call when already hidden (no-op).
        """
        self._schedule_on_main_thread(self._hide_impl)

    def _hide_impl(self) -> None:
        """Internal implementation of hide() - must run on main thread."""
        if not self._is_visible:
            return

        self._stop_pulse()

        # Cancel any pending auto-hide
        if self._auto_hide_id and self._root:
            try:
                self._root.after_cancel(self._auto_hide_id)
            except tk.TclError:
                pass
            self._auto_hide_id = None

        if self._root:
            try:
                self._root.withdraw()
            except tk.TclError:
                pass

        self._is_visible = False
        self._current_state = None

        logger.debug("Indicator hidden")

    def update_state(self, state: IndicatorState) -> None:
        """Update the indicator state without hiding.

        Thread-safe: Can be called from any thread.

        Args:
            state: New state to display

        No-op if indicator is not visible.
        """
        self._schedule_on_main_thread(lambda: self._update_state_impl(state))

    def _update_state_impl(self, state: IndicatorState) -> None:
        """Internal implementation of update_state() - must run on main thread."""
        if not self._is_visible:
            return

        # Cancel any pending auto-hide
        if self._auto_hide_id and self._root:
            try:
                self._root.after_cancel(self._auto_hide_id)
            except tk.TclError:
                pass
            self._auto_hide_id = None

        self._current_state = state
        self._update_visuals(state)

        # Set up auto-hide for success state
        if state == "success" and self._root:
            self._auto_hide_id = self._root.after(SUCCESS_AUTO_HIDE_MS, self.hide)

        logger.debug(f"Indicator state updated to: {state}")

    def destroy(self) -> None:
        """Destroy the indicator window and release all resources.

        Permanently destroys the tkinter window and cleans up all references.
        Must be called on application exit to prevent resource leaks.
        After calling destroy(), the indicator cannot be shown again.
        """
        self._stop_pulse()

        # Cancel any pending auto-hide
        if self._auto_hide_id and self._root:
            try:
                self._root.after_cancel(self._auto_hide_id)
            except tk.TclError:
                pass
            self._auto_hide_id = None

        if self._root:
            try:
                self._root.destroy()
            except tk.TclError:
                pass

        self._root = None
        self._canvas = None
        self._label = None
        self._is_visible = False
        self._current_state = None

        logger.debug("Indicator destroyed")

    @property
    def is_visible(self) -> bool:
        """Check if the indicator is currently visible.

        Returns:
            True if the indicator window is displayed, False otherwise.
        """
        return self._is_visible

    @property
    def current_state(self) -> Optional[IndicatorState]:
        """Get the current visual state of the indicator.

        Returns:
            The current IndicatorState ('recording', 'processing', 'success',
            'error'), or None if the indicator is hidden.
        """
        return self._current_state

    def update(self) -> None:
        """Process pending tkinter events.

        Manually pumps the tkinter event loop. Call this periodically if
        the indicator is used without running a tkinter mainloop (e.g.,
        when integrated with another GUI framework).
        """
        if self._root:
            try:
                self._root.update()
            except tk.TclError:
                pass
