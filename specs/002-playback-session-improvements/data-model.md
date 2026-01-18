# Data Model: Enhanced Playback Controls and Performance

**Feature**: 002-playback-session-improvements  
**Date**: 2026-01-17  
**Status**: Phase 1 Design

This document defines all data entities, their attributes, relationships, and validation rules for the enhanced playback and session management features.

## Entity Overview

```
ReadingSession (extends existing)
    ├── Contains: session metadata, content, playback position
    └── Persisted as: JSON file in %APPDATA%/vox/sessions/

PlaybackState (new)
    ├── Contains: real-time playback status, position, speed, control flags
    └── Lifecycle: In-memory only (not persisted, recreated on resume)

AudioChunk (new)
    ├── Contains: chunk index, text segment, synthesized audio, status
    └── Lifecycle: In-memory only (discarded after playback)

SessionIndex (new)
    ├── Contains: list of all sessions with quick-access metadata
    └── Persisted as: sessions.json in %APPDATA%/vox/sessions/
```

---

## Entity Definitions

### 1. ReadingSession (Enhanced)

**Purpose**: Represents a saved reading session with URL, content, and playback position for persistence and resumption.

**Note**: This entity already exists in `src/session/models.py` and will be enhanced with additional fields for the new features.

#### Attributes

| Attribute | Type | Required | Default | Validation | Description |
|-----------|------|----------|---------|------------|-------------|
| `session_name` | str | Yes | - | 1-64 chars, alphanumeric+hyphen/underscore, unique | User-provided session name (unique identifier) |
| `session_id` | str | Yes | UUID v4 | UUID format | Internal unique identifier (auto-generated) |
| `url` | str | Yes | - | Valid URL format | Source URL of the content |
| `title` | str | Yes | - | 1-500 chars | Page title (from HTML `<title>` or filename) |
| `extracted_text` | str | Yes | - | Max 10MB | Full extracted text content from the page |
| `playback_position` | int | No | 0 | ≥0, ≤len(extracted_text) | Current character offset in extracted_text |
| `created_at` | datetime | Yes | datetime.now() | ISO 8601 | Timestamp when session was created |
| `last_accessed` | datetime | Yes | datetime.now() | ISO 8601 | Timestamp of last access/resume |
| `tts_settings` | dict | No | {} | Valid JSON | TTS settings: voice, speed (for consistent playback) |
| `extraction_settings` | dict | No | {} | Valid JSON | Extraction settings used (for reference) |

#### Validation Rules

- **session_name**: Must match regex `^[a-zA-Z0-9_-]{1,64}$` (sanitized from user input)
- **url**: Must start with `http://` or `https://` or be file path
- **extracted_text**: Must not be empty when saving session
- **playback_position**: Must be within bounds `[0, len(extracted_text)]`
- **Uniqueness**: session_name must be unique across all sessions (enforced by SessionManager)

#### Relationships

- **1:1 with SessionIndex entry**: Each ReadingSession has one corresponding entry in SessionIndex
- **1:N with AudioChunk**: During playback, extracted_text is split into N AudioChunk instances (not persisted)

#### State Transitions

```
[New] --save()--> [Saved] --resume()--> [Active] --quit()--> [Saved (updated position)]
                    ↓
                delete() --> [Deleted]
```

#### Methods

```python
def is_valid() -> bool:
    """Check if session has all required fields and passes validation."""
    
def to_dict() -> dict:
    """Serialize session to dictionary for JSON persistence."""
    
def from_dict(data: dict) -> ReadingSession:
    """Deserialize session from dictionary (load from JSON)."""
    
def update_position(new_position: int) -> None:
    """Update playback position and last_accessed timestamp."""
```

---

### 2. PlaybackState (New)

**Purpose**: Tracks real-time playback state during active audio playback, including pause/resume status, speed, position, and chunk buffer.

**Note**: This entity is in-memory only and is NOT persisted. It is recreated when a session is resumed.

#### Attributes

