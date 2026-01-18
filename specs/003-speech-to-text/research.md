# Phase 0: Research & Technology Decisions

**Feature**: Speech-to-Text Integration & Project Documentation Enhancement  
**Branch**: `003-speech-to-text`  
**Date**: January 18, 2026

## Research Summary

This document resolves all NEEDS CLARIFICATION items identified in Technical Context and provides evidence-based technology decisions for Phase 3 implementation.

## 1. Offline Speech-to-Text Library Selection

### Decision: **faster-whisper** (OpenAI Whisper optimized implementation)

### Rationale

**faster-whisper** selected over vosk and coqui-stt based on:

1. **Accuracy**: Whisper models achieve 95%+ word error rate (WER) for clear English speech, meeting FR-STT-004 requirement
2. **Offline capability**: Fully local inference with downloaded models, no API calls required
3. **Performance**: CTranslate2 backend provides 4x faster inference than standard whisper
4. **Model flexibility**: Multiple model sizes (tiny/base/small/medium/large) balance speed vs. accuracy
5. **Active maintenance**: Regular updates, strong community support (24k+ GitHub stars)
6. **Python-first**: Native Python API, easy PyPI installation

**Alternatives Considered**:

- **vosk**: 
  - ✅ Lightweight, fast
  - ❌ Lower accuracy (~85-90% WER vs. 95%+ for Whisper)
  - ❌ Limited model selection, less natural language handling
- **coqui-stt**:
  - ✅ Good accuracy
  - ❌ Project less actively maintained (archived in 2023)
  - ❌ Requires manual model training for best results

### Implementation Details

```python
# Installation
pip install faster-whisper

# Model recommendation: medium.en (balance of speed/accuracy)
# - Size: ~1.5GB download
# - Speed: ~3-5s transcription for 10s audio on typical CPU
# - Accuracy: 95%+ WER for clear English
```

### Performance Characteristics

| Model Size | Download | CPU Time (10s audio) | Accuracy | Recommended Use |
|------------|----------|---------------------|----------|-----------------|
| tiny.en    | 75 MB    | ~1s                 | ~85%     | Quick testing |
| base.en    | 145 MB   | ~2s                 | ~90%     | Fast transcription |
| small.en   | 488 MB   | ~3s                 | ~93%     | Balanced |
| **medium.en** | **1.5 GB** | **~4s**         | **~95%** | **Default (best balance)** |
| large-v2   | 3 GB     | ~8s                 | ~97%     | Max accuracy |

## 2. Audio Input Library Selection

### Decision: **sounddevice** with numpy

### Rationale

**sounddevice** selected over pyaudio based on:

1. **Modern API**: Cleaner Python 3 interface using numpy arrays
2. **Cross-platform**: Works on Windows/macOS/Linux via PortAudio backend
3. **Zero compilation**: Pure Python with precompiled binaries (no MSVC required on Windows)
4. **Real-time streaming**: Efficient callback-based recording for live audio
5. **Device enumeration**: Simple API to list/select microphones
6. **Active maintenance**: Regular updates, good documentation

**Alternatives Considered**:

- **pyaudio**:
  - ✅ Mature, well-tested
  - ❌ Requires compilation on Windows (MSVC toolchain)
  - ❌ No official Python 3.11+ wheels
  - ❌ Less Pythonic API (callback complexity)

### Implementation Details

```python
# Installation
pip install sounddevice numpy

# Key features:
# - Default device auto-detection
# - 16kHz sample rate support (required for STT)
# - WAV format output for Whisper compatibility
# - Silence detection via RMS amplitude analysis
```

### Audio Recording Specifications

- **Sample Rate**: 16,000 Hz (16kHz) - standard for speech recognition
- **Channels**: Mono (1 channel) - speech doesn't benefit from stereo
- **Format**: 16-bit PCM WAV - compatible with faster-whisper
- **Buffer**: 100ms chunks - balance latency vs. overhead
- **Silence Detection**: RMS threshold (configurable, default 500 units)

