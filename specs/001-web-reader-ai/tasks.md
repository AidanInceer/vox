---
description: "Task breakdown for Web Reader AI feature implementation"
---

# Tasks: Web Reader AI - Desktop Text-to-Speech Browser Integration

**Input**: Design documents from `/specs/001-web-reader-ai/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md (generated), contracts/ (generated)

**Status**: Ready for implementation
**Organization**: Tasks grouped by user story with dependencies; each user story independently testable and deployable

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions
- Each task is specific enough for direct implementation

## Implementation Strategy

**MVP Focus**: User Stories 1-2 deliver core value (any tab reading, URL input)
**Phased Approach**: Build foundation → tab detection → text extraction → TTS → controls → persistence
**Parallel Opportunities**: UI development can proceed in parallel with extraction/TTS after foundation is complete
**Testing**: Tests written first, failing tests before implementation (Test-First Development mandate)

## Phase 1: Setup & Foundation (Shared Infrastructure)

**Purpose**: Project initialization, configuration, testing framework setup

- [X] T001 Create project directory structure per implementation plan in src/, tests/, docs/
- [X] T002 Initialize pyproject.toml with Python 3.13 dependencies: Pillow, NumPy, Pandas, requests, beautifulsoup4, piper-tts, pywinauto, pytest, pytest-cov, ruff (dev), pre-commit (dev)
- [X] T003 [P] Configure pytest with >80% coverage requirement and pytest.ini settings in root
- [X] T004 [P] Create src/config.py with configuration constants (default TTS provider, output paths, timeouts)
- [X] T005 [P] Create src/utils/errors.py with custom exception classes (ExtractionError, TTSError, BrowserDetectionError, TabNotFoundError)
- [X] T006 [P] Create src/utils/logging.py with structured logging configuration
- [X] T007 Create README.md with project overview, quick start, development instructions

---

## Phase 2: Foundational Components (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on

- [X] T008 [P] Create src/browser/tab_info.py with TabInfo dataclass (browser_name, tab_id, title, url, window_handle)
- [X] T009 [P] Create src/extraction/text_extractor.py abstract interface with extract_text(source) → str method signature
- [X] T010 [P] Create src/tts/synthesizer.py abstract TTS interface with synthesize(text) → bytes method signature
- [X] T011 [P] Create src/session/models.py with ReadingSession dataclass (session_id, page_url, title, playback_position, created_at, extraction_settings)
- [X] T012 Create tests/unit/test_errors.py validating all custom exception classes instantiate and format correctly
- [X] T013 Create tests/unit/test_models.py validating dataclass serialization/deserialization for Tab, Page, Session models

**Checkpoint**: Foundation complete - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Page Reading (Priority: P1)

**Goal**: User can read any browser tab aloud without switching to that tab

**Independent Test**: Given a background browser tab, select it from tab list, verify text extraction and audio playback within 2 seconds without focus switch

### Tests for User Story 1 (Test-First Development)

> **WRITE THESE TESTS FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Create tests/unit/test_browser_detector.py with test cases:
  - test_detect_chrome_tabs() - Mock Chrome process, verify >=1 tab detected with title/url
  - test_detect_edge_tabs() - Mock Edge process, verify tabs detected
  - test_detect_firefox_tabs() - Mock Firefox process, verify tabs detected
  - test_tab_detect_inactive_tabs() - Verify inactive background tabs are detected (core US1 requirement)
  - test_detect_all_browsers_simultaneously() - Multiple browsers open, verify all tabs detected

- [ ] T015 [P] [US1] Create tests/unit/test_text_extractor.py with test cases:
  - test_extract_simple_html() - Parse basic HTML, extract text content
  - test_extract_preserves_reading_order() - Text extracted in DOM traversal order
  - test_extract_with_complex_dom() - Nested divs, tables, lists; verify correct extraction
  - test_extract_unicode_content() - Handle special characters, emojis

- [ ] T016 [P] [US1] Create tests/unit/test_tts_synthesizer.py with test cases:
  - test_synthesize_basic_text() - Convert text to audio bytes
  - test_synthesize_long_text() - Handle text >1000 characters
  - test_synthesize_multiple_speeds() - Verify speed parameter affects output

- [ ] T017 [P] [US1] Create tests/integration/test_tab_to_speech.py with test cases:
  - test_full_tab_read_flow() - Open tab, extract text, synthesize, play audio (mocked)
  - test_inactive_tab_read() - Read from background tab without focus switch
  - test_playback_pause_resume() - Start audio, pause, resume from same position
  - test_read_multiple_tabs_sequentially() - Read tab1, then tab2; verify correct content for each

### Implementation for User Story 1

- [ ] T018 [P] [US1] Create src/browser/detector.py implementing Windows process detection:
  - `detect_browser_tabs()` → List[TabInfo]
  - Uses pywinauto to enumerate Chrome, Edge, Firefox processes
  - Extracts tab titles/URLs from window titles or accessibility APIs
  - Returns: list of TabInfo objects with browser_name, tab_id, title, url
  - File: src/browser/detector.py

- [ ] T019 [P] [US1] Create src/browser/accessibility.py wrapping Windows Accessibility API:
  - `get_window_text(window_handle)` → str
  - `get_browser_tabs(process_name)` → List[TabInfo]
  - File: src/browser/accessibility.py

- [ ] T020 [P] [US1] Create src/extraction/html_parser.py implementing BeautifulSoup integration:
  - `parse_html(html_content)` → BeautifulSoup object
  - Extract visible text from DOM
  - Filter out script/style tags
  - File: src/extraction/html_parser.py

- [ ] T021 [US1] Create src/extraction/dom_walker.py implementing DOM traversal:
  - `walk_dom(soup)` → List[str] (ordered text segments)
  - Traverse tree in reading order (depth-first)
  - Preserve paragraph/section boundaries
  - File: src/extraction/dom_walker.py

- [ ] T022 [US1] Implement src/extraction/text_extractor.py concrete class:
  - `extract_from_tab(tab_info)` → str
  - Call browser detector → get tab HTML content
  - Parse HTML → extract text
  - Return combined text
  - File: src/extraction/text_extractor.py

- [ ] T023 [P] [US1] Create src/tts/piper_provider.py implementing Piper neural TTS:
  - `synthesize_piper(text, voice='en_US-libritts-high', speed=1.0)` → bytes (WAV audio)
  - Uses pre-trained Piper models (downloaded on first use, cached locally)
  - Runs completely offline; no API keys or internet required
  - Handle model loading and synthesis errors gracefully
  - File: src/tts/piper_provider.py

- [ ] T024 [P] [US1] Create src/tts/playback.py implementing audio playback:
  - `play_audio(audio_bytes)` → None
  - Use winsound or python-audio library
  - Support pause/resume (store playback state)
  - Support volume/speed controls
  - File: src/tts/playback.py

- [ ] T025 [US1] Implement src/tts/synthesizer.py concrete class:
  - `synthesize_text(text)` → bytes
  - Delegate to Azure provider
  - Cache results to avoid re-synthesis
  - File: src/tts/synthesizer.py

- [ ] T026 [US1] Create src/main.py entry point with basic CLI:
  - Accept command-line arguments: --tab-id, --url, --file
  - Call TextExtractor → Synthesizer → Playback
  - Output progress to console
  - File: src/main.py

**Checkpoint**: User Story 1 complete and independently testable. Can be demoed as: "Select a browser tab, hit read button, hear content aloud from that tab without switching focus."

---

## Phase 4: User Story 2 - Pointing to Web Pages (Priority: P1)

**Goal**: User can provide URL or file path to application and have that content read aloud

**Independent Test**: Given a URL and a local HTML file, verify text extraction and playback works without browser involvement

### Tests for User Story 2

> **WRITE THESE TESTS FIRST**

- [ ] T027 [P] [US2] Create tests/unit/test_url_fetcher.py with test cases:
  - test_fetch_valid_url() - HTTP GET request, verify response content
  - test_fetch_with_timeout() - Request exceeds timeout, handle gracefully
  - test_fetch_invalid_url() - Non-existent domain, return error
  - test_fetch_requires_auth() - Password-protected page, handle 401

- [ ] T028 [P] [US2] Create tests/unit/test_file_loader.py with test cases:
  - test_load_local_html_file() - Read HTML from disk
  - test_load_nonexistent_file() - File not found, return error
  - test_load_with_encoding() - Handle UTF-8 and other encodings

- [ ] T029 [P] [US2] Create tests/integration/test_url_to_speech.py with test cases:
  - test_full_url_read_flow() - Fetch URL, extract text, synthesize, playback
  - test_file_read_flow() - Load local HTML, extract, synthesize, playback
  - test_complex_webpage_extraction() - Real webpage with nav/header/footer, verify main content prioritized

### Implementation for User Story 2

- [ ] T030 [P] [US2] Create src/extraction/url_fetcher.py:
  - `fetch_url(url, timeout=10)` → str (HTML content)
  - Use requests library
  - Handle redirects, timeouts, errors
  - Return HTML or raise URLFetchError
  - File: src/extraction/url_fetcher.py

- [ ] T031 [P] [US2] Create src/extraction/file_loader.py:
  - `load_file(file_path)` → str (HTML content)
  - Accept .html, .htm files
  - Auto-detect encoding
  - Return content or raise FileLoadError
  - File: src/extraction/file_loader.py

- [ ] T032 [US2] Update src/extraction/text_extractor.py to support multiple sources:
  - `extract_from_url(url)` → str
  - `extract_from_file(file_path)` → str
  - Reuse HTML parsing logic from existing impl
  - File: src/extraction/text_extractor.py (update existing)

- [ ] T033 [P] [US2] Create src/extraction/content_filter.py implementing section extraction:
  - `filter_main_content(soup)` → BeautifulSoup (filtered DOM)
  - Detect and remove: nav, header, footer, sidebar, ads
  - Prioritize main article/content sections
  - File: src/extraction/content_filter.py

- [ ] T034 [US2] Update src/main.py to accept URL and file arguments:
  - `pagereader read --url https://...`
  - `pagereader read --file local.html`
  - File: src/main.py (update CLI)

