# Feature Specification: Speech-to-Text Integration & Project Documentation Enhancement

**Feature Branch**: `003-speech-to-text`  
**Created**: January 18, 2026  
**Status**: Draft  
**Input**: User description: "For phase three of the project, there are a few things I want you to do: For the prerequisites, I want you to add an agents and a claude.md file with all the required information to ensure that this Python project is high quality and general software engineering best practises are implemented. Also, add a high-level summary and overview of the project structure and what this project does. Overhaul the main README file so it's focused on how to use it, what it is, how to install it, and how to run it. And then for phase three, the core implementation, I want you to change the name of the project from Page Reader to something else which also incorporates speech-to-text as well as a text-to-speech. For phase three of the project, that will be adding a second component to this that allows someone through the CLI to call Page Reader, record their voice, and have that be transformed to text."

## Clarifications

### Session 2026-01-18

- Q: What should be the implementation order of the user stories? → A: **Voice Recording to Text should be completed last (P4)**. Implementation sequence: (1) Project Rebranding (P1), (2) Developer Documentation (P2), (3) README Overhaul (P3), (4) Voice Recording to Text (P4). This ensures all foundational work (naming, documentation standards) is in place before implementing the new STT feature.
- Q: What should the new project name be? → A: **vox**. This name reflects the core audio-text capabilities (voice-focused, bidirectional), is concise, memorable, and available on PyPI/GitHub.
- Q: What CLI command structure should be used for TTS and STT features? → A: **`vox read --url <url>` for TTS, `vox transcribe` for STT**. TTS uses "read" verb matching the original vox concept, STT uses distinct "transcribe" verb for clarity.
- Q: Which speech-to-text engine should be used? → A: **Whisper (via faster-whisper library)**. Provides excellent accuracy (95%+), active development, good performance with medium-sized models (~1-2GB), and strong community support.
- Q: How should users stop the recording? → A: **Press Enter to stop recording**. Simpler and more user-friendly than Ctrl+C, provides clear intentional action. Silence detection (5 seconds) acts as automatic fallback if user forgets to press Enter.
- Q: What should be the default output behavior for transcriptions? → A: **Display in terminal (stdout)**. Provides immediate feedback. Users can optionally save to file using `--output file.txt` flag or redirect stdout via shell (`> file.txt`).
- Q: What should happen when multiple microphones are available? → A: **Use system default microphone**. Respects Windows audio settings, predictable behavior, no interactive prompts. Users configure preferred mic via Windows Sound settings.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Project Rebranding (Priority: P1)

Project name is updated from "vox" to a new name that reflects both text-to-speech and speech-to-text capabilities, visible across all codebase references, documentation, and distribution artifacts.

**Why this priority**: P1 - Essential foundation for all subsequent work. Users should understand the tool now handles bidirectional audio-text conversion. Must be completed first to avoid rework in documentation and code.

**Independent Test**: Can be fully tested by verifying the new name appears consistently in: CLI commands, package name, README, pyproject.toml, help text, and distributed executables.

**Acceptance Scenarios**:

1. **Given** user installs the package, **When** pip install completes, **Then** package is installed as "vox"
2. **Given** user runs help command, **When** CLI help displays, **Then** "vox" appears in banner and description
3. **Given** user examines project documentation, **When** README and other docs are reviewed, **Then** all references use "vox" consistently
4. **Given** user downloads standalone executable, **When** filename is checked, **Then** executable is named `vox.exe`

---

### User Story 2 - Developer Documentation & Best Practices (Priority: P2)

Developers contributing to the project can quickly understand project structure, coding standards, and AI agent guidelines through comprehensive documentation files.

**Why this priority**: P2 - Establishes quality standards and guidelines before major development work begins. Ensures consistent code quality for subsequent features.

**Independent Test**: Can be fully tested by verifying new developers can: (1) understand project architecture from overview docs, (2) follow coding standards from guidelines, (3) configure AI agents using provided templates.

**Acceptance Scenarios**:

