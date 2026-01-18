# Developer Quickstart: Enhanced Playback Controls and Performance

**Feature**: 002-playback-session-improvements  
**Date**: 2026-01-17  
**Target Audience**: Developers implementing this feature

This guide provides step-by-step instructions for implementing session management, playback controls, and streaming chunking for vox.

---

## Prerequisites

**Before starting**:
1. ✅ Read [spec.md](spec.md) - Understand user requirements and acceptance criteria
2. ✅ Read [research.md](research.md) - Technology decisions and best practices
3. ✅ Read [data-model.md](data-model.md) - Entity definitions and relationships
4. ✅ Read contracts: [session-manager.md](contracts/session-manager.md), [playback-controller.md](contracts/playback-controller.md), [chunk-synthesizer.md](contracts/chunk-synthesizer.md)

**Environment setup**:
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install new dependency (pygame for audio playback)
uv pip install pygame>=2.6.0

# Verify installation
python -c "import pygame; print(pygame.version.ver)"
```

---

## Implementation Order

Follow test-first development (Red-Green-Refactor) for each component:

### Phase 1: Session Management (Priority P1)
1. Write tests for SessionManager
2. Implement SessionManager (save, load, list, resume, delete)
3. Update CLI to add --save-session flag
4. Update CLI to add list-sessions and resume commands

### Phase 2: Playback Controls (Priority P1)
1. Write tests for PlaybackController
2. Implement PlaybackController (keyboard input, state management)
3. Integrate pygame.mixer for audio playback with pause/resume/seek
4. Update main.py to use PlaybackController

### Phase 3: Streaming Chunking (Priority P2)
1. Write tests for ChunkSynthesizer
2. Implement ChunkSynthesizer (text splitting, background synthesis)
3. Integrate with PlaybackController for seamless playback
4. Add performance metrics (time to first audio, chunk gaps)

---

## Step-by-Step Implementation

### Step 1: SessionManager Tests (TDD)

**File**: `tests/unit/test_session_manager.py`

**Objective**: Write failing tests for all SessionManager methods

**Tests to write**:
```python
import pytest
from src.session.manager import SessionManager
from pathlib import Path
import tempfile

@pytest.fixture
def temp_storage(tmp_path):
    """Temporary storage directory for tests."""
    return tmp_path / "sessions"

@pytest.fixture
def manager(temp_storage):
    """SessionManager instance with temporary storage."""
    return SessionManager(storage_dir=temp_storage)

def test_save_session_creates_file(manager, temp_storage):
    """Test that save_session creates JSON file."""
    session_id = manager.save_session(
        session_name="test-session",
        url="https://example.com",
        extracted_text="Test content",
        playback_position=0
    )
    
    assert session_id is not None
    assert (temp_storage / "test-session.json").exists()

def test_save_session_with_invalid_name_raises_error(manager):
    """Test that invalid session name raises ValueError."""
    with pytest.raises(ValueError, match="Invalid session name"):
        manager.save_session(
            session_name="invalid name!",  # Spaces and special chars
            url="https://example.com",
            extracted_text="Test content"
        )

def test_save_session_with_duplicate_name_raises_error(manager):
    """Test that duplicate session name raises ValueError."""
    manager.save_session("duplicate", "https://example.com", "Content")
    
    with pytest.raises(ValueError, match="already exists"):
        manager.save_session("duplicate", "https://example.com", "Content")

def test_load_session_returns_correct_data(manager):
    """Test that load_session returns saved data."""
    session_id = manager.save_session("test", "https://example.com", "Content", 100)
    session = manager.load_session("test")
    
    assert session.session_name == "test"
    assert session.url == "https://example.com"
    assert session.extracted_text == "Content"
    assert session.playback_position == 100

def test_list_sessions_returns_all_sessions(manager):
    """Test that list_sessions returns all saved sessions."""
    manager.save_session("session1", "https://example.com/1", "Content 1")
    manager.save_session("session2", "https://example.com/2", "Content 2")
    
    sessions = manager.list_sessions()
    assert len(sessions) == 2
    assert any(s["session_name"] == "session1" for s in sessions)
    assert any(s["session_name"] == "session2" for s in sessions)

