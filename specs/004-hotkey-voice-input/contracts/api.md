# API Contracts: Hotkey Voice Input

**Feature**: 004-hotkey-voice-input  
**Date**: 2026-01-21

## Overview

This document defines the internal module contracts for the hotkey voice input feature. These are internal Python APIs, not external REST/GraphQL endpoints.

---

## Module: hotkey/manager.py

### HotkeyManager

Manages global hotkey registration and lifecycle.

```python
class HotkeyManager:
    """
    Global hotkey registration and management.
    
    Thread Safety: Callbacks execute in listener thread.
    Use queue for main thread dispatch if needed.
    """
    
    def register_hotkey(self, hotkey: str, callback: Callable[[], None]) -> None:
        """
        Register a global hotkey.
        
        Args:
            hotkey: Hotkey string in pynput format (e.g., '<ctrl>+<alt>+space')
            callback: Function to call when hotkey is pressed (no args)
        
        Raises:
            ValueError: If hotkey format is invalid
            HotkeyAlreadyRegisteredError: If hotkey already registered
        """
        ...
    
    def unregister_hotkey(self, hotkey: str) -> None:
        """
        Unregister a previously registered hotkey.
        
        Args:
            hotkey: Hotkey string to unregister
        
        Raises:
            KeyError: If hotkey not registered
        """
        ...
    
    def start(self) -> None:
        """
        Start listening for registered hotkeys.
        
        Raises:
            RuntimeError: If already listening
        """
        ...
    
    def stop(self) -> None:
        """
        Stop listening for hotkeys.
        
        Safe to call multiple times.
        """
        ...
    
    @property
    def is_listening(self) -> bool:
        """Return True if currently listening for hotkeys."""
        ...
```

---

## Module: ui/indicator.py

### RecordingIndicator

Translucent overlay window for recording state feedback.

```python
class RecordingIndicator:
    """
    Translucent pill-shaped overlay positioned above taskbar.
    
    Thread Safety: Methods must be called from main thread or via root.after().
    """
    
    def __init__(self, width: int = 200, height: int = 40):
        """
        Initialize indicator (does not create window yet).
        
        Args:
            width: Pill width in pixels
            height: Pill height in pixels
        """
        ...
    
    def show(self, state: Literal["recording", "processing", "success", "error"] = "recording") -> None:
        """
        Show the indicator with the specified state.
        
        Args:
            state: Visual state to display
                - "recording": Red pulsing indicator
                - "processing": Blue indicator with spinner
                - "success": Green checkmark, auto-hides after 0.5s
                - "error": Orange warning indicator
        
        Creates window if not already created.
        """
        ...
    
    def hide(self) -> None:
        """
        Hide the indicator.
        
        Safe to call when already hidden.
        """
        ...
    
    def update_state(self, state: Literal["recording", "processing", "success", "error"]) -> None:
        """
        Update the indicator state without hiding.
        
        Args:
            state: New state to display
        
        No-op if indicator is not visible.
        """
        ...
    
    def destroy(self) -> None:
        """
        Destroy the indicator window and release resources.
        
        Must be called on application exit.
        """
        ...
```

---

## Module: clipboard/paster.py

### ClipboardPaster

Handles clipboard operations and paste simulation.

```python
class ClipboardPaster:
    """
    Clipboard management and paste simulation.
    
    Thread Safety: Thread-safe for paste_text calls.
    """
    
    def paste_text(self, text: str, restore_clipboard: bool = True) -> bool:
        """
        Copy text to clipboard and simulate Ctrl+V paste.
        
        Args:
            text: Text to paste at current cursor position
            restore_clipboard: If True, restore original clipboard after paste
        
        Returns:
            True if paste simulation completed, False if failed
        
        Note:
            Target application must have focus for paste to work.
            Small delay (~150ms) occurs for clipboard operations.
        """
        ...
    
    def copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to clipboard without pasting.
        
        Args:
            text: Text to copy
        """
        ...
    
    def get_clipboard(self) -> str:
        """
        Get current clipboard text content.
        
        Returns:
            Clipboard text, or empty string if not text
        """
        ...
```

---

## Module: persistence/database.py

### VoxDatabase

SQLite database wrapper for settings and history.

```python
class VoxDatabase:
    """
    SQLite database for settings and transcription history.
    
    Thread Safety: Uses check_same_thread=False for multi-thread access.
    """
    
    def __init__(self, db_path: Path | None = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to database file, or None for default
                     Default: %APPDATA%/vox/vox.db
        
        Creates database and schema if not exists.
        """
        ...
    
    # Settings operations
    
    def get_setting(self, key: str, default: str | None = None) -> str | None:
        """Get a setting value by key."""
        ...
    
    def set_setting(self, key: str, value: str) -> None:
        """Set a setting value (insert or update)."""
        ...
    
    def get_all_settings(self) -> dict[str, str]:
        """Get all settings as a dictionary."""
        ...
    
    # History operations
    
    def add_transcription(
        self, 
        text: str, 
        duration_seconds: float | None = None
    ) -> int:
        """
        Add a transcription to history.
        
        Args:
            text: Transcribed text
            duration_seconds: Recording duration
        
        Returns:
            ID of inserted record
        """
        ...
    
    def get_history(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> list[TranscriptionRecord]:
        """
        Get transcription history (newest first).
        
        Args:
            limit: Maximum records to return
            offset: Records to skip (for pagination)
        
        Returns:
            List of TranscriptionRecord objects
        """
        ...
    
    def get_transcription(self, record_id: int) -> TranscriptionRecord | None:
        """Get a specific transcription by ID."""
        ...
    
    def delete_transcription(self, record_id: int) -> bool:
        """
        Delete a transcription.
        
        Returns:
            True if deleted, False if not found
        """
        ...
    
    def clear_history(self) -> int:
        """
        Delete all transcription history.
        
        Returns:
            Number of records deleted
        """
        ...
    
    def close(self) -> None:
        """Close database connection."""
        ...
```