| Attribute | Type | Required | Default | Validation | Description |
|-----------|------|----------|---------|------------|-------------|
| `is_playing` | bool | Yes | False | - | True if audio is currently playing |
| `is_paused` | bool | Yes | False | - | True if playback is paused |
| `current_position_ms` | int | Yes | 0 | ≥0 | Current playback position in milliseconds |
| `total_duration_ms` | int | Yes | 0 | ≥0 | Total audio duration in milliseconds |
| `playback_speed` | float | Yes | 1.0 | 0.5 ≤ speed ≤ 2.0 | Current playback speed (1.0 = normal) |
| `current_chunk_index` | int | Yes | 0 | ≥0 | Index of chunk currently playing |
| `chunk_buffer` | list[AudioChunk] | Yes | [] | Max 10 chunks | Queue of synthesized chunks ready for playback |
| `text_chunks` | list[str] | Yes | [] | - | All text chunks (for reference and seeking) |
| `shutdown_event` | threading.Event | Yes | Event() | - | Signal for graceful shutdown (keyboard Q) |

#### Validation Rules

- **playback_speed**: Must be within range `[0.5, 2.0]` (enforced by PlaybackController)
- **current_position_ms**: Must not exceed `total_duration_ms`
- **chunk_buffer**: Limited to 10 chunks maximum (memory management)
- **Mutual exclusivity**: `is_playing` and `is_paused` cannot both be True

#### State Transitions

```
[Idle] --play()--> [Playing] --pause()--> [Paused] --resume()--> [Playing]
                      ↓                                              ↓
                   quit() <----------------------------------------quit()
                      ↓
                   [Stopped]
```

#### Methods

```python
def play() -> None:
    """Start playback (is_playing=True, is_paused=False)."""
    
def pause() -> None:
    """Pause playback (is_paused=True, is_playing=False)."""
    
def resume() -> None:
    """Resume playback from paused state (is_playing=True, is_paused=False)."""
    
def stop() -> None:
    """Stop playback and reset state (is_playing=False, is_paused=False)."""
    
def seek(offset_ms: int) -> None:
    """Seek to position (can be negative for backward seek)."""
    
def adjust_speed(delta: float) -> None:
    """Adjust speed by delta (clamped to [0.5, 2.0])."""
```

---

### 3. AudioChunk (New)

**Purpose**: Represents a segment of text and its synthesized audio for streaming playback.

**Note**: This entity is in-memory only and is NOT persisted. Chunks are discarded after playback.

#### Attributes

| Attribute | Type | Required | Default | Validation | Description |
|-----------|------|----------|---------|------------|-------------|
| `chunk_index` | int | Yes | - | ≥0 | Sequential index in the full text (0-based) |
| `text_content` | str | Yes | - | 50-300 words | Text segment (~150 words, sentence-aware split) |
| `audio_data` | bytes | No | None | Valid WAV format | Synthesized audio bytes (None if not yet synthesized) |
| `duration_ms` | int | No | 0 | ≥0 | Audio duration in milliseconds |
| `synthesis_status` | enum | Yes | PENDING | [PENDING, COMPLETE, FAILED] | Status of synthesis operation |
| `error_message` | str | No | None | - | Error message if synthesis_status=FAILED |

#### Validation Rules

- **text_content**: Must be non-empty, 50-300 word range (enforced by ChunkSynthesizer)
- **audio_data**: Required if synthesis_status=COMPLETE, None otherwise
- **duration_ms**: Must be >0 if synthesis_status=COMPLETE

#### Synthesis Status States

```
[PENDING] --synthesize_success()--> [COMPLETE]
            |
            +--synthesize_failure()--> [FAILED]
```

#### Methods

```python
def is_ready() -> bool:
    """Check if chunk is ready for playback (synthesis_status=COMPLETE)."""
    
def word_count() -> int:
    """Return word count of text_content."""
    
def mark_complete(audio_data: bytes, duration_ms: int) -> None:
    """Mark chunk as complete with synthesized audio."""
    
def mark_failed(error_message: str) -> None:
    """Mark chunk as failed with error message."""
```

---

### 4. SessionIndex (New)

**Purpose**: Fast-access index of all saved sessions for listing without loading full session files.

**Note**: Persisted as `sessions.json` in `%APPDATA%/vox/sessions/` directory.

#### Structure

