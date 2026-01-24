"""Unit tests for Fluent UI components.

Tests for FluentCard, ModelSlider, ThemeToggle, SpeedSlider,
KeyCapLabel, HistoryItemCard, and EmptyState components.
"""

import pytest
import ttkbootstrap as ttk

from src.ui.components import (
    EmptyState,
    FluentCard,
    HistoryItemCard,
    KeyCapLabel,
    ModelSlider,
    SpeedSlider,
    ThemeToggle,
)
from src.ui.styles import SPACING


@pytest.fixture
def root():
    """Create a test window for UI components."""
    window = ttk.Window(themename="cosmo")
    yield window
    window.destroy()


class TestFluentCard:
    """Tests for FluentCard component."""

    def test_card_creation(self, root: ttk.Window) -> None:
        """Test basic card creation."""
        card = FluentCard(root, title="Test Card")
        assert card is not None
        assert card._title == "Test Card"

    def test_card_without_title(self, root: ttk.Window) -> None:
        """Test card creation without title."""
        card = FluentCard(root)
        assert card._title == ""
        assert card._title_label is None

    def test_card_with_title(self, root: ttk.Window) -> None:
        """Test card creation with title creates label."""
        card = FluentCard(root, title="Settings")
        card.update_idletasks()  # Force widget creation
        assert card._title_label is not None

    def test_card_content_property(self, root: ttk.Window) -> None:
        """Test content frame is accessible."""
        card = FluentCard(root, title="Test")
        content = card.content
        assert content is not None
        assert isinstance(content, ttk.Frame)

    def test_card_set_title(self, root: ttk.Window) -> None:
        """Test updating card title."""
        card = FluentCard(root, title="Original")
        card.set_title("Updated")
        assert card._title == "Updated"

    def test_card_custom_padding(self, root: ttk.Window) -> None:
        """Test card with custom padding."""
        card = FluentCard(root, padding=SPACING["lg"])
        assert card._padding == SPACING["lg"]

    def test_card_shadow_offset(self, root: ttk.Window) -> None:
        """Test card has shadow offset constant."""
        assert FluentCard.SHADOW_OFFSET == 4

    def test_card_corner_radius(self, root: ttk.Window) -> None:
        """Test card has corner radius constant."""
        assert FluentCard.CORNER_RADIUS == 8


class TestModelSlider:
    """Tests for ModelSlider component."""

    def test_slider_creation(self, root: ttk.Window) -> None:
        """Test basic slider creation."""
        slider = ModelSlider(root, on_change=lambda x: None)
        assert slider is not None

    def test_default_model(self, root: ttk.Window) -> None:
        """Test default model is medium."""
        slider = ModelSlider(root, on_change=lambda x: None)
        assert slider.get_model() == "medium"

    def test_set_model(self, root: ttk.Window) -> None:
        """Test setting model value."""
        slider = ModelSlider(root, on_change=lambda x: None)
        slider.set_model("large-v3")
        assert slider.get_model() == "large-v3"

    def test_invalid_model(self, root: ttk.Window) -> None:
        """Test invalid model doesn't change value."""
        slider = ModelSlider(root, on_change=lambda x: None)
        original = slider.get_model()
        slider.set_model("invalid-model")
        assert slider.get_model() == original

    def test_model_index_mapping(self, root: ttk.Window) -> None:
        """Test model index mapping is correct."""
        from src.ui.components.model_slider import STT_MODELS

        assert STT_MODELS[0] == "tiny"
        assert STT_MODELS[3] == "medium"
        assert STT_MODELS[6] == "large-v3"


class TestThemeToggle:
    """Tests for ThemeToggle component."""

    def test_toggle_creation(self, root: ttk.Window) -> None:
        """Test basic toggle creation."""
        toggle = ThemeToggle(root, on_change=lambda x: None)
        assert toggle is not None

    def test_default_theme(self, root: ttk.Window) -> None:
        """Test default theme is light."""
        toggle = ThemeToggle(root, on_change=lambda x: None)
        assert toggle.get_theme() == "light"

    def test_set_theme_dark(self, root: ttk.Window) -> None:
        """Test setting theme to dark."""
        toggle = ThemeToggle(root, on_change=lambda x: None)
        toggle.set_theme("dark")
        assert toggle.get_theme() == "dark"

    def test_invalid_theme(self, root: ttk.Window) -> None:
        """Test invalid theme doesn't change value."""
        toggle = ThemeToggle(root, on_change=lambda x: None)
        toggle.set_theme("invalid")
        assert toggle.get_theme() == "light"


