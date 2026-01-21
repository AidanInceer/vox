"""Integration tests for application lifecycle.

Tests cover:
- Application launch and initialization
- Window creation and display
- Controller start/stop lifecycle
- Clean shutdown
"""

from unittest.mock import MagicMock, patch


class TestApplicationLifecycle:
    """Tests for application launch and shutdown."""

    @patch("src.ui.main_window.ttk")
    @patch("src.ui.main_window.configure_styles")
    def test_app_initializes_components(
        self,
        mock_configure_styles: MagicMock,
        mock_ttk: MagicMock,
    ) -> None:
        """Application should initialize database, controller, and window."""
        from src.persistence.database import VoxDatabase
        from src.ui.main_window import VoxMainWindow
        from src.voice_input.controller import VoiceInputController

        # Create mocks
        mock_window = MagicMock()
        mock_ttk.Window.return_value = mock_window
        mock_window.style = MagicMock()

        mock_db = MagicMock(spec=VoxDatabase)
        mock_db.get_setting.return_value = "<ctrl>+<alt>+space"

        mock_controller = MagicMock(spec=VoiceInputController)
        mock_controller._on_state_change = None
        mock_controller._on_error = None
        mock_controller._on_error = None
        mock_controller._indicator = None

        # Create main window
        window = VoxMainWindow(
            controller=mock_controller,
            database=mock_db,
        )

        # Verify window was created
        mock_ttk.Window.assert_called_once()
        assert window._controller is mock_controller
        assert window._database is mock_db

    @patch("src.ui.main_window.ttk")
    @patch("src.ui.main_window.configure_styles")
    def test_on_close_stops_controller(
        self,
        mock_configure_styles: MagicMock,
        mock_ttk: MagicMock,
    ) -> None:
        """on_close should stop the controller and cleanup."""
        from src.persistence.database import VoxDatabase
        from src.ui.main_window import VoxMainWindow
        from src.voice_input.controller import VoiceInputController

        # Create mocks
        mock_window = MagicMock()
        mock_ttk.Window.return_value = mock_window
        mock_window.style = MagicMock()

        mock_db = MagicMock(spec=VoxDatabase)
        mock_db.get_setting.return_value = "<ctrl>+<alt>+space"

        mock_controller = MagicMock(spec=VoiceInputController)
        mock_controller._on_state_change = None
        mock_controller._on_error = None
        mock_controller._indicator = None

        # Create main window
        window = VoxMainWindow(
            controller=mock_controller,
            database=mock_db,
        )

        # Call on_close
        window.on_close()

        # Verify controller was stopped
        mock_controller.stop.assert_called_once()

        # Verify window was destroyed
        mock_window.destroy.assert_called_once()

    @patch("src.ui.main_window.ttk")
    @patch("src.ui.main_window.configure_styles")
    def test_on_close_invokes_callback(
        self,
        mock_configure_styles: MagicMock,
        mock_ttk: MagicMock,
    ) -> None:
        """on_close should invoke the provided callback."""
        from src.persistence.database import VoxDatabase
        from src.ui.main_window import VoxMainWindow
        from src.voice_input.controller import VoiceInputController

        # Create mocks
        mock_window = MagicMock()
        mock_ttk.Window.return_value = mock_window
        mock_window.style = MagicMock()

        mock_db = MagicMock(spec=VoxDatabase)
        mock_db.get_setting.return_value = "<ctrl>+<alt>+space"

        mock_controller = MagicMock(spec=VoiceInputController)
        mock_controller._on_state_change = None
        mock_controller._on_error = None
        mock_controller._indicator = None

        close_callback = MagicMock()

        # Create main window with callback
        window = VoxMainWindow(
            controller=mock_controller,
            database=mock_db,
            on_close_callback=close_callback,
        )

        # Call on_close
        window.on_close()

        # Verify callback was invoked
        close_callback.assert_called_once()

    @patch("src.ui.main_window.ttk")
    @patch("src.ui.main_window.configure_styles")
    def test_show_displays_window(
        self,
        mock_configure_styles: MagicMock,
        mock_ttk: MagicMock,
    ) -> None:
        """show() should display the window."""
        from src.persistence.database import VoxDatabase
        from src.ui.main_window import VoxMainWindow
        from src.voice_input.controller import VoiceInputController

        # Create mocks
        mock_window = MagicMock()
        mock_ttk.Window.return_value = mock_window
        mock_window.style = MagicMock()

        mock_db = MagicMock(spec=VoxDatabase)
        mock_db.get_setting.return_value = "<ctrl>+<alt>+space"

        mock_controller = MagicMock(spec=VoiceInputController)
        mock_controller._on_state_change = None
        mock_controller._on_error = None
        mock_controller._indicator = None

        # Create main window
        window = VoxMainWindow(
            controller=mock_controller,
            database=mock_db,
        )

        # Call show
        window.show()

        # Verify window methods called
        mock_window.deiconify.assert_called()
        mock_window.lift.assert_called()

    @patch("src.ui.main_window.ttk")
    @patch("src.ui.main_window.configure_styles")
    def test_hide_withdraws_window(
        self,
        mock_configure_styles: MagicMock,
        mock_ttk: MagicMock,
    ) -> None:
        """hide() should withdraw the window."""
        from src.persistence.database import VoxDatabase
        from src.ui.main_window import VoxMainWindow
        from src.voice_input.controller import VoiceInputController

        # Create mocks
        mock_window = MagicMock()
        mock_ttk.Window.return_value = mock_window
        mock_window.style = MagicMock()

        mock_db = MagicMock(spec=VoxDatabase)
        mock_db.get_setting.return_value = "<ctrl>+<alt>+space"

        mock_controller = MagicMock(spec=VoiceInputController)
        mock_controller._on_state_change = None
        mock_controller._on_error = None
        mock_controller._indicator = None

        # Create main window
        window = VoxMainWindow(
            controller=mock_controller,
            database=mock_db,
        )

        # Call hide
        window.hide()

        # Verify window was withdrawn
        mock_window.withdraw.assert_called()
        assert window._is_minimized_to_tray is True


