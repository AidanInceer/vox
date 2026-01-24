# Quickstart: Fluent UI Redesign

**Branch**: `006-fluent-ui-redesign`
**Date**: January 24, 2026

## Prerequisites

- Python 3.13+
- Existing vox development environment set up
- Windows 11 (or Windows 10 for testing fallback)

## Quick Setup

```bash
# 1. Checkout the feature branch
git checkout 006-fluent-ui-redesign

# 2. Ensure dependencies are installed (no new deps needed)
uv pip install -e ".[dev]"

# 3. Run the app to see current UI
python -m src.main
```

## Development Workflow

### Testing Style Changes

The UI is in `src/ui/`. Key files to modify:

```
src/ui/
├── styles.py          # Theme, colors, fonts, spacing (MODIFY)
├── main_window.py     # Main window layout (MODIFY)
├── components/        # Reusable components (ADD NEW)
│   ├── card.py        # FluentCard component
│   ├── model_slider.py
│   ├── theme_toggle.py
│   ├── speed_slider.py
│   ├── keycap.py
│   ├── history_item.py
│   └── empty_state.py
└── indicator.py       # Recording indicator (MINOR UPDATES)
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run UI-specific tests
pytest tests/unit/test_ui*.py

# Run with coverage
pytest tests/ --cov=src/ui --cov-report=term-missing
```

### Visual Testing

Since this is a visual feature, manual testing is essential:

```bash
# Launch app in development mode
python -m src.main

# Test checklist:
# [ ] Compare against Windows 11 Settings app
# [ ] Toggle light/dark theme
# [ ] Resize window (400px to 1920px)
# [ ] Navigate with keyboard only (Tab, Enter)
# [ ] Check all tabs render correctly
```

## Key Implementation Notes

### Theme Switching

```python
# In main_window.py
from src.ui.styles import switch_theme

def _on_theme_change(self, theme: str) -> None:
    switch_theme(self._root, theme)
    self._database.set_setting("theme", theme)
```

### Creating Cards

```python
# Replace LabelFrame with FluentCard
from src.ui.components.card import FluentCard

# Old:
frame = ttk.LabelFrame(parent, text="Settings")

# New:
card = FluentCard(parent, title="Settings")
# Add children to card.content, not card directly
label = ttk.Label(card.content, text="Option")
```

### Model Slider

```python
from src.ui.components.model_slider import ModelSlider
from src import config

slider = ModelSlider(
    parent,
    on_change=lambda model: config.set_stt_default_model(model)
)
slider.set_model(config.get_stt_default_model())
```

## File Changes Summary

| File                                | Action | Purpose                                  |
| ----------------------------------- | ------ | ---------------------------------------- |
| `src/ui/styles.py`                  | Modify | Update colors, fonts, spacing for Fluent |
| `src/ui/main_window.py`             | Modify | Refactor layouts, use new components     |
| `src/ui/components/__init__.py`     | Modify | Export new components                    |
| `src/ui/components/card.py`         | Create | FluentCard with shadow                   |
| `src/ui/components/model_slider.py` | Create | STT model selector                       |
| `src/ui/components/theme_toggle.py` | Create | Light/dark toggle                        |
| `src/ui/components/speed_slider.py` | Create | TTS speed control                        |
| `src/ui/components/keycap.py`       | Create | Hotkey visual display                    |
| `src/ui/components/history_item.py` | Create | History entry card                       |
| `src/ui/components/empty_state.py`  | Create | Empty list placeholder                   |
| `tests/unit/test_ui_components.py`  | Create | Component unit tests                     |

## Success Checklist

- [ ] App launches without errors
- [ ] Theme toggle switches light ↔ dark immediately
- [ ] STT model slider changes persist after restart
- [ ] TTS speed changes persist after restart
- [ ] All cards have visible shadow/elevation
- [ ] Tab navigation shows clear selection indicator
- [ ] History items show actions on hover
- [ ] Empty history shows friendly message
- [ ] Keyboard navigation works (Tab through all controls)
- [ ] No console errors or warnings
- [ ] All tests pass with ≥80% coverage
