# Implementation Plan: Speech-to-Text Integration & Project Documentation Enhancement

**Branch**: `003-speech-to-text` | **Date**: 2026-01-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-speech-to-text/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements four major components: (1) **Project Rebranding** from "vox" to "vox" to reflect bidirectional audio-text capabilities, (2) **Developer Documentation** with AI agent guidelines and project architecture overview, (3) **User-Focused README** emphasizing installation and usage, and (4) **Speech-to-Text Integration** enabling voice recording via `vox transcribe` command with Whisper-powered offline transcription. Technical approach uses OpenAI Whisper via faster-whisper library (medium model) for 95%+ accuracy, sounddevice for microphone capture, Enter key for manual stop, 5-second silence detection as fallback, and terminal display as default output.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: 
- Existing: Pillow (image processing), NumPy (numerical computation), Pandas (data analysis), pytest (testing), piper-tts (TTS), pywinauto (browser automation), pygame (audio playback)
- New for STT: faster-whisper (Whisper speech-to-text), sounddevice or pyaudio (microphone capture), numpy (audio processing)

**Storage**: File-based (screenshot files, extracted text output, optional transcription output files)  
**Testing**: pytest with ≥80% coverage requirement (critical paths require 95%+)  
**Target Platform**: Windows 11 (desktop application)  
**Project Type**: Single CLI tool (rebranding from vox to vox)  
**Performance Goals**: 
- Existing TTS: <500ms workflow
- New STT: <10 seconds transcription time for 1 minute audio (Whisper medium model)
- 95%+ word accuracy for clear English speech

**Constraints**: 
- Must handle Windows desktop screen capture reliably
- Must work offline (no cloud APIs or API keys)
- Must use system default microphone (Windows Sound settings)
- Must preserve backward compatibility for existing TTS sessions during rebranding

**Scale/Scope**: Single-user desktop utility supporting:
- Text-to-speech: reading from active windows, URLs, and saved screenshots
- Speech-to-text: voice recording and transcription via CLI
- CLI commands: `vox read --url <url>` for TTS, `vox transcribe` for STT

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Test-First Development** | ✅ PASS | Spec requires pytest with ≥80% coverage (95%+ for critical paths). Red-Green-Refactor cycle mandated. Unit tests required for STT functions, integration tests for end-to-end TTS+STT workflows. |
| **II. Text-Based I/O Protocol** | ✅ PASS | STT outputs transcribed text to stdout (terminal display default), supports file output via `--output` flag. Follows read-process-output pattern. Errors to stderr. |
| **III. Clear API Contracts** | ✅ PASS | Spec defines clear contracts: FR-STT-001 through FR-STT-010, FR-RB-001 through FR-RB-008. Input (microphone audio), output (transcribed text), side effects (file writing) documented. |
| **IV. Semantic Versioning** | ✅ PASS | Rebranding constitutes MAJOR version bump (breaking change to CLI interface: vox → vox). STT feature is MINOR addition. Constitution requires SemVer compliance. |
| **V. Simplicity & Clarity** | ✅ PASS | Whisper medium model chosen for balance (not over-engineered). Enter key for stop (simple UX). System default mic (no complex selection UI). YAGNI followed. |

### Code Quality Standards Compliance

| Standard | Status | Notes |
|----------|--------|-------|
| **Test Coverage** | ✅ PASS | Spec mandates 80% minimum, 95%+ for critical paths (STT transcription, TTS playback). Coverage gates enforced. |
| **SOLID Principles** | ✅ PASS | Modular design: separate STT module (src/stt/), clear separation from TTS (src/tts/). Single Responsibility maintained. |
| **DRY** | ✅ PASS | Audio processing utilities can be shared between TTS and STT. Rebranding follows systematic refactoring (no manual duplication). |
| **KISS** | ✅ PASS | Straightforward Whisper integration via faster-whisper. Simple recording stop (Enter key). No premature optimization. |
| **Import Organization** | ✅ PASS | Standard 3-group import structure (stdlib, third-party, local) enforced by ruff. |

### Python Environment Setup

| Requirement | Status | Notes |
|-------------|--------|-------|
| **UV Dependency Management** | ✅ PASS | Constitution mandates uv for dependency management. New dependencies (faster-whisper, sounddevice) added via `uv pip install`. |
| **Python 3.13+** | ✅ PASS | Project requires Python 3.13+. All dependencies compatible. |
| **Windows 11 Platform** | ✅ PASS | Target platform unchanged. Microphone access via Windows Sound settings. |

### Development Standards