```json
{
  "version": "1.0",
  "last_updated": "2026-01-17T10:30:00Z",
  "sessions": [
    {
      "session_name": "my-article",
      "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "url": "https://example.com/article",
      "title": "Example Article Title",
      "created_at": "2026-01-17T10:00:00Z",
      "last_accessed": "2026-01-17T10:20:00Z",
      "playback_position": 1234,
      "total_characters": 5000
    }
  ]
}
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | str | Yes | Schema version (for future migrations) |
| `last_updated` | datetime | Yes | Timestamp of last index update |
| `sessions` | list[dict] | Yes | List of session metadata entries |

**Session entry fields**:
- `session_name`: User-facing session name
- `session_id`: Internal UUID
- `url`: Source URL
- `title`: Page title
- `created_at`: Creation timestamp
- `last_accessed`: Last access timestamp
- `playback_position`: Current character offset
- `total_characters`: Total text length (for progress %)

#### Operations

- **Add**: Insert new session entry when session saved
- **Update**: Update last_accessed and playback_position on resume
- **Delete**: Remove entry when session deleted
- **List**: Read entire index for `list-sessions` command

---

## Data Relationships

```
SessionIndex
    │
    └──> [1:N] ReadingSession (references session_name, stored as separate JSON files)
                    │
                    └──> [1:N] AudioChunk (runtime only, generated from extracted_text during playback)
                                    │
                                    └──> PlaybackState (runtime only, tracks current chunk and buffer)
```

---

## Validation Summary

### At Save Time (SessionManager.save_session)

1. Validate session_name format (alphanumeric, 1-64 chars)
2. Check session_name uniqueness (error if duplicate)
3. Validate URL format
4. Ensure extracted_text is non-empty
5. Ensure playback_position is within bounds
6. Write to temporary file, then atomic rename (prevent corruption)
7. Update SessionIndex with new entry

### At Load Time (SessionManager.load_session)

1. Check session file exists
2. Parse JSON (handle parse errors gracefully)
3. Validate required fields present
4. Validate data types match schema
5. Update last_accessed timestamp
6. Return ReadingSession instance

### At Playback Time (PlaybackController)

1. Validate speed is in range [0.5, 2.0]
2. Validate seek position is within audio bounds
3. Validate chunk_buffer does not exceed 10 chunks
4. Ensure mutual exclusivity of is_playing/is_paused

---

## Storage Layout

```
%APPDATA%/vox/
└── sessions/
    ├── sessions.json                    # SessionIndex (master list)
    ├── my-article.json                  # ReadingSession for "my-article"
    ├── python-tutorial.json             # ReadingSession for "python-tutorial"
    └── news-summary.json                # ReadingSession for "news-summary"
```

**File naming**: `{slugify(session_name)}.json` where slugify converts spaces to hyphens, removes special chars

---

## Data Flow

### Save Session Flow

```
User: vox read --url https://example.com --save-session my-article
  ↓
Main CLI: Parse arguments, extract text, start playback
  ↓
SessionManager.save_session(session_name, url, text, position, tts_settings)
  ↓
1. Create ReadingSession instance
2. Validate fields (session_name, url, text)
3. Check uniqueness in SessionIndex
4. Serialize to JSON
5. Write to temporary file: my-article.json.tmp
6. Atomic rename: my-article.json.tmp → my-article.json
7. Update SessionIndex (add entry)
8. Return session_id
```

### Resume Session Flow

```
User: vox resume my-article
  ↓
SessionManager.load_session(session_name="my-article")
  ↓
1. Check SessionIndex for session_name → get session_id
2. Load JSON file: my-article.json
3. Deserialize to ReadingSession instance
4. Validate required fields
5. Update last_accessed timestamp
6. Return ReadingSession
  ↓
Main CLI: Extract text and playback_position
  ↓
ChunkSynthesizer: Split text into AudioChunks, synthesize from playback_position
  ↓
PlaybackController: Start playback at chunk containing playback_position
```

### Chunked Playback Flow

```
ChunkSynthesizer.prepare_chunks(extracted_text)
  ↓
1. Split text into ~150-word chunks (sentence-aware)
2. Create AudioChunk instances (status=PENDING)
3. Store in PlaybackState.text_chunks
  ↓
ChunkSynthesizer.synthesize_first_chunk()
  ↓
1. Synthesize chunk[0] (blocking)
2. Mark status=COMPLETE, store audio_data
3. Add to PlaybackState.chunk_buffer
4. Return first chunk
  ↓
PlaybackController.start_playback()
  ↓
1. Play first chunk audio
2. Start background synthesis thread
3. Start keyboard input thread
  ↓
Background thread: Synthesize chunk[1..N]
  ↓
1. For each chunk: synthesize → mark COMPLETE → add to buffer
2. Limit buffer to 10 chunks (discard old played chunks)
3. Check shutdown_event every iteration (quit on Q key)
  ↓
PlaybackController: Play chunks from buffer seamlessly
```

---

**Data Model Status**: ✅ Complete - All entities defined with attributes, validation, relationships, and state transitions. Ready for contracts generation.
