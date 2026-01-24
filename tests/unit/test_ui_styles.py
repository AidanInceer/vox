"""Unit tests for UI styles and typography consistency.

Tests verify that:
- FONTS dict contains all required type scale entries
- All font definitions follow the expected format
- Color palettes include required accessibility tokens
- Theme switching functions work correctly
"""

from src.ui.styles import (
    COLORS_DARK,
    COLORS_LIGHT,
    FONT_FAMILY,
    FONTS,
    ICONS,
    SPACING,
    THEMES,
    get_colors,
    get_current_theme,
)


class TestFontsTypeScale:
    """Tests for FONTS type scale definitions."""

    def test_fonts_contains_required_entries(self) -> None:
        """Verify FONTS dict has all required type scale entries."""
        required_entries = ["display", "title", "subtitle", "body", "caption", "mono"]
        for entry in required_entries:
            assert entry in FONTS, f"FONTS missing required entry: {entry}"

    def test_fonts_no_small_entry(self) -> None:
        """Verify FONTS does not have invalid 'small' entry (use caption instead)."""
        assert "small" not in FONTS, "FONTS should not have 'small' - use 'caption'"

    def test_fonts_format_is_tuple(self) -> None:
        """Verify all FONTS entries are tuples with (family, size, weight)."""
        for name, font_def in FONTS.items():
            assert isinstance(font_def, tuple), f"FONTS[{name}] should be a tuple"
            assert len(font_def) == 3, f"FONTS[{name}] should have 3 elements"
            family, size, weight = font_def
            assert isinstance(family, str), f"FONTS[{name}][0] (family) should be str"
            assert isinstance(size, int), f"FONTS[{name}][1] (size) should be int"
            assert isinstance(weight, str), f"FONTS[{name}][2] (weight) should be str"

    def test_fonts_use_segoe_ui_variable(self) -> None:
        """Verify standard fonts use Segoe UI Variable family."""
        non_mono_fonts = ["display", "title", "subtitle", "body", "caption"]
        for name in non_mono_fonts:
            family = FONTS[name][0]
            assert family == FONT_FAMILY, f"FONTS[{name}] should use {FONT_FAMILY}"

    def test_fonts_mono_uses_cascadia_code(self) -> None:
        """Verify mono font uses Cascadia Code."""
        assert FONTS["mono"][0] == "Cascadia Code", "FONTS[mono] should use Cascadia Code"

    def test_fonts_sizes_follow_hierarchy(self) -> None:
        """Verify font sizes follow visual hierarchy (display > title > subtitle >= body > caption)."""
        assert FONTS["display"][1] > FONTS["title"][1], "display should be larger than title"
        assert FONTS["title"][1] > FONTS["subtitle"][1], "title should be larger than subtitle"
        assert FONTS["subtitle"][1] >= FONTS["body"][1], "subtitle should be >= body"
        assert FONTS["body"][1] >= FONTS["caption"][1], "body should be >= caption"

    def test_fonts_weights_are_valid(self) -> None:
        """Verify font weights are valid values."""
        valid_weights = ["normal", "bold", "italic"]
        for name, font_def in FONTS.items():
            weight = font_def[2]
            assert weight in valid_weights, f"FONTS[{name}] has invalid weight: {weight}"


class TestSpacingGrid:
    """Tests for SPACING 8px grid system."""

    def test_spacing_contains_required_entries(self) -> None:
        """Verify SPACING dict has all required entries."""
        required_entries = ["xs", "sm", "md", "lg", "xl", "xxl"]
        for entry in required_entries:
            assert entry in SPACING, f"SPACING missing required entry: {entry}"

    def test_spacing_follows_8px_grid(self) -> None:
        """Verify SPACING values follow 8px grid (multiples of 4)."""
        for name, value in SPACING.items():
            assert value % 4 == 0, f"SPACING[{name}]={value} should be multiple of 4"

    def test_spacing_follows_hierarchy(self) -> None:
        """Verify spacing sizes follow hierarchy (xs < sm < md < lg < xl < xxl)."""
        assert SPACING["xs"] < SPACING["sm"]
        assert SPACING["sm"] < SPACING["md"]
        assert SPACING["md"] < SPACING["lg"]
        assert SPACING["lg"] < SPACING["xl"]
        assert SPACING["xl"] < SPACING["xxl"]


class TestColorPalettes:
    """Tests for color palette definitions."""

    def test_light_theme_has_required_colors(self) -> None:
        """Verify COLORS_LIGHT has all required color tokens."""
        required_colors = [
            "primary",
            "secondary",
            "success",
            "info",
            "warning",
            "danger",
            "background",
            "surface",
            "foreground",
            "muted",
            "border",
            "shadow",
            "accent",
            "on_accent",
            "disabled",
            "disabled_bg",
        ]
        for color in required_colors:
            assert color in COLORS_LIGHT, f"COLORS_LIGHT missing: {color}"

    def test_dark_theme_has_required_colors(self) -> None:
        """Verify COLORS_DARK has all required color tokens."""
        required_colors = [
            "primary",
            "secondary",
            "success",
            "info",
            "warning",
            "danger",
            "background",
            "surface",
            "foreground",
            "muted",
            "border",
            "shadow",
            "accent",
            "on_accent",
            "disabled",
            "disabled_bg",
        ]
        for color in required_colors:
            assert color in COLORS_DARK, f"COLORS_DARK missing: {color}"

    def test_color_values_are_hex(self) -> None:
        """Verify color values are valid hex format."""
        import re

        hex_pattern = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")

        for name, value in COLORS_LIGHT.items():
            assert hex_pattern.match(value), f"COLORS_LIGHT[{name}]={value} invalid hex"

        for name, value in COLORS_DARK.items():
            assert hex_pattern.match(value), f"COLORS_DARK[{name}]={value} invalid hex"

    def test_get_colors_returns_correct_palette(self) -> None:
        """Verify get_colors returns correct palette for theme."""
        assert get_colors("light") == COLORS_LIGHT
        assert get_colors("dark") == COLORS_DARK
        assert get_colors("invalid") == COLORS_LIGHT  # defaults to light


class TestThemes:
    """Tests for theme configuration."""

    def test_themes_dict_has_light_and_dark(self) -> None:
        """Verify THEMES dict has light and dark entries."""
        assert "light" in THEMES
        assert "dark" in THEMES

    def test_themes_map_to_ttkbootstrap_themes(self) -> None:
        """Verify THEMES map to valid ttkbootstrap theme names."""
        assert THEMES["light"] == "cosmo"
        assert THEMES["dark"] == "darkly"

    def test_get_current_theme_returns_string(self) -> None:
        """Verify get_current_theme returns a valid theme string."""
        theme = get_current_theme()
        assert theme in ["light", "dark"]


class TestIcons:
    """Tests for icon definitions."""

    def test_icons_contains_required_entries(self) -> None:
        """Verify ICONS dict has all required icon entries."""
        required_icons = [
            "status",
            "settings",
            "history",
            "record",
            "stop",
            "refresh",
            "delete",
            "copy",
            "check",
            "warning",
            "error",
        ]
        for icon in required_icons:
            assert icon in ICONS, f"ICONS missing required entry: {icon}"

    def test_icons_are_single_emoji_or_symbol(self) -> None:
        """Verify icons are emoji or unicode symbols (short strings)."""
        for name, icon in ICONS.items():
            assert isinstance(icon, str), f"ICONS[{name}] should be string"
            # Icons should be 1-2 characters (emoji can be 2 chars due to combining)
            assert len(icon) <= 4, f"ICONS[{name}]='{icon}' too long for icon"
