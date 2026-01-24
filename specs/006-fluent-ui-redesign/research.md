# Research: Fluent UI Redesign for Windows 11

**Branch**: `006-fluent-ui-redesign`
**Date**: January 24, 2026
**Spec**: [spec.md](./spec.md)

## 1. ttkbootstrap Theme Selection for Fluent Look

### Decision: Use `cosmo` theme with custom style overrides

**Rationale**:

- ttkbootstrap's `cosmo` theme has the cleanest base for modern styling
- Provides good foundation for both light and dark modes
- Supports bootstyle modifiers for consistent component variants
- Already used in the codebase (`litera` currently) so minimal learning curve

**Alternatives Considered**:

| Theme            | Pros            | Cons                       | Verdict               |
| ---------------- | --------------- | -------------------------- | --------------------- |
| litera (current) | Clean, light    | Too stark, dated borders   | ❌ Replace            |
| cosmo            | Modern, rounded | Needs shadow customization | ✅ Selected for light |
| darkly           | Good dark mode  | Different widget shapes    | ✅ Selected for dark  |
| flatly           | Flat design     | No depth/shadows           | ❌ Rejected           |
| superhero        | Dark, bold      | Too gaming-oriented        | ❌ Rejected           |

**Implementation Pattern**:

```python
# Dynamic theme switching
THEMES = {
    "light": "cosmo",
    "dark": "darkly",
}

def switch_theme(theme: str) -> None:
    style = ttk.Style()
    style.theme_use(THEMES[theme])
    configure_fluent_overrides(style, theme)
```

---

## 2. Elevated Card Component with Drop Shadow

### Decision: Custom ttk.Frame with Canvas shadow simulation

**Rationale**:

- ttkbootstrap doesn't natively support box-shadow
- Canvas underneath Frame can simulate shadow effect
- Consistent with spec requirement for elevated cards (FR-011)
- Minimal performance impact with static shadows

**Alternatives Considered**:

| Approach               | Pros                     | Cons                   | Verdict     |
| ---------------------- | ------------------------ | ---------------------- | ----------- |
| Canvas shadow          | Visual depth, performant | Requires custom widget | ✅ Selected |
| Border only            | Simple                   | Flat, not elevated     | ❌ Rejected |
| PIL shadow image       | True shadow              | Complex, slow          | ❌ Rejected |
| Platform-specific APIs | Native look              | Windows-only, complex  | ❌ Rejected |

**Implementation Pattern**:

```python
class FluentCard(ttk.Frame):
    """Card with elevated shadow effect."""

    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        # Shadow canvas underneath
        self._shadow_canvas = ttk.Canvas(
            parent,
            highlightthickness=0,
            bg=COLORS["shadow"]
        )
        # Offset shadow for depth effect
        self._shadow_offset = 4
```

---

## 3. Fluent-Style Tab Navigation

### Decision: Custom styled ttk.Notebook with rounded pill indicators

**Rationale**:

- Keep existing Notebook widget for compatibility
- Override styles for rounded selection indicator
- Add icons via compound labels
- Matches clarification decision (keep top tabs, add Fluent styling)

**Implementation Pattern**:

```python
def configure_fluent_tabs(style: ttk.Style) -> None:
    """Configure Fluent-style tab appearance."""
    style.configure(
        "Fluent.TNotebook.Tab",
        padding=[16, 8],
        font=(FONT_FAMILY, 11),
    )
    style.map(
        "Fluent.TNotebook.Tab",
        background=[("selected", COLORS["accent"])],
        foreground=[("selected", COLORS["on_accent"])],
    )
```

---

## 4. STT Model Slider (Faster ↔ More Accurate)

### Decision: ttk.Scale with custom tick labels

**Rationale**:

- Maps 7 discrete model values to slider positions
- User-friendly labels (Faster/More Accurate) hide technical model names
- ttkbootstrap Scale supports bootstyle for accent coloring
- Matches clarification decision for slider control

**Model Mapping**:

```python
STT_MODEL_SCALE = [
    ("tiny", "Fastest"),
    ("base", "Fast"),
    ("small", "Balanced-"),
    ("medium", "Balanced"),
    ("large", "Accurate"),
    ("large-v2", "More Accurate"),
    ("large-v3", "Most Accurate"),
]
```

**Implementation Pattern**:

```python
class ModelSlider(ttk.Frame):
    """STT model selection slider."""

    def __init__(self, parent, on_change: Callable[[str], None]):
        self._scale = ttk.Scale(
            self,
            from_=0,
            to=6,
            orient=HORIZONTAL,
            command=self._on_slide,
            bootstyle="primary",
        )
        self._faster_label = ttk.Label(self, text="⚡ Faster")
        self._accurate_label = ttk.Label(self, text="🎯 More Accurate")
```