1. **Given** developer reads the project overview, **When** examining documentation, **Then** high-level architecture, module purposes, and data flow are clearly explained
2. **Given** developer reviews claude.md or agents file, **When** following guidelines, **Then** AI coding standards, testing requirements, and quality gates are documented
3. **Given** developer examines project structure documentation, **When** locating code, **Then** directory organization, module responsibilities, and dependency relationships are clear
4. **Given** developer needs to understand best practices, **When** consulting documentation, **Then** code quality standards, testing patterns, and contribution workflows are specified

---

### User Story 3 - User-Focused README Overhaul (Priority: P3)

Users visiting the project repository can immediately understand what the tool does, how to install it, and how to use both TTS and STT features through clear, concise README documentation.

**Why this priority**: P3 - Critical for user adoption and onboarding. Should reflect the rebranded name and document both existing TTS and upcoming STT features.

**Independent Test**: Can be fully tested by new users reading only the README and successfully installing, configuring, and using both text-to-speech and speech-to-text features without external help.

**Acceptance Scenarios**:

1. **Given** user reads README introduction, **When** scanning the first section, **Then** project purpose and key features are understood within 30 seconds
2. **Given** user follows installation instructions, **When** executing commands, **Then** installation completes successfully on Windows 11 with all dependencies
3. **Given** user reads usage examples, **When** running provided commands, **Then** both TTS (URL reading) and STT (voice transcription) work as documented
4. **Given** user encounters issues, **When** consulting README, **Then** troubleshooting section provides solutions for common problems

---

### User Story 4 - Voice Recording to Text (Priority: P4)

User invokes the CLI with a voice recording command, speaks into their microphone, and receives the transcribed text output immediately.

**Why this priority**: P4 - Core speech-to-text functionality completed last after all foundational work (rebranding, documentation) is in place. Ensures new feature is documented correctly from the start.

**Independent Test**: Can be fully tested by running the CLI command, recording a 10-second voice sample, and verifying accurate text transcription is displayed and/or saved to a file.

**Acceptance Scenarios**:

1. **Given** user runs `vox transcribe`, **When** user speaks into microphone and presses Enter, **Then** recording stops and transcribed text appears in the terminal
2. **Given** user completes recording, **When** transcription finishes, **Then** text output is displayed with 95%+ accuracy for clear speech
3. **Given** user specifies `vox transcribe --output file.txt`, **When** transcription completes, **Then** text is saved to the specified file path
4. **Given** no microphone is detected, **When** user attempts `vox transcribe`, **Then** clear error message indicates microphone setup issue with troubleshooting steps

---

### Edge Cases

- What happens when the system default microphone hardware is not available or in use by another application?
- How does the system handle background noise during voice recording?
- What if the user's speech is too quiet or has heavy accent/non-standard pronunciation?
- How does the system behave if the recording duration exceeds a reasonable limit (e.g., 10 minutes)?
- What happens when the user stops speaking mid-recording (silence detection)?
- How does the CLI handle recording interruptions (Ctrl+C, system crash)?
- What if the transcription service (Whisper model) fails to load or encounters an error?
- How does the project name change affect existing saved sessions and configuration files?
- What happens if user has multiple microphones but none is set as system default in Windows?

## Requirements *(mandatory)*

### Functional Requirements

#### Speech-to-Text Core (FR-STT)

- **FR-STT-001**: Application MUST provide CLI command `vox transcribe` for initiating voice recording and transcription
- **FR-STT-002**: Application MUST detect and use the Windows system default microphone for audio capture (as configured in Windows Sound settings)
- **FR-STT-003**: Application MUST record audio at a minimum quality of 16kHz sample rate for accurate transcription
- **FR-STT-004**: Application MUST transcribe recorded speech to text with 95%+ word accuracy for clear English speech
- **FR-STT-005**: Application MUST display transcribed text to stdout (terminal) by default upon transcription completion
- **FR-STT-006**: Application MUST support optional `--output` flag to save transcription to a user-specified text file instead of or in addition to terminal display
- **FR-STT-007**: Application MUST use OpenAI Whisper via the faster-whisper library for offline speech-to-text processing, requiring no API keys or cloud services
- **FR-STT-008**: Application MUST provide visual feedback during recording (e.g., "Recording... Press Enter to stop")
- **FR-STT-009**: Application MUST stop recording when user presses Enter key
- **FR-STT-010**: Application MUST detect and handle silence periods to auto-terminate recording after 5 seconds of continuous silence as a fallback mechanism

