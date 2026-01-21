# Quickstart: Hotkey Voice Input

**Feature**: 004-hotkey-voice-input  
**Date**: 2026-01-21

## Overview

This guide provides quick setup instructions for implementing the hotkey voice input feature.

---

## Prerequisites

- Python 3.13+
- Windows 11
- Existing vox repository cloned
- Virtual environment activated

---

## 1. Install New Dependencies

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install new dependencies
uv pip install pynput pyperclip ttkbootstrap

# Or add to pyproject.toml and reinstall
uv pip install -e ".[dev]"
```

**Dependencies to add to pyproject.toml**:
```toml
dependencies = [
    # ... existing deps ...
    "pynput>=1.8.0",
    "pyperclip>=1.11.0",
    "ttkbootstrap>=1.10.0",
]
```

---

## 2. Create Module Structure

```bash
# Create new module directories
mkdir src/hotkey
mkdir src/clipboard
mkdir src/persistence
mkdir src/voice_input
mkdir src/ui

# Create __init__.py files
New-Item -ItemType File -Path src/hotkey/__init__.py
New-Item -ItemType File -Path src/clipboard/__init__.py
New-Item -ItemType File -Path src/persistence/__init__.py
New-Item -ItemType File -Path src/voice_input/__init__.py
```

---

## 3. Implementation Order

Follow this order for test-driven development:

### Phase 1: Core Infrastructure (P1 foundations)
1. `src/persistence/models.py` - Data classes
2. `src/persistence/database.py` - SQLite wrapper
3. `tests/unit/test_database.py` - Database tests

### Phase 2: Hotkey & Clipboard (P1 core)
4. `src/hotkey/manager.py` - HotkeyManager
5. `tests/unit/test_hotkey_manager.py`
6. `src/clipboard/paster.py` - ClipboardPaster
7. `tests/unit/test_clipboard_paster.py`

### Phase 3: Visual Feedback (P1 indicator)
8. `src/ui/indicator.py` - RecordingIndicator
9. `tests/unit/test_indicator.py`

### Phase 4: Integration (P1 complete)
10. `src/voice_input/controller.py` - VoiceInputController
11. `tests/unit/test_voice_controller.py`
12. `tests/integration/test_voice_input_flow.py`

### Phase 5: Settings UI (P2)
13. `src/ui/styles.py` - Theme configuration
14. `src/ui/main_window.py` - Settings + History window
15. `src/main.py` - Update entry point

---

## 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_database.py -v
```

---

## 5. Launch Application

```bash
# Run the application
python -m src.main

# Or via entry point (after install)
vox
```

---

## 6. Verify Installation

### Test Hotkey
1. Launch the application
2. Open Notepad
3. Press Ctrl+Alt+Space (starts recording)
4. Speak "hello world"
5. Press Ctrl+Alt+Space again (stops recording and transcribes)
6. Verify text appears in Notepad

### Test Settings
1. Click Settings tab
2. Change hotkey to Ctrl+Alt+V
3. Save and verify new hotkey works

### Test History
1. Complete a transcription
2. Open History tab
3. Verify transcription appears with timestamp
4. Click copy button and paste elsewhere

---

## Key Files Reference

| File | Purpose |
|------|---------|
| [spec.md](spec.md) | Feature specification |
| [plan.md](plan.md) | Implementation plan |
| [research.md](research.md) | Technical research |
| [data-model.md](data-model.md) | Database schema |
| [contracts/api.md](contracts/api.md) | Module contracts |

---

## Common Issues

### Hotkey Not Working
- Ensure application is running (window open)
- Check for hotkey conflicts with other apps
- Verify pynput is installed correctly

### Overlay Not Visible
- Check DPI awareness is enabled
- Verify Windows 11 (transparency requires Windows)
- Try running as administrator (usually not needed)

### Paste Not Working
- Ensure target application has focus
- Check clipboard permissions
- Verify pyperclip is working: `python -c "import pyperclip; pyperclip.copy('test')"`

### Database Errors
- Check %APPDATA%/vox/ directory exists
- Verify write permissions
- Delete vox.db to reset if corrupted

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     VoxMainWindow                           │
│  ┌─────────────────┐    ┌─────────────────────────────────┐│
│  │  Settings Tab   │    │         History Tab              ││
│  │  - Hotkey config│    │  - Transcription list           ││
│  │  - Save button  │    │  - Copy/Delete buttons          ││
│  └─────────────────┘    └─────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  VoiceInputController                        │
│  - Coordinates all components                                │
│  - Manages application state                                 │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌────────────┐ ┌───────────┐ ┌─────────────┐
│ HotkeyManager│ │  Existing  │ │ Recording │ │  Clipboard  │
│              │ │    STT     │ │ Indicator │ │   Paster    │
│ - Register   │ │  Module    │ │           │ │             │
│ - Listen     │ │            │ │ - Overlay │ │ - Copy      │
│ - Callback   │ │ - Record   │ │ - States  │ │ - Paste     │
└──────────────┘ │ - Transcribe│ └───────────┘ └─────────────┘
                 └────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   VoxDatabase   │
              │                 │
              │ - Settings      │
              │ - History       │
              └─────────────────┘
```
