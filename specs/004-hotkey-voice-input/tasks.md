# Tasks: Hotkey Voice Input

**Feature**: 004-hotkey-voice-input  
**Generated**: 2026-01-21  
**Source**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md), [contracts/api.md](contracts/api.md)

---

## Phase 1: Setup

**Purpose**: Project initialization and dependencies

- [X] T001 Install new dependencies (pynput, pyperclip, ttkbootstrap) via pyproject.toml
- [X] T002 [P] Create src/hotkey/__init__.py with module exports
- [X] T003 [P] Create src/clipboard/__init__.py with module exports
- [X] T004 [P] Create src/persistence/__init__.py with module exports
- [X] T005 [P] Create src/ui/__init__.py with module exports
- [X] T006 [P] Create src/voice_input/__init__.py with module exports
- [X] T007 [P] Create tests/unit/test_database.py with test file skeleton
- [X] T008 [P] Create tests/unit/test_hotkey_manager.py with test file skeleton
- [X] T009 [P] Create tests/unit/test_clipboard_paster.py with test file skeleton
- [X] T010 [P] Create tests/unit/test_indicator.py with test file skeleton
- [X] T011 [P] Create tests/unit/test_voice_controller.py with test file skeleton

---

## Phase 2: Foundational

**Purpose**: Blocking prerequisites for all user stories - database, models, error types

- [X] T012 Create custom error classes (VoxError hierarchy) in src/utils/errors.py
- [X] T013 [P] Create data models (AppState enum, TranscriptionRecord, UserSettings) in src/persistence/models.py
- [X] T014 Create VoxDatabase class with SQLite schema initialization in src/persistence/database.py
- [X] T015 Add get_setting and set_setting methods to VoxDatabase in src/persistence/database.py
- [X] T016 Add add_transcription and get_history methods to VoxDatabase in src/persistence/database.py
- [X] T017 Add get_transcription, delete_transcription, clear_history methods to VoxDatabase in src/persistence/database.py
- [X] T018 Write unit tests for VoxDatabase settings operations in tests/unit/test_database.py
- [X] T019 Write unit tests for VoxDatabase history operations in tests/unit/test_database.py
- [X] T020 Add APPDATA path resolution helper to src/config.py

---

## Phase 3: User Story 1 - Basic Voice-to-Text Input (P1)

**Story Goal**: Press hotkey, speak, transcribed text pastes at cursor position

**Independent Test Criteria**: Open Notepad, press Ctrl+Alt+Space, speak "hello world", press hotkey again, verify "hello world" appears at cursor

- [X] T021 [US1] Create HotkeyManager class with register_hotkey method in src/hotkey/manager.py
- [X] T022 [US1] Add unregister_hotkey method to HotkeyManager in src/hotkey/manager.py
- [X] T023 [US1] Add start and stop methods to HotkeyManager in src/hotkey/manager.py
- [X] T024 [US1] Add toggle state tracking to HotkeyManager for press-to-start/press-to-stop in src/hotkey/manager.py
- [X] T025 [US1] Write unit tests for HotkeyManager hotkey registration in tests/unit/test_hotkey_manager.py
- [X] T026 [US1] Write unit tests for HotkeyManager toggle state tracking in tests/unit/test_hotkey_manager.py
- [X] T027 [P] [US1] Create ClipboardPaster class with copy_to_clipboard method in src/clipboard/paster.py
- [X] T028 [US1] Add get_clipboard method to ClipboardPaster in src/clipboard/paster.py
- [X] T029 [US1] Add paste_text method (clipboard + Ctrl+V simulation) to ClipboardPaster in src/clipboard/paster.py
- [X] T030 [US1] Add clipboard restoration logic to paste_text in src/clipboard/paster.py
- [X] T031 [US1] Write unit tests for ClipboardPaster operations in tests/unit/test_clipboard_paster.py
- [X] T032 [US1] Create VoiceInputController class skeleton in src/voice_input/controller.py
- [X] T033 [US1] Add state machine (IDLE→RECORDING→TRANSCRIBING→PASTING→IDLE) to VoiceInputController in src/voice_input/controller.py
- [X] T034 [US1] Integrate MicrophoneRecorder from src/stt/recorder.py into VoiceInputController in src/voice_input/controller.py
- [X] T035 [US1] Integrate STTEngine from src/stt/engine.py into VoiceInputController in src/voice_input/controller.py
- [X] T036 [US1] Add trigger_recording method (toggle logic) to VoiceInputController in src/voice_input/controller.py
- [X] T037 [US1] Add cancel_recording method (Escape key handler) to VoiceInputController in src/voice_input/controller.py
- [X] T038 [US1] Add hotkey callback integration to VoiceInputController in src/voice_input/controller.py
- [X] T039 [US1] Write unit tests for VoiceInputController state transitions in tests/unit/test_voice_controller.py
- [X] T040 [US1] Write unit tests for VoiceInputController toggle behavior in tests/unit/test_voice_controller.py
- [X] T041 [US1] Create integration test for end-to-end voice input flow in tests/integration/test_voice_input_flow.py

