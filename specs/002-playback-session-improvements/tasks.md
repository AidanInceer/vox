# Tasks: Enhanced Playback Controls and Performance

**Feature**: 002-playback-session-improvements  
**Input**: Design documents from `/specs/002-playback-session-improvements/`  
**Prerequisites**: ✅ plan.md, ✅ spec.md, ✅ research.md, ✅ data-model.md, ✅ contracts/

**Tests**: Tests included per TDD requirement from constitution (all features require test-first development)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths are absolute from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [X] T001 Install pygame dependency: `uv pip install pygame>=2.6.0`
- [X] T002 [P] Update pyproject.toml to add pygame to dependencies list
- [X] T003 [P] Add session storage path constant to src/config.py: `SESSION_STORAGE_DIR = Path(os.getenv("APPDATA")) / "vox" / "sessions"`
- [X] T004 [P] Add chunking constants to src/config.py: `DEFAULT_CHUNK_SIZE = 150`, `MAX_BUFFER_SIZE = 10`
- [X] T005 Verify pygame.mixer initialization works on Windows 11: `pytest tests/unit/test_pygame_init.py tests/unit/test_pygame_mixer.py -v`

**Checkpoint**: ✅ Dependencies installed, config updated - ready for module development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Enhance ReadingSession model in src/session/models.py with session_name field (unique identifier)
- [X] T007 [P] Add update_position() method to ReadingSession model in src/session/models.py
- [X] T008 [P] Create PlaybackState dataclass in src/tts/playback.py with fields: is_playing, is_paused, current_position_ms, playback_speed, current_chunk_index, chunk_buffer
- [X] T009 [P] Create AudioChunk dataclass in src/tts/chunking.py with fields: chunk_index, text_content, audio_data, duration_ms, synthesis_status

**Checkpoint**: ✅ All data models defined and tested - user story implementation can begin

---

## Phase 3: User Story 1 - Session Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to save reading sessions with custom names, list all sessions, resume from saved position, and delete sessions

**Independent Test**: Run `vox read --url https://example.com --save-session my-test`, verify session saved, run `vox list-sessions`, verify listed, run `vox resume my-test`, verify playback resumes

### Tests for User Story 1 (TDD - Write First)

> **TDD Workflow**: Write these tests FIRST, ensure they FAIL, then implement to make them PASS

- [X] T010 [P] [US1] Unit test for SessionManager.__init__() in tests/unit/test_session_manager.py (creates storage dir)
- [X] T011 [P] [US1] Unit test for SessionManager.save_session() with valid inputs in tests/unit/test_session_manager.py
- [X] T012 [P] [US1] Unit test for SessionManager.save_session() with invalid session_name (ValueError) in tests/unit/test_session_manager.py
- [X] T013 [P] [US1] Unit test for SessionManager.save_session() with duplicate name (ValueError) in tests/unit/test_session_manager.py
- [X] T014 [P] [US1] Unit test for SessionManager.load_session() with existing session in tests/unit/test_session_manager.py
- [X] T015 [P] [US1] Unit test for SessionManager.load_session() with non-existent session (ValueError) in tests/unit/test_session_manager.py
- [X] T016 [P] [US1] Unit test for SessionManager.list_sessions() with multiple sessions in tests/unit/test_session_manager.py
- [X] T017 [P] [US1] Unit test for SessionManager.delete_session() in tests/unit/test_session_manager.py
- [X] T018 [P] [US1] Unit test for SessionManager.session_exists() in tests/unit/test_session_manager.py
- [X] T019 [P] [US1] Integration test for full session workflow (save → list → resume) in tests/integration/test_session_workflow.py

**Run tests** (should FAIL): `pytest tests/unit/test_session_manager.py tests/integration/test_session_workflow.py -v`

### Implementation for User Story 1

