<div align="center">
  <img src="imgs/logo.png" alt="vox Logo" width="200" />
</div>

# vox

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.0.0-orange.svg)](https://github.com/AidanInceer/vox/releases)

**Transform text to speech and speech to text—your voice-powered productivity tool for Windows**

Previously known as *vox* (versions ≤2.0.0)

---

## What is vox?

**vox** is a Windows desktop application that bridges the gap between text and audio. Read web articles aloud using high-quality neural text-to-speech, or transcribe your voice to text with industry-leading speech recognition—all offline, no API keys required.

**Perfect for:**
- 📖 Listening to articles while multitasking
- 🎙️ Capturing meeting notes by voice
- ♿ Accessibility needs (screen reading, voice input)
- 📝 Content creation and transcription
- 🌍 Learning languages through audio

**Core Features:**
- **Text-to-Speech (TTS)**: Read any browser tab or web URL aloud
  - 🎯 Read without switching windows
  - 🌐 Chrome, Edge, Firefox, Opera, Brave support
  - 🎮 Interactive playback controls (pause/resume/seek)
  - 💾 Save and resume reading sessions
  
- **Speech-to-Text (STT)**: Transcribe your voice to text
  - 🎤 High-accuracy voice transcription (95%+ for clear speech)
  - 🔇 Auto-stop on silence (5 seconds)
  - 💬 Instant terminal output or save to file
  - 🔒 Fully offline (no cloud services)

- **Desktop App with Hotkey Voice Input** (NEW): Quick voice-to-text anywhere
  - ⌨️ Global hotkey (Ctrl+Alt+Space) for instant voice input
  - 📋 Automatic paste at cursor position
  - 🔴 Visual recording indicator
  - 📜 Transcription history with copy support
  - ⚙️ Customizable hotkey configuration

**All processing happens locally**—your voice and content never leave your machine


---

## Installation

### Requirements

- **Windows 11**
- **Python 3.13+** (not needed for standalone executable)

### Option 1: Install from PyPI (Recommended)

```bash
pip install vox
```

### Option 2: Install with uv (Faster)

```bash
# Install uv first
pip install uv

# Install vox with uv
uv pip install vox
```

### Option 3: Standalone Executable

Download `vox.exe` from the [Releases](https://github.com/AidanInceer/vox/releases) page.  
No Python installation required—just run the executable.

### Verify Installation

```bash
# Check version
vox --version

# Display help
vox --help
```

---

## Usage

### Text-to-Speech: Read Web Content Aloud

#### Read a Web Page

```bash
# Read from any URL
vox read --url https://example.com/article

# Read with custom voice and speed
vox read --url https://example.com --voice en_US-libritts-high --speed 1.5

# Save audio to file instead of playing
vox read --url https://example.com --output article.wav
```

#### Read Local HTML Files

```bash
vox read --file article.html
```

#### Read Active Browser Tab

```bash
# Reads the currently focused tab (Chrome, Edge, Firefox, etc.)
vox read --active-tab
```

#### Interactive Playback Controls

During playback, use these keyboard shortcuts:

| Key | Action |
|-----|--------|
| `SPACE` | Pause/Resume playback |
| `→` (Right Arrow) | Seek forward 5 seconds |
| `←` (Left Arrow) | Seek backward 5 seconds |
| `Q` | Quit playback |

**Note**: Speed adjustment (e.g., `--speed 1.5`) must be set before playback starts.

#### Session Management

Save long reading sessions and resume later:

```bash
# Save a reading session
vox read --url https://example.com/long-article --save-session my-article

# List all saved sessions
vox list-sessions

# Resume a saved session (continues from where you left off)
vox resume my-article

# Delete a session
vox delete-session my-article
```

**Session features:**
- ⏮️ Resume from exact character position
- 📊 View progress (percentage complete)
- 📝 Custom session names (alphanumeric, hyphens, underscores)
- 🔍 List all sessions with timestamps and URLs

---

### Speech-to-Text: Transcribe Your Voice

#### Basic Transcription

```bash
# Start recording, speak, press Enter to stop
vox transcribe
# Transcription appears in terminal
```

#### Save Transcription to File

```bash
# Save to a text file
vox transcribe --output meeting-notes.txt
```

#### Use Different Model Sizes

```bash
# Faster but less accurate
vox transcribe --model small

# Slower but more accurate (default)
vox transcribe --model medium

# Maximum accuracy
vox transcribe --model large
```

#### Recording Controls

- **Press Enter** to stop recording and start transcription
- **Auto-stop**: Recording stops automatically after 5 seconds of silence
- **Real-time feedback**: "Recording..." indicator shows when mic is active

**Model Sizes & Performance** (approximate times for 10-second audio):

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | 75 MB | ~1s | ~85% |
| `small` | 488 MB | ~3s | ~93% |
| `medium` (default) | 1.5 GB | ~4s | ~95% |
| `large` | 3 GB | ~8s | ~97% |

---

### Desktop App: Hotkey Voice Input (NEW)

Launch the vox desktop application for quick voice-to-text input anywhere on your system.

#### Launch the Desktop App

```bash
# Start the desktop application
vox gui

# Start minimized to tray
vox gui --minimized
```

#### Quick Start Workflow

1. **Launch**: Run `vox gui` to open the desktop application
2. **Press Hotkey**: Press `Ctrl+Alt+Space` (default) to start recording
3. **Speak**: Say your text while the recording indicator appears
4. **Press Hotkey Again**: Press the hotkey to stop recording
5. **Auto-Paste**: Transcribed text is automatically pasted at your cursor position

#### Visual Recording Indicator

A small translucent pill appears above your taskbar showing the current state:

| Color | State | Meaning |
|-------|-------|---------|
| 🔴 Red (pulsing) | Recording | Microphone is active, speak now |
| 🔵 Blue (spinning) | Processing | Transcribing your speech |
| 🟢 Green (checkmark) | Success | Text pasted successfully |
| 🟠 Orange (warning) | Error | Something went wrong |

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Alt+Space` | Toggle recording (default hotkey) |
| `Escape` | Cancel current recording without transcribing |

#### Settings Tab

Customize the application from the Settings tab:

- **Hotkey Configuration**: Click "Capture" and press your preferred key combination
- **Restore Clipboard**: Toggle whether to restore your original clipboard content after pasting
- **Settings are saved** automatically and persist across restarts

#### History Tab

View and manage your transcription history:

- **View Past Transcriptions**: See all your transcribed text with timestamps
- **Copy to Clipboard**: Click the copy button next to any transcription
- **Word Count**: Each entry shows the number of words transcribed

#### Use Case: Voice Input in Any Application

The desktop app works with any text field or application:

```
Example Workflow:
1. Open Notepad, Word, browser, email, etc.
2. Click where you want to type
3. Press Ctrl+Alt+Space
4. Speak: "Hello, this is a test message"
5. Press Ctrl+Alt+Space again
6. Your spoken text appears at the cursor!
```

---

## Configuration

### Config File Location

Configuration is stored at:
```
%APPDATA%\vox\config.json
```

### Microphone Setup

**Windows Microphone Permissions:**

1. Open **Settings** → **Privacy & Security** → **Microphone**
2. Enable "Let apps access your microphone"
3. Verify your microphone is set as the **default device**:
   - Right-click speaker icon in taskbar → **Sound settings**
   - Under **Input**, select your preferred microphone
   - Click **Test your microphone** to verify it works

**vox uses the system default microphone**—configure it in Windows Sound settings before running `vox transcribe`.

---

## Troubleshooting

### Speech-to-Text Issues

#### "No microphone detected"

**Problem**: System cannot find any audio input devices  
**Solution**:
1. Check physical microphone connection (USB or 3.5mm jack)
2. Open **Device Manager** → **Audio inputs and outputs** → Verify microphone is listed and enabled
3. Restart the application
4. Try `vox transcribe` again

#### "Microphone permission denied"

**Problem**: Windows privacy settings block microphone access  
**Solution**:
1. Open **Settings** → **Privacy & Security** → **Microphone**
2. Enable "Let apps access your microphone"
3. Enable "Let desktop apps access your microphone"
4. Restart terminal/application
5. Run `vox transcribe` again

#### "Microphone in use by another application"

**Problem**: Another program (Zoom, Discord, etc.) is using the microphone  
**Solution**:
1. Close other applications using the microphone
2. Check Windows Task Manager for background apps (Teams, OBS, etc.)
3. Restart vox after closing conflicting apps

#### "Low transcription accuracy"

**Problem**: Transcription contains many errors or nonsense words  
**Solutions**:
1. **Reduce background noise**: Record in a quiet environment
2. **Speak clearly**: Enunciate words, avoid mumbling
3. **Check microphone quality**: Test with Windows Voice Recorder
4. **Use a larger model**: `vox transcribe --model large` (slower but more accurate)
5. **Adjust microphone position**: Speak 6-12 inches from mic
6. **Increase microphone volume**: Windows Sound settings → Input device properties

### Text-to-Speech Issues

#### "TTS voice sounds robotic"

**Problem**: Default voice lacks natural intonation  
**Solution**:
1. Try a different voice model: `vox read --url <url> --voice en_US-libritts-high`
2. Adjust speed: `vox read --url <url> --speed 1.2` (slightly faster often sounds more natural)
3. Check available voices: See [Piper TTS models](https://github.com/rhasspy/piper)

### Installation Issues

#### "Installation fails with dependency errors"

**Problem**: pip cannot install required packages  
**Solutions**:
1. **Upgrade pip**: `pip install --upgrade pip`
2. **Use uv**: `pip install uv && uv pip install vox` (faster, better resolver)
3. **Check Python version**: `python --version` (must be 3.13+)
4. **Install in virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install vox
   ```

---

## Advanced Configuration

### Customize TTS Settings (config.json)

Example `%APPDATA%\vox\config.json`:

```json
{
  "tts": {
    "voice": "en_US-libritts-high",
    "speed": 1.3,
    "output_device": "default"
  },
  "stt": {
    "model": "medium",
    "language": "en",
    "silence_duration": 5.0
  }
}
```

### STT Model Cache

Downloaded Whisper models are cached at:
```
%APPDATA%\vox\models\
```

Delete this folder to re-download models or free up space (~1.5-3GB per model).

---

## Contributing

Contributions are welcome! For detailed development guidelines, see [claude.md](claude.md).

**Quick checklist:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Write tests first (TDD approach, ≥80% coverage required)
4. Implement your changes
5. Run tests: `pytest tests/`
6. Run linting: `ruff check . && ruff format .`
7. Submit a pull request

**Commit Message Policy**: Use [Conventional Commits](https://www.conventionalcommits.org/)

Example:
```bash
feat(stt): add support for Spanish transcription
fix(tts): resolve playback crackling on fast speech
docs(readme): update installation instructions
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Credits

**vox** is built with these outstanding open-source projects:

- **[Piper TTS](https://github.com/rhasspy/piper)** - High-quality neural text-to-speech
- **[Whisper](https://github.com/openai/whisper)** - State-of-the-art speech recognition by OpenAI
- **[faster-whisper](https://github.com/guillaumekln/faster-whisper)** - Optimized Whisper implementation

---

## Links

- **Repository**: https://github.com/AidanInceer/vox
- **Issues**: https://github.com/AidanInceer/vox/issues
- **Releases**: https://github.com/AidanInceer/vox/releases

---

**Built with ❤️ using open-source technologies**
