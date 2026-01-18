# Tasks: Speech-to-Text Integration & Project Documentation Enhancement

**Feature**: 003-speech-to-text  
**Input**: Design documents from `/specs/003-speech-to-text/`  
**Prerequisites**: ✅ plan.md, ✅ spec.md, ✅ research.md, ✅ data-model.md, ✅ contracts/

**Tests**: Tests NOT included by default (per spec - STT tests are optional unless TDD requested). Will be added if explicitly required.

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- File paths are absolute from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management for rebranding and STT

- [X] T001 Update project name in pyproject.toml: change `name = "vox"` to `name = "vox"`
- [X] T002 [P] Update version in pyproject.toml to 3.0.0 (MAJOR bump for breaking CLI change)
- [X] T003 [P] Add faster-whisper dependency to pyproject.toml: `faster-whisper>=1.0.0`
- [X] T004 [P] Add sounddevice dependency to pyproject.toml: `sounddevice>=0.4.6`
- [X] T005 [P] Add scipy dependency to pyproject.toml: `scipy>=1.11.0` (for WAV file handling)
- [X] T006 Install new dependencies: `uv pip install faster-whisper sounddevice scipy`
- [X] T007 [P] Update entry point in pyproject.toml: change `vox = "src.main:main"` to `vox = "src.main:main"`
- [X] T008 [P] Update project URLs in pyproject.toml: change repository name from vox to vox
- [X] T009 [P] Update project description in pyproject.toml to reflect bidirectional audio-text capabilities

**Checkpoint**: ✅ Project renamed in build config, dependencies installed - ready for code changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on (config migration, shared utilities)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Create config migration utility in src/utils/migration.py with migrate_config() function
- [X] T011 [P] Implement detect_old_config() in src/utils/migration.py (checks for %APPDATA%/vox/)
- [X] T012 [P] Implement copy_config_files() in src/utils/migration.py (copies config.json, sessions/, models/)
- [X] T013 [P] Implement backup_old_config() in src/utils/migration.py (creates backup before migration)
- [X] T014 Add STT-specific error classes to src/utils/errors.py: MicrophoneError, TranscriptionError, ModelLoadError
- [X] T015 [P] Update config paths in src/config.py: change `APPDATA / "vox"` to `APPDATA / "vox"`
- [X] T016 [P] Add STT model cache path constant to src/config.py: `STT_MODEL_CACHE = APPDATA / "vox" / "models"`
- [X] T017 [P] Add STT configuration defaults to src/config.py: `DEFAULT_STT_MODEL = "medium"`, `SILENCE_DURATION = 5.0`, `SAMPLE_RATE = 16000`

**Checkpoint**: ✅ Migration utilities and shared config ready - user story implementation can begin

---

## Phase 3: User Story 1 - Project Rebranding (Priority: P1) 🎯 MVP

**Goal**: Rebrand project from "vox" to "vox" across all codebase references, documentation, and CLI commands

**Independent Test**: Run `pip install -e .`, verify `vox --help` works, check all help text shows "vox", verify config directory is `%APPDATA%/vox/`

### Implementation for User Story 1

#### Core Rebranding

- [X] T018 [P] [US1] Update CLI entry point name in src/main.py: change all "vox" strings to "vox" in help text
- [X] T019 [P] [US1] Update CLI parser description in src/main.py: change "vox CLI" to "vox CLI"
- [X] T020 [P] [US1] Update version banner in src/main.py to show "vox v3.0.0"
- [X] T021 [P] [US1] Update logger names in src/main.py: ensure all getLogger calls use module __name__
- [X] T022 [P] [US1] Update print statements in src/main.py to reference "vox" instead of "vox"
- [X] T023 [P] [US1] Rename CLI subcommand structure in src/main.py: add "read" subcommand for existing TTS functionality
- [X] T024 [US1] Implement argument parser with subcommands in src/main.py: "vox read" and "vox transcribe" (stub for US4)
- [X] T025 [US1] Update command_read() function in src/main.py to handle new subcommand structure
- [X] T026 [US1] Add config migration check in src/main.py main() function: call migrate_config() on first run
- [X] T027 [US1] Update all docstrings in src/main.py to reference "vox"

#### Module Docstrings and References

- [X] T028 [P] [US1] Update module docstring in src/__init__.py to reference "vox"
- [X] T029 [P] [US1] Update module docstring in src/config.py to reference "vox"
- [X] T030 [P] [US1] Update module docstrings in src/browser/__init__.py to reference "vox"
- [X] T031 [P] [US1] Update module docstrings in src/extraction/__init__.py to reference "vox"
- [X] T032 [P] [US1] Update module docstrings in src/tts/__init__.py to reference "vox"
- [X] T033 [P] [US1] Update module docstrings in src/session/__init__.py to reference "vox"
- [X] T034 [P] [US1] Update inline comments referencing "vox" across all src/ modules

