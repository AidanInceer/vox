# Phase 1: Data Model

**Feature**: Speech-to-Text Integration & Project Documentation Enhancement  
**Branch**: `003-speech-to-text`  
**Date**: January 18, 2026

## Overview

This document defines the core entities and data structures for the Speech-to-Text feature, along with updated models for project rebranding. All entities follow the Text-Based I/O Protocol from the constitution.

## 1. Speech-to-Text Entities

### 1.1 Voice Recording

**Purpose**: Represents audio captured from the microphone during a recording session.

**Attributes**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `audio_data` | `numpy.ndarray` | Raw PCM audio samples | Shape: (n_samples,), dtype: int16 |
| `sample_rate` | `int` | Sampling frequency in Hz | Must be 16000 (16kHz) |
| `duration` | `float` | Recording length in seconds | > 0, calculated from len(audio_data)/sample_rate |
| `channels` | `int` | Number of audio channels | Must be 1 (mono) |
| `format` | `str` | Audio format identifier | Always "PCM_16" |
| `timestamp` | `datetime` | When recording started | ISO 8601 format |
| `device_name` | `str` | Microphone device used | From device_manager |

**State Transitions**:

```
[Created] → [Recording] → [Stopped] → [Processed]
           ↓
        [Cancelled]
```

**Example** (Python dataclass):

```python
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class VoiceRecording:
    """Represents a captured audio recording from microphone."""
    audio_data: np.ndarray
    sample_rate: int = 16000
    duration: float = 0.0
    channels: int = 1
    format: str = "PCM_16"
    timestamp: datetime = None
    device_name: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        self.duration = len(self.audio_data) / self.sample_rate
```

### 1.2 Transcription Result

**Purpose**: Represents the text output from speech recognition processing.

**Attributes**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `text` | `str` | Transcribed text content | Non-empty string |
| `confidence` | `float` | Overall confidence score | 0.0 - 1.0 (if available from STT engine) |
| `language` | `str` | Detected/specified language | ISO 639-1 code (e.g., "en") |
| `duration` | `float` | Original audio duration | > 0 seconds |
| `processing_time` | `float` | Time to transcribe | > 0 seconds |
| `model_version` | `str` | STT model identifier | e.g., "whisper-medium.en" |
| `timestamp` | `datetime` | When transcription completed | ISO 8601 format |
| `segments` | `list[TranscriptionSegment]` | Optional detailed segments | Empty if not supported |

**Relationships**:

- Derived from: `VoiceRecording` (1:1 relationship)
- Can be saved to: File (text output)

**Example**:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class TranscriptionSegment:
    """Represents a time-aligned segment of transcription."""
    text: str
    start: float  # seconds
    end: float    # seconds
    confidence: float = 0.0