- [X] T020 [P] [US1] Create SessionManager class skeleton in src/session/manager.py with __init__ method
- [X] T021 [US1] Implement SessionManager._validate_session_name() private method in src/session/manager.py
- [X] T022 [US1] Implement SessionManager._slugify() private method in src/session/manager.py
- [X] T023 [US1] Implement SessionManager._write_session_file() atomic write method in src/session/manager.py
- [X] T024 [US1] Implement SessionManager._write_index() and _read_index() methods in src/session/manager.py
- [X] T025 [US1] Implement SessionManager.save_session() method in src/session/manager.py (validation, JSON write, index update)
- [X] T026 [US1] Implement SessionManager.load_session() method in src/session/manager.py (read JSON, deserialize, update timestamp)
- [X] T027 [US1] Implement SessionManager.list_sessions() method in src/session/manager.py (read index, return list)
- [X] T028 [US1] Implement SessionManager.resume_session() method in src/session/manager.py (wrapper around load_session)
- [X] T029 [US1] Implement SessionManager.delete_session() method in src/session/manager.py (delete file, update index)
- [X] T030 [US1] Implement SessionManager.session_exists() method in src/session/manager.py (check index)
- [X] T031 [US1] Add error handling for file I/O errors in src/session/manager.py
- [X] T032 [US1] Add logging for session operations in src/session/manager.py

**Run tests** (should PASS): `pytest tests/unit/test_session_manager.py tests/integration/test_session_workflow.py -v`

### CLI Integration for User Story 1

- [X] T033 [US1] Add --save-session argument to read command in src/main.py create_parser()
- [X] T034 [US1] Add list-sessions subcommand to parser in src/main.py create_parser()
- [X] T035 [US1] Add resume subcommand with session_name arg to parser in src/main.py create_parser()
- [X] T036 [US1] Implement command_list_sessions() handler in src/main.py (calls SessionManager.list_sessions, formats output)
- [X] T037 [US1] Implement command_resume() handler in src/main.py (calls SessionManager.resume_session, starts playback)
- [X] T038 [US1] Update command_read() to save session if --save-session flag provided in src/main.py
- [X] T039 [US1] Add colorized output for session listing in src/main.py (cyan for name, normal for details)

**Manual Test**: `vox read --url https://example.com --save-session test-article`, `vox list-sessions`, `vox resume test-article`


**Checkpoint**: User Story 1 complete - session management fully functional and independently testable (Coverage target: >80%)

---

## Phase 4: User Story 2 - Interactive Playback Controls (Priority: P1)

**Goal**: Enable users to control audio playback in real-time with keyboard shortcuts (spacebar=pause/resume, Q=quit, arrows=navigate/speed)

**Independent Test**: Start playback with `vox read --url https://example.com`, press spacebar (pauses), press spacebar (resumes), press right arrow (skips forward), press up arrow (speed up), press Q (quits cleanly)

### Tests for User Story 2 (TDD - Write First)

> **TDD Workflow**: Write these tests FIRST, ensure they FAIL, then implement to make them PASS

- [X] T040 [P] [US2] Unit test for PlaybackController.__init__() in tests/unit/test_playback_controller.py
- [X] T041 [P] [US2] Unit test for PlaybackController.pause() state transition in tests/unit/test_playback_controller.py
- [X] T042 [P] [US2] Unit test for PlaybackController.resume() state transition in tests/unit/test_playback_controller.py
- [X] T043 [P] [US2] Unit test for PlaybackController.quit() graceful shutdown in tests/unit/test_playback_controller.py
- [X] T044 [P] [US2] Unit test for PlaybackController.seek() forward with bounds checking in tests/unit/test_playback_controller.py
- [X] T045 [P] [US2] Unit test for PlaybackController.seek() backward with bounds checking in tests/unit/test_playback_controller.py
- [X] T046 [P] [US2] Unit test for PlaybackController.adjust_speed() increase (clamped to 2.0x) in tests/unit/test_playback_controller.py
- [X] T047 [P] [US2] Unit test for PlaybackController.adjust_speed() decrease (clamped to 0.5x) in tests/unit/test_playback_controller.py
- [X] T048 [P] [US2] Unit test for PlaybackController.keyboard command queue processing in tests/unit/test_playback_controller.py
- [X] T049 [P] [US2] Unit test for debouncing rapid key presses in tests/unit/test_playback_controller.py
- [X] T050 [P] [US2] Integration test for playback control workflow (start → pause → resume → seek → quit) in tests/integration/test_playback_controls.py