# Add more tests for delete, resume, error cases...
```

**Run tests** (they should fail):
```bash
pytest tests/unit/test_session_manager.py -v
# Expected: All tests FAIL (SessionManager not implemented yet)
```

---

### Step 2: Implement SessionManager

**File**: `src/session/manager.py`

**Objective**: Implement SessionManager to pass all tests

**Implementation outline**:
```python
import json
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
import re

from src.session.models import ReadingSession

class SessionManager:
    """Manages reading session persistence."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize with storage directory."""
        if storage_dir is None:
            # Default: %APPDATA%/vox/sessions
            import os
            appdata = os.getenv("APPDATA", ".")
            storage_dir = Path(appdata) / "vox" / "sessions"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "sessions.json"
        
        # Create empty index if doesn't exist
        if not self.index_file.exists():
            self._write_index({"version": "1.0", "sessions": []})
    
    def save_session(self, session_name: str, url: str, extracted_text: str,
                    playback_position: int = 0, tts_settings: Optional[dict] = None) -> str:
        """Save a new reading session."""
        # 1. Validate session_name
        self._validate_session_name(session_name)
        
        # 2. Check uniqueness
        if self.session_exists(session_name):
            raise ValueError(f"Session '{session_name}' already exists")
        
        # 3. Validate other inputs
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format")
        if not extracted_text or not extracted_text.strip():
            raise ValueError("Extracted text cannot be empty")
        if playback_position < 0 or playback_position > len(extracted_text):
            raise ValueError("Playback position out of bounds")
        
        # 4. Create ReadingSession
        session = ReadingSession(
            session_name=session_name,
            session_id=str(uuid.uuid4()),
            url=url,
            title=self._extract_title_from_url(url),
            extracted_text=extracted_text,
            playback_position=playback_position,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            tts_settings=tts_settings or {},
            extraction_settings={}
        )
        
        # 5. Write to file (atomic)
        self._write_session_file(session)
        
        # 6. Update index
        self._add_to_index(session)
        
        return session.session_id
    
    def load_session(self, session_name: str) -> ReadingSession:
        """Load existing session from disk."""
        # Implementation here...
        pass
    
    def list_sessions(self) -> list[dict]:
        """List all saved sessions."""
        # Implementation here...
        pass
    
    def delete_session(self, session_name: str) -> None:
        """Delete a session."""
        # Implementation here...
        pass
    
    def session_exists(self, session_name: str) -> bool:
        """Check if session exists."""
        # Implementation here...
        pass
    
    # Private helper methods
    def _validate_session_name(self, name: str) -> None:
        """Validate session name format."""
        if not re.match(r'^[a-zA-Z0-9_-]{1,64}$', name):
            raise ValueError(f"Invalid session name: {name}")
    
    def _slugify(self, name: str) -> str:
        """Convert session name to safe filename."""
        return name.lower().replace(" ", "-")
    
    def _write_session_file(self, session: ReadingSession) -> None:
        """Write session to JSON file atomically."""
        # Write to temp file, then rename (atomic operation)
        filename = f"{self._slugify(session.session_name)}.json"
        temp_file = self.storage_dir / f"{filename}.tmp"
        final_file = self.storage_dir / filename
        
        with open(temp_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
        
        temp_file.rename(final_file)
    
    # More helper methods...
```

**Run tests** (they should pass):
```bash
pytest tests/unit/test_session_manager.py -v
# Expected: All tests PASS
```

---

### Step 3: Update CLI for Session Management

**File**: `src/main.py`

**Changes**:
1. Add `--save-session` flag to read command
2. Add `list-sessions` subcommand
3. Add `resume` subcommand

**Implementation**:
```python
# In create_parser() function, update read_parser:
read_parser.add_argument(
    "--save-session",
    metavar="NAME",
    help="Save this reading session with the specified name"
)

# Add list-sessions subcommand:
list_sessions_parser = subparsers.add_parser(
    "list-sessions",
    help="List all saved reading sessions"
)

# Add resume subcommand:
resume_parser = subparsers.add_parser(
    "resume",
    help="Resume a saved reading session"
)
resume_parser.add_argument(
    "session_name",
    help="Name of the session to resume"
)

# In main() function, add handlers:
elif args.command == "list-sessions":
    command_list_sessions(args)
elif args.command == "resume":
    command_resume(args)

# Implement command handlers:
def command_list_sessions(args):
    """Handle list-sessions command."""
    from src.session.manager import SessionManager
    
    manager = SessionManager()
    sessions = manager.list_sessions()
    
    if not sessions:
        print("No saved sessions found.")
        return
    
    print(f"\nSaved Sessions ({len(sessions)}):\n")
    for session in sessions:
        print(f"  {Fore.CYAN}{session['session_name']}{Style.RESET_ALL}")
        print(f"    Title: {session['title']}")
        print(f"    URL: {session['url']}")
        print(f"    Progress: {session['progress_percent']:.1f}%")
        print(f"    Last accessed: {session['last_accessed']}")
        print()

def command_resume(args):
    """Handle resume command."""
    from src.session.manager import SessionManager
    
    manager = SessionManager()
    
    try:
        text, position = manager.resume_session(args.session_name)
        print_status(f"Resuming session '{args.session_name}' at position {position}")
        
        # Continue with TTS synthesis from position
        # (reuse existing synthesis code)
        
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

# In command_read(), add session save logic:
def command_read(args):
    # ... existing extraction and synthesis code ...
    
    # After playback completes, save session if --save-session provided
    if args.save_session:
        from src.session.manager import SessionManager
        manager = SessionManager()
        
        try:
            session_id = manager.save_session(
                session_name=args.save_session,
                url=args.url or args.file,
                extracted_text=content,
                playback_position=0,  # Will be updated when PlaybackController added
                tts_settings={"voice": voice, "speed": speed}
            )
            print_success(f"Session saved as '{args.save_session}'")
        except ValueError as e:
            print_warning(f"Failed to save session: {e}")
```

**Test manually**:
```bash
# Save a session
vox read --url https://example.com --save-session my-article

# List sessions
vox list-sessions

# Resume session
vox resume my-article
```

---

### Step 4: PlaybackController Tests (TDD)

**File**: `tests/unit/test_playback_controller.py`

**Objective**: Write failing tests for PlaybackController

**Key tests**:
- Pause/resume state transitions
- Keyboard command processing
- Seek forward/backward with bounds checking
- Speed adjustment with clamping
- Quit and graceful shutdown

*(Follow same TDD pattern as SessionManager)*

---

### Step 5: Implement PlaybackController

**File**: `src/tts/controller.py`

**Dependencies**: First update `src/tts/playback.py` to use pygame.mixer

**Playback.py changes**:
```python
import pygame
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

class AudioPlayback:
    def __init__(self):
        self.sound: Optional[pygame.mixer.Sound] = None
        self.channel: Optional[pygame.mixer.Channel] = None
    
    def play_audio(self, audio_bytes: bytes) -> None:
        """Play audio from bytes."""
        import io
        self.sound = pygame.mixer.Sound(io.BytesIO(audio_bytes))
        self.channel = self.sound.play()
    
    def pause(self) -> None:
        """Pause playback."""
        if self.channel:
            self.channel.pause()
    
    def resume(self) -> None:
        """Resume playback."""
        if self.channel:
            self.channel.unpause()
    
    def seek(self, position_ms: int) -> None:
        """Seek to position."""
        if self.sound and self.channel:
            self.channel.stop()
            self.channel = self.sound.play(start=position_ms / 1000.0)
    
    def set_speed(self, speed: float) -> None:
        """Adjust playback speed."""
        # Note: pygame doesn't support speed adjustment directly
        # Need to resample audio or use alternative library
        # For v1, log warning that speed changes require synthesis regeneration
        pass
```

**Controller implementation**: Follow contract in [playback-controller.md](contracts/playback-controller.md)

---

### Step 6: ChunkSynthesizer Implementation

**File**: `src/tts/chunking.py`

**Objective**: Implement streaming chunking for fast first-audio

**Key components**:
1. Text splitting (sentence-aware)
2. First chunk synthesis (blocking)
3. Background synthesis (threading)
4. Chunk buffer management

**Testing**: Integration test to verify <3s time-to-first-audio for 10,000 word article

---

## Testing Strategy

### Unit Tests
```bash
# Run all unit tests
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Run specific module tests
pytest tests/unit/test_session_manager.py -v
pytest tests/unit/test_playback_controller.py -v
pytest tests/unit/test_chunking.py -v
```

### Integration Tests
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific workflow tests
pytest tests/integration/test_session_workflow.py -v
pytest tests/integration/test_playback_controls.py -v
pytest tests/integration/test_chunked_playback.py -v
```

### Performance Benchmarks
```python
# In tests/integration/test_chunked_playback.py
def test_time_to_first_audio(long_article_text):
    """Verify first audio plays within 3 seconds."""
    start_time = time.time()
    
    chunker = ChunkSynthesizer(synthesizer)
    chunker.prepare_chunks(long_article_text)
    audio = chunker.synthesize_first_chunk()
    
    elapsed = time.time() - start_time
    assert elapsed < 3.0, f"First audio took {elapsed}s (target: <3s)"
```

---

## Code Quality Checks

**Before committing**:
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80

# Check coverage threshold (must be ≥80%)
```

---

## Debugging Tips

### Session Management
- **Sessions not saving**: Check `%APPDATA%/vox/sessions/` exists and is writable
- **Corrupted JSON**: Delete `sessions.json` and restart (auto-rebuilds)
- **Duplicate names**: Use unique session names or delete old session first

### Playback Controls
- **Keys not detected**: Verify msvcrt works on Windows (test with `msvcrt.kbhit()`)
- **Pause not working**: Check pygame.mixer initialized correctly
- **Speed changes ignored**: Note pygame doesn't support speed (requires audio resampling)

### Chunking
- **Slow first audio**: Profile `synthesize_first_chunk()` - should be <2s for 150 words
- **Gaps between chunks**: Increase buffer size or reduce chunk size
- **Memory leak**: Verify old chunks discarded after playback (limit buffer to 10)

---

## Performance Validation

**Success criteria** (from spec.md):
- ✅ SC-001: Session save/resume <5s per operation
- ✅ SC-002: Keyboard response <100ms latency
- ✅ SC-003: First audio <3s for 10,000 word articles
- ✅ SC-007: 95% chunk transitions <50ms gaps

**Measure with**:
```python
import time

# Time session save
start = time.time()
manager.save_session(...)
print(f"Save time: {time.time() - start:.2f}s")  # Target: <2s

# Time first audio
start = time.time()
chunker.synthesize_first_chunk()
print(f"First audio: {time.time() - start:.2f}s")  # Target: <3s
```

---

## Common Pitfalls

1. **❌ Don't use asyncio**: Piper TTS is synchronous, threading is simpler
2. **❌ Don't store audio in sessions**: Only store text + position (audio regenerated)
3. **❌ Don't block keyboard thread**: Use non-blocking msvcrt.kbhit() with sleep
4. **❌ Don't synthesize all chunks upfront**: Defeats purpose of streaming
5. **✅ Do validate session names**: Prevent path traversal attacks
6. **✅ Do use atomic writes**: Temp file + rename prevents corruption
7. **✅ Do respect sentence boundaries**: Don't split mid-sentence in chunks

---

## Next Steps After Implementation

1. **Manual testing**: Run through all user scenarios from spec.md
2. **Performance testing**: Verify success criteria with real articles
3. **Documentation**: Update README.md with new commands
4. **CHANGELOG**: Document new features (v1.1.0)
5. **PR review**: Submit for code review with test coverage report

---

## Resources

- **Spec**: [spec.md](spec.md) - User requirements and acceptance criteria
- **Research**: [research.md](research.md) - Technology decisions
- **Data model**: [data-model.md](data-model.md) - Entity definitions
- **Contracts**: [contracts/](contracts/) - API specifications
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) - Code standards

---

**Quickstart Status**: ✅ Complete - Step-by-step guide for implementing all features with TDD, testing, and debugging tips.