#### Build and Distribution

- [X] T035 [US1] Update executable name in scripts/build_exe.py: change output from "vox.exe" to "vox.exe"
- [X] T036 [P] [US1] Update build script references in scripts/build_exe.py to use "vox" naming
- [X] T037 [P] [US1] Update BUILD.md documentation to reference vox commands and executable name

#### Testing and Verification

- [X] T038 [US1] Run `pip install -e .` and verify `vox` command is available in PATH
- [X] T039 [US1] Run `vox --help` and verify all output shows "vox" not "vox"
- [X] T040 [US1] Run `vox read --help` and verify subcommand help displays correctly
- [X] T041 [US1] Verify config directory created at `%APPDATA%/vox/` on first run
- [X] T042 [US1] Test config migration: create old config at `%APPDATA%/vox/`, run vox, verify migration
- [X] T043 [US1] Run existing TTS commands with new syntax: `vox read --url https://example.com`
- [X] T044 [US1] Verify existing sessions still work after rebranding

**Checkpoint**: ✅ User Story 1 complete - project fully rebranded, CLI updated, config migration functional

---

## Phase 4: User Story 2 - Developer Documentation (Priority: P2)

**Goal**: Create comprehensive developer documentation with AI agent guidelines, project architecture overview, and coding standards

**Independent Test**: New developer reads docs and can: (1) understand architecture, (2) set up dev environment, (3) run tests, (4) follow coding standards

### Implementation for User Story 2

#### AI Agent Guidelines Document

- [ ] T045 [P] [US2] Create .specify/memory/claude.md with project overview section
- [ ] T046 [P] [US2] Add architecture overview to claude.md with module diagram and responsibilities
- [ ] T047 [P] [US2] Add data flow diagrams to claude.md for TTS and STT workflows
- [ ] T048 [P] [US2] Document code quality standards in claude.md: SOLID, DRY, KISS, test coverage requirements
- [ ] T049 [P] [US2] Add testing patterns section to claude.md: unit test structure, mocking strategies
- [ ] T050 [P] [US2] Add contribution workflow to claude.md: branch naming, commit messages, PR checklist
- [ ] T051 [P] [US2] Add AI agent guidelines section to claude.md: code generation, refactoring, debugging rules
- [ ] T052 [P] [US2] Add CI/CD pipeline documentation to claude.md: GitHub Actions workflow, pre-commit hooks
- [ ] T053 [P] [US2] Add technology stack section to claude.md: core dependencies, dev tools

#### Project Structure Documentation

- [ ] T054 [P] [US2] Add high-level project structure section to claude.md showing src/ directory organization
- [ ] T055 [P] [US2] Document module responsibilities in claude.md: browser/, extraction/, tts/, stt/, session/, utils/
- [ ] T056 [P] [US2] Add dependency relationships documentation to claude.md showing module interactions
- [ ] T057 [P] [US2] Document configuration management in claude.md: config.py, environment variables, model cache

#### Code Quality and Standards

- [ ] T058 [P] [US2] Document import organization standard in claude.md: stdlib, third-party, local
- [ ] T059 [P] [US2] Add error handling patterns to claude.md: custom exceptions, logging, graceful degradation
- [ ] T060 [P] [US2] Document type hinting requirements in claude.md: all function parameters and return types
- [ ] T061 [P] [US2] Add docstring standards to claude.md: format, required sections, examples

#### Verification

- [ ] T062 [US2] Verify claude.md covers all sections from research.md template
- [ ] T063 [US2] Test that new developer can understand architecture from claude.md alone
- [ ] T064 [US2] Verify AI agents (GitHub Copilot) can access and use claude.md context

**Checkpoint**: ✅ User Story 2 complete - comprehensive developer documentation enables new contributors

---

## Phase 5: User Story 3 - README Overhaul (Priority: P3)

**Goal**: Overhaul README.md to be user-focused with clear installation, usage, and troubleshooting sections

**Independent Test**: New user reads README and successfully installs vox, runs TTS command, understands troubleshooting steps

### Implementation for User Story 3

#### README Structure Overhaul

- [ ] T065 [US3] Rewrite README.md hero section with vox branding and tagline
- [ ] T066 [P] [US3] Add badges to README.md: PyPI version, license, Python version
- [ ] T067 [P] [US3] Create "What is vox?" section in README.md with feature list
- [ ] T068 [P] [US3] Create "Installation" section in README.md with PyPI and source install instructions
- [ ] T069 [P] [US3] Add "Verify Installation" subsection to README.md with `vox --version` command