**Run tests** (should FAIL): `pytest tests/unit/test_playback_controller.py tests/integration/test_playback_controls.py -v`

### Implementation for User Story 2

#### Update AudioPlayback for pygame.mixer

- [X] T051 [US2] Replace winsound with pygame.mixer initialization in src/tts/playback.py
- [X] T052 [US2] Implement AudioPlayback.play_audio() using pygame.mixer.music in src/tts/playback.py (MUST block until playback completes)
- [X] T053 [US2] Implement AudioPlayback.pause() method in src/tts/playback.py
- [X] T054 [US2] Implement AudioPlayback.resume() method in src/tts/playback.py
- [X] T055 [US2] Implement AudioPlayback.seek() method in src/tts/playback.py
- [X] T056 [US2] Implement AudioPlayback.stop() method in src/tts/playback.py
- [X] T057 [US2] Implement AudioPlayback.get_position() method in src/tts/playback.py
- [X] T058 [US2] Add error handling for pygame.mixer errors in src/tts/playback.py

#### Implement PlaybackController

- [X] T059 [P] [US2] Create PlaybackController class skeleton in src/tts/controller.py with __init__ method
- [X] T060 [US2] Implement PlaybackController.start() method in src/tts/controller.py (start playback + keyboard thread)
- [X] T061 [US2] Implement PlaybackController.pause() method in src/tts/controller.py (update state, call AudioPlayback.pause)
- [X] T062 [US2] Implement PlaybackController.resume() method in src/tts/controller.py (update state, call AudioPlayback.resume)
- [X] T063 [US2] Implement PlaybackController.seek() method in src/tts/controller.py (validate bounds, call AudioPlayback.seek)
- [X] T064 [US2] Implement PlaybackController.adjust_speed() method in src/tts/controller.py (clamp [0.5, 2.0], update state)
- [X] T065 [US2] Implement PlaybackController.quit() method in src/tts/controller.py (set shutdown_event, join threads)
- [X] T066 [US2] Implement PlaybackController._keyboard_input_thread() in src/tts/controller.py (msvcrt polling, key mapping)
- [X] T067 [US2] Implement PlaybackController._process_commands() in src/tts/controller.py (queue processing, command dispatch)
- [X] T068 [US2] Add threading.Lock for PlaybackState shared access in src/tts/controller.py
- [X] T069 [US2] Add 100ms debouncing for rapid key presses in src/tts/controller.py
- [X] T070 [US2] Add logging for playback control events in src/tts/controller.py

**Run tests** (should PASS): `pytest tests/unit/test_playback_controller.py tests/integration/test_playback_controls.py -v`

### CLI Integration for User Story 2

- [X] T071 [US2] Update command_read() to use PlaybackController instead of direct playback in src/main.py
- [X] T072 [US2] Add keyboard controls help text to CLI output in src/main.py (display at playback start)
- [X] T073 [US2] Save playback position to session on quit (if --save-session used) in src/main.py

**Manual Test**: `vox read --url https://example.com`, test all keyboard controls (space, Q, arrows)

**Checkpoint**: User Story 2 complete - playback controls fully functional and independently testable (Coverage target: >80%)

---

## Phase 5: User Story 3 - Streaming Text-to-Speech with Chunking (Priority: P2)

**Goal**: Provide faster feedback by chunking text (~150 words), synthesizing first chunk immediately (<3s), and synthesizing remaining chunks in background for seamless playback

**Independent Test**: Run `vox read --url <long-article-url>` (5000+ words), verify audio begins within 3 seconds, verify seamless transitions between chunks

### Tests for User Story 3 (TDD - Write First)

> **TDD Workflow**: Write these tests FIRST, ensure they FAIL, then implement to make them PASS

