# Claude Development Guidelines for vox

## Project Overview

**vox** is a bidirectional audio-text conversion CLI tool for Windows 11 that enables:
- **Text-to-Speech (TTS)**: Read web content aloud from URLs, browser tabs, or HTML files using offline neural TTS
- **Speech-to-Text (STT)**: Transcribe voice recordings to text using Whisper-powered offline recognition

**Target Users**: Windows 11 users who need accessibility features, hands-free content consumption, or voice transcription capabilities without cloud dependencies.

**Key Design Philosophy**:
- **Offline-first**: No API keys, no cloud services, complete privacy
- **Test-driven**: ≥80% coverage requirement, ≥95% for critical paths
- **Simple UX**: CLI-based with intuitive commands and keyboard controls
- **Modular architecture**: Clear separation between TTS, STT, extraction, and session management

**Version**: 3.0.0 (MAJOR bump for rebranding from "vox" to "vox" with breaking CLI changes)

---

## Architecture Overview

### System Architecture

```
┌───────────────────────────────────────────────────────────┐
│                        vox CLI                            │
│                     (src/main.py)                         │
│                                                           │
│  ┌──────────────────┐           ┌──────────────────┐      │
│  │  vox read        │           │  vox transcribe  │      │
│  │  (TTS Commands)  │           │  (STT Commands)  │      │
│  └────────┬─────────┘           └─────────┬────────┘      │
└───────────┼───────────────────────────────┼───────────────┘
            │                               │
            ▼                               ▼
┌───────────────────────┐       ┌─────────────────────┐
│   TTS Module          │       │   STT Module        │
│   (src/tts/)          │       │   (src/stt/)        │
│                       │       │                     │
│  ┌────────────────┐   │       │  ┌───────────────┐  │
│  │ Synthesizer    │   │       │  │ Recorder      │  │
│  │ (Piper TTS)    │   │       │  │ (sounddevice) │  │
│  └────────────────┘   │       │  └───────────────┘  │
│  ┌────────────────┐   │       │  ┌───────────────┐  │
│  │ Playback       │   │       │  │ Transcriber   │  │
│  │ (pygame)       │   │       │  │ (Whisper)     │  │
│  └────────────────┘   │       │  └───────────────┘  │
│  ┌────────────────┐   │       │  ┌───────────────┐  │
│  │ Chunking       │   │       │  │ Engine        │  │
│  │                │   │       │  │ (faster-      │  │
│  └────────────────┘   │       │  │  whisper)     │  │
└───────────┬───────────┘       │  └───────────────┘  │
            │                   └─────────────────────┘
            │
            ▼
┌───────────────────────┐       ┌─────────────────────┐
│ Extraction Module     │       │ Browser Module      │
│ (src/extraction/)     │       │ (src/browser/)      │
│                       │       │                     │
│  ┌────────────────┐   │       │  ┌───────────────┐  │
│  │ URL Fetcher    │   │       │  │ Detector      │  │
│  │ (requests)     │   │       │  │ (pywinauto)   │  │
│  └────────────────┘   │       │  └───────────────┘  │
│  ┌────────────────┐   │       │  ┌───────────────┐  │
│  │ HTML Parser    │   │       │  │ Accessibility │  │
│  │ (BeautifulSoup)│   │       │  │               │  │
│  └────────────────┘   │       │  └───────────────┘  │
│  ┌────────────────┐   │       └─────────────────────┘
│  │ Text Extractor │   │
│  │ (DOM Walker)   │   │
│  └────────────────┘   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐       ┌─────────────────────┐
│ Session Module        │       │ Utils Module        │
│ (src/session/)        │       │ (src/utils/)        │
│                       │       │                     │
│  ┌────────────────┐   │       │  ┌───────────────┐  │
│  │ Manager        │   │       │  │ Errors        │  │
│  │                │   │       │  │               │  │
│  └────────────────┘   │       │  └───────────────┘  │
│  ┌────────────────┐   │       │  ┌───────────────┐  │
│  │ Models         │   │       │  │ Logging       │  │
│  │ (dataclasses)  │   │       │  │               │  │
│  └────────────────┘   │       │  └───────────────┘  │
└───────────────────────┘       │  ┌───────────────┐  │
                                │  │ Migration     │  │
┌───────────────────────┐       │  │               │  │
│ Config Module         │       │  └───────────────┘  │
│ (src/config.py)       │       └─────────────────────┘
│ - Paths, settings     │
│ - Model cache         │
│ - Default values      │
└───────────────────────┘
```

### Module Responsibilities

