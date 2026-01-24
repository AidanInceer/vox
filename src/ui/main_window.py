"""Main application window with settings and history tabs.

This module provides the primary user interface for the vox desktop
application, including settings configuration and transcription history.
"""

import logging
from typing import Any, Callable, Optional

import ttkbootstrap as ttk
from ttkbootstrap.constants import (
    BOTH,
    BOTTOM,
    DISABLED,
    HORIZONTAL,
    LEFT,
    NORMAL,
    NW,
    RIGHT,
    VERTICAL,
    W,
    X,
    Y,
)

from src.persistence.database import VoxDatabase
from src.persistence.models import AppState
from src.ui.components import (
    EmptyState,
    FluentCard,
    HistoryItemCard,
    KeyCapLabel,
    ModelSlider,
    SpeedSlider,
    ThemeToggle,
)
from src.ui.indicator import RecordingIndicator
from src.ui.styles import (
    FONTS,
    ICONS,
    SPACING,
    THEMES,
    WINDOW_SIZE,
    configure_fluent_overrides,
    configure_styles,
    switch_theme,
)
from src.ui.system_tray import SystemTrayManager
from src.voice_input.controller import VoiceInputController

try:
    from pynput import keyboard
except ImportError:
    keyboard = None  # type: ignore

logger = logging.getLogger(__name__)


