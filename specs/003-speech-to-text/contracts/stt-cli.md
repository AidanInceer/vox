# STT CLI Command Contract

**Feature**: Speech-to-Text Integration  
**Date**: January 18, 2026  
**Purpose**: Define CLI interface for voice recording and transcription

## Command: `transcribe`

### Synopsis

```bash
[app_name] transcribe [OPTIONS]
```

### Description

Records audio from the system microphone and transcribes it to text using an offline speech-to-text engine.

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | PATH | stdout | Save transcription to file |
| `--format` | `-f` | TEXT | "text" | Output format: "text" or "json" |
| `--device` | `-d` | INT | default | Microphone device ID (use `list-devices` to see options) |
| `--model` | `-m` | TEXT | "medium.en" | Whisper model size: tiny.en, base.en, small.en, medium.en, large-v2 |
| `--language` | `-l` | TEXT | "en" | Language code (ISO 639-1) |
| `--silence-duration` | | FLOAT | 5.0 | Seconds of silence before auto-stop |
| `--no-silence-detection` | | FLAG | False | Disable auto-stop on silence |
| `--max-duration` | | INT | 600 | Maximum recording duration in seconds (10 minutes) |
| `--help` | `-h` | FLAG | - | Show help message |

### Examples

```bash
# Basic transcription (records until silence or Enter key)
[app_name] transcribe

# Save transcription to file
[app_name] transcribe --output transcript.txt

# Use JSON output format with metadata
[app_name] transcribe --format json --output result.json

# Specify microphone device
[app_name] transcribe --device 2

# Use smaller model for faster processing
[app_name] transcribe --model base.en

# Custom silence detection (3 seconds)
[app_name] transcribe --silence-duration 3.0

# Disable auto-stop on silence (manual stop only)
[app_name] transcribe --no-silence-detection
```

### Behavior

#### Recording Phase

1. **Initialization** (< 1 second):
   - Detect available microphones
   - Select device (default or specified by --device)
   - Initialize audio stream (16kHz, mono, 16-bit PCM)
   - Display status: `[*] Initializing microphone...`

2. **Recording** (user-controlled):
   - Display: `[*] Recording... (Press Enter to stop or wait for silence)`
   - Capture audio in real-time
   - If silence detection enabled:
     - Monitor RMS amplitude
     - Auto-stop after `--silence-duration` seconds of silence
   - Manual stop: Press Enter or Ctrl+C
   - Display: `[*] Recorded X.X seconds`

3. **Termination Conditions**:
   - Enter key pressed
   - Ctrl+C signal
   - Silence detected (if enabled)
   - Maximum duration reached (--max-duration)

#### Transcription Phase

1. **Model Loading** (first time only, ~2-5 seconds):
   - Download model if not cached (show progress bar)
   - Load model into memory
   - Display: `[*] Loading speech-to-text model...`

2. **Processing** (< 10 seconds for typical recording):
   - Transcribe audio using faster-whisper
   - Display: `[*] Transcribing audio...`

3. **Output**:
   - **Text format** (default):
     ```
     [OK] Transcription complete
     
     This is the transcribed text from your recording.
     ```
   
   - **JSON format** (--format json):
     ```json
     {
       "text": "This is the transcribed text from your recording.",
       "confidence": 0.95,
       "language": "en",
       "duration": 5.2,
       "processing_time": 3.1,
       "model_version": "whisper-medium.en",
       "timestamp": "2026-01-18T10:30:45"
     }
     ```

### Exit Codes

| Code | Meaning | Scenario |
|------|---------|----------|
| 0 | Success | Transcription completed and output successfully |
| 1 | General error | Unexpected error during execution |
| 2 | Microphone error | No microphone detected or access denied |
| 3 | Recording error | Failed to capture audio |
| 4 | Transcription error | STT processing failed |
| 5 | Model error | Failed to load or download model |
| 130 | User interrupt | Ctrl+C pressed before recording started |

### Error Messages

