# Data Model: Hotkey Voice Input

**Feature**: 004-hotkey-voice-input  
**Date**: 2026-01-21

## Overview

This document defines the data entities, relationships, and storage schema for the hotkey voice input feature.

---

## Entities

### 1. TranscriptionRecord

Represents a single completed voice transcription.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `text` | TEXT | NOT NULL | Transcribed text content |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When transcription occurred |
| `duration_seconds` | REAL | NULLABLE | Audio recording duration |
| `word_count` | INTEGER | NULLABLE | Number of words in transcription |

**Validation Rules**:
- `text` must not be empty
- `duration_seconds` must be positive if provided
- `word_count` computed as `len(text.split())`

---

### 2. UserSettings

Key-value store for user preferences.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `key` | TEXT | PRIMARY KEY | Setting identifier |
| `value` | TEXT | NOT NULL | Setting value (JSON-encoded if complex) |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification time |

**Default Settings**:
| Key | Default Value | Description |
|-----|---------------|-------------|
| `hotkey` | `<ctrl>+<alt>+space` | Activation hotkey combination (toggle: press to start, press again to stop) |
| `restore_clipboard` | `true` | Restore clipboard after paste |

---

### 3. ApplicationState (Runtime Only)

Tracks the current state of the application. Not persisted.

| State | Description |
|-------|-------------|
| `IDLE` | Application running, waiting for hotkey |
| `RECORDING` | Actively recording voice input |
| `TRANSCRIBING` | Processing audio through Whisper |
| `PASTING` | Copying to clipboard and simulating paste |
| `ERROR` | Error state, awaiting recovery |

**State Transitions**:
```
IDLE → RECORDING (hotkey pressed)
RECORDING → TRANSCRIBING (hotkey pressed again to stop)
RECORDING → IDLE (cancelled via Escape)
TRANSCRIBING → PASTING (transcription successful)
TRANSCRIBING → ERROR (transcription failed)
PASTING → IDLE (paste complete)
ERROR → IDLE (error acknowledged)
```

---

## Database Schema (SQLite)

### DDL

```sql
-- Settings table (key-value store)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transcription history table
CREATE TABLE IF NOT EXISTS transcription_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL,
    word_count INTEGER
);

-- Index for efficient history queries (newest first)
CREATE INDEX IF NOT EXISTS idx_history_created 
    ON transcription_history(created_at DESC);
```

### Storage Location

```
%APPDATA%/vox/
├── vox.db              # SQLite database
└── models/             # Existing Whisper model cache
```

---

## Data Access Patterns

### Settings Operations

| Operation | Query |
|-----------|-------|
| Get setting | `SELECT value FROM settings WHERE key = ?` |
| Set setting | `INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)` |
| Get all settings | `SELECT key, value FROM settings` |

### History Operations

| Operation | Query |
|-----------|-------|
| Add transcription | `INSERT INTO transcription_history (text, duration_seconds, word_count) VALUES (?, ?, ?)` |
| Get recent history | `SELECT id, text, created_at, word_count FROM transcription_history ORDER BY created_at DESC LIMIT ? OFFSET ?` |
| Get transcription by ID | `SELECT text FROM transcription_history WHERE id = ?` |
| Delete transcription | `DELETE FROM transcription_history WHERE id = ?` |
| Clear all history | `DELETE FROM transcription_history` |
| Count history | `SELECT COUNT(*) FROM transcription_history` |

---

## Python Data Classes

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum, auto


class AppState(Enum):
    """Application state enumeration."""
    IDLE = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    PASTING = auto()
    ERROR = auto()


@dataclass
class TranscriptionRecord:
    """Represents a completed transcription."""
    id: Optional[int]
    text: str
    created_at: datetime
    duration_seconds: Optional[float] = None
    word_count: Optional[int] = None
    
    def __post_init__(self):
        if self.word_count is None and self.text:
            self.word_count = len(self.text.split())


@dataclass
class UserSettings:
    """User preferences container."""
    hotkey: str = "<ctrl>+<alt>+space"
    restore_clipboard: bool = True
    
    def to_dict(self) -> dict:
        return {
            "hotkey": self.hotkey,
            "restore_clipboard": self.restore_clipboard,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        return cls(
            hotkey=data.get("hotkey", "<ctrl>+<alt>+space"),
            restore_clipboard=data.get("restore_clipboard", "true").lower() == "true",
        )
```

---

## Relationships

```
UserSettings (1) ←──── uses ────→ (1) HotkeyManager
                                        │
                                        │ triggers
                                        ▼
                                  VoiceInputController
                                        │
                                        │ creates
                                        ▼
                              TranscriptionRecord (*)
                                        │
                                        │ stored in
                                        ▼
                                  transcription_history table
```

---

## Migration Strategy

This is a new feature - no migration from existing data structures needed.

**Initial Data**:
- Insert default settings on first launch
- History table starts empty

```python
def init_defaults(db: VoxDatabase):
    """Initialize default settings if not present."""
    defaults = UserSettings()
    for key, value in defaults.to_dict().items():
        if db.get_setting(key) is None:
            db.set_setting(key, str(value))
```
