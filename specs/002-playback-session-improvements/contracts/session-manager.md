# SessionManager API Contract

**Module**: `src/session/manager.py`  
**Purpose**: Manage session persistence - save, load, list, resume, and delete reading sessions  
**Owner**: Session Management (Feature 002)

---

## Class: SessionManager

**Responsibilities**:
- Save reading sessions to disk with user-provided names
- Load existing sessions from disk
- List all saved sessions with metadata
- Resume playback from saved session
- Delete sessions by name
- Maintain SessionIndex for fast listing

**Dependencies**:
- `src/session/models.ReadingSession`: Data model for session entity
- `pathlib.Path`: File system operations
- `json`: Serialization/deserialization
- `typing`: Type annotations
- `logging`: Error logging

---

## Methods

### `__init__(storage_dir: Optional[Path] = None)`

**Purpose**: Initialize SessionManager with storage directory

**Parameters**:
- `storage_dir` (Optional[Path]): Directory for session storage. If None, defaults to `%APPDATA%/PageReader/sessions/`

**Returns**: None

**Side Effects**:
- Creates storage directory if it doesn't exist
- Creates empty SessionIndex (`sessions.json`) if it doesn't exist

**Raises**:
- `OSError`: If unable to create storage directory or index file

**Example**:
```python
manager = SessionManager()  # Uses default %APPDATA%/PageReader/sessions/
# or
manager = SessionManager(storage_dir=Path("./custom/path"))
```

---

### `save_session(session_name: str, url: str, extracted_text: str, playback_position: int = 0, tts_settings: Optional[dict] = None) -> str`

**Purpose**: Save a new reading session to disk

**Parameters**:
- `session_name` (str): User-provided session name (1-64 chars, alphanumeric+hyphen/underscore)
- `url` (str): Source URL of the content
- `extracted_text` (str): Full extracted text from the page
- `playback_position` (int, optional): Current playback position in characters (default: 0)
- `tts_settings` (dict, optional): TTS settings (voice, speed) for consistent playback

**Returns**: 
- `str`: Generated session_id (UUID v4)

**Side Effects**:
- Creates JSON file: `{storage_dir}/{slugify(session_name)}.json`
- Updates SessionIndex with new entry
- Writes atomically (temp file + rename)

**Raises**:
- `ValueError`: If session_name invalid (empty, too long, bad format)
- `ValueError`: If session_name already exists (duplicate)
- `ValueError`: If url invalid format
- `ValueError`: If extracted_text is empty
- `ValueError`: If playback_position out of bounds
- `OSError`: If unable to write session file

**Validation**:
- session_name: Must match `^[a-zA-Z0-9_-]{1,64}$`
- url: Must start with `http://`, `https://`, or be valid file path
- extracted_text: Must be non-empty
- playback_position: Must be `0 ≤ position ≤ len(extracted_text)`

**Example**:
```python
session_id = manager.save_session(
    session_name="my-article",
    url="https://example.com/article",
    extracted_text="This is the full article text...",
    playback_position=0,
    tts_settings={"voice": "en_US-libritts-high", "speed": 1.0}
)
# Returns: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

---

### `load_session(session_name: str) -> ReadingSession`

**Purpose**: Load an existing session from disk

**Parameters**:
- `session_name` (str): Name of the session to load

**Returns**:
- `ReadingSession`: Loaded session object with all fields populated

**Side Effects**:
- Updates `last_accessed` timestamp in session file
- Updates `last_accessed` in SessionIndex

**Raises**:
- `ValueError`: If session_name not found in SessionIndex
- `OSError`: If unable to read session file
- `json.JSONDecodeError`: If session file corrupted (invalid JSON)
- `KeyError`: If required fields missing from session file

**Example**:
```python
session = manager.load_session("my-article")
print(session.url)  # "https://example.com/article"
print(session.playback_position)  # 1234
```

---

### `list_sessions() -> list[dict]`

**Purpose**: List all saved sessions with metadata (fast operation, reads SessionIndex only)

**Parameters**: None

**Returns**:
- `list[dict]`: List of session metadata dicts. Each dict contains:
  - `session_name` (str): User-facing session name
  - `session_id` (str): Internal UUID
  - `url` (str): Source URL
  - `title` (str): Page title
  - `created_at` (str): ISO 8601 timestamp
  - `last_accessed` (str): ISO 8601 timestamp
  - `playback_position` (int): Current character offset
  - `total_characters` (int): Total text length
  - `progress_percent` (float): Playback progress as percentage

**Side Effects**: None (read-only operation)

**Raises**:
- `OSError`: If unable to read SessionIndex file
- `json.JSONDecodeError`: If SessionIndex corrupted

**Example**:
```python
sessions = manager.list_sessions()
for session in sessions:
    print(f"{session['session_name']}: {session['title']} ({session['progress_percent']:.1f}%)")