**Checkpoint**: User Story 2 complete. Can be demoed as: "Provide a URL or file, application reads content aloud."

---

## Phase 5: User Story 3 - Browser Tab Detection & Pointing (Priority: P2)

**Goal**: User can see list of all open browser tabs and select one to read without manual URL entry

**Independent Test**: Given multiple open tabs across different browsers, open tab picker UI, select a tab, verify correct content is read

### Tests for User Story 3

- [ ] T035 [P] [US3] Create tests/unit/test_tab_picker.py with test cases:
  - test_list_all_open_tabs() - Multiple browsers, verify all tabs listed
  - test_select_tab_by_id() - Select tab from list, return correct TabInfo
  - test_tab_list_updates() - New tab opened, verify list updates

- [ ] T036 [P] [US3] Create tests/integration/test_tab_selection_workflow.py with test cases:
  - test_picker_ui_displays_tabs() - UI shows all tabs with titles
  - test_select_background_tab_and_read() - Select non-active tab, read it

### Implementation for User Story 3

- [ ] T037 [P] [US3] Create src/ui/tab_picker.py with tab selection interface:
  - Display all open tabs in console/GUI list
  - Accept user selection by ID or title
  - Return selected TabInfo
  - File: src/ui/tab_picker.py

- [ ] T038 [US3] Update src/main.py with tab picker command:
  - `pagereader tabs` - List all open browser tabs
  - `pagereader read --tab <id>` - Read selected tab
  - File: src/main.py (update CLI)

