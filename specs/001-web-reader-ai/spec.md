# Feature Specification: Web Reader AI - Desktop Text-to-Speech Browser Integration

**Feature Branch**: `001-web-reader-ai`  
**Created**: 2026-01-16  
**Status**: Draft  
**Input**: User description: "Point to a tab or a web page and have an AI bot read the text back to me that is on the web page. The application should be a programme that I can run on my computer, not a web application."

## Clarifications

### Session 2026-01-16

- Q: Should application support reading from non-active browser tabs? → A: **YES - Read from any tab regardless of active state.** Application can point to any browser tab (Chrome, Edge, Firefox, or any other browser) whether active, inactive, or selected, and read the content without requiring the user to switch focus to that tab.
- Q: Which browsers should be supported initially? → A: **Any browser.** Support all browsers that can be detected through OS-level window/tab detection mechanisms, prioritizing Chrome, Edge, and Firefox initially, but not limiting to these.
- Q: Which text-to-speech provider should be used? → A: **Piper (open-source neural TTS).** Use Piper (Python package: piper-tts) as the primary TTS provider. Piper is production-ready, runs completely offline, uses pre-trained neural models, requires no paid API keys or cloud services, and delivers natural-sounding speech quality comparable to commercial services. Supports voice selection and speed adjustment (0.5x - 2.0x).
- Q: What CI/CD pipeline and code quality standards should be implemented? → A: **Lean but Solid (Option B).** Implement comprehensive but reasonable CI/CD: (1) Pre-commit hooks run ruff format only (format-on-save, no linting friction); (2) GitHub Actions runs ruff lint with default rules + pytest with ≥80% coverage gates on every PR; (3) No mypy type checking (pytest catches type issues through execution); (4) Branch protection requires all checks pass + 1 review before merge. Tooling: ruff (lint+format), pytest (testing), pytest-cov (coverage reporting).

### Session 2026-01-17

- Q: Should application support reading from browser tabs or just URLs/files? → A: **URL-only MVP (Option A).** Simplify to core functionality: URL input only. Remove browser tab detection, file path support. Users pass URL via CLI, application fetches, extracts text, synthesizes to speech. Browser tabs and file support deferred to P2/future phases.
- Q: How should the CLI frontend be styled for better usability? → A: **Colorized with Progress (Option B).** Use colored output (green/cyan for success, red for errors) with progress indicators for long operations. Clear section dividers. Balances visual clarity with minimal dependencies (no full TUI framework).
- Q: Which packaging/distribution model for standalone CLI tool? → A: **Both PyPI + Standalone Exe (Option C).** Support: (1) PyPI publication for developer installation (`pip install vox`); (2) PyInstaller-generated standalone `.exe` for end users without Python. Both entry points named `vox`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - URL to Audio Reading (Priority: P1)

User provides a URL to the application via CLI, and the application automatically fetches, extracts text, synthesizes to speech, and plays the audio.

**Why this priority**: P1 - Core MVP functionality. Complete end-to-end reading workflow.