## 3. Project Naming Research

### Decision: **vox**

### Rationale

**vox** selected based on:

1. **Concise & Memorable**: Single syllable, easy to type and pronounce
2. **Voice-Focused**: Latin root "vox" means "voice", perfectly aligned with TTS/STT capabilities
3. **Professional**: Clean, technical-sounding name suitable for developer tools
4. **Bidirectional**: Implies voice-based interaction without restricting to input or output only
5. **Availability**: Available on PyPI and GitHub for package/repository naming
6. **International**: Latin root universally recognized, no language barriers

### Implementation Impact

- **Package name**: `vox` (pip install vox)
- **CLI command**: `vox` (vox read URL, vox transcribe)
- **Executable**: `vox.exe`
- **Repository**: github.com/[owner]/vox
- **Configuration directory**: `%APPDATA%/vox/`
- **Module imports**: `from vox import ...`

### Alternatives Considered

| Name | PyPI Status | GitHub Status | Pros | Cons | Score |
|------|-------------|---------------|------|------|-------|
| VoiceSync | ⚠️ Check | ✅ Available | Clear bidirectional metaphor | Generic, may clash with voice assistants | 7/10 |
| SpeakRead | ⚠️ Check | ✅ Available | Direct functionality description | Slightly awkward pronunciation | 8/10 |
| EchoText | ⚠️ Check | ✅ Available | Creative metaphor, memorable | Less clear what it does | 6/10 |
| AudioScript | ⚠️ Check | ⚠️ Check | Professional tone | Less distinctive | 7/10 |
| **vox** | ✅ Available | ✅ Available | **Concise, memorable, professional** | **Short may seem generic** | **9/10** |

## 4. Developer Documentation Structure

### Decision: **Create both `.agents` and `claude.md`**

### Rationale