- [ ] T039 [US3] Create src/ui/cli.py CLI interface with commands:
  - `pagereader read --active` - Read currently active tab
  - `pagereader read --url <url>` - Read from URL
  - `pagereader read --file <path>` - Read from file
  - `pagereader tabs` - List all open tabs
  - File: src/ui/cli.py

**Checkpoint**: User Story 3 complete. Provides convenient tab picking UI.

---

## Phase 6: User Story 4 - Reading Control & Navigation (Priority: P2)

**Goal**: User can control playback (speed, volume, pause/resume, section skip)

**Independent Test**: Given audio playing from a webpage, verify speed/volume changes apply, pause works, resume continues from same position

### Tests for User Story 4

- [ ] T040 [P] [US4] Create tests/unit/test_playback_controls.py with test cases:
  - test_set_playback_speed() - Speed 0.5x, 1.0x, 2.0x; verify output reflects speed
  - test_set_volume() - Volume 0-100%; verify audio level changes
  - test_pause_resume() - Pause at position X, resume; verify position preserved

- [ ] T041 [P] [US4] Create tests/integration/test_control_workflow.py with test cases:
  - test_adjust_speed_during_playback() - Audio playing, change speed; verify no artifacts
  - test_section_skip() - Long article, skip to next section; verify correct jump