| Standard | Status | Notes |
|----------|--------|-------|
| **pytest Testing** | ✅ PASS | All new STT code requires pytest unit tests and integration tests. |
| **ruff Linting** | ✅ PASS | Code quality enforced via ruff for new STT module and rebranding changes. |
| **pyproject.toml** | ✅ PASS | Dependencies managed in pyproject.toml. Project name update: vox → vox. |

### Versioning & Release Policy

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Conventional Commits** | ✅ PASS | All commits follow Conventional Commits. Rebranding is breaking change (MAJOR), STT is feature (MINOR). |
| **commitizen** | ✅ PASS | Automated version bumping via commitizen. Version updated in pyproject.toml. |
| **GitHub Actions CI/CD** | ✅ PASS | Existing CI/CD pipeline covers linting, testing. New STT code passes same gates. |

### Gate Evaluation

**Result**: ✅ **ALL GATES PASS** - No constitution violations. Proceed to Phase 0 research.

All constitutional principles are satisfied:
- Test-first development with coverage gates enforced
- Text-based I/O for STT (stdout/file output)
- Clear API contracts for all STT requirements
- Semantic versioning followed (MAJOR bump for rebranding)
- Simplicity maintained (Whisper medium model, Enter key stop, system default mic)
- SOLID/DRY/KISS principles upheld
- UV/pytest/ruff tooling compliance
- Conventional commits and CI/CD enforcement

## Project Structure

### Documentation (this feature)

```text
specs/003-speech-to-text/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── cli-commands.md  # vox read and vox transcribe contracts
│   └── stt-api.md       # STT module API contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── config.py            # [MODIFY] Update project name references
├── main.py              # [MODIFY] Rebrand CLI, add vox transcribe command
├── browser/             # [EXISTING] Browser tab detection (unchanged)
│   ├── __init__.py
│   ├── accessibility.py
│   ├── detector.py
│   └── tab_info.py
├── extraction/          # [EXISTING] Text extraction from URLs/HTML (unchanged)
│   ├── __init__.py
│   ├── content_filter.py
│   ├── dom_walker.py
│   ├── file_loader.py
│   ├── html_parser.py
│   ├── text_extractor.py
│   └── url_fetcher.py
├── session/             # [EXISTING] TTS session management (unchanged)
│   ├── __init__.py
│   ├── manager.py
│   └── models.py
├── stt/                 # [NEW] Speech-to-text module
│   ├── __init__.py
│   ├── engine.py        # Whisper/faster-whisper wrapper
│   ├── recorder.py      # Microphone audio capture (sounddevice)
│   ├── transcriber.py   # Main transcription orchestrator
│   └── audio_utils.py   # Silence detection, audio processing
├── tts/                 # [EXISTING] Text-to-speech (Piper TTS)
│   ├── __init__.py
│   ├── chunking.py
│   ├── controller.py
│   ├── piper_provider.py
│   ├── playback.py
│   └── synthesizer.py
├── ui/                  # [EXISTING] UI components (unchanged)
│   └── __init__.py
└── utils/               # [EXISTING] Shared utilities
    ├── __init__.py
    ├── errors.py        # [MODIFY] Add STT-specific exceptions
    └── logging.py

tests/
├── __init__.py
├── contract/            # [NEW] Contract tests for CLI commands
│   ├── test_cli_vox_read.py
│   └── test_cli_vox_transcribe.py
├── integration/         # [EXISTING + NEW] End-to-end tests
│   ├── test_tts_workflow.py          # [EXISTING]
│   └── test_stt_workflow.py          # [NEW]
└── unit/                # [EXISTING + NEW] Unit tests
    ├── test_extraction/               # [EXISTING]
    ├── test_tts/                      # [EXISTING]
    └── test_stt/                      # [NEW]
        ├── test_engine.py
        ├── test_recorder.py
        ├── test_transcriber.py
        └── test_audio_utils.py

# Root-level files to modify for rebranding
pyproject.toml           # [MODIFY] name: vox → vox, add faster-whisper/sounddevice deps
README.md                # [OVERHAUL] User-focused: what/install/usage/troubleshooting
.specify/memory/
└── claude.md or agents  # [NEW] AI agent guidelines, architecture overview
docs/
└── BUILD.md             # [EXISTING] Build instructions (update for vox)
scripts/
└── build_exe.py         # [MODIFY] Update executable name: vox.exe → vox.exe
```

**Structure Decision**: Single project structure maintained (Option 1). New `src/stt/` module added alongside existing `src/tts/` for separation of concerns. Rebranding touches multiple files but preserves existing architecture. Tests mirror source structure with new `test_stt/` and `test_cli_vox_transcribe.py` for STT coverage.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: ✅ **NO VIOLATIONS** - No complexity tracking required. All constitutional requirements satisfied.