---

## 5. Theme Persistence and Switching

### Decision: Store theme preference in database, switch via Style.theme_use()

**Rationale**:

- Database already stores user settings (VoxDatabase.get_setting/set_setting)
- ttkbootstrap supports runtime theme switching
- No app restart required (FR-009 updated per clarification)

**Implementation Pattern**:

```python
def switch_theme(root: ttk.Window, theme: str) -> None:
    """Switch between light and dark themes."""
    theme_name = "cosmo" if theme == "light" else "darkly"
    root.style.theme_use(theme_name)
    configure_fluent_overrides(root.style, theme)
    # Persist
    database.set_setting("theme", theme)
```

---

## 6. Type Scale Implementation

### Decision: Define FONTS dict with Fluent type ramp

**Rationale**:

- Spec requires defined type scale (FR-007)
- Segoe UI Variable is Windows 11 native font
- ttkbootstrap allows font configuration per widget

**Type Scale**:

```python
FONTS: Final[dict[str, tuple[str, int, str]]] = {
    "display": (FONT_FAMILY, 28, "bold"),      # App title, hero text
    "title": (FONT_FAMILY, 20, "bold"),        # Section headers
    "subtitle": (FONT_FAMILY, 14, "bold"),     # Card headers
    "body": (FONT_FAMILY, 14, "normal"),       # Primary content
    "caption": (FONT_FAMILY, 12, "normal"),    # Helper text
    "mono": ("Cascadia Code", 12, "normal"),   # Hotkey display
}
```

---

## 7. 8px Grid Spacing System

### Decision: Replace current PADDING dict with 8px-based SPACING

**Rationale**:

- Spec requires 8px grid (FR-005)
- Current uses arbitrary 5/10/15/20 values
- 8px multiples align with Fluent Design guidelines

**Spacing Scale**:

```python
SPACING: Final[dict[str, int]] = {
    "xs": 4,    # Tight internal padding
    "sm": 8,    # Default internal padding
    "md": 16,   # Section margins
    "lg": 24,   # Card margins
    "xl": 32,   # Page margins
    "xxl": 48,  # Major section gaps
}
```

---

## 8. Icon Integration

### Decision: Unicode symbols for icons (no external icon library)

**Rationale**:

- ttkbootstrap doesn't have built-in icon support
- Unicode symbols work cross-platform
- Avoids adding new dependencies (spec assumption)
- Segoe UI Emoji font renders consistently on Windows 11

**Icon Mapping**:

```python
ICONS: Final[dict[str, str]] = {
    "status": "🏠",
    "settings": "⚙️",
    "history": "📋",
    "record": "🎤",
    "stop": "⏹️",
    "refresh": "🔄",
    "delete": "🗑️",
    "copy": "📄",
    "check": "✅",
    "warning": "⚠️",
    "error": "❌",
    "theme_light": "☀️",
    "theme_dark": "🌙",
}
```

---

## 9. Auto-Save Settings

### Decision: Bind to widget `<<ThemeChanged>>` and `command` callbacks

**Rationale**:

- FR-022 requires auto-save on change
- ttkbootstrap widgets support command callbacks
- Debounce rapid changes (e.g., slider dragging)

**Implementation Pattern**:

```python
def _create_setting_control(self, on_change: Callable):
    """Create control with auto-save."""
    def debounced_save(value):
        if hasattr(self, "_save_timer"):
            self._root.after_cancel(self._save_timer)
        self._save_timer = self._root.after(500, lambda: on_change(value))
    return debounced_save
```

---

## 10. Accessibility: Focus Indicators

### Decision: Custom focus styles via ttk.Style.map

**Rationale**:

- FR-032 requires keyboard navigation support
- ttkbootstrap widgets support focus state styling
- High-contrast focus ring for visibility

**Implementation Pattern**:

```python
style.map(
    "TButton",
    focuscolor=[("focus", COLORS["accent"])],
    relief=[("focus", "solid")],
)
```

---

## Dependencies

No new dependencies required. All features implementable with existing ttkbootstrap.

## Risk Assessment

| Risk                      | Likelihood | Impact | Mitigation                                              |
| ------------------------- | ---------- | ------ | ------------------------------------------------------- |
| Shadow effect performance | Low        | Medium | Use static canvas, no animations                        |
| Theme switch flicker      | Medium     | Low    | Test on slower machines, add transition delay if needed |
| Font fallback on Win10    | Medium     | Low    | Segoe UI Variable falls back to Segoe UI gracefully     |
| Slider discrete values    | Low        | Low    | Round to nearest model on release                       |