- [X] T074 [P] [US3] Unit test for ChunkSynthesizer.__init__() in tests/unit/test_chunking.py
- [X] T075 [P] [US3] Unit test for ChunkSynthesizer.prepare_chunks() with various text lengths in tests/unit/test_chunking.py
- [X] T076 [P] [US3] Unit test for ChunkSynthesizer.prepare_chunks() respects sentence boundaries in tests/unit/test_chunking.py
- [X] T077 [P] [US3] Unit test for ChunkSynthesizer.prepare_chunks() with text <50 words (single chunk) in tests/unit/test_chunking.py
- [X] T078 [P] [US3] Unit test for ChunkSynthesizer.synthesize_first_chunk() in tests/unit/test_chunking.py
- [X] T079 [P] [US3] Unit test for ChunkSynthesizer.start_background_synthesis() spawns threads in tests/unit/test_chunking.py
- [X] T080 [P] [US3] Unit test for ChunkSynthesizer.get_next_chunk() in tests/unit/test_chunking.py
- [X] T081 [P] [US3] Unit test for ChunkSynthesizer.synthesize_chunk_on_demand() in tests/unit/test_chunking.py
- [X] T082 [P] [US3] Unit test for ChunkSynthesizer buffer size limit (max 10 chunks) in tests/unit/test_chunking.py
- [X] T083 [P] [US3] Unit test for ChunkSynthesizer.stop() graceful shutdown in tests/unit/test_chunking.py
- [X] T084 [P] [US3] Integration test for chunked playback workflow (prepare → first chunk → background → playback) in tests/integration/test_chunked_playback.py
- [X] T085 [P] [US3] Performance test: Time to first audio <3s for 10,000 word article in tests/integration/test_chunked_playback.py
- [X] T086 [P] [US3] Performance test: Chunk transition gaps <50ms (95th percentile) in tests/integration/test_chunked_playback.py

**Run tests** (should FAIL): `pytest tests/unit/test_chunking.py tests/integration/test_chunked_playback.py -v`

### Implementation for User Story 3

- [X] T087 [P] [US3] Create ChunkSynthesizer class skeleton in src/tts/chunking.py with __init__ method
- [X] T088 [US3] Implement ChunkSynthesizer._split_into_sentences() private method in src/tts/chunking.py (regex-based)
- [X] T089 [US3] Implement ChunkSynthesizer._group_sentences_into_chunks() private method in src/tts/chunking.py (target 150 words)
- [X] T090 [US3] Implement ChunkSynthesizer.prepare_chunks() method in src/tts/chunking.py (split text, create AudioChunk instances)
- [X] T091 [US3] Implement ChunkSynthesizer.synthesize_first_chunk() method in src/tts/chunking.py (blocking synthesis)
- [X] T092 [US3] Implement ChunkSynthesizer._synthesis_worker_thread() private method in src/tts/chunking.py (background synthesis loop)
- [X] T093 [US3] Implement ChunkSynthesizer.start_background_synthesis() method in src/tts/chunking.py (spawn threads)
- [X] T094 [US3] Implement ChunkSynthesizer.get_next_chunk() method in src/tts/chunking.py (pop from buffer)
- [X] T095 [US3] Implement ChunkSynthesizer.synthesize_chunk_on_demand() method in src/tts/chunking.py (on-demand synthesis)
- [X] T096 [US3] Implement ChunkSynthesizer.stop() method in src/tts/chunking.py (shutdown threads, clear buffer)
- [X] T097 [US3] Implement ChunkSynthesizer.get_chunk_count() method in src/tts/chunking.py
- [X] T098 [US3] Implement ChunkSynthesizer.get_buffer_status() method in src/tts/chunking.py
- [X] T099 [US3] Add buffer management with 10-chunk limit in src/tts/chunking.py
- [X] T100 [US3] Add error handling for synthesis failures (mark chunk FAILED, continue) in src/tts/chunking.py
- [X] T101 [US3] Add shutdown_event checking in synthesis threads in src/tts/chunking.py
- [X] T102 [US3] Add logging for chunking operations in src/tts/chunking.py

**Run tests** (should PASS): `pytest tests/unit/test_chunking.py tests/integration/test_chunked_playback.py -v`