### Implementation for User Story 4

- [ ] T042 [P] [US4] Create src/tts/playback.py advanced controls (update existing):
  - `set_playback_speed(factor)` - 0.5x to 2.0x
  - `set_volume(level)` - 0-100%
  - `pause()` and `resume()` - Pause/resume with position tracking
  - `skip_to_section(section_num)` - Jump to next section marker
  - File: src/tts/playback.py (update)

- [ ] T043 [US4] Create src/extraction/section_splitter.py for document structure:
  - `split_into_sections(text)` → List[Section]
  - Detect section boundaries (headers, paragraph breaks)
  - Return sections with start position, heading text
  - File: src/extraction/section_splitter.py

- [ ] T044 [US4] Update src/tts/synthesizer.py to map sections to audio:
  - Track section boundaries in synthesized audio
  - Enable skip-to-section functionality
  - File: src/tts/synthesizer.py (update)

- [ ] T045 [US4] Create src/ui/playback_ui.py with interactive controls:
  - Display: Current time, total duration, playback speed, volume
  - Keyboard shortcuts: P=pause, R=resume, +/- for speed/volume, N=next section
  - File: src/ui/playback_ui.py

- [ ] T046 [US4] Update src/main.py with playback interactive mode:
  - After synthesis, present playback UI with controls
  - Accept keypresses and adjust playback
  - File: src/main.py (update)

**Checkpoint**: User Story 4 complete. Provides fine-grained control over playback.

---

## Phase 7: User Story 5 - Save & Resume Reading (Priority: P3)

**Goal**: User can save reading sessions and resume later from same position

**Independent Test**: Start reading, save session, exit app, restart, resume; verify same content plays from saved position

### Tests for User Story 5

- [ ] T047 [P] [US5] Create tests/unit/test_session_persistence.py with test cases:
  - test_save_session() - Session saved to storage with all fields
  - test_load_session() - Load session, verify data integrity
  - test_session_list() - List all saved sessions

- [ ] T048 [P] [US5] Create tests/integration/test_session_resume_workflow.py with test cases:
  - test_save_and_resume_same_page() - Full workflow: read, save, resume

### Implementation for User Story 5

- [ ] T049 [P] [US5] Create src/session/storage.py with persistence layer:
  - SQLite database for session storage
  - Tables: sessions (id, url, title, position, timestamp, settings)
  - Methods: save_session(), load_session(), list_sessions(), delete_session()
  - File: src/session/storage.py

- [ ] T050 [US5] Create src/session/session_manager.py managing session lifecycle:
  - `save_reading_session(page_url, title, playback_position, settings)` → session_id
  - `load_session(session_id)` → ReadingSession
  - `resume_session(session_id)` → auto-fetch page, synthesize, playback from position
  - File: src/session/session_manager.py