class TestSpeedSlider:
    """Tests for SpeedSlider component."""

    def test_slider_creation(self, root: ttk.Window) -> None:
        """Test basic slider creation."""
        slider = SpeedSlider(root, on_change=lambda x: None)
        assert slider is not None

    def test_default_speed(self, root: ttk.Window) -> None:
        """Test default speed is 1.0."""
        slider = SpeedSlider(root, on_change=lambda x: None)
        assert slider.get_speed() == 1.0

    def test_set_speed(self, root: ttk.Window) -> None:
        """Test setting speed value."""
        slider = SpeedSlider(root, on_change=lambda x: None)
        slider.set_speed(1.5)
        assert slider.get_speed() == 1.5

    def test_speed_minimum_clamp(self, root: ttk.Window) -> None:
        """Test speed is clamped to minimum 0.5."""
        slider = SpeedSlider(root, on_change=lambda x: None)
        slider.set_speed(0.1)
        assert slider.get_speed() == 0.5

    def test_speed_maximum_clamp(self, root: ttk.Window) -> None:
        """Test speed is clamped to maximum 2.0."""
        slider = SpeedSlider(root, on_change=lambda x: None)
        slider.set_speed(3.0)
        assert slider.get_speed() == 2.0


class TestKeyCapLabel:
    """Tests for KeyCapLabel component."""

    def test_keycap_creation(self, root: ttk.Window) -> None:
        """Test basic keycap creation."""
        keycap = KeyCapLabel(root)
        assert keycap is not None

    def test_set_hotkey(self, root: ttk.Window) -> None:
        """Test setting hotkey string."""
        keycap = KeyCapLabel(root)
        keycap.set_hotkey("<ctrl>+<alt>+space")
        assert keycap._hotkey == "<ctrl>+<alt>+space"


class TestEmptyState:
    """Tests for EmptyState component."""

    def test_empty_state_creation(self, root: ttk.Window) -> None:
        """Test basic empty state creation."""
        empty = EmptyState(
            root,
            icon="📋",
            message="No items",
            description="Add some items",
        )
        assert empty is not None

    def test_empty_state_properties(self, root: ttk.Window) -> None:
        """Test empty state stores properties."""
        empty = EmptyState(
            root,
            icon="🎤",
            message="No recordings",
            description="Start recording",
        )
        assert empty._icon == "🎤"
        assert empty._message == "No recordings"
        assert empty._description == "Start recording"

    def test_empty_state_optional_description(self, root: ttk.Window) -> None:
        """Test empty state with no description."""
        empty = EmptyState(root, icon="📋", message="Empty")
        assert empty._description == ""


class TestHistoryItemCard:
    """Tests for HistoryItemCard component."""

    def test_history_item_creation(self, root: ttk.Window) -> None:
        """Test basic history item creation."""

        # Mock record object
        class MockRecord:
            id = 1
            text = "Test transcription"
            timestamp = "2026-01-24"

        record = MockRecord()
        item = HistoryItemCard(
            root,
            record=record,
            on_copy=lambda x: None,
            on_delete=lambda x: None,
        )
        assert item is not None

    def test_history_item_stores_callbacks(self, root: ttk.Window) -> None:
        """Test history item stores callbacks."""

        class MockRecord:
            id = 1
            text = "Test"
            timestamp = "2026-01-24"

        copy_called = []
        delete_called = []

        item = HistoryItemCard(
            root,
            record=MockRecord(),
            on_copy=lambda x: copy_called.append(x),
            on_delete=lambda x: delete_called.append(x),
        )
        assert item._on_copy is not None
        assert item._on_delete is not None
