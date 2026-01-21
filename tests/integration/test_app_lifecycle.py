"""Integration tests for application lifecycle.

Tests cover:
- Application launch and initialization
- Window creation and display
"""

from unittest.mock import MagicMock, patch


class TestApplicationLifecycle:
    """Tests for application launch and GUI."""

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