**Independent Test**: Can be fully tested by providing any URL (e.g., https://example.com) and verifying the application completes the entire workflow (fetch → extract → synthesize → play) within 10 seconds.

**Acceptance Scenarios**:

1. **Given** user runs `vox read --url https://example.com`, **When** the command executes, **Then** the application fetches the page within 3 seconds, extracts visible text, and begins audio playback
2. **Given** text is extracted from a web page, **When** audio is synthesized, **Then** audio is output with clear, natural-sounding speech at default speed (1.0x)
3. **Given** a complex web page is provided, **When** text is extracted, **Then** content is presented in logical reading order (main content prioritized over navigation/footer)
4. **Given** an invalid or inaccessible URL is provided, **When** the application processes it, **Then** a clear error message is displayed (e.g., "URL fetch failed: check internet connection")

---

### User Story 2 - CLI User Experience (Priority: P1)

User can easily understand what the application is doing via colorized, progress-aware CLI output with clear status messages and error handling.

**Why this priority**: P1 - Essential for usability. Users need to know what's happening during the reading workflow.

**Independent Test**: Can be fully tested by running commands and verifying colored output displays (cyan for status, green for success, red for errors) and progress indicators appear for long operations.

**Acceptance Scenarios**:

1. **Given** user runs a read command, **When** the application is fetching/synthesizing, **Then** colored status messages appear (e.g., cyan "[*] Fetching URL...", green "[OK] Generated 500KB audio")
2. **Given** an error occurs, **When** the application displays it, **Then** the error message is in red with helpful context (e.g., red "[ERROR] URL fetch failed - check internet connection")
3. **Given** user runs `vox --help`, **When** help is displayed, **Then** examples are shown with clear descriptions of available commands

---

### User Story 3 - Packaged Distribution (Priority: P1)

User can install and run vox as a global CLI tool either via `pip install vox` or by downloading a standalone `.exe` file.

**Why this priority**: P1 - Required for real-world usage. Users should not need Python knowledge to run the application.

**Independent Test**: Can be fully tested by: (1) Installing via PyPI and verifying `vox` works globally; (2) Running standalone exe on a clean system without Python and verifying it works.

**Acceptance Scenarios**:

1. **Given** user has Python installed, **When** user runs `pip install vox`, **Then** the command completes and `vox --help` works globally from any directory
2. **Given** user downloads `vox.exe` standalone, **When** user runs it from PowerShell/CMD without Python installed, **Then** the application works and can read URLs
3. **Given** user runs `vox read --url https://example.com`, **Then** both the pip-installed and exe versions produce identical behavior and output

---

### Deferred User Stories (v2+)

The following are removed from v1.0 MVP scope and deferred to v2.0+:

- ❌ **US4-OLD**: Browser tab detection (requires complex tab enumeration; URL input sufficient for MVP)
- ❌ **US5-OLD**: Playback controls (pause/resume/skip) (audio plays in full; users can use system volume for adjustments)
- ❌ **US6-OLD**: Save & resume reading sessions (convenience feature; non-essential for MVP)
- ❌ **US7-OLD**: Extraction settings (power-user feature; deferred)
- ❌ **US8-OLD**: Multiple voices and languages (currently locked to en_US-libritts-high)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Application MUST accept a URL as CLI argument (`vox read --url <URL>`)
- **FR-002**: Application MUST fetch HTML content from provided URL within 3 seconds (or timeout with error)
- **FR-003**: Application MUST extract visible text content from fetched HTML with ≥95% accuracy
- **FR-004**: Application MUST extract text in logical reading order (prioritizing main content over navigation/footer)
- **FR-005**: Application MUST synthesize extracted text to speech using Piper neural TTS at 1.0x speed (default)
- **FR-006**: Application MUST play synthesized audio via system speakers using winsound
- **FR-007**: Application MUST display colorized CLI output with status messages and progress indicators
- **FR-008**: Application MUST handle errors gracefully with clear, user-friendly error messages
- **FR-009**: Application MUST run as standalone desktop application on Windows 11 with no web server required
- **FR-010**: Application MUST be distributable via PyPI (`pip install vox`) with CLI entry point
- **FR-011**: Application MUST be buildable as standalone `.exe` using PyInstaller with zero Python dependencies required to run

### Non-Functional Requirements

- **NFR-001**: Complete URL → Audio workflow within 10 seconds (3s fetch + 5s TTS + 2s playback start)
- **NFR-002**: Memory footprint <300 MB during active reading
- **NFR-003**: Application startup time <2 seconds
- **NFR-004**: All source code formatted with ruff (120 char lines, PEP 8)
- **NFR-005**: All code must maintain ≥80% test coverage with pytest

### Key Entities

- **ReadingTask**: Represents a single read request
  - `url`: Source URL
  - `extracted_text`: Full extracted text content
  - `audio_bytes`: Generated WAV audio data
  - `status`: 'fetching', 'extracting', 'synthesizing', 'playing', 'complete', 'error'
  - `error_message`: Error details if status is 'error'

### Success Criteria *(mandatory)*

- **SC-001**: Users can read any web page aloud within 10 seconds of running the command
- **SC-002**: Text extraction accuracy is ≥95% for standard English web pages
- **SC-003**: Audio narration is intelligible and natural-sounding
- **SC-004**: CLI output is colorized and easy to understand
- **SC-005**: Application works as standalone `.exe` with no Python required
- **SC-006**: Application works via PyPI with `pip install vox`
- **SC-007**: All 185+ existing tests continue to pass
- **SC-008**: No regressions in existing functionality (tabs, file input removed but existing tests remain for removed features)

## Assumptions

- User has a working internet connection for fetching remote web pages
- Piper neural TTS engine is available and downloadable on first use
- Operating system is Windows 11 or later
- Users have system audio output configured (speakers or headphones)
- Python 3.13+ is available for PyPI-based installation
- PyInstaller is available during build process for standalone exe generation
- GitHub Actions or similar CI/CD is available for automated exe builds
- ruff and pytest are available in development environment

## Out of Scope (v1.0)

- Browser tab detection and reading
- Local HTML file input
- Playback pause/resume/skip controls
- Session persistence (save/resume reading)
- Extraction configuration options (power-user features)
- Multiple voices or languages
- Video or image description synthesis
- Automatic content summarization
- Linux or macOS support
- Web-based UI (desktop CLI only)

- Multi-language support (beyond English)
- Mobile/tablet applications
- Web-based version of the application
- Real-time closed captioning or on-screen highlighting
- PDF form filling or interactive element handling
