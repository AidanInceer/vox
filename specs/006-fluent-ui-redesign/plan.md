# Implementation Plan: Fluent UI Redesign for Windows 11

**Branch**: `006-fluent-ui-redesign` | **Date**: January 24, 2026 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-fluent-ui-redesign/spec.md`

## Summary

Modernize the Vox desktop application UI to follow Windows 11 Fluent Design principles. Key changes include:

- Restyled top tabs with rounded indicators and icons
- Elevated card components with drop shadows replacing LabelFrame
- Manual light/dark theme toggle with runtime switching
- STT model slider (Faster↔More Accurate) and TTS speed controls
- 8px grid spacing system and Fluent type scale
- Hover-reveal actions on history items

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**:

- ttkbootstrap (UI theming - `cosmo` for light, `darkly` for dark)
- piper-tts (text-to-speech)
- faster-whisper (speech-to-text)
- pynput (global hotkeys)

**Storage**: SQLite database (`src/persistence/database.py`) + JSON config (`config.json`)
**Testing**: pytest with >80% coverage requirement
**Target Platform**: Windows 11 (Windows 10 fallback)
**Project Type**: Desktop GUI application
**Performance Goals**: Theme switch <100ms, no UI blocking
**Constraints**: No new dependencies beyond existing ttkbootstrap

**Current UI Files**:
| File | Lines | Refactoring Needed |
|------|-------|-------------------|
| src/ui/main_window.py | 857 | Significant - replace layouts, use new components |
| src/ui/styles.py | 133 | Moderate - update colors, fonts, spacing |
| src/ui/components/base.py | ~50 | Minor - ensure compatible with new components |

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle               | Status      | Notes                                                     |
| ----------------------- | ----------- | --------------------------------------------------------- |
| Test-First Development  | ✅ Pass     | Unit tests required for all new components                |
| Text-Based I/O Protocol | ✅ N/A      | UI feature, no CLI changes                                |
| Clear API Contracts     | ✅ Pass     | Contracts defined in `contracts/ui-components.md`         |
| Semantic Versioning     | ✅ Pass     | MINOR version bump (new feature, non-breaking)            |
| Simplicity & Clarity    | ✅ Pass     | Using existing ttkbootstrap, no framework change          |
| Code Quality (≥80%)     | ✅ Required | Must maintain coverage on new components                  |
| SOLID Principles        | ✅ Pass     | Components follow SRP, composable design                  |
| DRY                     | ✅ Pass     | Reusable components (FluentCard, sliders, etc.)           |
| KISS                    | ✅ Pass     | Unicode icons (no icon library), simple shadow simulation |
| Import Organization     | ✅ Pass     | Standard import ordering enforced by ruff                 |

**Post-Design Re-check**: ✅ All gates pass. No complexity violations.

## Project Structure

### Documentation (this feature)

```text
specs/006-fluent-ui-redesign/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output (complete)
├── data-model.md        # Phase 1 output (complete)
├── quickstart.md        # Phase 1 output (complete)
├── contracts/           # Phase 1 output (complete)
│   └── ui-components.md # Component interfaces
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── config.py            # [EXISTING] STT/TTS settings (no changes needed)
├── main.py              # [EXISTING] App entry (no changes)
├── persistence/
│   └── database.py      # [EXISTING] Settings storage (no changes needed)
└── ui/
    ├── __init__.py      # [MODIFY] Export new components
    ├── styles.py        # [MODIFY] Fluent colors, fonts, spacing, theme switch
    ├── main_window.py   # [MODIFY] Refactor all tabs with Fluent components
    ├── indicator.py     # [MINOR] Update colors to match theme
    ├── system_tray.py   # [EXISTING] No changes
    ├── events.py        # [EXISTING] No changes
    ├── mixins/          # [EXISTING] No changes
    └── components/
        ├── __init__.py  # [MODIFY] Export new components
        ├── base.py      # [EXISTING] Base component
        ├── card.py      # [NEW] FluentCard with shadow
        ├── model_slider.py    # [NEW] STT model selector
        ├── theme_toggle.py    # [NEW] Light/dark toggle
        ├── speed_slider.py    # [NEW] TTS speed control
        ├── keycap.py          # [NEW] Hotkey visual display
        ├── history_item.py    # [NEW] History entry card
        └── empty_state.py     # [NEW] Empty list placeholder

tests/
├── unit/
│   ├── test_ui_styles.py      # [NEW] Style/theme tests
│   └── test_ui_components.py  # [NEW] Component tests
└── integration/
    └── test_app_lifecycle.py  # [MODIFY] Add theme persistence tests
```

**Structure Decision**: Single project structure maintained. New components added under `src/ui/components/` following existing pattern.

## Complexity Tracking

> No violations - design follows all constitution principles.

| Aspect        | Decision                | Rationale                            |
| ------------- | ----------------------- | ------------------------------------ |
| GUI Framework | ttkbootstrap (existing) | No framework change per assumptions  |
| Shadow Effect | Canvas simulation       | Simple, performant, no external deps |
| Icons         | Unicode symbols         | No icon library dependency           |
| Theme Storage | SQLite settings         | Reuse existing VoxDatabase           |
| Model Config  | Existing config.py      | Functions already exist              |

## Phase Summary

| Phase   | Deliverables                             | Status                  |
| ------- | ---------------------------------------- | ----------------------- |
| Phase 0 | research.md                              | ✅ Complete             |
| Phase 1 | data-model.md, contracts/, quickstart.md | ✅ Complete             |
| Phase 2 | tasks.md                                 | ⏳ Run `/speckit.tasks` |
