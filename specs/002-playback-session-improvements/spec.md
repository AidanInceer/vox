# Feature Specification: Enhanced Playback Controls and Performance

**Feature Branch**: `002-playback-session-improvements`  
**Created**: 2026-01-17  
**Status**: Draft  
**Input**: User description: "Enhanced playback controls, session management, and performance improvements through text chunking for PageReader"

## Clarifications

### Session 2026-01-18

- Q: Should play_audio() block until audio finishes (synchronous) or return immediately (non-blocking)? → A: Blocking (synchronous) - play_audio() must wait until audio finishes before returning
  - Implementation: Added `pygame.mixer.music.get_busy()` polling loop in AudioPlayback.play_audio() to block until playback completes
  - Technical detail: Polls at 10Hz using `pygame.time.Clock().tick(10)` to avoid busy-waiting while maintaining responsiveness

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Session Management (Priority: P1)

User can save reading sessions with custom names for later retrieval, allowing them to pause reading on one device and resume on another or at a different time.

**Why this priority**: P1 - Core functionality for user convenience. Enables users to manage multiple reading sessions and return to previously read content without losing their place.

**Independent Test**: Can be fully tested by running `pagereader read --url https://example.com --save-session my-article`, verifying the session is saved with the specified name, and that saved sessions can be listed and resumed independently.

**Acceptance Scenarios**:

1. **Given** user runs `pagereader read --url https://example.com --save-session my-article`, **When** the reading begins, **Then** the session is saved with name "my-article" including URL, content, and playback position
2. **Given** a session named "my-article" exists, **When** user runs `pagereader list-sessions`, **Then** "my-article" appears in the list with creation date and URL
3. **Given** a saved session exists, **When** user runs `pagereader resume my-article`, **Then** playback resumes from the last known position
4. **Given** user provides an invalid session name, **When** attempting to resume, **Then** a clear error message appears (e.g., "Session 'xyz' not found")

---

### User Story 2 - Interactive Playback Controls (Priority: P1)

User can control audio playback in real-time using keyboard shortcuts to pause, resume, skip forward/backward, adjust speed, and quit playback.

**Why this priority**: P1 - Essential for usability. Users need control over audio playback without relying on system-level controls or stopping the entire application.

**Independent Test**: Can be fully tested by starting playback and verifying each keyboard control works independently: spacebar pauses/resumes, Q quits, arrow keys navigate and adjust speed.

**Acceptance Scenarios**:

1. **Given** audio is playing, **When** user presses spacebar, **Then** playback pauses and displays "Paused" status
2. **Given** audio is paused, **When** user presses spacebar, **Then** playback resumes from the same position
3. **Given** audio is playing, **When** user presses Q, **Then** playback stops immediately and application exits cleanly
4. **Given** audio is playing, **When** user presses right arrow, **Then** playback skips forward 10 seconds
5. **Given** audio is playing, **When** user presses left arrow, **Then** playback skips backward 10 seconds
6. **Given** audio is playing, **When** user presses up arrow, **Then** playback speed increases by 0.25x (max 2.0x)
7. **Given** audio is playing, **When** user presses down arrow, **Then** playback speed decreases by 0.25x (min 0.5x)
8. **Given** playback speed changes, **When** speed reaches min/max limits, **Then** a message displays the current speed (e.g., "Speed: 2.0x (max)")

---

### User Story 3 - Streaming Text-to-Speech with Chunking (Priority: P2)

User experiences faster feedback and improved responsiveness when reading long articles, as the application begins audio playback after processing the first chunk while preparing subsequent chunks in the background.

**Why this priority**: P2 - Performance enhancement. Significantly improves user experience for long content but core functionality works without it.

**Independent Test**: Can be fully tested by reading a long article (5000+ words) and verifying audio begins within 2-3 seconds while remaining chunks process in background, compared to 10+ seconds for full processing.

**Acceptance Scenarios**:

