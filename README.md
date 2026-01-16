# PageReader: Desktop Text-to-Speech Browser Integration

## Overview

**PageReader** is a Windows desktop application that reads any browser tab aloud using open-source neural text-to-speech (TTS). Point to any browser tab—even if it's in the background—and PageReader will extract the text and read it back to you with high-quality, natural-sounding speech.

### Core Features

- 🎯 **Read Any Browser Tab** - No need to switch focus or bring tabs to foreground
- 🌐 **Multiple Browsers** - Works with Chrome, Edge, Firefox, Opera, Brave
- 🔗 **URL & File Input** - Read directly from URLs or local HTML files
- 🎙️ **Open Source TTS** - Powered by Piper neural TTS engine (fully offline, no API keys)
- ⚙️ **Playback Controls** - Pause, resume, adjust speed
- 💾 **Session Persistence** - Save and resume reading sessions
- 🔧 **Configurable** - Customize extraction settings, voice selection, speech speed

## Quick Start

### Prerequisites

- Python 3.13+
- Windows 11
- pip or [uv](https://astral.sh/blog/uv/)

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/PageReader.git
cd PageReader

# Install dependencies (using uv)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### First Run

```bash
# List all open browser tabs
python -m src.main tabs

# Read a specific tab by ID
python -m src.main read --tab 12345

# Read from a URL
python -m src.main read --url https://example.com

# Read a local file
python -m src.main read --file /path/to/page.html
```

## Development

### Project Structure

```
PageReader/
├── src/                      # Application source code
│   ├── browser/              # Browser tab detection
│   ├── extraction/           # Text extraction from pages/URLs
│   ├── tts/                  # Text-to-speech synthesis
│   ├── session/              # Session management
│   ├── ui/                   # CLI and UI components
│   ├── utils/                # Utilities (logging, errors, etc.)
│   └── config.py             # Configuration constants
│
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests (individual components)
│   ├── integration/          # Integration tests (component interactions)
│   ├── contract/             # Contract tests (API specifications)
│   └── performance/          # Performance benchmarks
│
├── docs/                     # Documentation
├── pyproject.toml            # Project configuration & dependencies
├── pytest.ini                # Pytest configuration
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
└── .github/
    └── workflows/            # GitHub Actions CI/CD
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test suite
pytest tests/unit/             # Unit tests only
pytest tests/integration/      # Integration tests only

# Run with specific markers
pytest -m unit                 # Only unit-marked tests
pytest -m integration          # Only integration-marked tests

# Run with verbose output
pytest -v

# Run with detailed coverage report
pytest --cov=src --cov-report=html
```

### Code Quality

The project enforces code quality standards using:

- **ruff**: Fast Python linter and formatter (PEP 8 compliance)
- **pytest**: Testing framework with >80% coverage requirement
- **pre-commit hooks**: Automated formatting on every commit

#### Setting Up Pre-Commit Hooks

```bash
# Install pre-commit hooks (runs on every git commit)
pre-commit install

# Manually run pre-commit checks
pre-commit run --all-files

# Run ruff linting
ruff check src/

# Run ruff formatting
ruff format src/ tests/
```

#### CI/CD Pipeline

GitHub Actions automatically:
- Runs ruff linting on every PR
- Runs full test suite with coverage reporting
- Enforces ≥80% test coverage gate
- Requires all checks to pass before merge

Branch protection rules require:
- All GitHub Actions checks passing
- At least 1 code review approval

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Write tests first** (Test-First Development)
   ```bash
   # Create test file in tests/ with failing test
   vim tests/unit/test_new_feature.py
   pytest tests/unit/test_new_feature.py  # Should FAIL
   ```

3. **Implement feature**
   ```bash
   # Write implementation to make tests pass
   vim src/module/new_feature.py
   pytest tests/unit/test_new_feature.py  # Should PASS
   ```

4. **Verify code quality**
   ```bash
   pytest --cov=src              # Coverage check (≥80% required)
   ruff check src/               # Linting check
   ruff format src/ tests/       # Auto-formatting
   ```

5. **Pre-commit hooks** (automatic on commit)
   ```bash
   git add .
   git commit -m "feat: add new feature"  # Pre-commit runs ruff format
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/new-feature
   ```

7. **GitHub Actions validates**
   - Ruff lint check
   - Full test suite with coverage
   - Coverage gate enforcement
   - All must pass before merge

## Architecture & Design

### Core Modules

- **browser/**: Windows API integration to detect and enumerate browser tabs across all installed browsers
- **extraction/**: HTML parsing with BeautifulSoup and text extraction with reading order preservation
- **tts/**: Piper neural TTS engine integration for offline speech synthesis
- **session/**: SQLite-based persistence for reading sessions and playback position
- **ui/**: Command-line interface for user interaction
- **utils/**: Logging, error handling, caching, and validation utilities

### Design Principles

The implementation follows PageReader's Constitution:

1. **Test-First Development**: All code is tested before being written. Tests are comprehensive and cover success paths and edge cases.
2. **Text-Based I/O**: Core operations work with text streams. Speech synthesis is layered on top of text operations.
3. **Clear API Contracts**: Each module exports well-defined interfaces with clear input/output specifications.
4. **Semantic Versioning**: Version numbers follow strict semantic versioning (MAJOR.MINOR.PATCH).
5. **Code Quality**: SOLID principles, DRY (Don't Repeat Yourself), KISS (Keep It Simple Stupid) applied throughout.

### Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---|
| Language | Python 3.13 | Cross-platform, rich ecosystem for accessibility tools |
| TTS | Piper (open-source) | Free, offline-capable, neural quality speech |
| HTML Parsing | BeautifulSoup4 | Robust DOM parsing, handles malformed HTML |
| HTTP Client | requests | Simple, reliable URL fetching with good error handling |
| Browser Detection | pywinauto | Windows-native process/window enumeration |
| Testing | pytest | Industry-standard, excellent coverage reporting |
| Linting | ruff | Fast, all-in-one Python linter+formatter |
| CI/CD | GitHub Actions | Native GitHub integration, free for open source |

## Usage Examples

### Reading Browser Tabs

```bash
# List all open tabs across all browsers
pagereader tabs

# Read a specific tab (use tab ID from list)
pagereader read --tab abc123

# Read the currently active tab
pagereader read --active
```

### Reading Web Pages

```bash
# Read from a URL
pagereader read --url https://news.ycombinator.com

# Read from a local file
pagereader read --file ~/Documents/article.html

# Read from URL and save session
pagereader read --url https://example.com --save-session my-article
```

### Session Management

```bash
# List saved sessions
pagereader sessions

# Resume a saved session
pagereader resume my-article

# Delete a session
pagereader delete-session my-article
```

### Playback Controls

During playback, use keyboard shortcuts:
- `SPACE` - Pause/Resume
- `<` / `>` - Decrease/Increase speed
- `+` / `-` - Increase/Decrease volume
- `N` - Next section
- `P` - Previous section
- `Q` - Quit

## Success Metrics (v1.0 MVP)

- ✅ Extract text from any browser tab in <3 seconds without focus switch
- ✅ Achieve ≥95% text extraction accuracy on English content
- ✅ Generate natural-sounding speech with ≥90% user satisfaction
- ✅ Handle pages up to 100 MB without performance degradation
- ✅ Resume saved sessions in <1 second
- ✅ Detect ≥95% of open browser tabs across all major browsers
- ✅ Maintain <300 MB memory footprint during operation
- ✅ Support speed adjustment (0.5x - 2.0x) with real-time feedback
- ✅ Recover 100% of saved sessions across application restarts

## Roadmap

### v1.0 (Current MVP)
- [x] Read any browser tab without focus switch
- [x] Read from URLs and local files
- [x] Playback controls (pause/resume/speed)
- [x] Session persistence
- [ ] Tab picker UI

### v1.1 (Planned)
- [ ] Multiple language support
- [ ] PDF document reading
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
