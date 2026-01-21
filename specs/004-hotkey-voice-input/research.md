# Research: Hotkey Voice Input

**Feature**: 004-hotkey-voice-input  
**Date**: 2026-01-21

## Overview

This document captures research findings for implementing the hotkey-triggered voice input desktop application on Windows 11.

---

## 1. Global Hotkey Registration

### Decision: pynput library

**Rationale**: 
- More mature and better maintained than `keyboard` library
- Built-in `GlobalHotKeys` class for easy registration
- Does not require administrator privileges on Windows 11
- Works well with threading (callbacks run in separate thread)

**Alternatives Considered**:
| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| `pynput` | Mature, no admin, GlobalHotKeys class | Slightly larger API | ✅ Selected |
| `keyboard` | Simple API | May need admin for some apps | ❌ Rejected |
| `pywin32` | Low-level control | Complex, overkill | ❌ Rejected |

**Implementation Pattern**:
```python
from pynput import keyboard

class HotkeyManager:
    def __init__(self):
        self._listener = None
        self._callbacks = {}
    
    def register_hotkey(self, hotkey: str, callback: callable):
        # hotkey format: '<ctrl>+<alt>+space'
        self._callbacks[hotkey] = callback
    
    def start(self):
        self._listener = keyboard.GlobalHotKeys(self._callbacks)
        self._listener.start()
```

**Key Notes**:
- Hotkey format uses angle brackets: `<ctrl>+<alt>+space`
- Callbacks run in listener thread - use queue for main thread dispatch
- **Toggle behavior**: Same hotkey starts and stops recording (first press = start, second press = stop and transcribe)
- Escape key registered separately for cancellation (discards recording without transcribing)

---

## 2. Translucent Overlay Window (Recording Indicator)

### Decision: tkinter with transparency attributes

**Rationale**:
- Built into Python stdlib (no extra dependency)
- Windows 11 supports `-transparentcolor` attribute
- Can be positioned above taskbar using screen geometry
- Same framework as main settings window

**Alternatives Considered**:
| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| tkinter | Stdlib, simple, fast | Less modern styling | ✅ Selected |
| PyQt6 | Native look | +30MB, slower launch | ❌ Rejected |
| Pygame | Game-oriented | Wrong paradigm | ❌ Rejected |

**Implementation Pattern**:
```python
import tkinter as tk
import ctypes

# Enable DPI awareness for Windows 11
ctypes.windll.shcore.SetProcessDpiAwareness(2)

class RecordingIndicator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # No title bar
        self.root.wm_attributes("-topmost", True)  # Always on top
        self.root.wm_attributes("-transparentcolor", "#010101")  # Magic color
        
    def _position_above_taskbar(self):
        screen_height = self.root.winfo_screenheight()
        taskbar_height = 48  # Windows 11 default
        y = screen_height - taskbar_height - self.height - 10
        x = (self.root.winfo_screenwidth() - self.width) // 2
        self.root.geometry(f"+{x}+{y}")
```

**Key Notes**:
- DPI awareness critical for correct positioning on high-DPI displays
- Pill shape achieved via canvas arcs and rectangles
- States: recording (red), processing (blue), success (green)
- Window should not steal focus (`-disabled` attribute if needed)

---

## 3. Clipboard Operations and Paste Simulation

### Decision: pyperclip + pynput keyboard simulation

**Rationale**:
- `pyperclip` provides simple, cross-platform clipboard API
- `pynput` already loaded for hotkeys, can simulate Ctrl+V
- Optionally restore original clipboard content after paste

**Implementation Pattern**:
```python
import pyperclip
from pynput.keyboard import Controller, Key

class ClipboardPaster:
    def __init__(self):
        self._keyboard = Controller()
    
    def paste_text(self, text: str, restore_clipboard: bool = True):
        original = pyperclip.paste() if restore_clipboard else None
        pyperclip.copy(text)
        time.sleep(0.05)  # Ensure clipboard ready
        
        with self._keyboard.pressed(Key.ctrl):
            self._keyboard.press('v')
            self._keyboard.release('v')
        
        if original:
            time.sleep(0.1)
            pyperclip.copy(original)
```