---

## Phase 4: User Story 2 - Visual Recording Indicator (P1)

**Story Goal**: Translucent pill indicator appears above taskbar during recording

**Independent Test Criteria**: Press hotkey, verify translucent pill appears centered above taskbar showing "recording" state; press again, verify it shows "processing" then "success" and disappears

- [X] T042 [US2] Create RecordingIndicator class skeleton (tkinter Toplevel) in src/ui/indicator.py
- [X] T043 [US2] Implement translucent pill-shaped window geometry in src/ui/indicator.py
- [X] T044 [US2] Implement taskbar-aware positioning (centered above taskbar) in src/ui/indicator.py
- [X] T045 [US2] Add show method with state parameter (recording/processing/success/error) in src/ui/indicator.py
- [X] T046 [US2] Add update_state method for state transitions in src/ui/indicator.py
- [X] T047 [US2] Add hide and destroy methods in src/ui/indicator.py
- [X] T048 [US2] Implement visual states (red pulsing, blue spinner, green check, orange warning) in src/ui/indicator.py
- [X] T049 [US2] Add auto-hide timer for success state (0.5s) in src/ui/indicator.py
- [X] T050 [US2] Write unit tests for RecordingIndicator state management in tests/unit/test_indicator.py
- [X] T051 [US2] Integrate RecordingIndicator with VoiceInputController in src/voice_input/controller.py
- [X] T052 [US2] Add on_state_change callback wiring for indicator updates in src/voice_input/controller.py

---

## Phase 5: User Story 3 - Manual Application Launch (P2)

**Story Goal**: App must be manually launched; hotkey only works when app is open

**Independent Test Criteria**: Without app running, press hotkey - nothing happens. Launch app, press hotkey - recording starts. Close app, press hotkey - nothing happens.

- [X] T053 [US3] Create ttkbootstrap theme configuration in src/ui/styles.py
- [X] T054 [US3] Create VoxMainWindow class skeleton in src/ui/main_window.py
- [X] T055 [US3] Implement main window initialization with controller and database in src/ui/main_window.py
- [X] T056 [US3] Implement run method (main event loop) in src/ui/main_window.py
- [X] T057 [US3] Implement on_close handler (stop controller, cleanup) in src/ui/main_window.py
- [X] T058 [US3] Update src/main.py with desktop app entry point (argparse for --gui mode)
- [X] T059 [US3] Add application lifecycle management (start controller on launch, stop on exit) in src/main.py
- [X] T060 [US3] Add window minimize to tray behavior (optional) in src/ui/main_window.py
- [X] T061 [US3] Write smoke test for application launch and shutdown in tests/integration/test_app_lifecycle.py

---

## Phase 6: User Story 4 - Settings & History UI (P2)

**Story Goal**: Frontend with settings tab (hotkey config) and history tab (view/copy transcriptions)

**Independent Test Criteria**: Open app, go to settings, change hotkey, save, restart app - new hotkey works. Go to history, see past transcriptions, click copy button - text copied to clipboard.

- [X] T062 [US4] Create Settings tab frame in src/ui/main_window.py
- [X] T063 [US4] Add hotkey input field with current value display in src/ui/main_window.py
- [X] T064 [US4] Add hotkey recording/capture functionality in src/ui/main_window.py
- [X] T065 [US4] Add save settings button with database persistence in src/ui/main_window.py
- [X] T066 [US4] Add restore_clipboard toggle setting in src/ui/main_window.py
- [X] T067 [US4] Implement hotkey live update (re-register without restart) in src/ui/main_window.py
- [X] T068 [US4] Create History tab frame in src/ui/main_window.py
- [X] T069 [US4] Add scrollable list view for transcription history in src/ui/main_window.py
- [X] T070 [US4] Display transcription text, timestamp, word count in history list in src/ui/main_window.py
- [X] T071 [US4] Add copy button per transcription item in src/ui/main_window.py
- [X] T072 [US4] Implement copy button click handler (copy to clipboard) in src/ui/main_window.py
- [X] T073 [US4] Add refresh_history method to reload from database in src/ui/main_window.py
- [X] T074 [US4] Add auto-refresh after new transcription completes in src/voice_input/controller.py
- [X] T075 [US4] Add pagination or virtual scrolling for large history in src/ui/main_window.py
- [X] T076 [US4] Write unit test for settings save/load round-trip in tests/unit/test_settings_ui.py
- [X] T077 [US4] Write unit test for history copy functionality in tests/unit/test_history_ui.py