### Integration with PlaybackController

- [X] T103 [US3] Update PlaybackController.start() to accept ChunkSynthesizer in src/tts/controller.py
- [X] T104 [US3] Update PlaybackController playback loop to consume chunks from ChunkSynthesizer.get_next_chunk() in src/tts/controller.py
- [X] T105 [US3] Add "Buffering..." indicator when chunk buffer empty in src/tts/controller.py
- [X] T106 [US3] Update PlaybackController.seek() to trigger on-demand synthesis if seeking to unsynthesized chunk in src/tts/controller.py
- [X] T107 [US3] Update command_read() to use ChunkSynthesizer for text synthesis in src/main.py
- [X] T108 [US3] Add progress display during chunking (e.g., "Synthesizing chunk 3/8...") in src/main.py

**Manual Test**: `vox read --url <long-article-url>` (find article with 5000+ words), verify first audio <3s, verify smooth playback

**Checkpoint**: User Story 3 complete - streaming chunking fully functional and independently testable (Coverage target: >80%)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, documentation, and release preparation

- [X] T109 [P] Update README.md with new features: --save-session flag, list-sessions command, resume command, playback controls
- [X] T110 [P] Update README.md with keyboard controls documentation (table: key → action)
- [X] T111 [P] Add session management examples to README.md (save, list, resume, delete)
- [X] T112 [P] Add performance notes to README.md (chunking benefits, time to first audio)
- [X] T113 [P] Update CHANGELOG.md for v1.1.0 release (new features, breaking changes if any)
- [X] T114 [P] Update pyproject.toml version from 1.0.0 to 1.1.0
- [X] T115 [P] Add docstrings to all public methods in SessionManager (src/session/manager.py)
- [X] T116 [P] Add docstrings to all public methods in PlaybackController (src/tts/controller.py)
- [X] T117 [P] Add docstrings to all public methods in ChunkSynthesizer (src/tts/chunking.py)
- [X] T118 [P] Run ruff format on all modified files
- [X] T119 [P] Run ruff lint on all modified files and fix issues
- [X] T120 Verify test coverage ≥80% for all new modules: `pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80`
- [X] T121 Run full test suite: `pytest tests/ -v`
- [X] T122 [P] Create example session files for documentation/testing
- [ ] T123 [P] Test PyInstaller build with new pygame dependency: `python scripts/build_exe.py` (Manual - run before release)
- [ ] T124 Manual testing: Complete all acceptance scenarios from spec.md for US1, US2, US3 (Manual - QA phase)
- [ ] T125 Performance validation: Verify all success criteria from spec.md (SC-001 through SC-008) (Manual - QA phase)

**Final Checkpoint**: ✅ **IMPLEMENTATION COMPLETE** - All automated tasks finished, ready for manual QA and release v1.1.0

**Automated Tasks**: 122/122 complete (100%)
**Manual QA Tasks**: 3 remaining (T123-T125) - perform before final release

---

## Task Summary

**Total Tasks**: 125  
**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 4 tasks
- Phase 3 (User Story 1 - Session Management): 30 tasks
- Phase 4 (User Story 2 - Playback Controls): 33 tasks
- Phase 5 (User Story 3 - Chunking): 35 tasks
- Phase 6 (Polish): 18 tasks

**By User Story**:
- US1 (Session Management): 30 tasks (19 tests + 11 implementation)
- US2 (Playback Controls): 33 tasks (11 tests + 22 implementation)
- US3 (Chunking): 35 tasks (13 tests + 22 implementation)
- Shared/Polish: 27 tasks

**Parallel Opportunities**:
- Phase 1: T002, T003, T004 (config updates) can run in parallel
- Phase 2: T007, T008, T009 (data models) can run in parallel
- US1 Tests: T010-T019 can be written in parallel (different test cases)
- US1 Implementation: T020-T022 (private methods) can run in parallel
- US2 Tests: T040-T050 can be written in parallel
- US3 Tests: T074-T086 can be written in parallel
- Polish: T109-T119 (docs + formatting) can run in parallel

---