**Key Notes**:
- Small delay (50ms) needed between clipboard copy and paste simulation
- Restore original clipboard content to be user-friendly
- Target application must have focus for paste to work

---

## 4. GUI Framework for Settings Window

### Decision: tkinter + ttkbootstrap

**Rationale**:
- ttkbootstrap provides modern Windows 11-style themes
- Sub-second launch time (critical for background app)
- Minimal bundle size increase (~500KB)
- Same framework as overlay indicator

**Theme Selection**: `flatly` or `cosmo` for Windows 11 aesthetic

**Implementation Pattern**:
```python
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class VoxSettingsWindow:
    def __init__(self):
        self.root = ttk.Window(themename="flatly")
        self.root.title("Vox")
        self.root.geometry("600x450")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History")
```

---

## 5. Data Persistence

### Decision: SQLite (single vox.db file)

**Rationale**:
- Built into Python stdlib (sqlite3 module)
- Efficient queries for transcription history (indexed)
- ACID compliant for concurrent access
- Single file storage in `%APPDATA%/vox/`

**Alternatives Considered**:
| Storage | Pros | Cons | Verdict |
|---------|------|------|---------|
| SQLite | Stdlib, indexed, ACID | Slightly more complex | ✅ Selected |
| JSON file | Simple | O(n) queries, race conditions | ❌ Rejected |
| TinyDB | Simple API | Extra dependency | ❌ Rejected |

**Schema**: See [data-model.md](data-model.md)

**Storage Location**: `%APPDATA%/vox/vox.db`

---

## 6. Integration with Existing STT Module

### Decision: Reuse existing stt/ module without modification

**Rationale**:
- `MicrophoneRecorder` already handles audio capture with silence detection
- `STTEngine` already handles Whisper model loading and transcription
- `Transcriber` orchestrates the workflow
- Only need to suppress CLI output and return text programmatically

**Integration Pattern**:
```python
from src.stt.transcriber import Transcriber

class VoiceInputController:
    def __init__(self):
        self.transcriber = Transcriber()
    
    def record_and_transcribe(self) -> str:
        # Use existing transcriber, capture result
        return self.transcriber.transcribe()
```

**Modifications Needed**:
- Transcriber may need a `silent=True` mode to suppress CLI output
- Return transcription text directly instead of printing
- These are minimal changes to existing module

---

## 7. Windows 11 Specific Considerations

### DPI Awareness
Call early in application startup:
```python
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
```

### Taskbar Detection
Windows 11 taskbar is always at bottom by default. Height is typically 48px.

### Focus Behavior
- Overlay window should not steal focus from target application
- Use tkinter `-disabled` attribute if focus issues arise
- Paste simulation requires target app to have focus

### UAC/Permissions
- `pynput` works without admin rights
- No special permissions needed for clipboard or overlay

---

## 8. New Dependencies

Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing deps ...
    "pynput>=1.8.0",
    "pyperclip>=1.11.0",
    "ttkbootstrap>=1.10.0",
]
```

**Impact**:
- pynput: ~200KB
- pyperclip: ~15KB
- ttkbootstrap: ~500KB
- Total: ~715KB additional

---

## Summary

| Component | Technology | Status |
|-----------|------------|--------|
| Global Hotkeys | pynput | Researched ✅ |
| Overlay Window | tkinter | Researched ✅ |
| Clipboard/Paste | pyperclip + pynput | Researched ✅ |
| Settings GUI | tkinter + ttkbootstrap | Researched ✅ |
| Data Storage | SQLite | Researched ✅ |
| STT Integration | Existing stt/ module | Researched ✅ |
| Windows 11 APIs | DPI awareness, taskbar | Researched ✅ |

All NEEDS CLARIFICATION items from Technical Context have been resolved.