#### TTS Usage Documentation

- [ ] T070 [P] [US3] Create "Usage" section in README.md with TTS examples
- [ ] T071 [P] [US3] Add "Text-to-Speech: Read Web Content Aloud" subsection to README.md
- [ ] T072 [P] [US3] Document `vox read --url` command in README.md with examples
- [ ] T073 [P] [US3] Document `vox read --file` command in README.md with examples
- [ ] T074 [P] [US3] Document `vox read --active-tab` command in README.md
- [ ] T075 [P] [US3] Document playback controls in README.md: Space, arrows, Q key

#### STT Usage Documentation (Preparation for US4)

- [ ] T076 [P] [US3] Add "Speech-to-Text: Transcribe Your Voice" subsection to README.md
- [ ] T077 [P] [US3] Document `vox transcribe` command in README.md with examples
- [ ] T078 [P] [US3] Document `vox transcribe --output` flag in README.md for file saving
- [ ] T079 [P] [US3] Document recording controls in README.md: Enter to stop, auto-stop on silence

#### Configuration and Troubleshooting

- [ ] T080 [P] [US3] Create "Configuration" section in README.md documenting config file location
- [ ] T081 [P] [US3] Add "Microphone Setup" subsection to README.md with Windows privacy settings guidance
- [ ] T082 [P] [US3] Create "Troubleshooting" section in README.md
- [ ] T083 [P] [US3] Add "No microphone detected" troubleshooting entry to README.md with solution steps
- [ ] T084 [P] [US3] Add "Microphone permission denied" troubleshooting entry to README.md
- [ ] T085 [P] [US3] Add "Microphone in use" troubleshooting entry to README.md
- [ ] T086 [P] [US3] Add "Low transcription accuracy" troubleshooting entry to README.md
- [ ] T087 [P] [US3] Add "TTS voice sounds robotic" troubleshooting entry to README.md
- [ ] T088 [P] [US3] Add "Installation fails" troubleshooting entry to README.md

#### Advanced Configuration and Credits

- [ ] T089 [P] [US3] Create "Advanced Configuration" section in README.md with config.json examples
- [ ] T090 [P] [US3] Document STT model options in README.md: tiny, base, small, medium, large
- [ ] T091 [P] [US3] Add "Contributing" section to README.md with link to CONTRIBUTING.md (or claude.md)
- [ ] T092 [P] [US3] Add "License" section to README.md
- [ ] T093 [P] [US3] Add "Credits" section to README.md acknowledging Whisper and Piper TTS
- [ ] T094 [P] [US3] Add rebranding notice to README.md: "Previously known as vox (versions ≤2.0.0)"

#### Verification

- [ ] T095 [US3] Test README readability: new user should understand purpose in 30 seconds
- [ ] T096 [US3] Verify installation instructions work on fresh Windows 11 system
- [ ] T097 [US3] Verify all command examples in README are syntactically correct
- [ ] T098 [US3] Test troubleshooting steps resolve common issues

**Checkpoint**: ✅ User Story 3 complete - README enables successful onboarding for new users

---

## Phase 6: User Story 4 - Voice Recording to Text (Priority: P4)

**Goal**: Implement speech-to-text functionality with `vox transcribe` command, microphone recording, and Whisper transcription

**Independent Test**: Run `vox transcribe`, speak for 10 seconds, press Enter, verify transcribed text appears in terminal with 95%+ accuracy

### Module Creation for User Story 4

- [ ] T099 [P] [US4] Create src/stt/ directory for speech-to-text module
- [ ] T100 [P] [US4] Create src/stt/__init__.py with module docstring
- [ ] T101 [P] [US4] Create src/stt/engine.py for Whisper engine wrapper
- [ ] T102 [P] [US4] Create src/stt/recorder.py for microphone audio capture
- [ ] T103 [P] [US4] Create src/stt/transcriber.py for transcription orchestration
- [ ] T104 [P] [US4] Create src/stt/audio_utils.py for silence detection and audio processing

### STT Engine Implementation (Whisper)