- [ ] T051 [US5] Update src/main.py with session commands:
  - `pagereader save` - Save current reading to session
  - `pagereader resume <session_id>` - Resume saved session
  - `pagereader sessions` - List all saved sessions
  - File: src/main.py (update)

**Checkpoint**: User Story 5 complete. Enables multi-session reading workflows.

---

## Phase 8: User Story 6 - Content Extraction Options (Priority: P3)

**Goal**: User can configure which page elements to include in extraction (main only, include alt-text, etc.)

**Independent Test**: Extract same page with different settings; verify extraction differs based on configuration

### Tests for User Story 6

- [ ] T052 [P] [US6] Create tests/unit/test_extraction_settings.py with test cases:
  - test_extract_main_content_only() - Nav/footer excluded, main text included
  - test_extract_with_alt_text() - Image alt-text included in output
  - test_extract_exclude_script() - Script tags properly removed

- [ ] T053 [P] [US6] Create tests/integration/test_settings_application.py with test cases:
  - test_apply_settings_to_extraction() - Settings persist and apply across extractions

### Implementation for User Story 6

- [ ] T054 [P] [US6] Create src/config/extraction_settings.py:
  - ExtractionSettings dataclass: include_nav, include_header, include_footer, include_alt_text, etc.
  - `load_settings()` → ExtractionSettings from config file
  - `save_settings(settings)` → persist to config
  - File: src/config/extraction_settings.py

- [ ] T055 [US6] Update src/extraction/content_filter.py to respect settings:
  - `filter_content(soup, settings)` - Apply user-defined filters
  - File: src/extraction/content_filter.py (update)

- [ ] T056 [US6] Create src/ui/settings_menu.py for user configuration:
  - Display extraction options
  - Allow toggle on/off
  - Save preferences
  - File: src/ui/settings_menu.py

- [ ] T057 [US6] Update src/main.py with settings commands:
  - `pagereader settings` - Show current settings
  - `pagereader settings --main-only` - Toggle main-content-only mode
  - File: src/main.py (update)

**Checkpoint**: User Story 6 complete. Enables power-user customization.

---

**Total Tasks**: Now 70 tasks (was 68; added T064-T066 for CI/CD setup)

- [ ] T058 [P] Create src/utils/validators.py with input validation:
  - `validate_url(url)` → bool
  - `validate_file_path(path)` → bool
  - `validate_tab_id(tab_id)` → bool
  - File: src/utils/validators.py

- [ ] T059 [P] Create src/utils/cache.py for caching extracted text:
  - Cache extracted text from URLs (avoid re-fetching)
  - Cache synthesized audio (avoid re-synthesizing)
  - TTL: 1 hour per cache entry
  - File: src/utils/cache.py

- [ ] T060 [P] Add error handling throughout:
  - Update all modules to raise appropriate custom exceptions
  - Add error messages to output
  - File: various (update existing)

- [ ] T061 [P] Create docs/API_REFERENCE.md:
  - Document all public functions/classes
  - Include example usage for each module
  - File: docs/api_reference.md

- [ ] T062 Create docs/ARCHITECTURE.md:
  - High-level system design
  - Module interaction diagrams
  - Data flow diagrams
  - File: docs/architecture.md

- [ ] T063 Run pytest with coverage:
  - Generate coverage report
  - Verify >=80% unit test coverage
  - File: pytest --cov=src tests/

- [X] T064 [P] Create .github/workflows/tests.yml GitHub Actions pipeline (REQUIRED):
  - Trigger: on every push to PR and main branch
  - Steps: (1) checkout code, (2) setup Python 3.13, (3) install dependencies via uv/pip, (4) run ruff lint, (5) run pytest with coverage, (6) enforce ≥80% coverage gate, (7) report results
  - Fail PR if: lint fails OR coverage <80%
  - File: .github/workflows/tests.yml