---

## Post-Design Constitution Review

*Re-evaluation after Phase 1 design (data model, contracts, quickstart) completion.*

### Design Verification

All Phase 1 artifacts have been generated and reviewed:
- ✅ [data-model.md](data-model.md): 6 entities defined (VoiceRecording, TranscriptionResult, MicrophoneDevice, STTEngine, RenamingStrategy, ConfigMigration)
- ✅ [contracts/stt-cli.md](contracts/stt-cli.md): CLI command contracts for `vox read` and `vox transcribe`
- ✅ [contracts/rebranding.md](contracts/rebranding.md): Rebranding contracts for file updates and migrations
- ✅ [quickstart.md](quickstart.md): Developer quickstart guide
- ✅ [research.md](research.md): Technology decisions documented

### Constitution Compliance Post-Design

| Principle | Post-Design Status | Notes |
|-----------|-------------------|-------|
| **Test-First Development** | ✅ MAINTAINED | Quickstart includes test-first workflow. Data model includes testable validation rules. |
| **Text-Based I/O** | ✅ MAINTAINED | STT contracts specify stdout output, file output via `--output` flag. Clean CLI interface. |
| **Clear API Contracts** | ✅ MAINTAINED | All entities have well-defined attributes, validation rules, relationships. CLI contracts specify inputs/outputs/exit codes. |
| **Semantic Versioning** | ✅ MAINTAINED | Rebranding contracts specify MAJOR version bump (2.x → 3.0.0) for breaking CLI change. |
| **Simplicity** | ✅ MAINTAINED | Data model avoids over-engineering. 6 entities, simple relationships, straightforward state transitions. |

### New Dependencies Review

| Dependency | Purpose | Constitution Impact |
|------------|---------|---------------------|
| `faster-whisper` | STT engine | ✅ Offline (no cloud APIs), well-documented, active maintenance |
| `sounddevice` | Microphone capture | ✅ Cross-platform, simple API, no external services |
| `numpy` | Audio processing | ✅ Already dependency for existing features |

**Verdict**: ✅ **All new dependencies align with offline-first, simplicity principles.**

### Architecture Review

**Single Project Structure Maintained**:
- New `src/stt/` module added alongside `src/tts/`
- Clean separation of concerns (SOLID: Single Responsibility)
- No architectural complexity violations
- Test structure mirrors source structure

**Modular Design**:
- STT module independent from TTS module
- Shared utilities in `src/utils/` (DRY principle)
- Clear interfaces between recorder, engine, transcriber

### Testing Strategy Compliance

From [quickstart.md](quickstart.md):
- ✅ Test-first workflow documented
- ✅ Unit test coverage requirements specified (≥80%, 95%+ for critical paths)
- ✅ Integration test patterns defined
- ✅ Mocking strategies for external dependencies (sounddevice, faster_whisper)

### Final Gate Evaluation

**Result**: ✅ **ALL GATES CONTINUE TO PASS POST-DESIGN**

No new constitution violations introduced by Phase 1 design decisions:
- Modular architecture preserved
- Test-first approach reinforced in quickstart
- Text-based I/O contracts clearly defined
- Semantic versioning properly applied to rebranding
- Simplicity maintained across data model and contracts
- All SOLID/DRY/KISS principles upheld

**Ready to proceed to Phase 2** (task breakdown via `/speckit.tasks` command).

---

## Phase Completion Summary

### Phase 0: Research ✅ Complete
- Technology decisions made and documented
- All unknowns resolved
- Best practices identified

### Phase 1: Design ✅ Complete
- Data model: 6 entities with validation rules
- Contracts: CLI commands, rebranding strategy
- Quickstart: Developer implementation guide
- Agent context updated (GitHub Copilot)

### Next Steps
Run `/speckit.tasks` to generate task breakdown (tasks.md) for implementation.

---

## Artifacts Generated

| Artifact | Path | Status |
|----------|------|--------|
| Implementation Plan | [plan.md](plan.md) | ✅ Complete |
| Research | [research.md](research.md) | ✅ Complete |
| Data Model | [data-model.md](data-model.md) | ✅ Complete |
| Quickstart Guide | [quickstart.md](quickstart.md) | ✅ Complete |
| STT CLI Contracts | [contracts/stt-cli.md](contracts/stt-cli.md) | ✅ Complete |
| Rebranding Contracts | [contracts/rebranding.md](contracts/rebranding.md) | ✅ Complete |
| Agent Context | [.github/agents/copilot-instructions.md](../../.github/agents/copilot-instructions.md) | ✅ Updated |