- [ ] T105 [P] [US4] Create STTEngine class skeleton in src/stt/engine.py with __init__ method
- [ ] T106 [US4] Implement STTEngine._load_model() in src/stt/engine.py: load faster-whisper model
- [ ] T107 [US4] Implement STTEngine._check_model_cache() in src/stt/engine.py: verify model exists or download
- [ ] T108 [US4] Implement STTEngine.transcribe_audio() in src/stt/engine.py: transcribe WAV file to text
- [ ] T109 [US4] Implement STTEngine._extract_text() in src/stt/engine.py: extract text from segments
- [ ] T110 [US4] Add error handling for model load failures in src/stt/engine.py (ModelLoadError)
- [ ] T111 [P] [US4] Add logging for transcription progress in src/stt/engine.py
- [ ] T112 [P] [US4] Implement STTEngine.get_model_info() in src/stt/engine.py: return model name, size, status

### Microphone Recording Implementation

- [ ] T113 [P] [US4] Create MicrophoneRecorder class skeleton in src/stt/recorder.py with __init__ method
- [ ] T114 [US4] Implement MicrophoneRecorder._detect_default_device() in src/stt/recorder.py using sounddevice
- [ ] T115 [US4] Implement MicrophoneRecorder._validate_device() in src/stt/recorder.py: check device availability
- [ ] T116 [US4] Implement MicrophoneRecorder.start_recording() in src/stt/recorder.py: start InputStream with callback
- [ ] T117 [US4] Implement MicrophoneRecorder._audio_callback() in src/stt/recorder.py: collect audio chunks
- [ ] T118 [US4] Implement MicrophoneRecorder.stop_recording() in src/stt/recorder.py: stop stream, concatenate chunks
- [ ] T119 [US4] Implement MicrophoneRecorder.wait_for_enter() in src/stt/recorder.py: blocking input() for Enter key
- [ ] T120 [US4] Add error handling for microphone detection failures in src/stt/recorder.py (MicrophoneError)
- [ ] T121 [P] [US4] Add logging for recording start/stop events in src/stt/recorder.py
- [ ] T122 [US4] Implement MicrophoneRecorder.save_wav() in src/stt/recorder.py: save audio to 16kHz mono WAV

### Audio Processing and Silence Detection

- [ ] T123 [P] [US4] Implement calculate_rms() in src/stt/audio_utils.py: compute RMS energy of audio chunk
- [ ] T124 [P] [US4] Implement detect_silence() in src/stt/audio_utils.py: check if chunk below threshold
- [ ] T125 [P] [US4] Create SilenceDetector class in src/stt/audio_utils.py with state tracking
- [ ] T126 [US4] Implement SilenceDetector.process_chunk() in src/stt/audio_utils.py: track consecutive silent chunks
- [ ] T127 [US4] Implement SilenceDetector.is_silence_threshold_reached() in src/stt/audio_utils.py: 5-second check
- [ ] T128 [US4] Implement SilenceDetector.reset() in src/stt/audio_utils.py: reset counter on sound detected

### Transcription Orchestrator

- [ ] T129 [P] [US4] Create Transcriber class skeleton in src/stt/transcriber.py with __init__ method
- [ ] T130 [US4] Implement Transcriber.transcribe() in src/stt/transcriber.py: main orchestration method
- [ ] T131 [US4] Implement Transcriber._record_audio() in src/stt/transcriber.py: record with Enter or silence stop
- [ ] T132 [US4] Implement Transcriber._process_recording() in src/stt/transcriber.py: save WAV, call engine
- [ ] T133 [US4] Implement Transcriber._display_result() in src/stt/transcriber.py: print to stdout
- [ ] T134 [US4] Implement Transcriber._save_result() in src/stt/transcriber.py: save to file if --output provided
- [ ] T135 [US4] Add error handling for transcription failures in src/stt/transcriber.py (TranscriptionError)
- [ ] T136 [P] [US4] Add progress indicators in src/stt/transcriber.py: "Recording...", "Transcribing..."

### CLI Integration for User Story 4

- [ ] T137 [US4] Add transcribe subcommand to parser in src/main.py: `vox transcribe`
- [ ] T138 [P] [US4] Add --output argument to transcribe subcommand in src/main.py
- [ ] T139 [P] [US4] Add --model argument to transcribe subcommand in src/main.py (default: medium)
- [ ] T140 [US4] Implement command_transcribe() handler in src/main.py
- [ ] T141 [US4] Initialize Transcriber instance in command_transcribe() with config from args
- [ ] T142 [US4] Call Transcriber.transcribe() and handle output in command_transcribe()
- [ ] T143 [US4] Add error handling in command_transcribe() for MicrophoneError, ModelLoadError, TranscriptionError
- [ ] T144 [P] [US4] Add colorized status messages in command_transcribe(): cyan for progress, green for success

### Manual Testing and Verification