---

## Module: voice_input/controller.py

### VoiceInputController

Main integration controller coordinating all components.

```python
class VoiceInputController:
    """
    Coordinates hotkey listening, recording, transcription, and pasting.
    
    This is the main orchestrator for the voice input feature.
    """
    
    def __init__(
        self,
        database: VoxDatabase,
        on_state_change: Callable[[AppState], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ):
        """
        Initialize the voice input controller.
        
        Args:
            database: Database instance for settings/history
            on_state_change: Callback when application state changes
            on_error: Callback when error occurs
        """
        ...
    
    def start(self) -> None:
        """
        Start the voice input controller.
        
        Loads settings, registers hotkeys, begins listening.
        
        Raises:
            RuntimeError: If already started
        """
        ...
    
    def stop(self) -> None:
        """
        Stop the controller and release resources.
        
        Safe to call multiple times.
        """
        ...
    
    def trigger_recording(self) -> None:
        """
        Manually trigger a recording session.
        
        Same as pressing the hotkey programmatically.
        """
        ...
    
    def cancel_recording(self) -> None:
        """
        Cancel an in-progress recording.
        
        No-op if not recording.
        """
        ...
    
    @property
    def state(self) -> AppState:
        """Get current application state."""
        ...
    
    @property
    def is_recording(self) -> bool:
        """Return True if currently recording."""
        ...
    
    def update_hotkey(self, new_hotkey: str) -> None:
        """
        Update the activation hotkey.
        
        Args:
            new_hotkey: New hotkey in pynput format
        
        Raises:
            ValueError: If hotkey format invalid
        
        Persists to database and re-registers hotkey.
        """
        ...
```

---

## Module: ui/main_window.py

### VoxMainWindow

Main application window with settings and history tabs.

```python
class VoxMainWindow:
    """
    Main application window.
    
    Contains tabs for Settings and History.
    """
    
    def __init__(
        self,
        controller: VoiceInputController,
        database: VoxDatabase,
    ):
        """
        Initialize the main window.
        
        Args:
            controller: Voice input controller instance
            database: Database instance
        """
        ...
    
    def run(self) -> None:
        """
        Start the main window event loop.
        
        Blocks until window is closed.
        """
        ...
    
    def show(self) -> None:
        """Show the window (if hidden/minimized)."""
        ...
    
    def hide(self) -> None:
        """Hide the window to system tray/minimize."""
        ...
    
    def refresh_history(self) -> None:
        """Refresh the history list from database."""
        ...
    
    def on_close(self) -> None:
        """
        Handle window close event.
        
        Stops controller and exits application.
        """
        ...
```

---

## Error Types

```python
class VoxError(Exception):
    """Base exception for Vox errors."""
    pass


class HotkeyError(VoxError):
    """Hotkey registration or listening error."""
    pass


class HotkeyAlreadyRegisteredError(HotkeyError):
    """Attempted to register an already registered hotkey."""
    pass


class RecordingError(VoxError):
    """Audio recording error."""
    pass


class TranscriptionError(VoxError):
    """Speech-to-text transcription error."""
    pass


class PasteError(VoxError):
    """Clipboard or paste simulation error."""
    pass
```

---

## Event Flow

```
User presses hotkey (Ctrl+Alt+Space) - START RECORDING
    │
    ▼
HotkeyManager.callback()
    │
    ▼
VoiceInputController.trigger_recording()
    │
    ├── state → RECORDING
    ├── RecordingIndicator.show("recording")
    │
    ▼
MicrophoneRecorder.start_recording()
    │
    ├── (user speaks)
    ├── (recording continues until hotkey pressed again)
    │
    ▼
User presses hotkey again (Ctrl+Alt+Space) - STOP RECORDING
    │
    ▼
MicrophoneRecorder.stop_recording()
    │
    ├── state → TRANSCRIBING
    ├── RecordingIndicator.update_state("processing")
    │
    ▼
STTEngine.transcribe(audio)
    │
    ├── state → PASTING
    ├── RecordingIndicator.update_state("success")
    │
    ▼
ClipboardPaster.paste_text(result)
    │
    ├── VoxDatabase.add_transcription(result)
    │
    ▼
RecordingIndicator.hide()
    │
    ├── state → IDLE
    │
    ▼
Done

--- CANCEL FLOW ---

User presses Escape (during recording)
    │
    ▼
VoiceInputController.cancel_recording()
    │
    ├── MicrophoneRecorder.stop_recording()
    ├── (audio discarded, no transcription)
    ├── RecordingIndicator.hide()
    ├── state → IDLE
    │
    ▼
Done (no paste)
```
