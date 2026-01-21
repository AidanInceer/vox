"""Unit tests for RecordingIndicator class.

Tests cover:
- Indicator window creation and positioning
- State transitions (recording, processing, success, error)
- Show/hide/destroy lifecycle
"""

from unittest.mock import MagicMock, patch

import pytest

from src.ui.indicator import (
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    STATE_COLORS,
    SUCCESS_AUTO_HIDE_MS,
    TASKBAR_HEIGHT,
    RecordingIndicator,
)


class TestRecordingIndicatorInit:
    """Tests for indicator initialization."""

    def test_init_sets_dimensions(self) -> None:
        """Indicator should be initialized with specified dimensions."""
        indicator = RecordingIndicator(width=300, height=50)
        assert indicator._width == 300
        assert indicator._height == 50
        indicator.destroy()

    def test_init_uses_default_dimensions(self) -> None:
        """Indicator should use default 200x40 dimensions."""
        indicator = RecordingIndicator()
        assert indicator._width == DEFAULT_WIDTH
        assert indicator._height == DEFAULT_HEIGHT
        indicator.destroy()

    def test_init_does_not_create_window(self) -> None:
        """Indicator should not create window until show() is called."""
        indicator = RecordingIndicator()
        assert indicator._root is None
        indicator.destroy()

    def test_init_sets_default_state(self) -> None:
        """Indicator should have no visible state initially."""
        indicator = RecordingIndicator()
        assert indicator.is_visible is False
        assert indicator.current_state is None
        indicator.destroy()


class TestRecordingIndicatorPositioning:
    """Tests for indicator positioning above taskbar."""

    def test_positions_centered_horizontally(self) -> None:
        """Indicator should be centered horizontally on screen."""
        indicator = RecordingIndicator(width=200, height=40)

        # Mock the screen dimensions
        with patch.object(indicator, "_create_window"):
            indicator._root = MagicMock()
            indicator._root.winfo_screenwidth.return_value = 1920
            indicator._root.winfo_screenheight.return_value = 1080

            x, y = indicator._calculate_position()

            # Should be centered: (1920 - 200) / 2 = 860
            assert x == 860

        indicator.destroy()

    def test_positions_above_taskbar(self) -> None:
        """Indicator should be positioned above the Windows taskbar."""
        indicator = RecordingIndicator(width=200, height=40)

        with patch.object(indicator, "_create_window"):
            indicator._root = MagicMock()
            indicator._root.winfo_screenwidth.return_value = 1920
            indicator._root.winfo_screenheight.return_value = 1080

            x, y = indicator._calculate_position()

            # Should be above taskbar: 1080 - 48 - 40 - 10 = 982
            expected_y = 1080 - TASKBAR_HEIGHT - 40 - 10
            assert y == expected_y

        indicator.destroy()


class TestRecordingIndicatorStates:
    """Tests for visual state management."""

    @pytest.fixture
    def mock_indicator(self) -> RecordingIndicator:
        """Create an indicator with mocked tkinter components."""
        indicator = RecordingIndicator()
        indicator._root = MagicMock()
        indicator._canvas = MagicMock()
        indicator._pill_bg = "pill_bg_id"
        indicator._text_id = "text_id"
        indicator._root.winfo_screenwidth.return_value = 1920
        indicator._root.winfo_screenheight.return_value = 1080
        return indicator

    def test_show_creates_window(self) -> None:
        """show() should create the indicator window."""
        indicator = RecordingIndicator()

        with patch.object(indicator, "_create_window") as mock_create:
            with patch.object(indicator, "_update_visuals"):
                with patch.object(indicator, "_calculate_position", return_value=(0, 0)):
                    indicator._root = MagicMock()
                    indicator.show("recording")
                    mock_create.assert_called_once()

        indicator.destroy()

    def test_show_with_recording_state(self, mock_indicator: RecordingIndicator) -> None:
        """show('recording') should display red recording indicator."""
        mock_indicator.show("recording")

        assert mock_indicator.current_state == "recording"
        assert mock_indicator.is_visible is True

        # Verify canvas was configured with recording colors
        mock_indicator._canvas.itemconfig.assert_any_call(
            mock_indicator._pill_bg,
            fill=STATE_COLORS["recording"]["bg"],
        )

        mock_indicator.destroy()

    def test_show_with_processing_state(self, mock_indicator: RecordingIndicator) -> None:
        """show('processing') should display blue processing indicator."""
        mock_indicator.show("processing")

        assert mock_indicator.current_state == "processing"

        # Verify canvas was configured with processing colors
        mock_indicator._canvas.itemconfig.assert_any_call(
            mock_indicator._pill_bg,
            fill=STATE_COLORS["processing"]["bg"],
        )

        mock_indicator.destroy()

    def test_show_with_success_state(self, mock_indicator: RecordingIndicator) -> None:
        """show('success') should display green checkmark."""
        mock_indicator.show("success")

        assert mock_indicator.current_state == "success"

        # Verify canvas was configured with success colors
        mock_indicator._canvas.itemconfig.assert_any_call(
            mock_indicator._pill_bg,
            fill=STATE_COLORS["success"]["bg"],
        )

        mock_indicator.destroy()

    def test_show_with_error_state(self, mock_indicator: RecordingIndicator) -> None:
        """show('error') should display orange warning indicator."""
        mock_indicator.show("error")

        assert mock_indicator.current_state == "error"

        # Verify canvas was configured with error colors
        mock_indicator._canvas.itemconfig.assert_any_call(
            mock_indicator._pill_bg,
            fill=STATE_COLORS["error"]["bg"],
        )

        mock_indicator.destroy()

    def test_update_state_changes_visual(self, mock_indicator: RecordingIndicator) -> None:
        """update_state() should change the indicator appearance."""
        # First show with recording state
        mock_indicator.show("recording")

        # Reset mock to track new calls
        mock_indicator._canvas.itemconfig.reset_mock()

        # Update to processing
        mock_indicator.update_state("processing")

        assert mock_indicator.current_state == "processing"
        mock_indicator._canvas.itemconfig.assert_any_call(
            mock_indicator._pill_bg,
            fill=STATE_COLORS["processing"]["bg"],
        )

        mock_indicator.destroy()

    def test_update_state_noop_when_hidden(self) -> None:
        """update_state() should be no-op when indicator is hidden."""
        indicator = RecordingIndicator()
        indicator._canvas = MagicMock()

        # Don't show, just try to update
        indicator.update_state("processing")

        # Should not have called itemconfig since not visible
        indicator._canvas.itemconfig.assert_not_called()
        assert indicator.current_state is None

        indicator.destroy()


