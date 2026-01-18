# Research: Enhanced Playback Controls and Performance

**Feature**: 002-playback-session-improvements  
**Date**: 2026-01-17  
**Status**: Phase 0 Complete

This document resolves all NEEDS CLARIFICATION items from the Technical Context section and documents technology decisions for implementation.

## Research Items

### 1. Session Persistence: Storage Mechanism

**Question**: JSON file storage vs SQLite database for session persistence?

**Decision**: JSON file storage

**Rationale**:
- **Simplicity**: JSON is human-readable, easy to debug, no schema migrations
- **Constitution compliance**: YAGNI principle - database overhead unnecessary for single-user desktop app
- **Access patterns**: Low frequency (save on quit, load on resume), no complex queries needed
- **Volume**: Expecting <100 sessions per user, each <1MB (text + metadata)
- **Dependencies**: Zero additional dependencies (uses Python standard library json module)
- **Implementation**: One JSON file per session in `%APPDATA%/PageReader/sessions/` directory

**Alternatives considered**:
- SQLite: Rejected - adds complexity, requires schema management, overkill for simple key-value access
- pickle: Rejected - not human-readable, potential security issues, harder to debug
- shelve: Rejected - Python-specific format, less portable than JSON

**Storage location**: `%APPDATA%/PageReader/sessions/` (Windows: `C:\Users\<user>\AppData\Roaming\PageReader\sessions\`)
- One JSON file per session: `{session_name}.json`
- Session index file: `sessions.json` (list of all sessions with metadata for fast listing)

---

### 2. Keyboard Input Handling

**Question**: pynput vs keyboard vs msvcrt for Windows keyboard input during audio playback?

**Decision**: msvcrt (Windows standard library) with threading

**Rationale**:
- **Zero dependencies**: msvcrt is Python standard library for Windows
- **Platform fit**: PageReader targets Windows 11 exclusively per constitution
- **Simplicity**: msvcrt.kbhit() and msvcrt.getch() provide non-blocking keyboard input
- **Constitution compliance**: KISS principle - no need for cross-platform keyboard library
- **Performance**: <100ms latency achievable with proper threading
- **Implementation**: Background thread polls msvcrt.kbhit() every 50ms, dispatches key events to playback controller

**Alternatives considered**:
- pynput: Rejected - external dependency, cross-platform overhead unnecessary, more complex API
- keyboard: Rejected - requires admin privileges on Windows (security risk), external dependency
- curses: Rejected - not available on Windows without external packages

**Key mapping**:
- Space: Pause/Resume (msvcrt detects ' ')
- Q: Quit (msvcrt detects 'q' or 'Q')
- Arrow keys: Detected via msvcrt special key sequences (0x00 or 0xE0 prefix)
  - Up/Down: Speed adjustment
  - Left/Right: Skip backward/forward

---

### 3. Audio Playback with Pause/Resume/Seek

**Question**: Need library supporting pause/resume/seek - pygame, sounddevice, or pydub vs current winsound?

**Decision**: pygame.mixer (audio playback module)

**Rationale**:
- **Feature completeness**: pygame.mixer supports pause/unpause, seeking, speed control
- **Windows compatibility**: Well-tested on Windows, no system-level audio driver conflicts
- **Mature library**: Stable API, extensive documentation, active community
- **Performance**: Low latency (<50ms) for playback control operations
- **Constitution compliance**: Simple API, well-documented, single dependency
- **Implementation**: 
  - Load WAV audio from bytes into pygame.mixer.Sound object
  - Use Sound.play() for playback, Sound.pause()/unpause() for control
  - Seek via Sound.set_pos() for skip operations
  - Speed via pygame.mixer.set_frequency() (requires resampling)

**Alternatives considered**:
- winsound: Rejected - current implementation, no pause/resume/seek support, blocking API
- sounddevice: Rejected - complex API, requires manual buffer management, overkill for WAV playback
- pydub: Rejected - not designed for real-time playback control, uses ffmpeg/libav (external binaries)
- pyaudio: Rejected - complex streaming API, requires manual chunk management

**Speed adjustment note**: pygame.mixer frequency adjustment changes playback speed without pitch shift (acceptable for TTS use case). For pitch-preserving speed control (future enhancement), consider librosa time-stretching (deferred to v2).

---

### 4. Background Processing: Chunking Architecture

**Question**: asyncio vs threading for background chunk synthesis?

**Decision**: threading.Thread with queue.Queue

**Rationale**:
- **Compatibility**: Piper TTS (piper-tts) is synchronous, no native async support
- **Simplicity**: threading + queue is standard Python pattern for producer-consumer
- **Constitution compliance**: KISS principle - no need for async complexity when blocking I/O is unavoidable
- **Performance**: Threading sufficient for 50+ concurrent chunks (CPU-bound synthesis work)
- **Implementation**:
  - Main thread: Playback management and keyboard input handling
  - Synthesis thread pool (2-4 threads): Background chunk synthesis
  - queue.Queue for chunk handoff (thread-safe, FIFO)
  - threading.Event for graceful shutdown on quit

**Alternatives considered**:
- asyncio: Rejected - Piper TTS is synchronous (would require run_in_executor wrapper), adds complexity
- multiprocessing: Rejected - overkill, high memory overhead, IPC complexity, harder debugging
- concurrent.futures.ThreadPoolExecutor: Considered - viable alternative, slightly more abstraction than raw threading

**Chunking strategy**:
- Text split into ~150-word chunks (sentence-boundary aware to avoid mid-sentence cuts)
- First chunk synthesized immediately (blocking), playback starts
- Remaining chunks queued for background synthesis
- ChunkSynthesizer maintains buffer of 3-5 ready chunks ahead of playback position
- On-demand synthesis if user seeks beyond buffer (brief pause with "buffering" indicator)

---

## Best Practices

### Session Management Best Practices

**File operations**:
- Atomic writes: Write to temporary file, then rename (prevents corruption on crash)
- Read-only mode for loading (prevents accidental overwrites)
- Graceful degradation: If session file corrupted, log error, skip loading, don't crash app

**Naming conventions**:
- Session names: Alphanumeric + hyphens/underscores, max 64 characters
- Sanitize user input to prevent path traversal attacks (`../../etc/passwd`)
- Auto-generate safe filename from session name: `slugify(session_name).json`

**Concurrency**:
- Single-user application, no file locking needed
- If session save/load is slow, show progress indicator (but expect <100ms with JSON)

### Playback Control Best Practices

**Keyboard input thread safety**:
- Shared state (PlaybackState) protected by threading.Lock
- Keyboard thread writes to command queue, playback thread reads (decouples input from playback)
- Debounce rapid key presses (100ms window to prevent double-triggers)

**Graceful shutdown**:
- Q key sets shutdown_event (threading.Event)
- All threads check shutdown_event every iteration
- Join all threads with timeout (5 seconds) before exit
- Clean up resources: close audio handles, save playback position

**Error handling**:
- Keyboard input errors logged but don't crash app (continue playback)
- Playback errors (audio device unavailable) notify user, attempt recovery
- Speed/seek bounds checked before applying (prevent invalid state)

### Chunking Best Practices

**Text splitting**:
- Split on sentence boundaries (use regex for `.!?` followed by whitespace/newline)
- Target ~150 words per chunk, allow ±20% variance to respect sentence boundaries
- Minimum chunk size: 50 words (avoid too-short chunks with high overhead)
- Maximum chunk size: 300 words (avoid long synthesis delays)

**Queue management**:
- Pre-fill buffer with 3 chunks (ahead of playback) for seamless transitions
- Monitor queue depth: If dropping below 2 chunks, prioritize next chunks
- Discard unsynthesized chunks on seek (no point synthesizing skipped content)
- Clear queue on quit (cancel pending work, free memory)

**Memory management**:
- Each chunk WAV audio ~500KB-1MB (16-bit, 22050 Hz, mono)
- Limit in-memory queue to 10 chunks (~5-10MB buffer) to prevent memory bloat
- Discard played chunks immediately after playback (keep only current + buffered)

### Piper TTS Integration

**Voice model**:
- Continue using `en_US-libritts-high` (default from v1.0)
- Speed control: Pass `length_scale` parameter to Piper (inverse of speed: 1.0x = 1.0, 1.5x = 0.67)
- Quality: High quality model for clear TTS output

**Performance**:
- Piper synthesis: ~150 words in 1-2 seconds on modern CPU (CPU-bound, benefits from threading)
- GPU acceleration: Piper supports ONNX models (not required for 150-word chunks, consider for v2)

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Session storage | JSON (stdlib) | Python 3.13+ | Simple, human-readable, zero dependencies |
| Session location | %APPDATA%/PageReader | Windows std | User-writable, persistent across updates |
| Keyboard input | msvcrt (stdlib) | Python 3.13+ | Windows-native, zero dependencies, non-blocking |
| Audio playback | pygame.mixer | 2.6.0+ | Pause/resume/seek support, mature, Windows-tested |
| Background processing | threading + queue (stdlib) | Python 3.13+ | Simple, compatible with sync TTS, sufficient performance |
| Text chunking | regex + custom logic | - | Sentence-aware splitting, ~150 words/chunk |
| TTS synthesis | piper-tts (existing) | 1.2.0+ | Existing dependency, high-quality neural TTS |

**New dependencies**: pygame (only new external dependency)  
**Standard library additions**: threading, queue, msvcrt (all already available in Python 3.13)

---

## Implementation Notes

### Phase 1 Priorities

1. **Session management (P1)**: Implement SessionManager with save/load/list/resume
2. **Playback controls (P1)**: Implement PlaybackController with keyboard input handling
3. **Chunking (P2)**: Implement ChunkSynthesizer with background threading

### Testing Strategy

- **Unit tests**: All functions with >80% coverage
  - SessionManager: Test save, load, list, resume, error handling
  - PlaybackController: Test keyboard input parsing, state transitions
  - ChunkSynthesizer: Test text splitting, queue management, thread coordination
  
- **Integration tests**: End-to-end workflows
  - Session workflow: Save session → quit → list sessions → resume session
  - Playback controls: Start playback → pause → skip → adjust speed → quit
  - Chunked playback: Long article → verify first chunk plays within 3s → verify seamless transitions

### Performance Validation

- **Session operations**: Measure save/load times with pytest-benchmark (target <2s)
- **Keyboard latency**: Measure time from key press to state change (target <100ms)
- **First chunk time**: Measure extraction → first audio playback (target <3s for 10,000 word article)
- **Chunk transitions**: Measure gaps between chunks (target <50ms, 95th percentile)

---

**Research Status**: ✅ Complete - All NEEDS CLARIFICATION items resolved. Ready for Phase 1 (data model + contracts).