#### Project Rebranding (FR-RB)

- **FR-RB-001**: Project name MUST be changed from "vox" to "vox" reflecting both TTS and STT capabilities
- **FR-RB-002**: TTS CLI command MUST be `vox read --url <url>` to maintain compatibility with original vox "read" concept
- **FR-RB-003**: New project name MUST appear in all CLI command help text and version information
- **FR-RB-004**: PyPI package name MUST be updated to reflect new project name
- **FR-RB-005**: All code-level references (module imports, class names, function names) MUST be refactored to use new name conventions where appropriate
- **FR-RB-006**: Standalone executable filename MUST reflect new project name
- **FR-RB-007**: Git repository name and remote URLs MUST be updated to new name
- **FR-RB-008**: All documentation files (README, specs, comments) MUST reference the new project name

#### Documentation & Best Practices (FR-DOC)

- **FR-DOC-001**: Project MUST include an "agents" or "claude.md" file with AI agent coding guidelines and quality standards
- **FR-DOC-002**: Documentation MUST specify required code quality practices (linting with ruff, testing with pytest, coverage ≥80%)
- **FR-DOC-003**: Documentation MUST include a high-level project architecture overview explaining module organization
- **FR-DOC-004**: Documentation MUST describe data flow for both TTS and STT workflows
- **FR-DOC-005**: Documentation MUST specify testing requirements and CI/CD pipeline expectations
- **FR-DOC-006**: Documentation MUST outline contribution guidelines and code review standards
- **FR-DOC-007**: README MUST be overhauled with clear sections: What It Is, Installation, Usage (TTS + STT), Troubleshooting
- **FR-DOC-008**: README MUST prioritize end-user instructions over developer/contributor details
- **FR-DOC-009**: README MUST provide quick-start examples for both TTS and STT use cases within first 3 sections

### Key Entities

- **Voice Recording**: Audio captured from microphone, represented by audio buffer/stream data with sample rate, duration, and format metadata
- **Transcription Result**: Text output from speech-to-text processing, including confidence scores, timestamps (if supported), and raw text content
- **Microphone Device**: System audio input hardware, identified by device name, capabilities, and availability status
- **STT Engine Configuration**: Settings for speech recognition model, including language, model size, and quality parameters

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully record voice and receive accurate text transcription within 10 seconds of stopping recording
- **SC-002**: Speech-to-text transcription achieves 95%+ word accuracy for clear English speech in quiet environments
- **SC-003**: CLI command for voice recording works consistently across Windows 11 systems with standard microphone hardware
- **SC-004**: Project rebranding is complete with zero broken references or outdated naming in distributed packages and documentation
- **SC-005**: New developers can understand project architecture and start contributing within 1 hour of reading documentation
- **SC-006**: README enables new users to install and use both TTS and STT features successfully on first attempt (90%+ success rate)
- **SC-007**: AI agents using claude.md guidelines produce code meeting quality standards (80%+ test coverage, passing linting)
- **SC-008**: Voice recording handles microphone setup issues gracefully with clear error messages reducing support requests by 70%

## Assumptions *(mandatory)*

- Users have a functional microphone connected and configured in Windows 11 audio settings
- Users are recording in environments with minimal background noise for optimal transcription accuracy
- English language is the primary target for speech-to-text transcription in this phase
- The new project name will be determined through collaborative discussion and will balance clarity with brevity
- Existing saved TTS sessions will remain compatible after rebranding through migration or backward compatibility
- The project will continue to prioritize offline functionality, using local speech-to-text models rather than cloud APIs
- Standard Python packaging conventions will be followed for renaming (package name matches CLI entry point)
- Documentation follows Markdown best practices and is version-controlled in the repository