class TestRecordingIndicatorLifecycle:
    """Tests for show/hide/destroy lifecycle."""

    @pytest.fixture
    def mock_indicator(self) -> RecordingIndicator:
        """Create an indicator with mocked tkinter components."""
        indicator = RecordingIndicator()
        indicator._root = MagicMock()
        indicator._canvas = MagicMock()
        indicator._pill_bg = "pill_bg_id"
        indicator._text_id = "text_id"
        indicator._root.winfo_screenwidth.return_value = 1920
        indicator._root.winfo_screenheight.return_value = 1080
        return indicator

    def test_hide_hides_window(self, mock_indicator: RecordingIndicator) -> None:
        """hide() should hide the indicator window."""
        mock_indicator.show("recording")
        mock_indicator.hide()

        assert mock_indicator.is_visible is False
        mock_indicator._root.withdraw.assert_called()

        mock_indicator.destroy()

    def test_hide_is_idempotent(self, mock_indicator: RecordingIndicator) -> None:
        """hide() should be safe to call when already hidden."""
        # Don't show, just hide multiple times
        mock_indicator._is_visible = False
        mock_indicator.hide()
        mock_indicator.hide()

        # Should not raise any errors
        mock_indicator.destroy()

    def test_destroy_releases_resources(self, mock_indicator: RecordingIndicator) -> None:
        """destroy() should release window resources."""
        mock_indicator.show("recording")
        mock_indicator.destroy()

        assert mock_indicator._root is None
        assert mock_indicator._canvas is None
        assert mock_indicator.is_visible is False
        assert mock_indicator.current_state is None

    def test_success_state_auto_hides(self, mock_indicator: RecordingIndicator) -> None:
        """Success state should auto-hide after 0.5 seconds."""
        mock_indicator.show("success")

        # Verify auto-hide timer was set
        mock_indicator._root.after.assert_called_with(
            SUCCESS_AUTO_HIDE_MS,
            mock_indicator.hide,
        )

        mock_indicator.destroy()

    def test_show_cancels_previous_auto_hide(self, mock_indicator: RecordingIndicator) -> None:
        """Showing a new state should cancel previous auto-hide timer."""
        # Set up a fake auto-hide id
        mock_indicator._auto_hide_id = "fake_timer_id"

        mock_indicator.show("recording")

        # Should have tried to cancel the previous timer
        mock_indicator._root.after_cancel.assert_called_with("fake_timer_id")

        mock_indicator.destroy()


class TestRecordingIndicatorPulse:
    """Tests for recording state pulse animation."""

    def test_recording_state_starts_pulse(self) -> None:
        """Recording state should start pulsing animation."""
        indicator = RecordingIndicator()
        indicator._root = MagicMock()
        indicator._canvas = MagicMock()
        indicator._pill_bg = "pill_bg_id"
        indicator._text_id = "text_id"
        indicator._root.winfo_screenwidth.return_value = 1920
        indicator._root.winfo_screenheight.return_value = 1080

        indicator.show("recording")

        # Verify after() was called to schedule pulsing
        assert any(
            call[0][0] == 500  # 500ms pulse interval
            for call in indicator._root.after.call_args_list
        )

        indicator.destroy()

    def test_non_recording_state_stops_pulse(self) -> None:
        """Non-recording states should not pulse."""
        indicator = RecordingIndicator()
        indicator._root = MagicMock()
        indicator._canvas = MagicMock()
        indicator._pill_bg = "pill_bg_id"
        indicator._text_id = "text_id"
        indicator._root.winfo_screenwidth.return_value = 1920
        indicator._root.winfo_screenheight.return_value = 1080
        indicator._pulse_id = "fake_pulse_id"

        indicator.show("processing")

        # Should have tried to cancel the pulse
        indicator._root.after_cancel.assert_called_with("fake_pulse_id")

        indicator.destroy()
