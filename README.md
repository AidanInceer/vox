<div align="center">
  <img src="imgs/logo.png" alt="PageReader Logo" width="200" />
</div>

# PageReader

A Windows desktop application that reads any browser tab or webpage aloud using open-source neural text-to-speech.

## What It Does

PageReader extracts text from browser tabs (Chrome, Edge, Firefox, etc.) or web URLs and reads it aloud using high-quality, offline TTS. No need to switch tabs or bring windows to the foreground.

**Key Features:**
- 🎯 Read any browser tab without switching focus
- 🌐 Supports Chrome, Edge, Firefox, Opera, Brave
- 🔗 Read from URLs or local HTML files
- 🎙️ Open-source Piper TTS (fully offline, no API keys)
- 🎮 Interactive playback controls (pause/resume/seek with keyboard shortcuts)
- 💾 Save and resume reading sessions with custom names
- ⚡ Streaming text-to-speech with chunking for faster feedback (<3s to first audio)

## Installation

### Option 1: Using pip

```bash
pip install pagereader
```

### Option 2: Using uv (recommended - faster)

```bash
# Install uv first
pip install uv

# Install pagereader
uv pip install pagereader
```

### Option 3: Standalone Executable

Download `pagereader.exe` from the [Releases](https://github.com/AidanInceer/PageReader/releases) page. No Python installation required.

### Requirements

- Windows 11
- Python 3.13+ (not needed for standalone executable)

## Usage

### Basic Commands

```bash
# Read from a URL
pagereader read --url https://example.com

# Read with custom voice and speed
pagereader read --url https://example.com --voice en_US-libritts-high --speed 1.5

# Save audio to file instead of playing
pagereader read --url https://example.com --output audio.wav

# Read from a local HTML file
pagereader read --file article.html
```

### Session Management

Save reading sessions and resume later from where you left off:

```bash
# Save a reading session with a custom name
pagereader read --url https://example.com/long-article --save-session my-article

# List all saved sessions
pagereader list-sessions

# Resume a saved session
pagereader resume my-article

# Delete a session
pagereader delete-session my-article
```

Session features:
- 📝 Save with custom names (alphanumeric, hyphens, underscores)
- 📊 View progress (character position and percentage complete)
- ⏮️ Resume from exact position where you quit
- 🗑️ Delete sessions you no longer need
- 🔍 List all sessions with timestamps and URLs

### Interactive Playback Controls

During audio playback, use keyboard shortcuts to control playback:

| Key | Action |
|-----|--------|
| `SPACE` | Pause/Resume playback |
| `→` (Right Arrow) | Seek forward 5 seconds |
| `←` (Left Arrow) | Seek backward 5 seconds |
| `Q` | Quit playback gracefully |

**Note**: Speed adjustment must be set before playback starts using the `--speed` flag (e.g., `--speed 1.5`). Runtime speed control during playback is not supported.

### Streaming Playback Performance

For longer articles (>200 words), PageReader uses intelligent chunking:
- ✅ First audio chunk synthesized in <3 seconds
- ✅ Background synthesis of remaining chunks while playing
- ✅ Seamless transitions between chunks (<50ms gaps)
- ✅ Memory-efficient buffering (max 10 chunks in memory)

Example with a 5,000-word article:
```bash
pagereader read --url https://example.com/long-article
# First audio starts playing within 3 seconds
# Remaining chunks synthesize in background
```

## Development

### Project Structure

```
PageReader/
├── src/                   # Source code
│   ├── browser/           # Browser tab detection
│   ├── extraction/        # Text extraction from HTML
│   ├── tts/               # Text-to-speech synthesis
│   ├── session/           # Session management
│   └── ui/                # CLI interface
├── tests/                 # Test suite
└── pyproject.toml         # Dependencies and configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD approach)
4. Implement your changes
5. Run tests: `pytest tests/`
6. Submit a pull request

See [CONSTITUTION.md](CONSTITUTION.md) for development standards.

## License

MIT License - see LICENSE file for details.

## Links

- **Repository**: https://github.com/AidanInceer/PageReader
- **Issues**: https://github.com/AidanInceer/PageReader/issues

- [ ] Content summarization
- [ ] Bookmark integration
- [ ] Reading history

### v2.0 (Future)
- [ ] macOS and Linux support
- [ ] Web server mode for remote access
- [ ] Mobile app companion
- [ ] Voice profile customization

## Contributing

Contributions are welcome! Please follow the development workflow above and ensure:
1. All new code is covered by tests (≥80% coverage required)
2. Tests are written before implementation (Test-First Development)
3. Code passes ruff linting checks
4. All GitHub Actions checks pass on your PR
5. **Follow Conventional Commits** for all commit messages (see below)

### Commit Message Policy

This project uses [Conventional Commits](https://www.conventionalcommits.org/) to ensure consistent, machine-readable commit history. All commits must follow this format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Commit Types**:
- `feat`: New feature for the user
- `fix`: Bug fix for the user
- `docs`: Documentation-only changes
- `style`: Code style changes (formatting, missing semi-colons, etc.)
- `refactor`: Code refactoring without changing behavior
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `build`: Changes to build system or dependencies
- `ci`: Changes to CI/CD configuration files
- `chore`: Other changes that don't modify src or test files
- `revert`: Reverts a previous commit

**Examples**:
```bash
feat(tts): add speed adjustment controls
fix(extraction): handle malformed HTML without crashing
docs(readme): update installation instructions
test(browser): add unit tests for tab detection
```

**Using Commitizen**:
This project includes [Commitizen](https://commitizen-tools.github.io/commitizen/) to help you create properly formatted commits:

```bash
# Interactive commit (prompts you for type, scope, description, etc.)
cz commit

# Or use the shorthand
cz c

# Bump version and generate changelog (maintainers only)
cz bump
```

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open a GitHub issue or visit the project repository.

---

**Built with ❤️ using open-source technologies**

This project is currently in the specification and design phase as part of the Speckit learning process. Check back for updates as development progresses.

## License

This is a personal learning project.