@dataclass
class TranscriptionResult:
    """Represents the output of speech-to-text processing."""
    text: str
    confidence: float = 0.0
    language: str = "en"
    duration: float = 0.0
    processing_time: float = 0.0
    model_version: str = ""
    timestamp: datetime = None
    segments: List[TranscriptionSegment] = field(default_factory=list)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_json(self) -> dict:
        """Export as JSON-serializable dict."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "language": self.language,
            "duration": self.duration,
            "processing_time": self.processing_time,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat(),
            "segments": [
                {"text": seg.text, "start": seg.start, "end": seg.end, "confidence": seg.confidence}
                for seg in self.segments
            ]
        }
```

### 1.3 Microphone Device

**Purpose**: Represents an audio input device available for recording.

**Attributes**:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `device_id` | `int` | System device identifier | >= 0 |
| `name` | `str` | Human-readable device name | Non-empty |
| `channels` | `int` | Maximum input channels | >= 1 |
| `sample_rate` | `int` | Default sample rate | > 0, typically 44100 or 48000 |
| `is_default` | `bool` | System default input device | True/False |
| `is_available` | `bool` | Device currently available | True/False |

**Example**:

```python
from dataclasses import dataclass

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
```

### 1.4 STT Engine Configuration

**Purpose**: Settings for the speech recognition model and processing parameters.

**Attributes**:

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `model_name` | `str` | Whisper model size | "medium.en" |
| `language` | `str` | Target language code | "en" |
| `device` | `str` | Compute device | "cpu" (or "cuda" if GPU) |
| `compute_type` | `str` | Precision type | "int8" (CPU) or "float16" (GPU) |
| `beam_size` | `int` | Beam search width | 5 |
| `vad_filter` | `bool` | Voice activity detection | True |
| `silence_threshold` | `int` | RMS silence level | 500 |
| `silence_duration` | `float` | Silence timeout (seconds) | 5.0 |

**Example**:

```python
from dataclasses import dataclass

@dataclass
class STTEngineConfig:
    """Configuration for the speech-to-text engine."""
    model_name: str = "medium.en"
    language: str = "en"
    device: str = "cpu"
    compute_type: str = "int8"
    beam_size: int = 5
    vad_filter: bool = True
    silence_threshold: int = 500
    silence_duration: float = 5.0
    
    def to_dict(self) -> dict:
        """Export as dictionary for serialization."""
        return {
            "model_name": self.model_name,
            "language": self.language,
            "device": self.device,
            "compute_type": self.compute_type,
            "beam_size": self.beam_size,
            "vad_filter": self.vad_filter,
            "silence_threshold": self.silence_threshold,
            "silence_duration": self.silence_duration
        }
```

## 2. Rebranding Impact on Existing Entities

### 2.1 Application Metadata (Updated)

**Before** (`src/config.py`):

```python
APP_NAME = "vox"
APP_VERSION = "1.1.0"
CLI_COMMAND = "vox"
```

**After** (TBD based on naming decision from research.md):

```python
APP_NAME = "[NEW_NAME]"  # e.g., "SpeakRead", "VoiceSync", etc.
APP_VERSION = "2.0.0"      # MAJOR bump for breaking change
CLI_COMMAND = "[new_command]"
```

### 2.2 Session Model (Extended)

Existing `session/models.py` will be extended to support STT session metadata (if needed for future phases):

```python
# Future extension (not Phase 3 scope):
@dataclass
class STTSession:
    """Represents a saved STT recording/transcription session."""
    session_id: str
    audio_path: Path
    transcription_path: Path
    created_at: datetime
    duration: float
    model_version: str
```

## 3. Data Flow Diagrams

### 3.1 STT Workflow (Voice → Text)

```
User Input (CLI)
    ↓
[Microphone Device Detection]
    ├── Query sounddevice.query_devices()
    ├── Create MicrophoneDevice objects
    └── Select default or user-specified device
    ↓
[Audio Recording]
    ├── Initialize sounddevice.InputStream
    ├── Capture audio chunks (100ms buffers)
    ├── Monitor RMS for silence detection
    ├── Build VoiceRecording object
    └── Terminate on Enter/Ctrl+C or silence timeout
    ↓
[Speech-to-Text Processing]
    ├── Load faster-whisper model (lazy, cached)
    ├── Create STTEngineConfig
    ├── Transcribe audio_data
    └── Generate TranscriptionResult
    ↓
[Output]
    ├── Print text to stdout (print_success)
    ├── Optional: Save to file
    └── Optional: JSON output for --json flag
```

### 3.2 Rebranding Data Migration

```
Existing Data:
    - Session files in %APPDATA%/vox/
    - Configuration in config.py

Migration Strategy:
    1. Detect old "vox" directory
    2. Copy to new "[NEW_NAME]" directory
    3. Update session file paths in models
    4. Preserve backward compatibility for 1 release
    5. Show migration notice on first run
```

## 4. Data Validation Rules

### Audio Quality Validation

```python
def validate_audio_recording(recording: VoiceRecording) -> tuple[bool, str]:
    """Validate audio recording meets STT requirements."""
    if recording.sample_rate != 16000:
        return False, f"Sample rate must be 16000 Hz, got {recording.sample_rate}"
    
    if recording.channels != 1:
        return False, f"Audio must be mono (1 channel), got {recording.channels}"
    
    if recording.duration < 0.1:
        return False, "Recording too short (< 0.1 seconds)"
    
    if recording.duration > 600:  # 10 minutes
        return False, "Recording too long (> 10 minutes)"
    
    # Check if audio has any signal (not just silence)
    rms = np.sqrt(np.mean(recording.audio_data**2))
    if rms < 100:  # Configurable threshold
        return False, "Recording appears to be silent (RMS < 100)"
    
    return True, "Valid"
```

### Transcription Result Validation

```python
def validate_transcription(result: TranscriptionResult) -> tuple[bool, str]:
    """Validate transcription result."""
    if not result.text or result.text.isspace():
        return False, "Transcription text is empty"
    
    if result.confidence < 0 or result.confidence > 1:
        return False, f"Confidence must be 0-1, got {result.confidence}"
    
    if result.processing_time <= 0:
        return False, "Processing time must be positive"
    
    return True, "Valid"
```

## 5. Error Handling

### STT-Specific Errors (add to `src/utils/errors.py`)

```python
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

## Data Model Summary

### New Entities: 4
1. VoiceRecording
2. TranscriptionResult
3. MicrophoneDevice
4. STTEngineConfig

### Updated Entities: 1
1. Application Metadata (rebranding)

### Relationships
- VoiceRecording → TranscriptionResult (1:1)
- MicrophoneDevice → VoiceRecording (N:1, many recordings can use same device)
- STTEngineConfig → TranscriptionResult (1:N, one config used for many transcriptions)

### File Formats
- **Audio**: WAV (PCM 16-bit, 16kHz mono)
- **Transcription Output**: Plain text (.txt) or JSON (.json)
- **Configuration**: YAML or JSON (persisted in user data directory)

**Status**: ✅ Data model complete, ready for contract definitions (Phase 1 next step)
