# Feature Specification: Hotkey Voice Input

**Feature Branch**: `004-hotkey-voice-input`  
**Created**: January 21, 2026  
**Status**: Draft  
**Input**: User description: "Transform CLI tool into a desktop application that runs in the background, triggered by a hotkey (Ctrl+Alt+Space) to record voice, transcribe it, and paste the transcribed text at the current cursor position in any application."

## Clarifications

### Session 2026-01-21

- Q: What type of feedback should indicate recording state? → A: Visual only (translucent pill above taskbar)
- Q: Should app auto-start with Windows? → A: No, manual launch required; hotkey only works when app is open
- Q: What frontend features are needed? → A: Settings (hotkey config) + transcription history with copy
- Q: What Windows versions to support? → A: Windows 11 only
- Q: Is audio input already available in codebase? → A: Yes, existing stt/ module needs repackaging for desktop
- Q: How should recording stop? → A: Hotkey toggle only (press to start, press again to stop); no silence detection

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Voice-to-Text Input (Priority: P1)

As a user, I want to press a hotkey (Ctrl+Alt+Space) while typing in any application, speak my words, and have them automatically typed where my cursor is positioned, so that I can input text hands-free without switching applications.

**Why this priority**: This is the core value proposition - enabling voice input anywhere on the system. Without this, the application has no purpose.

**Independent Test**: Can be fully tested by opening any text input field (Notepad, browser, Word), pressing the hotkey, speaking a phrase, and verifying the text appears at the cursor position.

**Acceptance Scenarios**:

1. **Given** the application is running in the background and Notepad is open with cursor positioned, **When** I press Ctrl+Alt+Space and say "hello world", **Then** "hello world" is typed at the cursor position in Notepad
2. **Given** the application is running and I'm typing in a web browser form field, **When** I press Ctrl+Alt+Space and speak a sentence, **Then** the transcribed text appears in the form field at the cursor position
3. **Given** the application is running and I activate the hotkey, **When** I speak clearly, **Then** the transcription begins within 1 second of speech detection
4. **Given** I have activated recording with the hotkey, **When** I press the hotkey again, **Then** the recording ends and transcription is pasted automatically

---

### User Story 2 - Visual Recording Indicator (Priority: P1)

As a user, I want a small translucent pill-shaped visual indicator centered above the taskbar when recording is active, so that I know when to start and stop speaking without audio distractions.

**Why this priority**: Without feedback, users won't know if the application registered their hotkey press or when recording is active, making the application unusable.

**Independent Test**: Can be tested by pressing the hotkey and observing that the translucent pill indicator appears centered above the taskbar.

**Acceptance Scenarios**:

1. **Given** the application is idle, **When** I press the hotkey, **Then** a small translucent pill-shaped indicator appears centered above the taskbar showing recording is active
2. **Given** recording is active, **When** I press the hotkey again to stop, **Then** the transcription completes, pastes, and the pill indicator shows completion then disappears
3. **Given** recording is active, **When** I press Escape, **Then** the recording is cancelled without pasting, and the pill indicator disappears

---

### User Story 3 - Manual Application Launch with Hotkey Listening (Priority: P2)

As a user, I want to manually open the application, and only then should it listen for the hotkey, so that I have control over when voice input is available.

**Why this priority**: Establishes the core desktop application interaction model. The app must be explicitly launched before hotkey listening begins.

**Independent Test**: Can be tested by launching the application manually and verifying hotkey listening only works after the app is open.

**Acceptance Scenarios**:

1. **Given** the application is not running, **When** I press the hotkey, **Then** nothing happens (no recording triggered)
2. **Given** I manually launch the application, **When** the application window opens, **Then** the hotkey becomes active and ready to trigger recording
3. **Given** the application is running, **When** I close or exit the application, **Then** the hotkey stops working until I relaunch the app

---

### User Story 4 - Application Frontend with Settings and Transcription History (Priority: P2)

As a user, I want a basic frontend window for the application where I can configure settings (like changing the hotkey) and view all my past transcriptions with an easy way to copy them.

**Why this priority**: Important for user adoption - provides control over settings and access to transcription history for reference or reuse.

**Independent Test**: Can be tested by opening the app, changing the hotkey in settings, and viewing/copying past transcriptions from the history view.

**Acceptance Scenarios**:

1. **Given** I open the application, **When** I navigate to settings, **Then** I can change the hotkey combination and save it
2. **Given** I set a custom hotkey, **When** I restart the application, **Then** my custom hotkey preference is preserved
3. **Given** I have recorded transcriptions, **When** I view the transcription history in the app, **Then** I see a list of all past transcriptions with timestamps
4. **Given** I am viewing transcription history, **When** I click a copy button next to a transcription, **Then** the transcription text is copied to my clipboard
5. **Given** I try to set a hotkey already used by the system, **When** I save, **Then** I receive a warning about potential conflicts