class VoxMainWindow:
    """Main application window for the Vox voice input application.

    Provides the primary user interface with a tabbed layout containing:
    - Status tab: Shows current state and manual recording trigger
    - Settings tab: Hotkey configuration and clipboard options
    - History tab: View and manage past transcriptions

    The window integrates with the VoiceInputController to display state
    changes and with the RecordingIndicator for visual feedback during
    recording operations.

    Thread Safety:
        All UI updates from background threads should be scheduled via
        `root.after()` to ensure thread-safe GUI updates.

    Attributes:
        _controller: The VoiceInputController instance.
        _database: The VoxDatabase instance for settings/history.
        _indicator: The RecordingIndicator for visual feedback.

    Example:
        >>> db = VoxDatabase()
        >>> controller = VoiceInputController(database=db)
        >>> window = VoxMainWindow(controller=controller, database=db)
        >>> window.run()  # Blocks until window is closed
    """

    def __init__(
        self,
        controller: VoiceInputController,
        database: VoxDatabase,
        on_close_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the main application window.

        Creates the ttkbootstrap window with all UI components, sets up
        the recording indicator, and wires up controller state changes
        to the UI.

        Args:
            controller: VoiceInputController instance for handling voice
                input operations.
            database: VoxDatabase instance for reading/writing settings
                and transcription history.
            on_close_callback: Optional callback function invoked when
                the window is closed. Useful for cleanup operations.
        """
        self._controller = controller
        self._database = database
        self._on_close_callback = on_close_callback
        self._indicator: Optional[RecordingIndicator] = None
        self._is_minimized_to_tray = False
        self._system_tray: Optional[SystemTrayManager] = None

        # Tray behavior: True = minimize to tray on close, False = exit
        self._minimize_to_tray_on_close = database.get_setting("minimize_to_tray", True)

        # Hotkey capture state
        self._is_capturing_hotkey = False
        self._captured_keys: set[str] = set()
        self._keyboard_listener: Optional[Any] = None

        # Auto-save debounce timer
        self._save_timer_id: Optional[str] = None
        self._save_debounce_ms = 500

        # Load theme preference from database
        saved_theme = database.get_setting("theme", "light")
        self._current_theme = saved_theme if saved_theme in THEMES else "light"
        theme_name = THEMES.get(self._current_theme, THEMES["light"])

        # Create the main window with saved theme
        self._root = ttk.Window(
            title="Vox - Voice Input",
            themename=theme_name,
            size=(WINDOW_SIZE["width"], WINDOW_SIZE["height"]),
            minsize=(WINDOW_SIZE["min_width"], WINDOW_SIZE["min_height"]),
        )

        # Configure Fluent styles and overrides
        configure_styles(self._root.style, self._current_theme)
        configure_fluent_overrides(self._root.style, self._current_theme)

        # Center window on screen
        self._root.place_window_center()

        # Handle window close event
        self._root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Build the UI
        self._build_ui()

        # Wire up controller state changes to indicator
        self._setup_indicator()

        # Setup system tray
        self._setup_system_tray()

        logger.info("VoxMainWindow initialized")

    def _build_ui(self) -> None:
        """Build the main window UI components."""
        # Create notebook (tabbed interface) with Fluent styling
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(
            fill=BOTH,
            expand=True,
            padx=SPACING["md"],
            pady=SPACING["md"],
        )

        # Enable keyboard navigation for tabs (Left/Right arrow keys)
        self._notebook.bind("<Left>", self._on_tab_key_left)
        self._notebook.bind("<Right>", self._on_tab_key_right)

        # Create tabs with icons
        self._build_status_tab()
        self._build_settings_tab()
        self._build_history_tab()

        # Add status bar at bottom
        self._build_status_bar()

    def _build_status_tab(self) -> None:
        """Build the main status/home tab with Fluent Design."""
        frame = ttk.Frame(self._notebook, padding=SPACING["lg"])
        self._notebook.add(frame, text=f"{ICONS['status']} Status")

        # App title with display font
        title_label = ttk.Label(
            frame,
            text="Vox Voice Input",
            font=FONTS["title"],
            bootstyle="primary",  # type: ignore[arg-type]
        )
        title_label.pack(pady=(0, SPACING["lg"]))

        # Status display in FluentCard with pill-style indicator
        status_card = FluentCard(frame, title="Current Status")
        status_card.pack(fill=X, pady=SPACING["md"])

        # Pill-style status container
        status_pill = ttk.Frame(status_card.content)
        status_pill.pack(pady=SPACING["sm"])

        self._status_icon = ttk.Label(
            status_pill,
            text="✅",
            font=FONTS["subtitle"],
        )
        self._status_icon.pack(side=LEFT, padx=(0, SPACING["xs"]))

        self._status_label = ttk.Label(
            status_pill,
            text="Ready",
            font=FONTS["subtitle"],
            bootstyle="success",  # type: ignore[arg-type]
        )
        self._status_label.pack(side=LEFT)

        # Hotkey display in FluentCard with KeyCapLabel
        hotkey_card = FluentCard(frame, title="Activation Hotkey")
        hotkey_card.pack(fill=X, pady=SPACING["md"])

        current_hotkey = self._database.get_setting("hotkey", "<ctrl>+<alt>+space") or "<ctrl>+<alt>+space"

        # Use KeyCapLabel for visual hotkey display
        hotkey_container = ttk.Frame(hotkey_card.content)
        hotkey_container.pack(pady=SPACING["sm"])
        self._hotkey_display = KeyCapLabel(hotkey_container)
        self._hotkey_display.set_hotkey(current_hotkey)
        self._hotkey_display.pack()

        # Instructions with caption styling
        instructions = ttk.Label(
            frame,
            text="Press the hotkey to start recording.\nPress again to stop and transcribe.",
            font=FONTS["caption"],
            bootstyle="secondary",  # type: ignore[arg-type]
            justify="center",
        )
        instructions.pack(pady=SPACING["lg"])

        # Manual trigger button - PRIMARY ACCENT FOCAL POINT
        # Large, prominent button with extra padding
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=SPACING["lg"])

        self._record_btn = ttk.Button(
            btn_frame,
            text=f"{ICONS['record']} Start Recording",
            command=self._on_record_button,
            bootstyle="primary",  # type: ignore[arg-type]
            width=30,
            padding=(SPACING["lg"], SPACING["md"]),
        )
        self._record_btn.pack()

    def _build_settings_tab(self) -> None:
        """Build the settings configuration tab with Fluent Design."""
        frame = ttk.Frame(self._notebook, padding=SPACING["lg"])
        self._notebook.add(frame, text=f"{ICONS['settings']} Settings")

        # Model & Voice Settings in FluentCard
        voice_card = FluentCard(frame, title="Model & Voice")
        voice_card.pack(fill=X, pady=SPACING["md"])

        # Model selection label
        model_label = ttk.Label(
            voice_card.content,
            text="Speech Recognition Model",
            font=FONTS["body"],
        )
        model_label.pack(anchor=W, pady=(0, SPACING["xs"]))

        # Model slider
        current_model = self._database.get_setting("stt_model", "medium")
        self._model_slider = ModelSlider(
            voice_card.content,
            on_change=self._on_model_change,
        )
        self._model_slider.set_model(current_model)
        self._model_slider.pack(fill=X, pady=SPACING["sm"])

        # TTS Speed label
        speed_label = ttk.Label(
            voice_card.content,
            text="Text-to-Speech Speed",
            font=FONTS["body"],
        )
        speed_label.pack(anchor=W, pady=(SPACING["md"], SPACING["xs"]))

        # Speed slider
        current_speed = float(self._database.get_setting("tts_speed", "1.0"))
        self._speed_slider = SpeedSlider(
            voice_card.content,
            on_change=self._on_speed_change,
        )
        self._speed_slider.set_speed(current_speed)
        self._speed_slider.pack(fill=X, pady=SPACING["sm"])

        # Appearance Settings in FluentCard
        appearance_card = FluentCard(frame, title="Appearance")
        appearance_card.pack(fill=X, pady=SPACING["md"])

        # Theme toggle
        theme_label = ttk.Label(
            appearance_card.content,
            text="Theme",
            font=FONTS["body"],
        )
        theme_label.pack(anchor=W, pady=(0, SPACING["xs"]))

        self._theme_toggle = ThemeToggle(
            appearance_card.content,
            on_change=self._on_theme_change,
        )
        self._theme_toggle.set_theme(self._current_theme)
        self._theme_toggle.pack(anchor=W)

        # Hotkey configuration in FluentCard
        hotkey_card = FluentCard(frame, title="Hotkey Configuration")
        hotkey_card.pack(fill=X, pady=SPACING["md"])

        # Current hotkey row - aligned grid
        hotkey_row = ttk.Frame(hotkey_card.content)
        hotkey_row.pack(fill=X, pady=SPACING["sm"])
        hotkey_row.columnconfigure(1, weight=1)

        current_label = ttk.Label(
            hotkey_row,
            text="Current:",
            font=FONTS["body"],
            width=10,
        )
        current_label.grid(row=0, column=0, sticky=W, padx=(0, SPACING["sm"]))

        current_hotkey = self._database.get_setting("hotkey", "<ctrl>+<alt>+space")
        self._settings_hotkey_var = ttk.StringVar(value=current_hotkey)
        self._settings_hotkey_entry = ttk.Entry(
            hotkey_row,
            textvariable=self._settings_hotkey_var,
            font=FONTS["mono"],
            width=25,
        )
        self._settings_hotkey_entry.grid(row=0, column=1, sticky=W, padx=SPACING["sm"])

        # Capture hotkey button
        capture_btn = ttk.Button(
            hotkey_row,
            text="Capture",
            command=self._on_capture_hotkey,
            bootstyle="info-outline",  # type: ignore[arg-type]
            width=12,
        )
        capture_btn.grid(row=0, column=2, padx=(SPACING["sm"], 0))

        # Clipboard settings in FluentCard
        clipboard_card = FluentCard(frame, title="Clipboard Options")
        clipboard_card.pack(fill=X, pady=SPACING["md"])

        restore_setting = self._database.get_setting("restore_clipboard", "true")
        is_restore_enabled = restore_setting == "true"
        self._restore_clipboard_var = ttk.BooleanVar(value=is_restore_enabled)
        restore_check = ttk.Checkbutton(
            clipboard_card.content,
            text="Restore clipboard after paste",
            variable=self._restore_clipboard_var,
            command=self._on_clipboard_setting_change,
            bootstyle="round-toggle",  # type: ignore[arg-type]
        )
        restore_check.pack(anchor=W, pady=SPACING["sm"])

    def _build_history_tab(self) -> None:
        """Build the transcription history tab with Fluent Design."""
        frame = ttk.Frame(self._notebook, padding=SPACING["lg"])
        self._notebook.add(frame, text=f"{ICONS['history']} History")

        # Header with refresh button
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=X, pady=(0, SPACING["md"]))

        header_label = ttk.Label(
            header_frame,
            text="Transcription History",
            font=FONTS["subtitle"],
        )
        header_label.pack(side=LEFT)

        refresh_btn = ttk.Button(
            header_frame,
            text=f"{ICONS['refresh']} Refresh",
            command=self.refresh_history,
            bootstyle="info-outline",  # type: ignore[arg-type]
            width=12,
        )
        refresh_btn.pack(side=RIGHT)

        clear_btn = ttk.Button(
            header_frame,
            text=f"{ICONS['delete']} Clear All",
            command=self._on_clear_history,
            bootstyle="danger-outline",  # type: ignore[arg-type]
            width=12,
        )
        clear_btn.pack(side=RIGHT, padx=SPACING["sm"])

        # Scrollable history list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=BOTH, expand=True)

        # Create canvas with scrollbar for history items
        self._history_canvas = ttk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=VERTICAL,
            command=self._history_canvas.yview,
        )
        self._history_inner_frame = ttk.Frame(self._history_canvas)

        self._history_inner_frame.bind(
            "<Configure>",
            lambda e: self._history_canvas.configure(scrollregion=self._history_canvas.bbox("all")),
        )

        self._history_canvas.create_window(
            (0, 0),
            window=self._history_inner_frame,
            anchor=NW,
        )
        self._history_canvas.configure(yscrollcommand=scrollbar.set)

        self._history_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Enable mousewheel scrolling
        self._history_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Load initial history
        self.refresh_history()

    def _build_status_bar(self) -> None:
        """Build the status bar at the bottom of the window."""
        status_frame = ttk.Frame(self._root)
        status_frame.pack(
            fill=X,
            side=BOTTOM,
            padx=SPACING["sm"],
            pady=SPACING["sm"],
        )

        self._status_bar_label = ttk.Label(
            status_frame,
            text="Ready",
            font=FONTS["caption"],
            bootstyle="secondary",  # type: ignore[arg-type]
        )
        self._status_bar_label.pack(side=LEFT)

        version_label = ttk.Label(
            status_frame,
            text="Vox v0.1.0",
            font=FONTS["caption"],
            bootstyle="secondary",  # type: ignore[arg-type]
        )
        version_label.pack(side=RIGHT)

    def _setup_indicator(self) -> None:
        """Set up the recording indicator and wire to controller."""
        self._indicator = RecordingIndicator()

        # Pass main window's root for thread-safe scheduling
        self._indicator.set_main_root(self._root)

        # Connect controller state changes to indicator
        original_state_callback = self._controller._on_state_change
        original_error_callback = self._controller._on_error

        def combined_state_callback(state: AppState) -> None:
            self._on_controller_state_change(state)
            if original_state_callback:
                original_state_callback(state)

        def combined_error_callback(message: str) -> None:
            self._show_error_toast(message)
            if original_error_callback:
                original_error_callback(message)

        self._controller._on_state_change = combined_state_callback
        self._controller._on_error = combined_error_callback

        # Also update the controller's indicator reference
        self._controller._indicator = self._indicator

    def _setup_system_tray(self) -> None:
        """Set up the system tray icon and menu."""
        self._system_tray = SystemTrayManager(
            on_show=self._on_tray_show,
            on_hide=self._on_tray_hide,
            on_exit=self._on_tray_exit,
        )
        self._system_tray.start()
        logger.info("System tray initialized")

    def _on_tray_show(self) -> None:
        """Handle Show action from system tray."""
        self._root.after(0, self.show)

    def _on_tray_hide(self) -> None:
        """Handle Hide action from system tray."""
        self._root.after(0, self.hide)

    def _on_tray_exit(self) -> None:
        """Handle Exit action from system tray."""
        # Force exit (bypass minimize to tray)
        self._minimize_to_tray_on_close = False
        self._root.after(0, self.on_close)

    def _show_error_toast(self, message: str) -> None:
        """Show an error toast notification.

        Args:
            message: Error message to display
        """

        # Update status bar with error (thread-safe)
        def show_error():
            self._status_bar_label.configure(text=f"⚠️ {message}", bootstyle="danger")
            # Reset status after 5 seconds
            self._root.after(5000, lambda: self._status_bar_label.configure(text="Ready", bootstyle="secondary"))

        self._root.after(0, show_error)
        logger.warning(f"Error toast: {message}")

    def _on_controller_state_change(self, state: AppState) -> None:
        """Handle controller state changes to update UI.

        Args:
            state: New application state
        """
        state_messages = {
            AppState.IDLE: ("Ready", "success"),
            AppState.RECORDING: ("Recording...", "danger"),
            AppState.TRANSCRIBING: ("Transcribing...", "info"),
            AppState.PASTING: ("Pasting...", "warning"),
            AppState.ERROR: ("Error", "danger"),
        }

        message, style = state_messages.get(state, ("Unknown", "secondary"))

        # Update status label (thread-safe)
        self._root.after(0, lambda: self._update_status(message, style))

        # Update record button state with icons
        if state == AppState.IDLE:
            self._root.after(
                0,
                lambda: self._record_btn.configure(
                    text=f"{ICONS['record']} Start Recording",
                    state=NORMAL,
                ),
            )
        elif state == AppState.RECORDING:
            self._root.after(
                0,
                lambda: self._record_btn.configure(
                    text=f"{ICONS['stop']} Stop Recording",
                    state=NORMAL,
                ),
            )
        else:
            self._root.after(0, lambda: self._record_btn.configure(state=DISABLED))

        # Refresh history after successful transcription
        if state == AppState.IDLE:
            self._root.after(100, self.refresh_history)

    def _update_status(self, message: str, style: str) -> None:
        """Update the status display with pill-style icon.

        Args:
            message: Status message to display
            style: ttkbootstrap style name
        """
        # Map style to icon
        status_icons = {
            "success": "✅",
            "danger": "🔴",
            "info": "🔄",
            "warning": "⏳",
        }
        icon = status_icons.get(style, "⚪")

        self._status_icon.configure(text=icon)
        self._status_label.configure(text=message, bootstyle=style)
        self._status_bar_label.configure(text=f"{icon} {message}")

    def _on_tab_key_left(self, event: Any) -> str:
        """Handle Left arrow key for tab navigation.

        Args:
            event: Key event

        Returns:
            "break" to prevent default handling
        """
        current = self._notebook.index(self._notebook.select())
        if current > 0:
            self._notebook.select(current - 1)
        return "break"

    def _on_tab_key_right(self, event: Any) -> str:
        """Handle Right arrow key for tab navigation.

        Args:
            event: Key event

        Returns:
            "break" to prevent default handling
        """
        current = self._notebook.index(self._notebook.select())
        tab_count = self._notebook.index("end")
        if current < tab_count - 1:
            self._notebook.select(current + 1)
        return "break"

    def _format_hotkey_display(self, hotkey: str) -> str:
        """Format hotkey string for display.

        Args:
            hotkey: Hotkey in pynput format

        Returns:
            Human-readable hotkey string
        """
        # Convert pynput format to readable format
        display = hotkey.replace("<", "").replace(">", "")
        display = display.replace("+", " + ")
        display = display.title()
        return display

    def _on_record_button(self) -> None:
        """Handle record button click."""
        self._controller.trigger_recording()

    def _on_capture_hotkey(self) -> None:
        """Handle capture hotkey button - start listening for key combination."""
        if keyboard is None:
            logger.error("pynput not available for hotkey capture")
            self._status_bar_label.configure(text="Error: pynput not installed")
            return

        if self._is_capturing_hotkey:
            # Already capturing, stop and cancel
            self._stop_hotkey_capture(save=False)
            return

        # Start capture mode
        self._is_capturing_hotkey = True
        self._captured_keys = set()

        # Update UI to show we're capturing
        self._settings_hotkey_entry.configure(state=DISABLED)
        self._settings_hotkey_var.set("Press keys... (Enter to confirm, Esc to cancel)")
        self._status_bar_label.configure(text="Press your hotkey combination, then Enter to confirm")

        # Start keyboard listener
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_capture_key_press,
            on_release=self._on_capture_key_release,
        )
        self._keyboard_listener.start()

        logger.info("Started hotkey capture mode")

    def _on_capture_key_press(self, key: Any) -> None:
        """Handle key press during hotkey capture.

        Args:
            key: pynput key that was pressed
        """
        if not self._is_capturing_hotkey:
            return

        try:
            # Check for Enter to confirm
            if key == keyboard.Key.enter:
                self._root.after(0, lambda: self._stop_hotkey_capture(save=True))
                return

            # Check for Escape to cancel
            if key == keyboard.Key.esc:
                self._root.after(0, lambda: self._stop_hotkey_capture(save=False))
                return

            # Add the key to captured set
            key_str = self._key_to_string(key)
            if key_str:
                self._captured_keys.add(key_str)
                self._root.after(0, self._update_capture_display)

        except Exception as e:
            logger.error(f"Error in key capture: {e}")

    def _on_capture_key_release(self, key: Any) -> None:
        """Handle key release during hotkey capture.

        Args:
            key: pynput key that was released
        """
        # We don't remove keys on release to capture the full combination
        pass

    def _key_to_string(self, key: Any) -> Optional[str]:
        """Convert a pynput key to string format.

        Args:
            key: pynput Key or KeyCode

        Returns:
            String representation or None if not mappable
        """
        if keyboard is None:
            return None

        # Handle special keys
        special_key_map = {
            keyboard.Key.ctrl_l: "<ctrl>",
            keyboard.Key.ctrl_r: "<ctrl>",
            keyboard.Key.alt_l: "<alt>",
            keyboard.Key.alt_r: "<alt>",
            keyboard.Key.shift_l: "<shift>",
            keyboard.Key.shift_r: "<shift>",
            keyboard.Key.cmd: "<cmd>",
            keyboard.Key.space: "space",
            keyboard.Key.enter: "enter",
            keyboard.Key.tab: "tab",
            keyboard.Key.esc: "esc",
            keyboard.Key.backspace: "backspace",
            keyboard.Key.delete: "delete",
        }

        if hasattr(key, "name"):
            # It's a special Key
            return special_key_map.get(key)

        if hasattr(key, "char") and key.char:
            # It's a regular character
            return key.char.lower()

        if hasattr(key, "vk") and key.vk:
            # Try to get character from virtual key code
            # For F-keys and others
            vk = key.vk
            if 112 <= vk <= 123:  # F1-F12
                return f"f{vk - 111}"

        return None

    def _update_capture_display(self) -> None:
        """Update the hotkey entry to show captured keys."""
        if self._captured_keys:
            # Sort modifiers first, then other keys
            modifiers = []
            others = []
            for k in self._captured_keys:
                if k.startswith("<"):
                    modifiers.append(k)
                else:
                    others.append(k)

            display = "+".join(sorted(modifiers) + sorted(others))
            self._settings_hotkey_var.set(display)

    def _stop_hotkey_capture(self, save: bool) -> None:
        """Stop hotkey capture mode.

        Args:
            save: Whether to save the captured hotkey
        """
        self._is_capturing_hotkey = False

        # Stop the listener
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        # Re-enable the entry
        self._settings_hotkey_entry.configure(state=NORMAL)

        if save and self._captured_keys:
            # Build the hotkey string
            modifiers = []
            others = []
            for k in self._captured_keys:
                if k.startswith("<"):
                    modifiers.append(k)
                else:
                    others.append(k)

            if not modifiers:
                # Must have at least one modifier
                self._status_bar_label.configure(text="Hotkey must include a modifier (Ctrl, Alt, Shift)")
                # Restore previous value
                current = self._database.get_setting("hotkey", "<ctrl>+<alt>+space") or "<ctrl>+<alt>+space"
                self._settings_hotkey_var.set(current)
            elif not others:
                # Must have at least one non-modifier key
                self._status_bar_label.configure(text="Hotkey must include a non-modifier key")
                current = self._database.get_setting("hotkey", "<ctrl>+<alt>+space") or "<ctrl>+<alt>+space"
                self._settings_hotkey_var.set(current)
            else:
                # Valid hotkey
                hotkey = "+".join(sorted(modifiers) + sorted(others))
                self._settings_hotkey_var.set(hotkey)
                self._status_bar_label.configure(text=f"Captured: {hotkey} (click Save to apply)")
                logger.info(f"Captured hotkey: {hotkey}")
        else:
            # Cancelled or empty - restore previous value
            current = self._database.get_setting("hotkey", "<ctrl>+<alt>+space") or "<ctrl>+<alt>+space"
            self._settings_hotkey_var.set(current)
            self._status_bar_label.configure(text="Hotkey capture cancelled")

    def _on_model_change(self, model: str) -> None:
        """Handle model slider change with debounced save.

        Args:
            model: New model name
        """
        self._schedule_save("stt_model", model)

    def _on_speed_change(self, speed: float) -> None:
        """Handle speed slider change with debounced save.

        Args:
            speed: New speed value
        """
        self._schedule_save("tts_speed", str(speed))

    def _on_theme_change(self, theme: str) -> None:
        """Handle theme toggle change.

        Args:
            theme: "light" or "dark"
        """
        self._current_theme = theme
        switch_theme(self._root, theme)
        self._database.set_setting("theme", theme)
        self._show_save_confirmation(f"Theme changed to {theme}")

    def _on_clipboard_setting_change(self) -> None:
        """Handle clipboard setting change with auto-save."""
        restore_value = "true" if self._restore_clipboard_var.get() else "false"
        self._database.set_setting("restore_clipboard", restore_value)
        self._show_save_confirmation("Clipboard setting saved")

    def _schedule_save(self, setting_key: str, value: str) -> None:
        """Schedule a debounced save operation.

        Args:
            setting_key: Database setting key
            value: Value to save
        """
        # Cancel any pending save
        if self._save_timer_id:
            self._root.after_cancel(self._save_timer_id)

        # Schedule new save after debounce delay
        def do_save() -> None:
            self._database.set_setting(setting_key, value)
            self._show_save_confirmation(f"Saved {setting_key}")
            self._save_timer_id = None

        self._save_timer_id = self._root.after(self._save_debounce_ms, do_save)

    def _show_save_confirmation(self, message: str) -> None:
        """Show a brief save confirmation in the status bar.

        Args:
            message: Confirmation message to display
        """
        self._status_bar_label.configure(text=f"✅ {message}")
        # Reset to "Ready" after 2 seconds
        self._root.after(2000, lambda: self._status_bar_label.configure(text="Ready"))

    def _on_save_settings(self) -> None:
        """Handle save settings button click."""
        # Save hotkey
        new_hotkey = self._settings_hotkey_var.get()
        try:
            self._controller.update_hotkey(new_hotkey)
            self._hotkey_display.set_hotkey(new_hotkey)
        except ValueError as e:
            logger.error(f"Invalid hotkey: {e}")
            # Show error - TODO: add toast notification

        # Save clipboard setting
        restore_value = "true" if self._restore_clipboard_var.get() else "false"
        self._database.set_setting("restore_clipboard", restore_value)

        logger.info("Settings saved")
        self._status_bar_label.configure(text="Settings saved")

    def _on_clear_history(self) -> None:
        """Handle clear history button click."""
        count = self._database.clear_history()
        logger.info(f"Cleared {count} history items")
        self.refresh_history()
        self._status_bar_label.configure(text=f"Cleared {count} items")

    def _on_mousewheel(self, event: Any) -> None:
        """Handle mousewheel scrolling for history list."""
        self._history_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh_history(self) -> None:
        """Refresh the history list from the database.

        Clears all existing history items from the UI and reloads
        the latest transcription records from the database. Called
        automatically after successful transcriptions.
        """
        # Clear existing items
        for widget in self._history_inner_frame.winfo_children():
            widget.destroy()

        # Load history from database
        records = self._database.get_history(limit=100)

        if not records:
            empty_state = EmptyState(
                self._history_inner_frame,
                icon=ICONS["history"],
                message="No transcriptions yet",
                description="Use the hotkey to start recording!",
            )
            empty_state.pack(fill=BOTH, expand=True, pady=SPACING["xxl"])
            return

        # Create history items using HistoryItemCard
        for record in records:
            self._create_history_item(record)

    def _create_history_item(self, record) -> None:
        """Create a history item widget using HistoryItemCard.

        Args:
            record: TranscriptionRecord to display
        """
        item = HistoryItemCard(
            self._history_inner_frame,
            record=record,
            on_copy=self._on_copy_history_item,
            on_delete=self._on_delete_history_item,
        )
        item.pack(fill=X, pady=SPACING["xs"])

        # Separator
        sep = ttk.Separator(self._history_inner_frame, orient=HORIZONTAL)
        sep.pack(fill=X, pady=SPACING["xs"])

    def _on_copy_history_item(self, record_id: int) -> None:
        """Handle copy action for a history item.

        Args:
            record_id: ID of the record to copy
        """
        from src.clipboard.paster import ClipboardPaster

        record = self._database.get_transcription(record_id)
        if record:
            paster = ClipboardPaster()
            paster.copy_to_clipboard(record.text)
            self._show_save_confirmation("Copied to clipboard")

    def _on_delete_history_item(self, record_id: int) -> None:
        """Handle delete action for a history item.

        Args:
            record_id: ID of the record to delete
        """
        self._database.delete_transcription(record_id)
        self.refresh_history()
        self._show_save_confirmation("Item deleted")

    def show(self) -> None:
        """Show and focus the main window.

        Restores the window if it was hidden or minimized to the system tray.
        Brings the window to the foreground and gives it keyboard focus.
        """
        self._root.deiconify()
        self._root.lift()
        self._root.focus_force()
        self._is_minimized_to_tray = False

    def hide(self) -> None:
        """Hide the window (minimize to tray behavior).

        Withdraws the window from the display, effectively minimizing it
        to the system tray. The application continues running in the background.
        """
        self._root.withdraw()
        self._is_minimized_to_tray = True

    def run(self) -> None:
        """Start the main window event loop.

        Enters the tkinter mainloop, processing events until the window
        is closed. This method blocks the calling thread.
        """
        logger.info("Starting main window event loop")
        self._root.mainloop()

    def on_close(self) -> None:
        """Handle window close event.

        If minimize_to_tray_on_close is True, hides the window instead
        of closing. Otherwise performs cleanup and exits.

        Cleanup operations include:
        - Stopping any active hotkey capture
        - Stopping the voice input controller
        - Destroying the recording indicator
        - Stopping the system tray
        - Invoking the optional close callback
        - Destroying the main window
        """
        logger.info("Window close requested")

        # Check if we should minimize to tray instead of closing
        if self._minimize_to_tray_on_close and not self._is_minimized_to_tray:
            logger.info("Minimizing to system tray")
            self.hide()
            if self._system_tray:
                self._system_tray.show_notification(
                    "Vox", "Application minimized to tray. Use hotkey or tray icon to restore."
                )
            return

        # Stop hotkey capture if active
        if self._is_capturing_hotkey:
            self._stop_hotkey_capture(save=False)

        # Stop the controller
        self._controller.stop()

        # Destroy the indicator
        if self._indicator:
            self._indicator.destroy()

        # Stop system tray
        if self._system_tray:
            self._system_tray.stop()

        # Call user callback if provided
        if self._on_close_callback:
            try:
                self._on_close_callback()
            except Exception as e:
                logger.error(f"Error in close callback: {e}")

        # Destroy the window
        self._root.destroy()

        logger.info("Application closed")
