# Implementation Plan: Hotkey Voice Input

**Branch**: `004-hotkey-voice-input` | **Date**: 2026-01-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-hotkey-voice-input/spec.md`

## Summary

Transform the vox CLI tool into a Windows 11 desktop application that listens for a global hotkey (Ctrl+Alt+Space), records voice input until the hotkey is pressed again (toggle mode), transcribes it using the existing STT module, and pastes the result at the current cursor position. The app includes a settings UI and transcription history with copy functionality.

**Key Behavior**: Hotkey toggle mode (press to start, press again to stop and transcribe). No silence detection.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: 
- Existing: faster-whisper, sounddevice, scipy, colorama
- New: pynput (global hotkeys + keyboard simulation), pyperclip (clipboard), ttkbootstrap (modern GUI)  
**Storage**: SQLite (vox.db for settings + transcription history)  
**Testing**: pytest with >80% coverage requirement  
**Target Platform**: Windows 11 only  
**Project Type**: Desktop application with background hotkey listening  
**Performance Goals**: <500ms hotkey response, <5s end-to-end transcription cycle  
**Constraints**: Must reuse existing `src/stt/` module, keep TTS siloed  
**Scale/Scope**: Single-user desktop utility

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Test-First Development | ✅ PASS | Unit tests required for all new functions |
| Clear API Contracts | ✅ PASS | Contracts defined in `/contracts/` |
| Simplicity & Clarity (YAGNI) | ✅ PASS | No over-engineering, reusing existing STT |
| Modular Design | ✅ PASS | New modules: `hotkey/`, `ui/`, `clipboard/`, `persistence/` |
| DRY | ✅ PASS | Reusing existing recorder, transcriber, engine |
| KISS | ✅ PASS | tkinter (stdlib) + SQLite (stdlib) - minimal new deps |
| ≥80% Coverage | ✅ PASS | Required for all new code |
| SOLID | ✅ PASS | Single responsibility per module |

**Post-Design Re-Check**: ✅ All gates pass - design uses minimal dependencies, reuses existing STT infrastructure, maintains modularity.

## Project Structure

### Documentation (this feature)

```text
specs/004-hotkey-voice-input/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md           # Internal module contracts
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── main.py              # MODIFY: Add desktop app entry point
├── config.py            # MODIFY: Add hotkey/UI settings
├── stt/                 # REUSE: Existing STT module (minimal changes)
│   ├── engine.py        # Whisper model loading
│   ├── recorder.py      # Microphone recording (remove silence detection dependency)
│   ├── transcriber.py   # Orchestration
│   └── ...
├── tts/                 # KEEP: Siloed, not integrated
├── hotkey/              # NEW: Global hotkey management
│   ├── __init__.py
│   └── manager.py       # HotkeyManager class (toggle state tracking, uses pynput listener internally)
├── ui/                  # NEW: User interface components
│   ├── __init__.py
│   ├── indicator.py     # Translucent pill overlay
│   ├── main_window.py   # Settings + history window
│   └── styles.py        # ttkbootstrap theme config
├── clipboard/           # NEW: Clipboard and paste operations
│   ├── __init__.py
│   └── paster.py        # ClipboardPaster class
├── persistence/         # NEW: Settings and history storage
│   ├── __init__.py
│   ├── database.py      # SQLite wrapper
│   └── models.py        # Data models (TranscriptionRecord, Settings)
└── voice_input/         # NEW: Integration controller
    ├── __init__.py
    └── controller.py    # VoiceInputController (toggle state machine)

tests/
├── unit/
│   ├── test_hotkey_manager.py
│   ├── test_clipboard_paster.py
│   ├── test_database.py
│   ├── test_indicator.py
│   └── test_voice_controller.py
├── integration/
│   └── test_voice_input_flow.py
└── ...
```

**Structure Decision**: Single project with new modules added alongside existing structure. The existing `stt/` module is reused with minimal modification (remove silence detection as stop trigger). TTS functionality remains siloed in `tts/`.

## Complexity Tracking

> No violations - design follows all constitution principles.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| GUI Framework | tkinter + ttkbootstrap | Stdlib + minimal dep, fast launch |
| Storage | SQLite | Stdlib, efficient queries for history |
| Hotkeys | pynput | No admin required, mature library |
| Overlay | tkinter Toplevel | Reuse same framework as main window |
| Recording Stop | Hotkey toggle | User-requested; simpler than silence detection |

## Key Design Decisions

### Hotkey Toggle Behavior

Recording is controlled exclusively by hotkey toggle:
- **First press**: Start recording, show indicator
- **Second press**: Stop recording, transcribe, paste result, hide indicator
- **Escape during recording**: Cancel without transcribing

No automatic silence detection or timeout. User has full control.

### State Machine

```
IDLE ─────[hotkey]────→ RECORDING
  ↑                         │
  │                         │ [hotkey]
  │                         ↓
  │                    TRANSCRIBING
  │                         │
  │                         │ [success]
  │                         ↓
  └────────────────────  PASTING ────→ IDLE

RECORDING ───[Escape]───→ IDLE (cancel, no paste)
```