---

### User Story 5 - Error Handling and Recovery (Priority: P3)

As a user, I want clear error messages when something goes wrong (microphone unavailable, transcription fails), so that I can troubleshoot issues.

**Why this priority**: Important for reliability but users can work around issues; core functionality must work first.

**Independent Test**: Can be tested by disconnecting the microphone, pressing the hotkey, and verifying an appropriate error message appears.

**Acceptance Scenarios**:

1. **Given** no microphone is connected, **When** I press the hotkey, **Then** I see a notification explaining that no microphone is available
2. **Given** transcription fails due to unclear speech, **When** the operation completes, **Then** I receive feedback that transcription was unsuccessful
3. **Given** the application encounters an error, **When** the error is resolved, **Then** the application recovers automatically without restart

---

### Edge Cases

- What happens when the user presses the hotkey but doesn't speak?
  - Recording continues until hotkey pressed again; empty/silent audio results in no transcription pasted
- What happens when the hotkey is pressed while another recording is in progress?
  - The current recording is stopped and transcribed (toggle behavior: start → stop → transcribe)
- What happens when the cursor is not in a text-editable field?
  - The transcription still completes but may not be pasted; user receives feedback
- What happens during system high CPU/memory usage?
  - Recording continues but user is notified if transcription quality may be affected
- What happens if the application loses focus during recording?
  - Recording continues; paste operation targets the originally focused window/field

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Application MUST run as a background process on Windows
- **FR-002**: Application MUST register a global hotkey (default: Ctrl+Alt+Space) that works from any application
- **FR-003**: Application MUST capture audio from the system's default microphone when hotkey is activated
- **FR-004**: Application MUST transcribe recorded audio to text using speech-to-text capabilities
- **FR-005**: Application MUST paste transcribed text at the current cursor position in the active application
- **FR-006**: Application MUST provide visual feedback via a small translucent pill-shaped indicator centered above the taskbar when recording starts and ends (no audio feedback)
- **FR-007**: Application MUST have a frontend window for settings and transcription history
- **FR-008**: Application MUST allow users to configure the hotkey combination
- **FR-009**: Application MUST persist user settings between sessions
- **FR-010**: Application MUST handle cancellation of recording via Escape key (cancels without transcribing); hotkey press stops and transcribes
- **FR-011**: Application MUST gracefully handle missing or unavailable microphone
- **FR-012**: Application MUST use hotkey toggle to control recording (first press starts, second press stops and transcribes); NO automatic silence detection
- **FR-013**: Application MUST only listen for hotkey when explicitly launched by the user (no auto-start)
- **FR-014**: Application MUST be written in Python (per user requirement)
- **FR-015**: Application MUST keep existing text-to-speech functionality siloed/separate (not removed, but not integrated with this feature)
- **FR-016**: Application MUST store all transcriptions with timestamps and provide easy copy functionality from the history view
- **FR-017**: Application MUST target Windows 11 only

### Key Entities

- **Recording Session**: Represents a single voice capture instance; contains audio data, start/end timestamps, and transcription result
- **Transcription History**: Persistent storage of all past transcriptions with timestamps, accessible from the frontend for viewing and copying
- **User Settings**: Contains hotkey configuration and other user preferences (uses system default microphone per FR-003)
- **Application State**: Tracks whether application is idle, recording, transcribing, or in error state

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a voice-to-text input cycle (hotkey → speak → paste) in under 5 seconds for a typical sentence
- **SC-002**: Transcription accuracy achieves at least 90% word accuracy for clear speech in quiet environments
- **SC-003**: Hotkey response time is under 500ms from keypress to recording start feedback
- **SC-004**: Application consumes less than 50MB memory while idle in background
- **SC-005**: Application works correctly in 95% of common text input scenarios (browsers, text editors, office applications)
- **SC-006**: Users can successfully configure and use a custom hotkey within 1 minute of first opening settings
- **SC-007**: Application starts and becomes responsive within 3 seconds of launch

## Assumptions

- Windows 11 is the target operating system (no support for older Windows versions)
- User has a functional microphone connected to their computer
- User has appropriate permissions to register global hotkeys
- Internet connectivity may be required for transcription (depending on implementation approach)
- The existing speech-to-text module in the codebase can be leveraged or adapted
- Pasting will use standard clipboard/paste mechanism which works in most applications

## Dependencies

- Existing `stt/` (speech-to-text) module in the codebase (to be repackaged for desktop app)
- Windows 11 system APIs for global hotkey registration
- Windows 11 APIs for overlay/translucent window (recording indicator pill)
- Audio capture capabilities on Windows 11

## Out of Scope

- Text-to-speech functionality (siloed per user request, not part of this feature)
- Multi-language support (English only for initial version)
- Custom voice commands or macros
- Cloud-based transcription service integration (can use local models)
- Mobile or cross-platform support
- Voice training or speaker adaptation