## Out of Scope *(mandatory)*

- Multi-language support for speech-to-text (English only in Phase 3)
- Real-time streaming transcription (batch processing after recording completes)
- Voice activity detection for automatic recording start/stop beyond simple silence detection
- Cloud-based speech recognition services or API integrations
- Audio file transcription (e.g., upload existing MP3/WAV files) - CLI recording only
- Voice command integration for controlling TTS playback
- Speaker identification or diarization for multi-speaker transcription
- Integration with external note-taking or productivity applications
- Mobile platform support (remains Windows 11 desktop only)
- Voice training or personalized speech models
- Accent or dialect-specific transcription optimization

## Dependencies *(mandatory)*

### External Dependencies

- **Speech-to-text library**: Whisper via faster-whisper library (provides CTranslate2-optimized Whisper models for efficient offline transcription)
- **Audio input library**: Requires Python library for microphone access (e.g., sounddevice, pyaudio)
- **Existing TTS infrastructure**: Builds on Phase 1-2 Piper TTS and playback systems

### Internal Dependencies

- **Phase 1**: Core URL fetching and text extraction (already implemented)
- **Phase 2**: Playback session improvements and controls (already implemented)
- **CLI framework**: Existing Click or argparse CLI infrastructure for adding STT commands
- **Project structure**: Current module organization in src/ directory

### Process Dependencies

- **Naming decision**: Rebranding blocked until new project name is finalized through team/stakeholder discussion
- **Testing infrastructure**: Speech-to-text features require audio testing fixtures and mocking strategies
- **Documentation review**: Technical writing review for new README and developer documentation

## Notes *(optional)*

### Technical Considerations

- **Offline-first priority**: Following project precedent from Phase 1 (Piper TTS), the STT solution uses Whisper for fully offline transcription to avoid cloud dependencies and API costs
- **Whisper model selection**: faster-whisper provides multiple model sizes (tiny/base/small/medium/large). Default to **medium model** (1.5GB) for optimal balance between accuracy (95%+) and performance (~10 seconds transcription time for 1 minute audio on typical hardware).
- **Audio format consistency**: Record audio in WAV format at 16kHz to match Whisper model requirements without transcoding overhead
- **Microphone permissions**: Windows 11 has privacy controls for microphone access - documentation should guide users through permission setup
- **GPU acceleration**: faster-whisper supports optional CUDA acceleration; implementation should gracefully fall back to CPU if GPU unavailable

### Project Naming Decision

The project has been renamed to **vox**.

**Rationale**:
- **Concise & Memorable**: Single syllable, easy to type and pronounce
- **Voice-Focused**: Latin root "vox" means "voice", perfectly aligned with TTS/STT capabilities
- **Availability**: Available on PyPI and GitHub for package/repository naming
- **Professional**: Clean, technical-sounding name suitable for developer tools
- **Bidirectional**: Implies voice-based interaction without restricting to input or output only

**Implementation Notes**: Update all references from "vox" to "vox" including:
- Package name: `vox`
- CLI command: `vox`
- Executable: `vox.exe`
- Module imports: `from vox import ...`
- Configuration directory: `%APPDATA%/vox/`

### Documentation Structure Recommendation

For the new "agents" or "claude.md" file, suggest including:
1. **Project Overview**: High-level purpose, target users, key features
2. **Architecture**: Module diagram, data flow, separation of concerns
3. **Code Quality Standards**: Ruff linting rules, pytest coverage thresholds (80%+), type hinting guidelines
4. **Testing Patterns**: Unit test structure, integration test approach, mocking strategies for audio I/O
5. **CI/CD Pipeline**: GitHub Actions workflows, pre-commit hooks, branch protection rules
6. **Contribution Workflow**: Branch naming, commit message format, PR review checklist
7. **AI Agent Guidelines**: Specific instructions for code generation, refactoring principles, documentation requirements
