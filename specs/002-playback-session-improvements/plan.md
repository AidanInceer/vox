# Implementation Plan: Enhanced Playback Controls and Performance

**Branch**: `002-playback-session-improvements` | **Date**: 2026-01-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-playback-session-improvements/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance PageReader with three major capabilities: (1) Session management allowing users to save and resume reading sessions with custom names via `--save-session` flag; (2) Interactive playback controls enabling real-time keyboard shortcuts (spacebar=pause/resume, Q=quit, arrows=navigate/speed); (3) Streaming text-to-speech with chunking to provide faster feedback by synthesizing and playing first 150-word chunk within 3 seconds while preparing subsequent chunks in background.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: 
- Core: requests, beautifulsoup4 (text extraction), piper-tts (TTS synthesis), colorama (CLI output)
- Session persistence: [NEEDS CLARIFICATION: JSON file storage vs SQLite database]
- Keyboard input: [NEEDS CLARIFICATION: pynput vs keyboard library vs msvcrt for Windows]
- Audio playback: winsound (current), [NEEDS CLARIFICATION: Need library supporting pause/resume/seek - pygame, sounddevice, or pydub]
- Background processing: threading (likely), [NEEDS CLARIFICATION: asyncio vs threading for chunk synthesis]

**Storage**: 
- Session data: [NEEDS CLARIFICATION: File location - %APPDATA%/PageReader/sessions/ vs user home directory]
- Session format: JSON (likely) with schema: session_id, name, url, extracted_text, playback_position, created_at, last_accessed
- Audio chunks: In-memory queue during playback (no persistent storage)

**Testing**: pytest with >80% coverage requirement  
**Target Platform**: Windows 11 (desktop application)  
**Project Type**: Single CLI tool (PageReader) with enhanced playback capabilities  
**Performance Goals**: 
- Session save/load: <2 seconds per operation
- Keyboard input response: <100ms latency
- First chunk synthesis: <3 seconds for articles up to 10,000 words
- Chunk transition: seamless with <50ms gaps

**Constraints**: 
- Must maintain compatibility with existing PageReader CLI interface
- Keyboard controls must work during audio playback without blocking
- Chunk synthesis must not interfere with smooth playback
- Session data must persist across application restarts

**Scale/Scope**: Single-user desktop utility, support for managing multiple named sessions and concurrent chunk synthesis (up to 50 chunks)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Test-First Development ✅
- **Status**: PASS
- **Requirements**: All features require test-first development with unit tests (>80% coverage) and integration tests for end-to-end workflows
- **Compliance**: 
  - Session management: Unit tests for save/load/list/resume operations
  - Playback controls: Unit tests for keyboard input handling and state management
  - Chunking: Unit tests for text splitting, queue management, and synthesis
  - Integration tests: Full workflow tests for each user story

### Text-Based I/O Protocol ✅
- **Status**: PASS
- **Requirements**: Text input/output, stdout for results, stderr for errors, support JSON output where applicable
- **Compliance**: 
  - CLI interface via argparse (existing pattern)
  - Session list output: human-readable text + optional JSON format
  - Playback status: stdout messages with colorama formatting
  - Errors: stderr with clear messages

### Clear API Contracts ✅
- **Status**: PASS
- **Requirements**: Documented inputs/outputs/side effects, pure functions when possible, explicit state tracking
- **Compliance**:
  - Session module: Clear contracts for SessionManager (save_session, load_session, list_sessions, resume_session)
  - Playback controller: Clear state management with PlaybackState dataclass
  - Chunking: Pure functions for text splitting, explicit queue state for synthesis

### Semantic Versioning ✅
- **Status**: PASS
- **Requirements**: MAJOR.MINOR.PATCH - this is MINOR (new features, non-breaking)
- **Compliance**: Current version 1.0.0 → 1.1.0 (adds new --save-session flag, list-sessions and resume commands)

### Simplicity & Clarity ✅
- **Status**: PASS
- **Requirements**: YAGNI, readable code, docstrings for all public functions
- **Compliance**:
  - Start with simple JSON file storage for sessions (no database unless needed)
  - Use standard library threading for background synthesis (no complex async framework unless required)
  - Clear module boundaries: session/, playback controls in tts/, chunking in tts/
  - All public functions documented with docstrings

### Code Quality Standards ✅
- **Status**: PASS
- **Requirements**: 80% coverage, SOLID principles, DRY, KISS, import organization
- **Compliance**:
  - Coverage: All new modules require ≥80% line coverage
  - SOLID: Single responsibility (SessionManager, PlaybackController, ChunkSynthesizer as separate concerns)
  - DRY: Shared utilities for file I/O, error handling
  - KISS: Simple solutions first (JSON over database, threading over asyncio initially)
  - Import organization: Standard lib → third-party → local (enforced by ruff)

**GATE RESULT**: ✅ **PASS** - All constitution requirements satisfied. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/002-playback-session-improvements/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── session-manager.md
│   ├── playback-controller.md
│   └── chunk-synthesizer.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── session/
│   ├── __init__.py
│   ├── models.py         # ReadingSession dataclass (existing)
│   └── manager.py        # NEW: SessionManager for save/load/list/resume
├── tts/
│   ├── __init__.py
│   ├── synthesizer.py    # MODIFY: PiperSynthesizer (existing)
│   ├── playback.py       # MODIFY: AudioPlayback with pause/resume/seek (existing)
│   ├── controller.py     # NEW: PlaybackController for keyboard input handling
│   └── chunking.py       # NEW: ChunkSynthesizer for streaming TTS
├── main.py               # MODIFY: Add --save-session flag, list-sessions/resume commands
└── config.py             # MODIFY: Add session storage path, chunk size constants