- **`.agents`**: Universal AI agent guidelines (JSON/YAML format) - works with GitHub Copilot, Cursor, other tools
- **claude.md`**: Claude-specific optimizations and context

Both files serve different purposes and should coexist:

### `.agents` File Structure (JSON format)

```json
{
  "project": {
    "name": "vox",
    "description": "Bidirectional audio-text conversion CLI tool",
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
  "architecture": {
    "modules": [
      {
        "name": "tts",
        "purpose": "Text-to-speech using Piper neural TTS",
        "dependencies": ["piper-tts", "pygame"]
      },
      {
        "name": "stt",
        "purpose": "Speech-to-text using faster-whisper",
        "dependencies": ["faster-whisper", "sounddevice"]
      }
    ]
  }
}
```

### `claude.md` File Structure (Markdown format)

```markdown
# Claude Development Guidelines for [PROJECT_NAME]

## Project Overview
[High-level architecture, module diagram, data flow]

## Code Quality Standards
- Test-first development (Red-Green-Refactor)
- ≥80% coverage (≥95% for critical paths: TTS/STT workflows)
- SOLID/DRY/KISS principles
- Import organization: stdlib → 3rd party → local

## Module Responsibilities
### src/tts/ - Text-to-Speech
### src/stt/ - Speech-to-Text
### src/extraction/ - Web content extraction
### src/session/ - Playback session management

## Testing Patterns
- Unit tests: Mock external dependencies (audio I/O, network)
- Integration tests: End-to-end workflows (URL → audio, voice → text)
- Fixtures: Reusable test data (audio samples, HTML fixtures)

## Common Patterns
[Code examples, antipatterns to avoid]
```

## 5. Documentation Best Practices Research

### Architecture Documentation (ARCHITECTURE.md)

**Structure**:

1. **High-Level Overview**: System purpose, target users, key capabilities
2. **Module Diagram**: Visual representation of component relationships
3. **Data Flow**: 
   - TTS workflow: URL → fetch → extract → synthesize → play
   - STT workflow: mic → record → transcribe → output
4. **Technology Stack**: Python 3.13, key dependencies with versions
5. **Design Decisions**: Why certain libraries/patterns were chosen

### README Overhaul Strategy

**New Structure** (user-focused):

1. **Hero Section**: Logo, tagline, key features (30-second scan)
2. **What It Does**: 2-3 paragraph explanation with examples
3. **Installation**: 
   - PyPI installation (pip/uv)
   - Standalone .exe download
   - Prerequisites (Windows 11, Python 3.13+)
4. **Quick Start**: 
   - TTS example (read URL)
   - STT example (transcribe voice)
5. **Usage**: 
   - TTS commands (read, session management)
   - STT commands (transcribe, output options)
6. **Troubleshooting**: Common issues and solutions
7. **Contributing**: Link to CONTRIBUTING.md (brief)
8. **License**: MIT

**Remove/Minimize**:
- Developer setup details (move to CONTRIBUTING.md)
- Technical architecture (move to ARCHITECTURE.md)
- Build instructions (move to BUILD.md)

## 6. Integration Points

### Existing Codebase Integration

**Shared Infrastructure** (to be reused by STT):

1. **CLI Framework**: `src/main.py` - Add STT subcommands alongside existing TTS commands
2. **Error Handling**: `src/utils/errors.py` - Add STTError hierarchy
3. **Logging**: `src/utils/logging.py` - Reuse existing setup_logging()
4. **UI Utilities**: `src/ui/` - Reuse print_status/print_error for STT feedback
5. **Configuration**: `src/config.py` - Add STT model paths, audio settings

**New STT Module** (`src/stt/`):

- **Independent**: Minimal coupling to TTS module
- **Testable**: Pure functions, dependency injection for audio I/O
- **Documented**: Docstrings following existing patterns

## 7. Performance Considerations

### STT Latency Breakdown

| Phase | Target | Strategy |
|-------|--------|----------|
| Microphone detection | <500ms | Cache device list, lazy initialization |
| Recording start | <1s | Pre-allocate buffers, immediate feedback |
| Silence detection | Real-time | RMS calculation in callback (100ms chunks) |
| Transcription | <10s | Use medium.en model, run on CPU (GPU optional) |
| Output display | <100ms | Stream to stdout, async file write |

### Model Loading Optimization

- **Lazy loading**: Load Whisper model only when STT command invoked (not on CLI startup)
- **Caching**: Keep model in memory for multiple transcriptions in same session
- **Download management**: Auto-download model on first use, show progress

## 8. Testing Strategy

### STT Testing Approach

**Unit Tests** (src/stt/):
- **Mock audio I/O**: Use pytest monkeypatch for sounddevice.InputStream
- **Fixture audio**: Pre-recorded WAV files for consistent test data
- **Edge cases**: Empty audio, noise only, very long recordings

**Integration Tests**:
- **End-to-end**: Record → transcribe → verify output (use known audio samples)
- **CLI**: Invoke via subprocess, capture stdout/stderr
- **Error scenarios**: No microphone, permission denied, model missing

### Documentation Testing

- **README accuracy**: Verify all commands work as documented
- **Link validation**: All internal/external links resolve correctly
- **Code examples**: All code snippets are runnable and produce expected output

## Research Conclusion

All NEEDS CLARIFICATION items resolved:

1. ✅ **STT Library**: faster-whisper (medium.en model)
2. ✅ **Audio Library**: sounddevice + numpy
3. ✅ **Project Name**: vox (concise, voice-focused, available on PyPI/GitHub)
4. ✅ **Documentation Structure**: Both `.agents` (JSON) and `claude.md` (Markdown)
5. ✅ **Best Practices**: ARCHITECTURE.md + README overhaul strategy defined
6. ✅ **Integration Points**: Reuse existing CLI/error/logging infrastructure
7. ✅ **Performance**: Latency targets and optimization strategies defined
8. ✅ **Testing**: Mock-based unit tests + fixture-based integration tests

**Ready for Phase 1**: Data model and contract definitions can proceed with research decisions applied.
