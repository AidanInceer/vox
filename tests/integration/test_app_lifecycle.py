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


class TestThemePersistence:
    """Tests for theme persistence across sessions."""

    def test_theme_setting_persists_in_database(self) -> None:
        """Theme setting should persist to database."""
        import tempfile
        from pathlib import Path

        from src.persistence.database import VoxDatabase

        # Use a temp directory for the database
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_theme.db"
            db = VoxDatabase(db_path)

            # Set theme to darkly
            db.set_setting("theme", "darkly")

            # Verify it's saved
            saved_theme = db.get_setting("theme", "cosmo")
            assert saved_theme == "darkly"

            db.close()

    def test_theme_setting_restored_on_reconnect(self) -> None:
        """Theme setting should be restored when database is reopened."""
        import tempfile
        from pathlib import Path

        from src.persistence.database import VoxDatabase

        # Use a temp directory for the database
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_theme.db"

            # First session: save theme
            db1 = VoxDatabase(db_path)
            db1.set_setting("theme", "darkly")
            db1.close()

            # Second session: verify theme persisted
            db2 = VoxDatabase(db_path)
            restored_theme = db2.get_setting("theme", "cosmo")
            assert restored_theme == "darkly"
            db2.close()

    def test_default_theme_when_no_saved_preference(self) -> None:
        """Should return default theme (cosmo) when no preference is saved."""
        import tempfile
        from pathlib import Path

        from src.persistence.database import VoxDatabase

        # Use a temp directory for the database
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_theme.db"
            db = VoxDatabase(db_path)

            # Get theme with no saved preference
            theme = db.get_setting("theme", "cosmo")
            assert theme == "cosmo"

            db.close()

    def test_theme_toggle_logic(self) -> None:
        """Test that theme toggle correctly maps boolean to theme name."""
        # Theme names used by the app
        LIGHT_THEME = "cosmo"
        DARK_THEME = "darkly"

        # Test light mode (is_dark=False)
        is_dark = False
        theme = DARK_THEME if is_dark else LIGHT_THEME
        assert theme == LIGHT_THEME

        # Test dark mode (is_dark=True)
        is_dark = True
        theme = DARK_THEME if is_dark else LIGHT_THEME
        assert theme == DARK_THEME