1. **Given** user reads a 5000-word article, **When** text extraction completes, **Then** audio playback begins within 3 seconds (first chunk of 150 words synthesized)
2. **Given** first chunk is playing, **When** playback continues, **Then** subsequent chunks are synthesized in background without playback interruption
3. **Given** user skips forward during playback, **When** landing in an un-synthesized chunk, **Then** a brief "buffering" indicator appears and synthesis happens on-demand within 1 second
4. **Given** a short article (under 150 words), **When** reading begins, **Then** the entire article is treated as a single chunk with no chunking overhead
5. **Given** chunking is active, **When** network or processing errors occur mid-stream, **Then** playback continues with already-synthesized chunks and displays error for failed chunks

---

### Edge Cases

- What happens when user saves a session with a name that already exists? (System prompts for confirmation to overwrite or auto-appends timestamp)
- What happens when playback controls are pressed rapidly in succession? (System debounces inputs with 100ms delay to prevent command conflicts)
- What happens when user tries to skip forward beyond the end of audio? (Playback stops and displays "End of content reached")
- What happens when user tries to skip backward before the beginning? (Playback resets to start position 0:00)
- What happens when a chunk fails to synthesize during streaming? (System skips the chunk, logs error, and continues with next chunk; displays warning to user)
- What happens when user quits (Q) during chunk processing? (All background processing stops immediately, partial audio discarded, clean exit)
- What happens when audio buffer runs empty during chunk synthesis? (Brief pause indicator shows, playback resumes when next chunk ready)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Application MUST accept `--save-session <name>` flag with read command to save session with specified name
- **FR-002**: Application MUST store session data including URL, extracted text, current playback position, and timestamp
- **FR-003**: Application MUST provide `list-sessions` command that displays all saved sessions with names, URLs, and creation dates
- **FR-004**: Application MUST provide `resume <session-name>` command that resumes playback from saved position
- **FR-005**: Application MUST detect keyboard input during playback for real-time control
- **FR-006**: Application MUST pause playback when spacebar is pressed and resume on subsequent spacebar press
- **FR-007**: Application MUST quit playback and exit cleanly when Q key is pressed
- **FR-008**: Application MUST skip forward 10 seconds when right arrow key is pressed
- **FR-009**: Application MUST skip backward 10 seconds when left arrow key is pressed
- **FR-010**: Application MUST increase playback speed by 0.25x (max 2.0x) when up arrow key is pressed
- **FR-011**: Application MUST decrease playback speed by 0.25x (min 0.5x) when down arrow key is pressed
- **FR-012**: Application MUST display current playback speed when speed changes
- **FR-013**: Application MUST chunk extracted text into segments of approximately 150 words for streaming synthesis
- **FR-014**: Application MUST begin audio playback after synthesizing the first chunk (within 3 seconds)
- **FR-015**: Application MUST synthesize subsequent chunks in background while first chunk plays
- **FR-016**: Application MUST queue synthesized chunks for seamless playback without gaps
- **FR-017**: Application MUST handle on-demand synthesis when user skips to un-synthesized chunk
- **FR-018**: Application MUST display playback position and total duration during playback
- **FR-019**: Application MUST save playback position when user pauses or quits for session resumption
- **FR-020**: AudioPlayback.play_audio() MUST block (wait) until audio playback completes before returning to caller

### Key Entities

- **Session**: Represents a saved reading session with attributes: session name (unique identifier), URL, extracted text content, playback position (timestamp), creation date, last accessed date
- **Playback State**: Represents current playback status with attributes: playing/paused status, current position, playback speed, current chunk index, buffered chunks queue
- **Audio Chunk**: Represents a segment of synthesized audio with attributes: chunk index, text content (approximately 150 words), synthesized audio data, duration, synthesis status (pending/complete/failed)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create, save, and resume reading sessions within 5 seconds per operation
- **SC-002**: Playback controls respond to keyboard input within 100 milliseconds with no perceived lag
- **SC-003**: Audio playback begins within 3 seconds for articles up to 10,000 words (compared to 10+ seconds without chunking)
- **SC-004**: Users can skip forward/backward through audio without playback stopping or crashing
- **SC-005**: Playback speed adjustments take effect immediately without audio distortion or interruption
- **SC-006**: System handles at least 50 concurrent chunk synthesis operations without memory overflow
- **SC-007**: 95% of chunk transitions during playback are seamless with no audible gaps or interruptions
- **SC-008**: Keyboard controls work consistently across 100 consecutive operations without input drops or errors