# Output:
# my-article: Example Article (24.5%)
# python-tutorial: Python Basics (100.0%)
```

---

### `resume_session(session_name: str) -> tuple[str, int]`

**Purpose**: Resume playback from a saved session (convenience wrapper around load_session)

**Parameters**:
- `session_name` (str): Name of the session to resume

**Returns**:
- `tuple[str, int]`: (extracted_text, playback_position) for resuming playback

**Side Effects**:
- Calls `load_session()` which updates last_accessed timestamp

**Raises**:
- Same as `load_session()`

**Example**:
```python
text, position = manager.resume_session("my-article")
# Resume playback at position in text
```

---

### `delete_session(session_name: str) -> None`

**Purpose**: Delete a saved session from disk

**Parameters**:
- `session_name` (str): Name of the session to delete

**Returns**: None

**Side Effects**:
- Deletes session JSON file from storage directory
- Removes entry from SessionIndex

**Raises**:
- `ValueError`: If session_name not found
- `OSError`: If unable to delete file

**Example**:
```python
manager.delete_session("my-article")
# Session file and index entry removed
```

---

### `session_exists(session_name: str) -> bool`

**Purpose**: Check if a session with the given name exists

**Parameters**:
- `session_name` (str): Name to check

**Returns**:
- `bool`: True if session exists, False otherwise

**Side Effects**: None (read-only operation)

**Raises**: None (returns False on errors)

**Example**:
```python
if manager.session_exists("my-article"):
    print("Session exists")
else:
    print("Session not found")
```

---

### `_update_index() -> None` (Private)

**Purpose**: Update SessionIndex file with current sessions

**Parameters**: None

**Returns**: None

**Side Effects**:
- Writes SessionIndex to `sessions.json`
- Updates `last_updated` timestamp

**Raises**:
- `OSError`: If unable to write index file

**Note**: Internal method, not part of public API

---

### `_validate_session_name(session_name: str) -> None` (Private)

**Purpose**: Validate session name format

**Parameters**:
- `session_name` (str): Name to validate

**Returns**: None

**Raises**:
- `ValueError`: If name invalid (empty, too long, bad format)

**Validation Rules**:
- Must match regex `^[a-zA-Z0-9_-]{1,64}$`
- No path traversal characters (`../`, `..\\`)
- No special characters except hyphen and underscore

**Note**: Internal method, not part of public API

---

## Error Handling

**Philosophy**: Fail fast with clear error messages. Do not silently ignore errors.

**Error Categories**:
1. **User Input Errors** (ValueError): Invalid session name, duplicate name, empty text
2. **File System Errors** (OSError): Unable to read/write files, permission denied
3. **Data Corruption Errors** (json.JSONDecodeError, KeyError): Corrupted JSON, missing fields

**Error Recovery**:
- Corrupted session file: Log error, skip file, continue (list_sessions)
- Missing SessionIndex: Create new empty index (auto-recovery)
- Duplicate session name: Raise error, prompt user to choose different name

---

## Thread Safety

**Status**: Not thread-safe by design (single-user desktop application)

**Rationale**: PageReader is a single-user CLI tool with no concurrent session operations expected. If concurrent access needed in future, add file locking via `fcntl` (Unix) or `msvcrt.locking` (Windows).

---

## Performance Characteristics

| Operation | Time Complexity | Typical Duration | Notes |
|-----------|----------------|------------------|-------|
| `save_session()` | O(n) | <100ms | n = size of extracted_text (JSON serialization) |
| `load_session()` | O(n) | <100ms | n = size of extracted_text (JSON deserialization) |
| `list_sessions()` | O(m) | <10ms | m = number of sessions (reads index only, not full files) |
| `delete_session()` | O(1) | <10ms | File deletion + index update |
| `session_exists()` | O(1) | <5ms | Index lookup only |

**Memory**: O(n) where n = size of largest session file (typically <1MB per session)

---

## Testing Requirements

**Unit Tests** (`tests/unit/test_session_manager.py`):
- ✅ Test save_session with valid inputs
- ✅ Test save_session with invalid session_name (empty, too long, bad chars)
- ✅ Test save_session with duplicate session_name (should raise ValueError)
- ✅ Test save_session with empty extracted_text (should raise ValueError)
- ✅ Test load_session with existing session
- ✅ Test load_session with non-existent session (should raise ValueError)
- ✅ Test load_session with corrupted JSON (should raise json.JSONDecodeError)
- ✅ Test list_sessions with multiple sessions
- ✅ Test list_sessions with no sessions (empty list)
- ✅ Test delete_session with existing session
- ✅ Test delete_session with non-existent session (should raise ValueError)
- ✅ Test session_exists with existing/non-existent sessions
- ✅ Test atomic write (save_session should not corrupt on crash)

**Integration Tests** (`tests/integration/test_session_workflow.py`):
- ✅ Full workflow: save → quit → list → resume
- ✅ Multiple sessions: save multiple, list all, delete one, list again
- ✅ Resume with playback: save at position 1000, resume, verify position restored

**Coverage Target**: >80% line coverage for SessionManager

---

## Example Usage

```python
from src.session.manager import SessionManager

# Initialize manager
manager = SessionManager()

# Save a session
session_id = manager.save_session(
    session_name="tech-article",
    url="https://example.com/tech",
    extracted_text="Full article text here...",
    playback_position=0,
    tts_settings={"voice": "en_US-libritts-high", "speed": 1.0}
)

# List all sessions
sessions = manager.list_sessions()
for session in sessions:
    print(f"- {session['session_name']}: {session['title']} ({session['progress_percent']:.1f}%)")

# Resume a session
text, position = manager.resume_session("tech-article")
print(f"Resuming at character {position}")

# Delete a session
manager.delete_session("tech-article")
```

---

**Contract Status**: ✅ Complete - All public methods documented with inputs, outputs, side effects, errors, and examples.
