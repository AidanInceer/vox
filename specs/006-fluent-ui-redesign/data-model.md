# Data Model: Fluent UI Redesign

**Branch**: `006-fluent-ui-redesign`
**Date**: January 24, 2026
**Spec**: [spec.md](./spec.md)

## Overview

This feature primarily involves UI styling and layout changes. The data model additions are minimal, focused on persisting user preferences for theme and model/voice settings.

---

## Entities

### ThemeSettings (New)

Settings for the visual theme, stored in the database.

| Field | Type   | Default | Description                      |
| ----- | ------ | ------- | -------------------------------- |
| theme | string | "light" | Current theme: "light" or "dark" |

**Storage**: Database settings table (key-value)

```python
# Stored as:
db.set_setting("theme", "light")  # or "dark"
```

---

### ModelVoiceSettings (Extended)

Extended settings for STT model and TTS voice/speed. These already exist in `config.json` but need UI exposure.

| Field     | Type   | Default               | Description                                                         |
| --------- | ------ | --------------------- | ------------------------------------------------------------------- |
| stt_model | string | "medium"              | Whisper model: tiny, base, small, medium, large, large-v2, large-v3 |
| tts_voice | string | "en_US-libritts-high" | Piper TTS voice identifier                                          |
| tts_speed | float  | 1.0                   | Playback speed: 0.5 to 2.0                                          |

**Storage**: User config file (`%APPDATA%/vox/config.json`)

**Existing Functions** (no changes needed):

- `config.get_stt_default_model()` → returns model string
- `config.set_stt_default_model(model)` → saves model
- `config.load_user_config()` → full config dict
- `config.save_user_config(config)` → persists changes

---

### TabItem (UI Component)

Represents a navigation tab in the UI (no persistence).

| Field       | Type   | Description                                     |
| ----------- | ------ | ----------------------------------------------- |
| id          | string | Tab identifier: "status", "settings", "history" |
| icon        | string | Unicode icon symbol                             |
| label       | string | Display text                                    |
| is_selected | bool   | Currently active                                |

**Storage**: Runtime only (UI state)

---

### Card (UI Component)

Container component for grouping related content (no persistence).

| Field         | Type   | Description                         |
| ------------- | ------ | ----------------------------------- |
| title         | string | Card header text                    |
| content       | Widget | Child widgets                       |
| shadow_offset | int    | Shadow depth in pixels (default: 4) |

**Storage**: Runtime only (UI state)

---

## State Changes

### Settings Tab State

New UI state for the Settings tab:

```python
@dataclass
class SettingsTabState:
    """State for settings tab controls."""
    hotkey: str
    restore_clipboard: bool
    theme: str  # NEW: "light" or "dark"
    stt_model: str  # NEW: model name
    tts_voice: str  # NEW: voice identifier
    tts_speed: float  # NEW: 0.5-2.0
```

---

## Validation Rules

### Theme

- Must be one of: "light", "dark"

### STT Model

- Must be one of: "tiny", "base", "small", "medium", "large", "large-v2", "large-v3"
- Validated by existing `config.VALID_STT_MODELS`

### TTS Speed

- Range: 0.5 to 2.0
- Step: 0.1

---

## Relationships

```
┌─────────────────┐
│   VoxDatabase   │
│ (settings table)│
└────────┬────────┘
         │ stores
         ▼
┌─────────────────┐     ┌─────────────────┐
│  ThemeSettings  │     │ config.json     │
│  - theme        │     │ - stt_model     │
└─────────────────┘     │ - tts_voice     │
                        │ - tts_speed     │
                        └─────────────────┘
                              │
                              │ read/write
                              ▼
                    ┌─────────────────────┐
                    │  Settings Tab UI    │
                    │  - Appearance card  │
                    │  - Model & Voice    │
                    └─────────────────────┘
```

---

## Migration

No database schema changes required. Theme setting will be automatically created on first access:

```python
# Graceful default handling (already supported)
theme = database.get_setting("theme", "light")  # Returns "light" if not set
```