| Module | Purpose | Key Dependencies | Entry Point |
|--------|---------|------------------|-------------|
| **src/main.py** | CLI entry point, command parsing, orchestration | argparse | `vox` command |
| **src/tts/** | Text-to-speech synthesis and playback | piper-tts, pygame | `command_read()` |
| **src/stt/** | Speech-to-text recording and transcription | faster-whisper, sounddevice | `command_transcribe()` |
| **src/extraction/** | Web content fetching and text extraction | requests, BeautifulSoup | `extract_text_from_url()` |
| **src/browser/** | Active browser tab detection (Windows) | pywinauto | `get_active_tab()` |
| **src/session/** | TTS session persistence and resume | dataclasses, JSON | `SessionManager` |
| **src/utils/** | Shared utilities (errors, logging, config migration) | logging | Various |
| **src/config.py** | Configuration constants and paths | pathlib | `APPDATA`, `STT_MODEL_CACHE` |

---

## Data Flow Diagrams

### TTS Workflow: Read Web Content Aloud

```
┌──────────────┐
│ User Command │  vox read --url https://example.com
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 1. CONTENT ACQUISITION                                  │
│    ┌─────────────────────────────────────────┐          │
│    │ Browser Tab (--active-tab)              │          │
│    │  → src/browser/detector.py              │          │
│    │  → Get URL via pywinauto                │          │
│    └─────────────────────────────────────────┘          │
│                   OR                                    │
│    ┌─────────────────────────────────────────┐          │
│    │ URL (--url)                             │          │
│    │  → src/extraction/url_fetcher.py        │          │
│    │  → HTTP GET via requests                │          │
│    └─────────────────────────────────────────┘          │
│                   OR                                    │
│    ┌─────────────────────────────────────────┐          │
│    │ Local File (--file)                     │          │
│    │  → src/extraction/file_loader.py        │          │
│    │  → Read HTML from disk                  │          │
│    └─────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 2. TEXT EXTRACTION                                      │
│    src/extraction/html_parser.py                        │
│    → Parse HTML with BeautifulSoup                      │
│    → src/extraction/dom_walker.py                       │
│    → Walk DOM tree, extract visible text                │
│    → src/extraction/content_filter.py                   │
│    → Remove navigation, ads, scripts                    │
│    → Output: Clean text string                          │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 3. TEXT CHUNKING                                        │
│    src/tts/chunking.py                                  │
│    → Split text into sentence-based chunks              │
│    → Max chunk size: ~200 chars (for streaming)         │
│    → Preserve punctuation boundaries                    │
│    → Output: List[str] of chunks                        │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 4. SPEECH SYNTHESIS (Per Chunk)                         │
│    src/tts/synthesizer.py                               │
│    → Load Piper TTS model (cached)                      │
│    → Convert text chunk → WAV audio data                │
│    → src/tts/piper_provider.py                          │
│    → Invoke piper-tts library                           │
│    → Output: bytes (WAV format)                         │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 5. AUDIO PLAYBACK (Streaming)                           │
│    src/tts/playback.py                                  │
│    → Queue audio chunks                                 │
│    → Play via pygame.mixer                              │
│    → Interactive controls:                              │
│      - SPACE: pause/resume                              │
│      - LEFT/RIGHT: seek ±5s                             │
│      - Q: quit                                          │
│    → Save session state (optional, --save-session)      │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Audio Output │  Speakers/Headphones
└──────────────┘
```

**Performance Target**: <500ms from command → first audio playback

### STT Workflow: Transcribe Voice to Text

```
┌──────────────┐
│ User Command │  vox transcribe
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 1. MICROPHONE DETECTION                                 │
│    src/stt/recorder.py                                  │
│    → Detect system default microphone                   │
│    → Validate device availability                       │
│    → Check Windows audio permissions                    │
│    → Output: Device ID + Sample Rate                    │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 2. AUDIO RECORDING                                      │
│    src/stt/recorder.py (MicrophoneRecorder)             │
│    → Start sounddevice.InputStream                      │
│    → Capture audio chunks (100ms buffers)               │
│    → Settings:                                          │
│      - Sample rate: 16kHz (required for Whisper)        │
│      - Channels: Mono (1)                               │
│      - Format: 16-bit PCM                               │
│    → User controls:                                     │
│      - ENTER key: manual stop                           │
│      - Auto-stop: 5s silence detection                  │
│    → Output: numpy.ndarray (audio data)                 │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 3. AUDIO PREPROCESSING                                  │
│    src/stt/audio_utils.py                               │
│    → Normalize audio levels                             │
│    → Detect/trim leading/trailing silence               │
│    → Validate audio quality (RMS check)                 │
│    → Convert to WAV format (for Whisper input)          │
│    → Output: scipy WAV buffer                           │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 4. SPEECH RECOGNITION                                   │
│    src/stt/engine.py (STTEngine)                        │
│    → Load faster-whisper model (lazy load, cached)      │
│    → Model: medium.en (1.5GB, 95%+ accuracy)            │
│    → Transcribe audio → text                            │
│    → Extract segments + timestamps                      │
│    → Calculate confidence scores                        │
│    → Output: TranscriptionResult dataclass              │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 5. OUTPUT FORMATTING                                    │
│    src/stt/transcriber.py                               │
│    → Format transcribed text                            │
│    → Display to stdout (default)                        │
│    → Save to file (if --output flag provided)           │
│    → Show metadata:                                     │
│      - Duration, processing time, confidence            │
│    → Output: Text file or terminal display              │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Text Output  │  Terminal or File
└──────────────┘
```

**Performance Target**: <10s transcription time for 1 minute of audio

---

## Code Quality Standards

### SOLID Principles

**Single Responsibility Principle (SRP)**:
- Each module has one reason to change
- Example: `url_fetcher.py` only handles HTTP requests, not parsing
- Example: `recorder.py` only handles audio capture, not transcription

**Open/Closed Principle (OCP)**:
- Extend functionality via inheritance/composition, not modification
- Example: New TTS providers via `BaseTTSProvider` interface
- Example: New STT engines via `BaseSTTEngine` interface

**Liskov Substitution Principle (LSP)**:
- Subtypes must be substitutable for their base types
- Example: All TTS providers implement same `synthesize()` signature

**Interface Segregation Principle (ISP)**:
- Clients shouldn't depend on unused interfaces
- Example: `MicrophoneRecorder` doesn't expose transcription methods

**Dependency Inversion Principle (DIP)**:
- Depend on abstractions, not concrete implementations
- Example: `Synthesizer` depends on `BaseTTSProvider`, not `PiperProvider`

### DRY (Don't Repeat Yourself)

- **Audio processing utilities**: Shared between TTS and STT in `src/utils/audio.py` (when created)
- **Error handling**: Custom exceptions in `src/utils/errors.py` reused across modules
- **Logging**: Centralized `setup_logging()` in `src/utils/logging.py`
- **Configuration**: Single source of truth in `src/config.py`

### KISS (Keep It Simple, Stupid)

- **Prefer simplicity**: Use Enter key for stopping recording (not complex voice commands)
- **Default to sensible values**: Medium.en Whisper model (not largest), system default mic (no selection UI)
- **Avoid premature optimization**: Optimize only after profiling shows bottlenecks
- **Clear over clever**: Readable code > micro-optimizations

### Test Coverage Requirements

| Path Type | Minimum Coverage | Target |
|-----------|-----------------|--------|
| **Critical paths** (TTS/STT workflows) | ≥95% | 100% |
| **Core logic** (text extraction, audio processing) | ≥90% | 95% |
| **Utilities** (helpers, validators) | ≥80% | 90% |
| **CLI glue code** (main.py argument parsing) | ≥70% | 80% |
| **Overall project** | ≥80% | 85% |

**Coverage enforcement**:
```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term --cov-fail-under=80

# Critical path testing (must pass)
pytest tests/integration/test_tts_workflow.py --cov-fail-under=95
pytest tests/integration/test_stt_workflow.py --cov-fail-under=95
```

### Import Organization

**Standard 3-group structure** (enforced by ruff):

```python
# 1. Standard library imports (alphabetical)
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# 2. Third-party imports (alphabetical)
import numpy as np
import sounddevice as sd
from bs4 import BeautifulSoup
from faster_whisper import WhisperModel

# 3. Local application imports (alphabetical, absolute paths preferred)
from src.config import APPDATA, STT_MODEL_CACHE
from src.utils.errors import MicrophoneError, TranscriptionError
from src.utils.logging import setup_logging
```

**Import guidelines**:
- Use absolute imports: `from src.tts.synthesizer import Synthesizer` (not relative)
- Group imports logically with blank lines between groups
- Avoid wildcard imports: `from module import *` (banned by ruff)
- Use `TYPE_CHECKING` for type-only imports to avoid circular dependencies:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.session.models import Session
```

### Type Hinting Requirements

**All functions must have type hints** for parameters and return values:

```python
# ✅ CORRECT: Full type hints
def transcribe_audio(
    audio_data: np.ndarray,
    sample_rate: int = 16000,
    model_name: str = "medium.en"
) -> TranscriptionResult:
    """Transcribe audio data to text.
    
    Args:
        audio_data: Raw PCM audio samples (mono, 16-bit)
        sample_rate: Sampling frequency in Hz (default: 16000)
        model_name: Whisper model identifier (default: "medium.en")
    
    Returns:
        TranscriptionResult with text and metadata
    
    Raises:
        TranscriptionError: If transcription fails
    """
    ...

# ❌ INCORRECT: Missing type hints
def transcribe_audio(audio_data, sample_rate=16000, model_name="medium.en"):
    ...
```

**Complex types**:
```python
from typing import List, Dict, Optional, Union, Tuple

# Use specific types, not "Any"
def parse_segments(
    segments: List[Dict[str, Union[str, float]]]
) -> List[TranscriptionSegment]:
    ...

# Use Optional for nullable values
def get_cached_model(model_name: str) -> Optional[WhisperModel]:
    ...

# Use Tuple for fixed-size collections
def validate_audio(audio_data: np.ndarray) -> Tuple[bool, str]:
    """Returns (is_valid, error_message)"""
    ...
```

---

## Testing Patterns

### Test-First Development (Red-Green-Refactor)

**Mandated by constitution**:

1. **RED**: Write failing test first
   ```python
   def test_transcribe_audio_returns_text():
       """Test that transcription returns non-empty text."""
       # Arrange
       audio_data = load_test_audio("sample_10s.wav")
       engine = STTEngine(model_name="medium.en")
       
       # Act
       result = engine.transcribe_audio(audio_data)
       
       # Assert
       assert result.text != ""
       assert len(result.text) > 0
   ```

2. **GREEN**: Write minimal code to pass test
   ```python
   class STTEngine:
       def transcribe_audio(self, audio_data: np.ndarray) -> TranscriptionResult:
           # Minimal implementation
           model = self._load_model()
           segments, _ = model.transcribe(audio_data)
           text = "".join(seg.text for seg in segments)
           return TranscriptionResult(text=text)
   ```

3. **REFACTOR**: Improve code quality while keeping tests green
   ```python
   class STTEngine:
       def transcribe_audio(self, audio_data: np.ndarray) -> TranscriptionResult:
           # Refactored with error handling, logging, validation
           self._validate_audio(audio_data)
           model = self._load_model()
           segments, info = model.transcribe(audio_data)
           text = self._extract_text(segments)
           return self._build_result(text, info)
   ```

### Unit Test Structure

**Location**: `tests/unit/test_<module>_<class>.py`

**Pattern**:
```python
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.stt.recorder import MicrophoneRecorder
from src.utils.errors import MicrophoneError


class TestMicrophoneRecorder:
    """Unit tests for MicrophoneRecorder class."""
    
    @pytest.fixture
    def mock_sounddevice(self):
        """Mock sounddevice module to avoid hardware dependencies."""
        with patch("src.stt.recorder.sd") as mock_sd:
            mock_sd.default.device = (0, None)
            mock_sd.query_devices.return_value = {
                "name": "Test Microphone",
                "max_input_channels": 2,
                "default_samplerate": 44100
            }
            yield mock_sd
    
    def test_detect_default_device_success(self, mock_sounddevice):
        """Test that default microphone is detected correctly."""
        # Arrange
        recorder = MicrophoneRecorder()
        
        # Act
        device_id, device_name = recorder._detect_default_device()
        
        # Assert
        assert device_id == 0
        assert device_name == "Test Microphone"
        mock_sounddevice.query_devices.assert_called_once()
    
    def test_detect_default_device_no_microphone(self, mock_sounddevice):
        """Test error handling when no microphone is found."""
        # Arrange
        mock_sounddevice.default.device = (None, None)
        recorder = MicrophoneRecorder()
        
        # Act & Assert
        with pytest.raises(MicrophoneError, match="No microphone detected"):
            recorder._detect_default_device()
```

### Mocking Strategies

**Mock external dependencies** (audio I/O, network, file system):

```python
# Mock HTTP requests
@patch("src.extraction.url_fetcher.requests.get")
def test_fetch_url_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test</body></html>"
    mock_get.return_value = mock_response
    
    result = fetch_url("https://example.com")
    assert "Test" in result

# Mock file I/O
@patch("src.extraction.file_loader.Path.read_text")
def test_load_local_file(mock_read_text):
    mock_read_text.return_value = "<html>Content</html>"
    result = load_file("test.html")
    assert "Content" in result

# Mock audio devices
@patch("sounddevice.InputStream")
def test_start_recording(mock_input_stream):
    mock_stream = MagicMock()
    mock_input_stream.return_value = mock_stream
    
    recorder = MicrophoneRecorder()
    recorder.start_recording()
    
    mock_input_stream.assert_called_once()
    mock_stream.start.assert_called_once()
```

### Test Fixtures

**Reusable test data** in `tests/fixtures/`:

```python
# tests/conftest.py (shared fixtures)
import pytest
import numpy as np
from pathlib import Path

@pytest.fixture
def sample_audio_10s() -> np.ndarray:
    """10-second sample audio at 16kHz."""
    return np.random.randint(-32768, 32767, 160000, dtype=np.int16)

@pytest.fixture
def sample_html() -> str:
    """Sample HTML with article content."""
    return Path("tests/fixtures/sample_article.html").read_text()

@pytest.fixture
def mock_whisper_model():
    """Mock Whisper model for STT tests."""
    with patch("faster_whisper.WhisperModel") as mock:
        mock_instance = MagicMock()
        mock_instance.transcribe.return_value = (
            [{"text": "Hello world", "start": 0.0, "end": 1.5}],
            {"language": "en", "duration": 10.0}
        )
        mock.return_value = mock_instance
        yield mock
```

### Integration Tests

**End-to-end workflow testing** in `tests/integration/`:

```python
# tests/integration/test_tts_workflow.py
import pytest
from unittest.mock import patch

from src.main import command_read


class TestTTSWorkflow:
    """Integration tests for full TTS workflow."""
    
    @patch("src.tts.playback.pygame.mixer")
    @patch("src.extraction.url_fetcher.requests.get")
    def test_read_url_to_audio_success(self, mock_get, mock_mixer):
        """Test complete workflow: URL → fetch → extract → synthesize → play."""
        # Arrange
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = """
            <html><body>
            <article>This is a test article with some content.</article>
            </body></html>
        """
        
        # Act
        args = argparse.Namespace(
            url="https://example.com",
            voice="en_US-libritts-high",
            speed=1.0,
            output=None,
            save_session=None
        )
        command_read(args)
        
        # Assert
        mock_get.assert_called_once()
        mock_mixer.init.assert_called_once()
        mock_mixer.music.play.assert_called()
```

---

## Contribution Workflow

### Branch Naming Convention

```
<type>/<short-description>

Examples:
- feat/speech-to-text-integration
- fix/microphone-detection-error
- docs/update-readme
- refactor/extract-audio-utils
- test/add-stt-unit-tests
```

**Types**:
- `feat/`: New features
- `fix/`: Bug fixes
- `docs/`: Documentation changes
- `refactor/`: Code restructuring without behavior change
- `test/`: Adding or updating tests
- `chore/`: Build, CI, dependencies

### Commit Messages (Conventional Commits)

**Format**: `<type>(<scope>): <description>`

**Examples**:
```
feat(stt): add Whisper model loader with caching
fix(tts): resolve playback stutter on long audio
docs(readme): update installation instructions for v3.0.0
refactor(extraction): extract DOM walking into separate function
test(stt): add unit tests for microphone detection
chore(deps): update faster-whisper to 1.0.1
```

**Types**: feat, fix, docs, style, refactor, test, chore  
**Scope**: Module name (stt, tts, extraction, cli, etc.)  
**Description**: Imperative mood ("add" not "added"), lowercase, no period

**Commit message body** (optional):
```
feat(stt): add silence detection for auto-stop

Implements RMS-based silence detection with configurable threshold.
Recording stops automatically after 5 seconds of silence.

Closes #42
```

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] **Tests**: All new code has tests (≥80% coverage, ≥95% for critical paths)
- [ ] **Tests pass**: `pytest` runs without failures
- [ ] **Linting**: `ruff check src/` passes
- [ ] **Formatting**: `ruff format src/` applied
- [ ] **Type hints**: All functions have parameter and return type hints
- [ ] **Docstrings**: All public functions/classes have docstrings
- [ ] **Commit messages**: Follow Conventional Commits format
- [ ] **No breaking changes**: Or documented in CHANGELOG.md with BREAKING CHANGE note
- [ ] **Documentation updated**: README, ARCHITECTURE, or module docstrings updated if needed
- [ ] **No hardcoded secrets**: No API keys, passwords, or sensitive data in code
- [ ] **PR description**: Includes context, testing steps, and closes issue(s)

**PR Template**:
```markdown
## Description
[Brief description of changes]

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
[How to test these changes]

## Checklist
- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
```

### Development Workflow

1. **Create feature branch**: `git checkout -b feat/my-feature`
2. **Write failing test**: Follow Red-Green-Refactor
3. **Implement feature**: Write minimal code to pass test
4. **Run tests**: `pytest --cov=src --cov-fail-under=80`
5. **Lint and format**: `ruff check src/ && ruff format src/`
6. **Commit changes**: `git commit -m "feat(module): add feature"`
7. **Push branch**: `git push origin feat/my-feature`
8. **Open PR**: Use PR template, request review
9. **Address feedback**: Make changes, push updates
10. **Merge**: Squash and merge after approval

---

## AI Agent Guidelines

### Code Generation Rules

**When generating new code**:

1. **Always write tests first**: Follow Red-Green-Refactor cycle
2. **Use type hints**: All parameters and return values must be typed
3. **Add docstrings**: Google-style format with Args, Returns, Raises sections
4. **Follow import order**: stdlib → third-party → local
5. **Handle errors gracefully**: Use custom exceptions from `src/utils/errors.py`
6. **Add logging**: Use `logging.getLogger(__name__)` for contextual logging
7. **Keep functions small**: Aim for <50 lines, single responsibility
8. **Avoid premature optimization**: Optimize only when profiling shows need

**Example generated function**:
```python
import logging
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

from src.config import STT_MODEL_CACHE
from src.utils.errors import ModelLoadError

logger = logging.getLogger(__name__)


def load_whisper_model(
    model_name: str = "medium.en",
    cache_dir: Optional[str] = None
) -> WhisperModel:
    """Load Whisper model with caching support.
    
    Args:
        model_name: Whisper model identifier (e.g., "medium.en")
        cache_dir: Optional cache directory (defaults to STT_MODEL_CACHE)
    
    Returns:
        Loaded WhisperModel instance
    
    Raises:
        ModelLoadError: If model fails to load or download
    
    Example:
        >>> model = load_whisper_model("medium.en")
        >>> model.transcribe(audio_data)
    """
    cache_dir = cache_dir or str(STT_MODEL_CACHE)
    logger.info(f"Loading Whisper model '{model_name}' from cache: {cache_dir}")
    
    try:
        model = WhisperModel(model_name, download_root=cache_dir)
        logger.info(f"Successfully loaded model '{model_name}'")
        return model
    except Exception as e:
        logger.error(f"Failed to load model '{model_name}': {e}")
        raise ModelLoadError(f"Could not load Whisper model '{model_name}': {e}")
```

### Refactoring Guidelines

**When refactoring existing code**:

1. **Ensure tests exist and pass**: Never refactor without test coverage
2. **Preserve behavior**: Refactoring should not change functionality
3. **Run tests after each change**: Continuous validation
4. **Extract functions**: Break large functions into smaller, testable units
5. **Improve naming**: Use descriptive names (no abbreviations unless standard)
6. **Remove duplication**: Apply DRY principle
7. **Simplify conditionals**: Replace nested ifs with guard clauses or polymorphism

**Refactoring example**:
```python
# BEFORE: Long function with nested logic
def process_audio(audio_data, options):
    if audio_data is not None:
        if len(audio_data) > 0:
            if options.get("normalize"):
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val * 32767
            if options.get("trim_silence"):
                threshold = options.get("threshold", 500)
                # ... complex silence detection logic ...
    return audio_data

# AFTER: Refactored with guard clauses and extracted functions
def process_audio(audio_data: np.ndarray, options: dict) -> np.ndarray:
    """Process audio with normalization and silence trimming."""
    if audio_data is None or len(audio_data) == 0:
        return audio_data
    
    if options.get("normalize"):
        audio_data = normalize_audio(audio_data)
    
    if options.get("trim_silence"):
        threshold = options.get("threshold", 500)
        audio_data = trim_silence(audio_data, threshold)
    
    return audio_data


def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    """Normalize audio levels to prevent clipping."""
    max_val = np.max(np.abs(audio_data))
    if max_val == 0:
        return audio_data
    return (audio_data / max_val * 32767).astype(np.int16)


def trim_silence(audio_data: np.ndarray, threshold: int) -> np.ndarray:
    """Trim leading and trailing silence from audio."""
    # Extracted silence detection logic
    ...
```

### Debugging Best Practices

**When debugging issues**:

1. **Check logs first**: Use `setup_logging()` output to understand flow
2. **Add strategic logging**: Log inputs, outputs, and key decision points
3. **Use debugger**: VS Code debugger with breakpoints (not just print statements)
4. **Write reproduction test**: Create failing test that reproduces bug
5. **Isolate the issue**: Use unit tests to narrow down problematic function
6. **Check assumptions**: Verify type expectations with `assert isinstance()`
7. **Review recent changes**: Use `git log` and `git diff` to find regressions

**Debugging workflow**:
```python
# 1. Add logging to understand state
logger.debug(f"Input audio_data shape: {audio_data.shape}, dtype: {audio_data.dtype}")

# 2. Add assertions to validate assumptions
assert audio_data.dtype == np.int16, f"Expected int16, got {audio_data.dtype}"
assert len(audio_data.shape) == 1, f"Expected 1D array, got shape {audio_data.shape}"

# 3. Write test that reproduces bug
def test_transcribe_with_stereo_audio():
    """Bug: transcribe fails with stereo audio (should convert to mono)."""
    stereo_audio = np.random.randint(-32768, 32767, (160000, 2), dtype=np.int16)
    result = transcribe_audio(stereo_audio)  # Should not raise error
    assert result.text != ""
```

---

## CI/CD Pipeline Documentation

### GitHub Actions Workflow

**Location**: `.github/workflows/ci.yml`

**Triggered on**: Push to `main`, all pull requests

**Jobs**:

1. **Linting** (ruff)
   ```yaml
   - name: Run ruff linter
     run: ruff check src/ tests/
   ```

2. **Formatting** (ruff format)
   ```yaml
   - name: Check code formatting
     run: ruff format --check src/ tests/
   ```

3. **Unit Tests** (pytest)
   ```yaml
   - name: Run unit tests
     run: pytest tests/unit/ --cov=src --cov-report=xml
   ```

4. **Integration Tests** (pytest)
   ```yaml
   - name: Run integration tests
     run: pytest tests/integration/ --cov=src --cov-append --cov-report=xml
   ```

5. **Coverage Check**
   ```yaml
   - name: Check coverage thresholds
     run: pytest --cov=src --cov-fail-under=80
   ```

6. **Type Checking** (mypy - optional)
   ```yaml
   - name: Run mypy type checker
     run: mypy src/ --ignore-missing-imports
   ```

### Pre-commit Hooks

**Location**: `.pre-commit-config.yaml`

**Hooks**:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]
```

**Installation**:
```bash
uv pip install pre-commit
pre-commit install
```

**Manual run**:
```bash
pre-commit run --all-files
```

### Build and Release Pipeline

**Build executable** (PyInstaller):
```bash
# scripts/build_exe.py
python scripts/build_exe.py  # Creates dist/vox.exe
```

**Version bumping** (commitizen):
```bash
cz bump  # Auto-increment version based on conventional commits
```

**Release workflow**:
1. Merge feature branches to `main`
2. Run `cz bump` to update version in `pyproject.toml` and `CHANGELOG.md`
3. Tag release: `git tag v3.0.0 && git push --tags`
4. GitHub Actions builds executable and creates release
5. Upload `vox.exe` to GitHub Releases

---

## Technology Stack

### Core Dependencies

| Dependency | Version | Purpose | License |
|------------|---------|---------|---------|
| **Python** | ≥3.13 | Programming language | PSF |
| **faster-whisper** | ≥1.0.0 | Speech-to-text (Whisper optimized) | MIT |
| **piper-tts** | ≥1.2.0 | Text-to-speech (neural TTS) | MIT |
| **sounddevice** | ≥0.4.6 | Microphone audio capture | MIT |
| **pygame** | ≥2.6.0 | Audio playback (TTS) | LGPL |
| **requests** | ≥2.31.0 | HTTP requests (URL fetching) | Apache 2.0 |
| **BeautifulSoup4** | ≥4.12.0 | HTML parsing | MIT |
| **pywinauto** | ≥0.6.9 | Browser automation (Windows) | BSD |
| **NumPy** | ≥1.24.0 | Audio processing (arrays) | BSD |
| **scipy** | ≥1.11.0 | WAV file handling | BSD |
| **Pillow** | ≥10.0.0 | Image processing (screenshots) | PIL |
| **colorama** | ≥0.4.6 | Terminal colors (CLI output) | BSD |

### Development Tools

| Tool | Version | Purpose | Command |
|------|---------|---------|---------|
| **pytest** | ≥7.4.0 | Testing framework | `pytest` |
| **pytest-cov** | ≥4.1.0 | Coverage measurement | `pytest --cov` |
| **ruff** | ≥0.1.0 | Linter and formatter | `ruff check`, `ruff format` |
| **uv** | Latest | Fast package manager | `uv pip install` |
| **commitizen** | ≥3.0.0 | Conventional commits | `cz bump` |
| **pre-commit** | ≥3.4.0 | Git hooks | `pre-commit run` |
| **PyInstaller** | ≥6.0.0 | Executable builder | `pyinstaller` |

### Platform Requirements

- **Operating System**: Windows 11 (primary target)
- **Python Version**: 3.13 or higher
- **Disk Space**: ~2GB for Whisper models (medium.en)
- **RAM**: ≥8GB recommended (Whisper model loading)
- **Audio**: Microphone for STT, speakers/headphones for TTS

### Optional Dependencies

- **mypy**: Type checking (not enforced but recommended)
- **black**: Alternative formatter (ruff format used instead)

---

## Project Structure

### Repository Layout

```
vox/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # CLI entry point (argparse, command routing)
│   ├── config.py                # Configuration constants (paths, defaults)
│   ├── browser/                 # Browser tab detection (Windows)
│   │   ├── __init__.py
│   │   ├── accessibility.py     # Windows accessibility API
│   │   ├── detector.py          # Browser process detection
│   │   └── tab_info.py          # Extract URL from active tab
│   ├── extraction/              # Web content extraction
│   │   ├── __init__.py
│   │   ├── url_fetcher.py       # HTTP GET requests
│   │   ├── file_loader.py       # Load HTML from disk
│   │   ├── html_parser.py       # BeautifulSoup wrapper
│   │   ├── dom_walker.py        # Walk DOM tree, extract text
│   │   ├── text_extractor.py    # Orchestrate extraction pipeline
│   │   └── content_filter.py    # Remove nav, ads, scripts
│   ├── tts/                     # Text-to-speech
│   │   ├── __init__.py
│   │   ├── synthesizer.py       # Main TTS orchestrator
│   │   ├── piper_provider.py    # Piper TTS integration
│   │   ├── chunking.py          # Split text into chunks
│   │   ├── playback.py          # pygame audio playback
│   │   └── controller.py        # Keyboard controls (pause/seek)
│   ├── stt/                     # Speech-to-text
│   │   ├── __init__.py
│   │   ├── transcriber.py       # Main STT orchestrator
│   │   ├── engine.py            # Whisper model wrapper
│   │   ├── recorder.py          # Microphone recording (sounddevice)
│   │   └── audio_utils.py       # Silence detection, preprocessing
│   ├── session/                 # TTS session management
│   │   ├── __init__.py
│   │   ├── manager.py           # Save/load/resume sessions
│   │   └── models.py            # Session dataclasses
│   └── utils/                   # Shared utilities
│       ├── __init__.py
│       ├── errors.py            # Custom exceptions
│       ├── logging.py           # Centralized logging setup
│       └── migration.py         # Config migration (vox → vox)
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/                    # Unit tests (mock dependencies)
│   │   ├── test_tts_synthesizer.py
│   │   ├── test_stt_recorder.py
│   │   ├── test_extraction_parser.py
│   │   └── ...
│   ├── integration/             # End-to-end tests
│   │   ├── test_tts_workflow.py
│   │   ├── test_stt_workflow.py
│   │   └── test_cli_commands.py
│   └── fixtures/                # Test data
│       ├── sample_article.html
│       ├── sample_audio_10s.wav
│       └── ...
├── specs/                       # Feature specifications
│   ├── 001-web-reader-ai/      # Legacy TTS feature
│   ├── 002-playback-session-improvements/
│   └── 003-speech-to-text/     # Current feature
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md
│       ├── tasks.md
│       ├── contracts/
│       └── checklists/
├── docs/                        # Documentation
│   ├── BUILD.md                 # Build instructions
│   └── ARCHITECTURE.md          # (Planned) Architecture deep dive
├── scripts/                     # Build and automation scripts
│   └── build_exe.py             # PyInstaller executable builder
├── .github/                     # GitHub configuration
│   ├── workflows/
│   │   └── ci.yml               # CI/CD pipeline
│   └── prompts/                 # AI agent prompts
│       └── speckit.implement.prompt.md
├── .specify/                    # Speckit configuration
│   ├── memory/
│   │   └── constitution.md      # Project constitution
│   ├── scripts/
│   └── templates/
├── pyproject.toml               # Project metadata, dependencies
├── pytest.ini                   # Pytest configuration
├── .gitignore                   # Git ignore rules
├── .pre-commit-config.yaml      # Pre-commit hooks
├── README.md                    # User-focused documentation
├── claude.md                    # This file (developer guidelines)
├── CHANGELOG.md                 # Version history
└── LICENSE                      # MIT license
```

### Module Dependency Map

```
main.py
  ├─→ tts/ (for vox read commands)
  │    ├─→ extraction/ (URL/HTML → text)
  │    ├─→ browser/ (active tab detection)
  │    ├─→ session/ (save/resume)
  │    └─→ utils/ (errors, logging)
  │
  └─→ stt/ (for vox transcribe commands)
       ├─→ utils/ (errors, logging)
       └─→ config (model paths)

tts/ ←→ session/ (bidirectional: TTS uses sessions, sessions store TTS state)
extraction/ → browser/ (extract active tab content)
All modules → utils/ (errors, logging)
All modules → config (paths, settings)
```

**Dependency rules**:
- **No circular dependencies**: Modules must form a DAG (directed acyclic graph)
- **Dependency inversion**: High-level modules depend on abstractions, not implementations
- **Shared utilities**: Common code extracted to `utils/` module

---

## Configuration Management

### Configuration File: src/config.py

**Purpose**: Single source of truth for all configuration constants.

**Key sections**:

1. **File Paths**
   ```python
   from pathlib import Path
   
   # Application data directory
   APPDATA = Path.home() / "AppData" / "Roaming"
   APP_DIR = APPDATA / "vox"  # Changed from "vox" in v3.0.0
   
   # TTS-specific paths
   TTS_MODEL_CACHE = APP_DIR / "models" / "tts"
   SESSION_DIR = APP_DIR / "sessions"
   
   # STT-specific paths
   STT_MODEL_CACHE = APP_DIR / "models" / "stt"
   ```

2. **TTS Defaults**
   ```python
   DEFAULT_TTS_VOICE = "en_US-libritts-high"
   DEFAULT_SPEED = 1.0
   DEFAULT_CHUNK_SIZE = 200  # characters
   ```

3. **STT Defaults**
   ```python
   DEFAULT_STT_MODEL = "medium.en"
   SAMPLE_RATE = 16000  # 16kHz (required for Whisper)
   SILENCE_DURATION = 5.0  # seconds
   SILENCE_THRESHOLD = 500  # RMS units
   ```

4. **Logging Configuration**
   ```python
   LOG_LEVEL = "INFO"
   LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
   LOG_FILE = APP_DIR / "vox.log"
   ```

### Environment Variables

**Optional overrides** via environment variables:

```bash
# Override model cache directories
export VOX_TTS_MODEL_CACHE="C:\custom\path\tts"
export VOX_STT_MODEL_CACHE="C:\custom\path\stt"

# Override log level
export VOX_LOG_LEVEL="DEBUG"

# Override silence detection
export VOX_SILENCE_THRESHOLD="300"
export VOX_SILENCE_DURATION="3.0"
```

**Reading environment variables** in `config.py`:
```python
import os

STT_MODEL_CACHE = Path(
    os.getenv("VOX_STT_MODEL_CACHE", str(APP_DIR / "models" / "stt"))
)
LOG_LEVEL = os.getenv("VOX_LOG_LEVEL", "INFO")
```

### Model Cache Management

**TTS models** (Piper TTS):
- Downloaded on first use to `%APPDATA%/vox/models/tts/`
- Size: ~20-50MB per voice
- Models persist across runs (cached)

**STT models** (Whisper):
- Downloaded on first use to `%APPDATA%/vox/models/stt/`
- Size: 75MB (tiny) to 3GB (large)
- Default: medium.en (~1.5GB)
- Models persist across runs (cached)

**Cache cleanup**:
```python
# Clear STT model cache
from src.config import STT_MODEL_CACHE
import shutil

shutil.rmtree(STT_MODEL_CACHE)  # Delete all models
```

### Configuration Migration

**vox → vox migration** (v3.0.0):

**Handled by** `src/utils/migration.py`:
```python
def migrate_config() -> bool:
    """Migrate config from old vox directory to new vox directory.
    
    Returns:
        True if migration occurred, False if no old config found
    """
    old_dir = APPDATA / "vox"
    new_dir = APPDATA / "vox"
    
    if not old_dir.exists() or new_dir.exists():
        return False
    
    logger.info(f"Migrating config: {old_dir} → {new_dir}")
    backup_old_config(old_dir)
    copy_config_files(old_dir, new_dir)
    return True
```

**Called automatically** on first run of vox v3.0.0 from `src/main.py`:
```python
def main():
    setup_logging()
    migrate_config()  # Auto-migrate on startup
    # ... rest of CLI logic
```

---

## Appendix: Quick Reference

### Common Commands

```bash
# Development
pytest --cov=src --cov-report=html        # Run tests with coverage
ruff check src/ tests/                    # Lint code
ruff format src/ tests/                   # Format code
pre-commit run --all-files                # Run all pre-commit hooks

# Installation
uv pip install -e .                       # Editable install
uv pip install -e ".[dev]"                # Install with dev dependencies

# CLI Usage
vox read --url https://example.com        # TTS: Read URL
vox transcribe                            # STT: Record and transcribe
vox list-sessions                         # TTS: List saved sessions
vox --version                             # Show version

# Build
python scripts/build_exe.py               # Build standalone executable

# Version Management
cz bump                                   # Auto-increment version
git tag v3.0.0 && git push --tags         # Create release tag
```

### Key Files to Modify

| Task | Files to Modify |
|------|----------------|
| Add STT feature | `src/stt/` (new module), `src/main.py` (add command), `tests/unit/test_stt_*.py` |
| Add TTS voice | `src/tts/piper_provider.py`, `src/config.py` (add voice constant) |
| Change CLI | `src/main.py` (argparse definition) |
| Add error type | `src/utils/errors.py` (custom exception class) |
| Update dependencies | `pyproject.toml` (dependencies section) |
| Change config paths | `src/config.py` (path constants) |

### Design Patterns Used

| Pattern | Usage | Location |
|---------|-------|----------|
| **Facade** | Simplify complex subsystems with unified interface | `src/tts/synthesizer.py`, `src/stt/transcriber.py` |
| **Strategy** | Pluggable TTS providers (Piper, future alternatives) | `src/tts/piper_provider.py` |
| **Template Method** | Standard workflow with customizable steps | `src/extraction/text_extractor.py` |
| **Observer** | Keyboard event handling for playback controls | `src/tts/controller.py` |
| **Factory** | Session creation with validation | `src/session/manager.py` |

---

## Document Metadata

- **Last Updated**: January 18, 2026
- **Version**: 1.0.0
- **Maintained By**: Development team, AI agents (Claude, GitHub Copilot)
- **Review Cycle**: Update on major feature additions or architectural changes

**Related Documents**:
- [README.md](README.md) - User-focused documentation
- [specs/003-speech-to-text/plan.md](specs/003-speech-to-text/plan.md) - Implementation plan
- [specs/003-speech-to-text/spec.md](specs/003-speech-to-text/spec.md) - Feature specification
- [.specify/memory/constitution.md](.specify/memory/constitution.md) - Project constitution