- [ ] T145 [US4] Test basic transcription: `vox transcribe`, speak 10 seconds, press Enter, verify text output
- [ ] T146 [US4] Test file output: `vox transcribe --output test.txt`, verify file contains transcription
- [ ] T147 [US4] Test silence detection: `vox transcribe`, speak 3 seconds, wait 5 seconds, verify auto-stop
- [ ] T148 [US4] Test Enter key stop: `vox transcribe`, speak, press Enter immediately, verify recording stops
- [ ] T149 [US4] Test no microphone error: disable microphone, run `vox transcribe`, verify clear error message
- [ ] T150 [US4] Test microphone permission error: deny mic access in Windows settings, verify error guidance
- [ ] T151 [US4] Test model download: delete model cache, run `vox transcribe`, verify auto-download
- [ ] T152 [US4] Verify transcription accuracy: record clear speech, check 95%+ word accuracy
- [ ] T153 [US4] Test background noise handling: record with moderate noise, verify transcription still works
- [ ] T154 [US4] Test different model sizes: `vox transcribe --model small`, verify faster but less accurate

**Checkpoint**: ✅ User Story 4 complete - speech-to-text fully functional with high accuracy (Coverage target: >80% for critical paths)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation updates, and release preparation

- [ ] T155 [P] Update CHANGELOG.md with v3.0.0 breaking changes and new features
- [ ] T156 [P] Verify all docstrings use "vox" not "vox"
- [ ] T157 [P] Run ruff linting on entire codebase: `ruff check .`
- [ ] T158 [P] Run ruff formatting on entire codebase: `ruff format .`
- [ ] T159 [P] Update constitution.md if any new coding standards were established
- [ ] T160 Build standalone executable: `python scripts/build_exe.py`, verify vox.exe works
- [ ] T161 Test end-to-end workflow: install fresh, run TTS, run STT, verify config migration
- [ ] T162 Prepare release notes for v3.0.0 with migration guide for existing users
- [ ] T163 [P] Update GitHub repository description and topics to include "speech-to-text"
- [ ] T164 Tag release: `git tag v3.0.0`, push to GitHub

**Final Verification**: All user stories independently testable, documentation complete, build artifacts generated

---

## Task Dependency Graph

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3-6 (User Stories) → Phase 7 (Polish)
                                                ↓
                        ┌──────────────────────┼──────────────────────┐
                        │                      │                      │
                    US1 (P1)              US2 (P2)              US3 (P3)
              Project Rebranding     Developer Docs         README Overhaul
                        │                      │                      │
                        └──────────────────────┴──────────────────────┘
                                            ↓
                                        US4 (P4)
                                  Voice Recording to Text
```

### Parallel Execution Opportunities

**Within User Story 1 (Rebranding)**:
- T028-T034: Module docstring updates (all [P], can run in parallel)
- T018-T022, T035-T037: Different file updates (parallelizable)

**Within User Story 2 (Developer Docs)**:
- T045-T061: All documentation sections (all [P], independent writes)

**Within User Story 3 (README)**:
- T067-T094: Most README sections (all [P], different sections)

**Within User Story 4 (STT)**:
- T099-T104: Module file creation (all [P])
- T105-T112, T113-T122, T123-T128: Different modules (engine, recorder, audio_utils can be built in parallel after skeleton created)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**User Story 1 only**: Project rebranding
- CLI renamed to `vox read`
- Config migration functional
- All references updated
- **Delivers**: Basic rebranding, existing TTS still works under new name

### Incremental Delivery

1. **Release 3.0.0-alpha**: US1 (Rebranding only)
2. **Release 3.0.0-beta**: US1 + US2 (Rebranding + Developer Docs)
3. **Release 3.0.0-rc1**: US1 + US2 + US3 (Rebranding + Docs + README)
4. **Release 3.0.0**: All user stories (Full STT integration)

### Testing Per User Story

- **US1**: Manual CLI testing, config migration testing
- **US2**: Documentation review by new developer
- **US3**: User onboarding test (can new user succeed?)
- **US4**: Transcription accuracy testing, error handling testing

---

## Summary

- **Total Tasks**: 164
- **User Story 1 (P1)**: 27 tasks (T018-T044)
- **User Story 2 (P2)**: 20 tasks (T045-T064)
- **User Story 3 (P3)**: 34 tasks (T065-T098)
- **User Story 4 (P4)**: 57 tasks (T099-T155)
- **Setup**: 9 tasks (T001-T009)
- **Foundational**: 8 tasks (T010-T017)
- **Polish**: 10 tasks (T155-T164)

- **Parallelizable Tasks**: 89 marked with [P]
- **MVP Scope**: User Story 1 (27 tasks)
- **Format Validation**: ✅ All tasks follow checklist format (checkbox, ID, labels, file paths)