- [X] T065 [P] Configure pre-commit hooks for local development (REQUIRED):
  - Install pre-commit framework
  - Configure: ruff format (auto-fix) on every commit
  - Does NOT run linting or tests (those are in CI)
  - File: .pre-commit-config.yaml

- [X] T066 [P] Create ruff configuration (REQUIRED):
  - Use ruff default PEP 8 ruleset (no custom rules needed)
  - Configure line length: 100 characters
  - Configure exclude: tests/, .venv/, build/
  - File: pyproject.toml [tool.ruff] section

- [ ] T067 Final integration test with real browser:
  - Open Chrome/Edge/Firefox with test tabs
  - Run full application workflow
  - Verify text extraction, TTS, playback all work end-to-end
  - File: tests/integration/test_full_system.py

- [ ] T068 Performance profiling:
  - Measure text extraction speed (target <3 seconds)
  - Measure TTS synthesis speed (target <5 seconds)
  - Measure memory usage (target <300 MB active)
  - File: tests/performance/test_benchmarks.py

- [ ] T069 Create CONTRIBUTING.md with development guidelines:
  - Code style (PEP 8)
  - Test-first requirements
  - PR checklist (tests passing, coverage maintained)
  - File: docs/contributing.md

- [ ] T070 Create CHANGELOG.md documenting v1.0.0 release

**Checkpoint**: Application feature-complete and ready for release.

---

## Dependencies & Execution Order

### Critical Path (Blocking Dependencies)

```
T001-T007 (Setup)
  ↓
T008-T013 (Foundation)
  ↓
T014-T026 (US1: Tab Reading)
  ↓
T027-T034 (US2: URL Input)
  ↓
T035-T046 (US3-4: Controls & Selection)
  ↓
T047-T057 (US5-6: Sessions & Settings)
  ↓
T058-T068 (Polish & Release)
```

### Parallel Execution Opportunities

**After T013 completes**, the following can run in parallel:
- T014-T026 (US1 implementation)
- T027-T034 (US2 implementation)
- T035-T046 (US3-4 implementation)

**After T026 completes (US1 done)**:
- T027-T034 (US2) and T035-T046 (US3-4) can continue in parallel

**After T034 completes (US2 done)**:
- T035-T046 (US3-4) can accelerate

**Final Polish (T058-T068)** can proceed after T057 with periodic merges

### MVP Scope (v1.0.0 - Minimum Viable Product)

**Required for release** (Tasks T001-T034):
- ✅ Setup & foundation
- ✅ US1: Read any browser tab without switching focus
- ✅ US2: Read from URL or local file
- ✅ Basic playback controls (play, pause, stop)

**Optional for v1.0** (Tasks T035-T068):
- ⚠️ US3: Tab picker UI (nice-to-have; CLI arg alternative exists)
- ⚠️ US4: Advanced controls (speed, volume, skip sections)
- ⚠️ US5: Session save/resume (convenience feature)
- ⚠️ US6: Extraction settings (power-user feature)
- ⚠️ Polish & optimization

**Release Gate**: T001-T034 complete, T064-T066 CI/CD setup complete, T063 passing (≥80% coverage), T067 passes on real browser, all GitHub Actions checks passing

---

## Success Metrics (from spec.md)

Each task contributes to one or more success criteria:

- **SC-001** (Read within 3 seconds): T018, T022, T032, T042, T044
- **SC-002** (95% text extraction accuracy): T014, T020, T021, T033
- **SC-003** (Voice quality 90% rated good): T023, T024, T025
- **SC-004** (Handle 100+ MB pages): T020, T066
- **SC-005** (Resume in 1 second): T049, T050
- **SC-006** (Speed/volume controls work): T042, T044, T046
- **SC-007** (Detect 95% of tabs): T014, T018, T019
- **SC-008** (Memory <300 MB): T066
- **SC-009** (100% session recovery): T047, T049, T050