```bash
# No microphone detected
[ERROR] No microphone detected. Please connect a microphone and try again.
Troubleshooting: https://[docs_url]/microphone-setup

# Permission denied
[ERROR] Microphone access denied. Please grant microphone permissions in Windows Settings.
Open: Settings > Privacy > Microphone > Allow apps to access your microphone

# Model download failed
[ERROR] Failed to download model 'medium.en'. Check your internet connection.
Retry: [app_name] transcribe --model medium.en

# Recording too short
[ERROR] Recording too short (< 0.1 seconds). Please try again.

# Transcription failed
[ERROR] Speech recognition failed. Possible causes:
  - Audio quality too low
  - Background noise too high
  - No speech detected in recording
```

### Output File Behavior

- If `--output` file exists: **Overwrite** without prompt
- If directory doesn't exist: Create parent directories
- If write fails: Print error to stderr, exit code 1

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Initialization | < 1s | Device detection + stream setup |
| Recording start | < 1s | From command invocation to first audio capture |
| Silence detection | Real-time | 100ms chunks, < 50ms latency |
| Transcription | < 10s | For typical 10-second recording with medium.en |
| Model loading (cached) | < 2s | Model already downloaded |
| Model loading (first time) | < 60s | Downloading ~1.5GB model |

## Command: `list-devices`

### Synopsis

```bash
[app_name] list-devices
```

### Description

Lists all available microphone devices with their IDs and names.

### Output

```
Available Microphone Devices:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ID  Name                        Channels  Sample Rate  Default
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  0   Microphone (Realtek Audio)  2         48000 Hz     ✓
  1   USB Microphone              1         44100 Hz
  2   Headset Microphone          1         48000 Hz
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use device ID with: [app_name] transcribe --device <ID>
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (at least one device found) |
| 2 | No devices found |

## Test Scenarios

### Unit Tests

```python
def test_transcribe_with_output_file():
    """Test transcription saves to specified file."""
    # Given: Mock audio recording and STT engine
    # When: Run transcribe --output test.txt
    # Then: File created with transcribed text

def test_transcribe_json_format():
    """Test JSON output format includes all metadata."""
    # Given: Mock transcription result
    # When: Run transcribe --format json
    # Then: Output is valid JSON with text, confidence, duration, etc.

def test_transcribe_custom_model():
    """Test specifying different Whisper model."""
    # Given: Mock model loader
    # When: Run transcribe --model tiny.en
    # Then: tiny.en model is loaded and used

def test_transcribe_no_microphone():
    """Test error handling when no microphone available."""
    # Given: No audio devices
    # When: Run transcribe
    # Then: Exit code 2, error message displayed

def test_transcribe_user_interrupt():
    """Test Ctrl+C during recording."""
    # Given: Recording in progress
    # When: Ctrl+C pressed
    # Then: Clean shutdown, partial recording discarded, exit code 130
```

### Integration Tests

```python
def test_transcribe_end_to_end():
    """Test full workflow with fixture audio file."""
    # Given: Pre-recorded audio file with known content
    # When: Mock microphone returns fixture audio
    # Then: Transcription matches expected text (±5% word error)

def test_transcribe_silence_detection():
    """Test auto-stop on silence."""
    # Given: Audio with 6 seconds of silence at end
    # When: Run transcribe --silence-duration 5
    # Then: Recording stops after ~5 seconds, text transcribed

def test_list_devices_shows_available():
    """Test device listing shows real devices."""
    # Given: System with microphones
    # When: Run list-devices
    # Then: At least one device listed with valid metadata
```

## Contract Summary

- **New Commands**: 2 (`transcribe`, `list-devices`)
- **Required Options**: None (all have defaults)
- **Output Formats**: 2 (text, JSON)
- **Exit Codes**: 6 distinct codes for error handling
- **Performance Targets**: 5 metrics defined
- **Test Coverage**: 8 scenarios (4 unit, 4 integration)

**Status**: ✅ STT CLI contract complete