## Dependencies & Execution Order

### Story-Level Dependencies

```
Foundational (Phase 2)
    ├── BLOCKS → US1 (Session Management)
    ├── BLOCKS → US2 (Playback Controls)
    └── BLOCKS → US3 (Chunking)

US1 (Session Management) - Can execute independently after Phase 2
US2 (Playback Controls) - Can execute independently after Phase 2
US3 (Chunking) - Depends on US2 (PlaybackController integration)
```

### Task-Level Dependencies (Critical Path)

**US1 Critical Path** (Sequential):
1. T010-T019 (tests) → T020 (skeleton) → T021-T024 (helpers) → T025-T030 (main methods) → T033-T039 (CLI)

**US2 Critical Path** (Sequential):
1. T040-T050 (tests) → T051-T058 (AudioPlayback) → T059-T070 (PlaybackController) → T071-T073 (CLI)

**US3 Critical Path** (Sequential):
1. T074-T086 (tests) → T087-T102 (ChunkSynthesizer) → T103-T108 (integration)

**Cross-Story Dependencies**:
- T103 (US3) depends on T060 (US2) - PlaybackController.start() must exist before ChunkSynthesizer integration
- T107 (US3) depends on T038 (US1) - Session save must work before chunked playback save

---

## Parallel Execution Examples

### Example 1: Maximum Parallelization (Multiple Developers)

**Week 1** (Foundational + US1 Start):
- Dev A: T001-T005 (Setup), then T010-T019 (US1 tests)
- Dev B: T006-T009 (Data models), then T020-T032 (US1 implementation)
- Dev C: T040-T050 (US2 tests)

**Week 2** (US1 Complete + US2 Implementation):
- Dev A: T033-T039 (US1 CLI integration)
- Dev B: T051-T070 (US2 implementation)
- Dev C: T074-T086 (US3 tests)

**Week 3** (US2 Complete + US3 Implementation):
- Dev A: T071-T073 (US2 CLI integration)
- Dev B: T087-T102 (US3 implementation)
- Dev C: T109-T119 (Documentation + polish)

**Week 4** (US3 Complete + Testing):
- All Devs: T103-T108 (US3 integration), T120-T125 (final testing)

### Example 2: Solo Developer (Sequential with Smart Parallelization)

**Phase 1-2** (Day 1): T001-T009 (setup + foundational)

**US1 MVP** (Days 2-3):
- Write all tests in batch: T010-T019 (should FAIL)
- Implement in order: T020-T039 (tests should PASS)

**US2 MVP** (Days 4-5):
- Write all tests in batch: T040-T050 (should FAIL)
- Implement in order: T051-T073 (tests should PASS)

**US3 Performance** (Days 6-7):
- Write all tests in batch: T074-T086 (should FAIL)
- Implement in order: T087-T108 (tests should PASS)

**Polish** (Day 8): T109-T125 (documentation, testing, release)

---

## MVP Scope Recommendation

**Minimum Viable Product** (v1.1.0-rc1): User Story 1 + User Story 2 ONLY

**Rationale**:
- US1 (Session Management) + US2 (Playback Controls) deliver core value
- US3 (Chunking) is performance enhancement, nice-to-have but not essential
- Can release v1.1.0-rc1 with US1+US2, gather feedback, then add US3 in v1.1.0 final

**MVP Tasks**: T001-T073 (73 tasks = 58% of total)  
**Full Release Tasks**: T001-T125 (125 tasks = 100%)

---

## Implementation Strategy

1. **Test-First (TDD)**: Write tests BEFORE implementation for every module
2. **Independent Stories**: Each user story can be developed, tested, and demoed independently
3. **Incremental Delivery**: Ship US1, then US1+US2, then US1+US2+US3
4. **Parallel Work**: Tests can be written in parallel with implementation if multiple devs
5. **Constitution Compliance**: Maintain >80% coverage at all times (gate for PR merge)

---

**Generated**: 2026-01-17  
**Status**: ✅ Ready for implementation - All 125 tasks defined with dependencies, parallel opportunities, and MVP scope