class TestGUICommand:
    """Tests for the GUI command in main.py."""

    @patch("src.persistence.database.VoxDatabase")
    @patch("src.voice_input.controller.VoiceInputController")
    @patch("src.ui.main_window.VoxMainWindow")
    def test_command_gui_initializes_app(
        self,
        mock_window_class: MagicMock,
        mock_controller_class: MagicMock,
        mock_db_class: MagicMock,
    ) -> None:
        """command_gui should initialize database, controller, and window."""
        from src.main import command_gui

        # Setup mocks
        mock_db = MagicMock()
        mock_db.get_setting.return_value = "<ctrl>+<alt>+space"
        mock_db_class.return_value = mock_db

        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller

        mock_window = MagicMock()
        mock_window_class.return_value = mock_window

        # Create args mock
        args = MagicMock()
        args.minimized = False

        # Call command_gui
        command_gui(args)

        # Verify initialization order
        mock_db_class.assert_called_once()
        mock_controller_class.assert_called_once_with(database=mock_db)
        mock_window_class.assert_called_once_with(
            controller=mock_controller,
            database=mock_db,
        )
        mock_controller.start.assert_called_once()
        mock_window.run.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("src.persistence.database.VoxDatabase")
    @patch("src.voice_input.controller.VoiceInputController")
    @patch("src.ui.main_window.VoxMainWindow")
    def test_command_gui_minimized_hides_window(
        self,
        mock_window_class: MagicMock,
        mock_controller_class: MagicMock,
        mock_db_class: MagicMock,
    ) -> None:
        """command_gui with --minimized should hide the window."""
        from src.main import command_gui

        # Setup mocks
        mock_db = MagicMock()
        mock_db.get_setting.return_value = "<ctrl>+<alt>+space"
        mock_db_class.return_value = mock_db

        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller

        mock_window = MagicMock()
        mock_window_class.return_value = mock_window

        # Create args mock with minimized=True
        args = MagicMock()
        args.minimized = True

        # Call command_gui
        command_gui(args)

        # Verify hide was called
        mock_window.hide.assert_called_once()
