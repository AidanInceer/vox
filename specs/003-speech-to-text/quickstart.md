# Developer Quickstart: Phase 3 Implementation

**Feature**: Speech-to-Text Integration & Project Documentation Enhancement  
**Branch**: `003-speech-to-text`  
**Date**: January 18, 2026  
**Target Audience**: Developers implementing Phase 3

## Prerequisites

Before starting implementation, ensure you have:

- [ ] Read [spec.md](spec.md) - Feature specification
- [ ] Read [research.md](research.md) - Technology decisions
- [ ] Read [data-model.md](data-model.md) - Entity definitions
- [ ] Read [constitution.md](../.specify/memory/constitution.md) - Project standards
- [ ] Python 3.13+ installed
- [ ] UV package manager installed (`pip install uv`)
- [ ] Git repository cloned and on `003-speech-to-text` branch

## Implementation Order

Follow user story priority order per clarifications in spec.md:

1. **P1: Project Rebranding** (Foundation)
2. **P2: Developer Documentation** (Standards)
3. **P3: README Overhaul** (User onboarding)
4. **P4: Voice Recording to Text** (Core STT feature)

## Phase 1: Project Rebranding

### Step 1.1: Name Selection

**Action Required**: Select project name from research.md candidates

**Process**:
1. Review naming candidates in [research.md Section 3](research.md#3-project-naming-research)
2. Verify PyPI availability: `https://pypi.org/search/?q=[name]`
3. Verify GitHub availability: `https://github.com/AidanInceer/[name]`
4. Get stakeholder approval
5. Document decision in [contracts/rebranding.md](contracts/rebranding.md)

**Blocked Until**: Name is selected and validated

### Step 1.2: Systematic Refactoring

**Checklist**: Use [contracts/rebranding.md](contracts/rebranding.md) as task list

**Key Files to Update** (in order):

1. `pyproject.toml` - Package name, entry point, URLs
2. `src/__init__.py` - Version bump to 2.0.0
3. `src/config.py` - APP_NAME constant
4. `src/main.py` - CLI parser program name
5. All `print()` statements displaying app name
6. `README.md` - All references and examples
7. Build scripts (`scripts/build_exe.py`, `.spec` file)

**Testing**:
```bash
# After each change, verify
pytest tests/ --cov=src
[new_command] --version
[new_command] --help
```

**Version Bump**:
```bash
# Update version with commitizen
cz bump --major  # MAJOR bump for breaking change
```

## Phase 2: Developer Documentation

### Step 2.1: Create Architecture Overview

**File**: `docs/ARCHITECTURE.md`

**Content Structure**:
```markdown
# [NewName] Architecture

## Overview
- System purpose and capabilities
- Target users
- Key features (TTS + STT)

## High-Level Architecture
[Diagram showing modules: TTS, STT, extraction, session, browser, CLI]

## Data Flow
### TTS Workflow
URL → fetch → extract → synthesize → play

### STT Workflow  
mic → record → transcribe → output

## Module Responsibilities
### src/tts/ - Text-to-Speech
### src/stt/ - Speech-to-Text (new)
### src/extraction/ - Web content extraction
### src/browser/ - Browser tab detection
### src/session/ - Session management
### src/ui/ - CLI display utilities
### src/utils/ - Shared utilities

## Technology Stack
- Python 3.13
- Piper TTS (text-to-speech)
- faster-whisper (speech-to-text)
- sounddevice (audio input)
- pygame (audio playback)
- pytest (testing)

## Design Decisions
[Reference research.md for STT/audio library choices]

## Testing Strategy
- Test-first development (Red-Green-Refactor)
- ≥80% coverage (≥95% for TTS/STT critical paths)
- Mock external dependencies (audio I/O, network)
```

**Reference**: See [existing project structure](../../README.md) for current modules

### Step 2.2: Create AI Agent Guidelines

**Files**: `.agents` (JSON) and `claude.md` (Markdown)

**.agents Format** (JSON):
```json
{
  "project": {
    "name": "[NewName]",
    "description": "Bidirectional audio-text conversion CLI",
    "type": "python-cli",
    "version": "2.0.0"
  },
  "standards": {
    "language": "Python 3.13",
    "testing": {
      "framework": "pytest",
      "coverage": "≥80% (≥95% critical paths)",
      "strategy": "test-first (Red-Green-Refactor)"
    },
    "code_quality": {
      "linter": "ruff",
      "formatter": "ruff format",
      "principles": ["SOLID", "DRY", "KISS"]
    }
  },
  "modules": {
    "tts": {
      "purpose": "Text-to-speech with Piper neural TTS",
      "dependencies": ["piper-tts", "pygame"]
    },
    "stt": {
      "purpose": "Speech-to-text with faster-whisper",
      "dependencies": ["faster-whisper", "sounddevice"]
    }
  }
}
```

**claude.md Structure**:
```markdown
# Claude Development Guidelines for [NewName]

## Project Overview
[Copy from ARCHITECTURE.md]

## Code Quality Standards
- Test-first: Write failing test first (Red-Green-Refactor)
- Coverage: ≥80% general, ≥95% for TTS/STT workflows
- SOLID principles: Single responsibility, open/closed, etc.
- DRY: Extract duplicated logic into shared functions
- KISS: Prefer simple solutions over clever optimizations
- Import organization: stdlib → 3rd party → local (with blank lines)

## Testing Patterns
### Unit Tests
- Mock external dependencies (sounddevice, network)
- Use fixtures for reusable test data
- Test edge cases (empty input, errors, boundary conditions)

### Integration Tests
- End-to-end workflows with fixture data
- CLI invocation via subprocess
- Verify stdout/stderr output

### Test Fixtures
- Audio samples: `tests/fixtures/audio/sample.wav`
- HTML pages: `tests/fixtures/html/article.html`
- Session data: `tests/fixtures/sessions/example.json`

## Common Patterns
[Code examples for typical tasks]

## Module Guidelines
[Specific patterns for each module]
```

## Phase 3: README Overhaul

### Step 3.1: Create User-Focused README

**File**: `README.md`

**New Structure** (replace existing):

```markdown
# [NewName]

[Logo if applicable]

*Tagline*: Bidirectional audio-text conversion for Windows - read web content aloud and transcribe your voice to text

## What It Does

[NewName] is a Windows desktop tool that:
- **Reads to you**: Convert web URLs to natural-sounding speech
- **Listens to you**: Transcribe your voice recordings to text
- **Runs offline**: No API keys, no cloud services, no subscription fees

Perfect for accessibility, productivity, note-taking, and content consumption.

## Features

### Text-to-Speech (TTS)
- 🌐 Read any web URL aloud
- 🎙️ High-quality neural voices (Piper TTS)
- 🎮 Interactive playback controls (pause/resume/seek)
- 💾 Save and resume reading sessions

### Speech-to-Text (STT)
- 🎤 Record from any microphone
- 📝 Accurate transcription (95%+ word accuracy)
- 💨 Fast processing (< 10 seconds typical)
- 📄 Save to text or JSON format

## Installation

### Using pip
```bash
pip install [new_name]
```

### Using uv (faster)
```bash
pip install uv
uv pip install [new_name]
```

### Standalone Executable
Download `[new_name].exe` from [Releases](releases-url). No Python required.

## Quick Start

### Read a web page aloud
```bash
[new_command] read --url https://example.com
```

### Transcribe your voice
```bash
[new_command] transcribe
# Speak into your microphone, press Enter when done
```

### Save transcription to file
```bash
[new_command] transcribe --output transcript.txt
```

## Full Usage Guide

[Detailed command reference - copy from existing README TTS sections, add STT sections]

## Troubleshooting

### No microphone detected
1. Connect microphone to computer
2. Open Settings > Privacy > Microphone
3. Enable "Allow apps to access your microphone"
4. Run `[new_command] list-devices` to verify

### Model download fails
Check internet connection. Models download automatically on first use (~1.5GB for medium.en).

### Low transcription accuracy
- Speak clearly and at moderate pace
- Reduce background noise
- Use a quality microphone
- Try `--model large-v2` for maximum accuracy (slower)

## Requirements

- Windows 11
- Python 3.13+ (if installing via pip)
- Microphone (for STT features)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for developer setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE)
```

### Step 3.2: Validate README

**Checklist**:
- [ ] All command examples are runnable and tested
- [ ] Installation instructions verified in fresh environment
- [ ] Links to releases, contributing guide are correct
- [ ] Troubleshooting covers common issues from testing
- [ ] Reflects new project name throughout
- [ ] Documents both TTS and STT features equally

## Phase 4: Voice Recording to Text (Core STT)

### Step 4.1: Setup Dependencies

**Update pyproject.toml**:

```toml
dependencies = [
    # ... existing dependencies ...
    "faster-whisper>=0.10.0",  # STT engine
    "sounddevice>=0.4.6",      # Microphone access
    # Note: numpy already in dependencies
]
```

**Install**:
```bash
uv pip install -e ".[dev]"
```

### Step 4.2: Create STT Module Structure

**Create directories**:
```bash
mkdir src/stt
mkdir tests/unit/test_stt
mkdir tests/fixtures/audio
```

**Create module files** (in test-first order):

#### 1. `src/stt/__init__.py`
```python
"""Speech-to-text module for [NewName]."""
from src.stt.device_manager import MicrophoneDevice, get_default_device, list_devices
from src.stt.recorder import VoiceRecorder
from src.stt.transcriber import Transcriber, TranscriptionResult

__all__ = [
    "MicrophoneDevice",
    "get_default_device",
    "list_devices",
    "VoiceRecorder",
    "Transcriber",
    "TranscriptionResult",
]
```

#### 2. `src/stt/device_manager.py` (Test First!)

**Test** (`tests/unit/test_stt/test_device_manager.py`):
```python
"""Tests for microphone device management."""
import pytest
from src.stt.device_manager import list_devices, get_default_device, MicrophoneDevice

def test_list_devices_returns_list():
    """Test list_devices returns a list of MicrophoneDevice objects."""
    devices = list_devices()
    assert isinstance(devices, list)
    if devices:  # If any devices exist
        assert all(isinstance(d, MicrophoneDevice) for d in devices)

def test_get_default_device_returns_device():
    """Test get_default_device returns a MicrophoneDevice."""
    device = get_default_device()
    assert device is None or isinstance(device, MicrophoneDevice)
    if device:
        assert device.is_default is True

def test_microphone_device_supports_recording():
    """Test MicrophoneDevice.supports_recording() method."""
    device = MicrophoneDevice(
        device_id=0,
        name="Test Mic",
        channels=1,
        sample_rate=48000,
        is_available=True
    )
    assert device.supports_recording() is True
    
    # Unavailable device
    device.is_available = False
    assert device.supports_recording() is False
```

**Implementation** (`src/stt/device_manager.py`):
```python
"""Microphone device detection and management."""
import sounddevice as sd
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MicrophoneDevice:
    """Represents an audio input device."""
    device_id: int
    name: str
    channels: int
    sample_rate: int
    is_default: bool = False
    is_available: bool = True
    
    def supports_recording(self) -> bool:
        """Check if device can be used for recording."""
        return self.is_available and self.channels >= 1

def list_devices() -> List[MicrophoneDevice]:
    """List all available microphone devices."""
    devices = []
    try:
        default_input = sd.default.device[0]  # Input device index
        for idx, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:  # Is an input device
                devices.append(MicrophoneDevice(
                    device_id=idx,
                    name=device['name'],
                    channels=device['max_input_channels'],
                    sample_rate=int(device['default_samplerate']),
                    is_default=(idx == default_input),
                    is_available=True
                ))
    except Exception as e:
        # Log error but return empty list (no devices available)
        pass
    return devices

def get_default_device() -> Optional[MicrophoneDevice]:
    """Get the system's default input device."""
    devices = list_devices()
    for device in devices:
        if device.is_default:
            return device
    return devices[0] if devices else None
```

#### 3. `src/stt/recorder.py` (Test First!)

**Test** (`tests/unit/test_stt/test_recorder.py`):
```python
"""Tests for voice recording."""
import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.stt.recorder import VoiceRecorder, VoiceRecording

@patch('src.stt.recorder.sd.InputStream')
def test_voice_recorder_initialization(mock_stream):
    """Test VoiceRecorder initializes correctly."""
    recorder = VoiceRecorder(device_id=0, sample_rate=16000)
    assert recorder.sample_rate == 16000
    assert recorder.device_id == 0

@patch('src.stt.recorder.sd.InputStream')
def test_voice_recorder_start_stop(mock_stream):
    """Test recording start and stop."""
    recorder = VoiceRecorder(device_id=0)
    recorder.start()
    assert recorder.is_recording is True
    
    recording = recorder.stop()
    assert recorder.is_recording is False
    assert isinstance(recording, VoiceRecording)

# More tests for silence detection, duration limits, etc.
```

**Implementation Pattern** (use data model from data-model.md):
```python
"""Voice recording from microphone."""
import sounddevice as sd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class VoiceRecording:
    """Represents captured audio recording."""
    audio_data: np.ndarray
    sample_rate: int = 16000
    # ... (see data-model.md for complete definition)

class VoiceRecorder:
    """Records audio from microphone."""
    
    def __init__(self, device_id: Optional[int] = None, sample_rate: int = 16000):
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.is_recording = False
        self._audio_buffer = []
    
    def start(self):
        """Start recording audio."""
        # Implementation with sounddevice.InputStream
        pass
    
    def stop(self) -> VoiceRecording:
        """Stop recording and return VoiceRecording."""
        # Implementation
        pass
    
    def _detect_silence(self, audio_chunk: np.ndarray, threshold: int = 500) -> bool:
        """Detect if audio chunk is silence."""
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms < threshold
```

#### 4. `src/stt/transcriber.py` (Test First!)

Follow same pattern: write tests first, then implement using faster-whisper as chosen in research.md.

### Step 4.3: Integrate STT into CLI

**Update `src/main.py`**:

```python
# Add STT imports
from src.stt import list_devices, get_default_device, VoiceRecorder, Transcriber

# Add transcribe subcommand
transcribe_parser = subparsers.add_parser("transcribe", help="Record voice and transcribe to text")
transcribe_parser.add_argument("--output", "-o", help="Save transcription to file")
transcribe_parser.add_argument("--format", "-f", choices=["text", "json"], default="text")
# ... (see contracts/stt-cli.md for complete options)

# Add list-devices subcommand
list_devices_parser = subparsers.add_parser("list-devices", help="List available microphones")

# Add handler functions
def handle_transcribe(args):
    """Handle transcribe command."""
    # Implementation per contracts/stt-cli.md
    pass

def handle_list_devices(args):
    """Handle list-devices command."""
    devices = list_devices()
    # Print formatted table per contracts/stt-cli.md
    pass
```

### Step 4.4: Testing Strategy

**Unit Tests** (80% coverage minimum):
- Mock sounddevice for all audio I/O
- Use numpy arrays as fixture audio data
- Test error conditions (no device, permission denied)

**Integration Tests** (end-to-end):
- Use pre-recorded WAV files as test fixtures
- Mock InputStream to return fixture data
- Verify transcription output matches expected text (±5% WER)

**Fixture Audio Creation**:
```python
# tests/fixtures/audio/create_fixtures.py
import numpy as np
import scipy.io.wavfile as wav

# Create 1-second sine wave (440 Hz) as test audio
sample_rate = 16000
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration))
audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
wav.write("tests/fixtures/audio/test_tone.wav", sample_rate, audio)
```

### Step 4.5: Error Handling

**Add STT errors to `src/utils/errors.py`**:
```python
# Speech-to-Text errors
class STTError(Exception):
    """Base exception for speech-to-text errors."""
    pass

class MicrophoneNotFoundError(STTError):
    """Raised when no microphone device is detected."""
    pass

class RecordingError(STTError):
    """Raised when audio recording fails."""
    pass

class TranscriptionError(STTError):
    """Raised when speech-to-text processing fails."""
    pass

class ModelLoadError(STTError):
    """Raised when STT model cannot be loaded."""
    pass
```

**Use in CLI handlers**:
```python
try:
    recording = recorder.record()
    result = transcriber.transcribe(recording)
    print_success(f"Transcription: {result.text}")
except MicrophoneNotFoundError:
    print_error("No microphone detected. Please connect a microphone.")
    sys.exit(2)
except RecordingError as e:
    print_error(f"Recording failed: {e}")
    sys.exit(3)
except TranscriptionError as e:
    print_error(f"Transcription failed: {e}")
    sys.exit(4)
```

## Development Workflow

### Daily Process

1. **Start day**: Pull latest from `003-speech-to-text` branch
2. **Select task**: Pick next item from user story (in priority order)
3. **Write tests first**: Red phase (failing test)
4. **Implement**: Green phase (make test pass)
5. **Refactor**: Improve code quality without breaking tests
6. **Run full suite**: `pytest tests/ --cov=src`
7. **Verify coverage**: Check report, add tests if < 80%
8. **Commit**: Conventional commit message (`feat:`, `fix:`, `docs:`, etc.)
9. **Push**: `git push origin 003-speech-to-text`

### Git Commit Messages

Follow conventional commits:
```bash
# Feature
git commit -m "feat(stt): add microphone device detection"

# Fix
git commit -m "fix(stt): handle missing microphone gracefully"

# Documentation
git commit -m "docs(readme): add STT usage examples"

# Tests
git commit -m "test(stt): add integration test for transcription"

# Refactor
git commit -m "refactor(stt): extract silence detection to helper"
```

### Code Review Checklist

Before requesting review:
- [ ] All tests pass (`pytest tests/`)
- [ ] Coverage ≥80% (≥95% for STT code)
- [ ] Ruff linting passes (`ruff check .`)
- [ ] Code formatted (`ruff format .`)
- [ ] Docstrings for all public functions
- [ ] Error handling with appropriate exceptions
- [ ] Manual testing of CLI commands
- [ ] Commit messages follow conventional commits

## Common Pitfalls & Solutions

### Pitfall 1: Audio I/O Blocking Tests

**Problem**: Tests hang when sounddevice tries to access real audio devices

**Solution**: Always mock sounddevice in unit tests
```python
@patch('src.stt.recorder.sd.InputStream')
def test_recorder(mock_stream):
    # Mock returns fake audio data
    pass
```

### Pitfall 2: Model Download in Tests

**Problem**: faster-whisper downloads large models during test runs

**Solution**: Mock model loading
```python
@patch('faster_whisper.WhisperModel')
def test_transcriber(mock_model):
    mock_model.return_value.transcribe.return_value = [({"text": "test"}, None)]
    # Test proceeds with mock
```

### Pitfall 3: Forgetting Test Coverage

**Problem**: New code merged without adequate tests

**Solution**: Run coverage check before committing
```bash
pytest tests/ --cov=src --cov-fail-under=80
# Fails if coverage < 80%
```

### Pitfall 4: Inconsistent Naming

**Problem**: Old "vox" references remain after rebranding

**Solution**: Use global search before merging
```bash
grep -r "vox" src/ tests/ --exclude-dir=specs
# Should return zero matches
```

## Resources

- [Spec (spec.md)](spec.md) - What to build
- [Research (research.md)](research.md) - Technology decisions
- [Data Model (data-model.md)](data-model.md) - Entity definitions
- [STT CLI Contract (contracts/stt-cli.md)](contracts/stt-cli.md) - CLI interface spec
- [Rebranding Checklist (contracts/rebranding.md)](contracts/rebranding.md) - Rename checklist
- [Constitution](../.specify/memory/constitution.md) - Project standards
- [faster-whisper Docs](https://github.com/guillaumekln/faster-whisper)
- [sounddevice Docs](https://python-sounddevice.readthedocs.io/)

## Getting Help

- **Stuck on implementation?** Review data-model.md for entity structure
- **Unclear on CLI behavior?** Check contracts/stt-cli.md examples
- **Test failing?** Review constitution testing patterns
- **Coverage too low?** Add edge case tests for error paths
- **Rebranding incomplete?** Use contracts/rebranding.md as checklist

## Success Criteria

Phase 3 is complete when:

1. ✅ Project renamed successfully (all checks in contracts/rebranding.md pass)
2. ✅ Documentation created (ARCHITECTURE.md, .agents, claude.md)
3. ✅ README overhauled (user-focused, documents TTS+STT)
4. ✅ STT feature working (`[new_command] transcribe` functional)
5. ✅ Tests pass (≥80% coverage, ≥95% for STT critical paths)
6. ✅ Manual testing complete (all CLI commands verified)
7. ✅ Version bumped to 2.0.0
8. ✅ Git tag created and pushed

**Timeline Estimate**: 3-5 days full-time development

**Good luck! Follow test-first, commit often, and refer to this guide when stuck.**