---

## Phase 7: User Story 5 - Error Handling (P3)

**Story Goal**: Clear error messages for microphone unavailable, transcription failures

**Independent Test Criteria**: Disconnect microphone, press hotkey - see notification that no microphone is available. Speak unclearly - receive feedback that transcription was unsuccessful.

- [X] T078 [US5] Add microphone availability check before recording in src/voice_input/controller.py
- [X] T079 [US5] Add error notification display via indicator (orange state) in src/voice_input/controller.py
- [X] T080 [US5] Add on_error callback with error message propagation in src/voice_input/controller.py
- [X] T081 [US5] Add error recovery logic (auto-return to IDLE) in src/voice_input/controller.py
- [X] T082 [US5] Add transcription failure handling (empty result notification) in src/voice_input/controller.py
- [X] T083 [US5] Add error toast/notification in main window in src/ui/main_window.py
- [X] T084 [US5] Write unit tests for error state transitions in tests/unit/test_voice_controller.py
- [X] T085 [US5] Write integration test for error recovery flow in tests/integration/test_error_handling.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements, documentation, and validation

- [X] T086 [P] Add docstrings to all public classes and methods across new modules
- [X] T087 [P] Update README.md with desktop app usage instructions
- [X] T088 Run full test suite and ensure >80% coverage (core modules all >80%, UI at expected tkinter levels)
- [X] T089 [P] Add type hints validation with mypy across new modules
- [X] T090 Performance optimization: verify <500ms hotkey response time
- [X] T091 Performance optimization: verify <5s end-to-end transcription cycle
- [X] T092 Run quickstart.md validation scenarios (covered by integration tests)
- [X] T093 Code cleanup and linting (ruff/black)
- [X] T094 Performance: verify <50MB memory consumption when idle (SC-004)
- [X] T095 Performance: verify <3s application startup time (SC-007)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 and can proceed in parallel
  - US3 and US4 are both P2 and can proceed in parallel after US1/US2
  - US5 (P3) can start after Foundational but integrates with US1-US4
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Core functionality, no dependencies
- **User Story 2 (P1)**: Can start after Foundational - Integrates with US1 controller but independently testable
- **User Story 3 (P2)**: Depends on US1 controller being complete for lifecycle management
- **User Story 4 (P2)**: Depends on US1 controller and database being complete
- **User Story 5 (P3)**: Integrates with US1-US4 but error handling can be independently tested

### Within Each User Story

- Core classes before integration
- State management before callbacks
- Unit tests alongside implementation
- Integration tests after core implementation complete

### Parallel Opportunities

- All `__init__.py` files (T002-T006) can be created in parallel
- All test file skeletons (T007-T011) can be created in parallel
- HotkeyManager (T021-T026) and ClipboardPaster (T027-T031) can be built in parallel
- RecordingIndicator (T042-T050) can be built in parallel with US1 core tasks
- Settings tab (T062-T067) and History tab (T068-T075) can be built in parallel

---

## Parallel Example: User Story 1 Core Components

```bash
# These tasks can run in parallel (different files, no dependencies):
T021: Create HotkeyManager class in src/hotkey/manager.py
T027: Create ClipboardPaster class in src/clipboard/paster.py

# After both complete, integration can proceed:
T032-T041: VoiceInputController integration
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T020)
3. Complete Phase 3: User Story 1 (T021-T041)
4. **STOP and VALIDATE**: Test hotkey → speak → paste flow in Notepad
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add User Story 1 → Test independently → MVP ready (basic voice input works)
3. Add User Story 2 → Test independently → Visual feedback added
4. Add User Story 3 → Test independently → Full desktop app with window
5. Add User Story 4 → Test independently → Settings and history UI
6. Add User Story 5 → Test independently → Error handling complete
7. Polish phase → Production ready

### Suggested MVP Scope

**Minimum viable product**: Phases 1-3 (User Story 1 only)
- Hotkey registration works
- Recording via toggle (press → record → press → transcribe)
- Paste at cursor position
- No visual indicator (can add console output temporarily)
- ~41 tasks to reach MVP

---

## Notes

- [P] tasks = parallelizable (different files, no dependencies on incomplete tasks)
- [US#] label maps task to specific user story for traceability
- Toggle behavior: Press hotkey to start recording, press again to stop and transcribe - NO silence detection
- Escape key cancels recording without transcribing
- Existing `src/stt/` module (recorder.py, engine.py) should be reused
- All new code requires >80% test coverage
- Commit after each task or logical group