tests/
├── unit/
│   ├── test_session_manager.py    # NEW: Unit tests for SessionManager
│   ├── test_playback_controller.py # NEW: Unit tests for PlaybackController
│   ├── test_chunking.py           # NEW: Unit tests for ChunkSynthesizer
│   ├── test_tts_synthesizer.py    # MODIFY: Add chunk synthesis tests (existing)
│   └── test_models.py             # MODIFY: Add session serialization tests (existing)
└── integration/
    ├── test_session_workflow.py   # NEW: End-to-end session save/resume tests
    ├── test_playback_controls.py  # NEW: End-to-end playback control tests
    └── test_chunked_playback.py   # NEW: End-to-end chunking + playback tests
```

**Structure Decision**: Single project structure (Option 1). PageReader is a desktop CLI application with clear module separation for session management (src/session/), TTS/playback (src/tts/), and CLI interface (src/main.py). No web/mobile components required. Extends existing structure with new modules for session persistence, playback control, and chunking.

---

## Post-Phase 1 Constitution Check

*Re-evaluation after design completion (Phase 0 Research + Phase 1 Design)*

### Design Review ✅

**Technology Decisions** (from research.md):
- ✅ **Session storage**: JSON files (simple, human-readable, zero dependencies)
- ✅ **Keyboard input**: msvcrt stdlib (Windows-native, zero dependencies)
- ✅ **Audio playback**: pygame.mixer (ONE new dependency, mature library)
- ✅ **Background processing**: threading + queue stdlib (simple, sufficient)

**Architecture Review** (from data-model.md + contracts):
- ✅ **Clear separation of concerns**: SessionManager, PlaybackController, ChunkSynthesizer as independent modules
- ✅ **Well-defined contracts**: All public APIs documented with inputs, outputs, side effects, error handling
- ✅ **Testability**: All components have clear unit test boundaries and integration test scenarios
- ✅ **Thread safety**: Explicit synchronization via locks, queues, events (documented in contracts)

**Complexity Assessment**:
- ✅ **No unnecessary abstractions**: Direct file I/O, no ORM, no complex design patterns
- ✅ **YAGNI compliance**: No features beyond spec requirements
- ✅ **KISS compliance**: Simple solutions chosen (JSON over DB, threading over asyncio)

### Constitution Compliance ✅

All original checks remain **PASS**:
1. ✅ Test-First Development: Tests specified in all contracts, quickstart provides TDD guidance
2. ✅ Text-Based I/O: CLI interface, stdout/stderr, optional JSON output
3. ✅ Clear API Contracts: All 3 contracts complete with detailed documentation
4. ✅ Semantic Versioning: 1.0.0 → 1.1.0 (MINOR version bump, non-breaking)
5. ✅ Simplicity & Clarity: No over-engineering, clear module boundaries
6. ✅ Code Quality Standards: 80% coverage target, SOLID principles, ruff enforcement

### New Dependencies Assessment ✅

**Added**: pygame (2.6.0+) for audio playback with pause/resume/seek support

**Justification**: 
- Current winsound library lacks pause/resume/seek functionality (required by FR-006 through FR-011)
- pygame.mixer is the simplest Windows-compatible library providing required features
- Well-tested, mature library (20+ years), active community, excellent documentation
- No external binary dependencies (pure Python + SDL2 bundled)

**Alternatives rejected**:
- sounddevice: Too complex, requires manual buffer management
- pydub: Not designed for real-time control, requires ffmpeg/libav
- pyaudio: Complex streaming API, excessive for simple WAV playback

**Constitution compliance**: Single focused dependency, well-justified need, no bloat

### Final Gate Result ✅

**Status**: ✅ **PASS** - Design maintains constitution compliance

**Summary**:
- All technology decisions align with simplicity and clarity principles
- Architecture follows SOLID principles with clear separation of concerns
- One new dependency (pygame) is well-justified and minimal
- Test coverage and code quality standards maintained
- Ready to proceed to implementation (Phase 2)

**Phase 1 Complete**: All design artifacts generated (research.md, data-model.md, contracts/, quickstart.md)

---

## Phase 2 Preview (Not Implemented by /speckit.plan)

**Next steps** (execute via `/speckit.tasks` command):
1. Generate tasks.md with detailed implementation checklist
2. Break down contracts into specific code tasks
3. Create GitHub issues or project board items
4. Assign priorities and estimated effort

**Note**: `/speckit.plan` stops here. Implementation begins with Phase 2 tasks generation.

---

## Summary

**Branch**: 002-playback-session-improvements  
**Spec**: [spec.md](spec.md)  
**Status**: Planning complete (Phase 0 + Phase 1) ✅

**Artifacts Generated**:
- ✅ [plan.md](plan.md) - This file (technical context, constitution check, project structure)
- ✅ [research.md](research.md) - Technology decisions and best practices
- ✅ [data-model.md](data-model.md) - Entity definitions (ReadingSession, PlaybackState, AudioChunk, SessionIndex)
- ✅ [contracts/session-manager.md](contracts/session-manager.md) - SessionManager API contract
- ✅ [contracts/playback-controller.md](contracts/playback-controller.md) - PlaybackController API contract
- ✅ [contracts/chunk-synthesizer.md](contracts/chunk-synthesizer.md) - ChunkSynthesizer API contract
- ✅ [quickstart.md](quickstart.md) - Developer implementation guide with TDD workflow
- ✅ Agent context updated (.github/agents/copilot-instructions.md)

**Ready for**: Phase 2 implementation via `/speckit.tasks` command

---

**Planning Complete**: All Phase 0 (Research) and Phase 1 (Design) outputs generated successfully.
