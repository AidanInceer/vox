# PageReader Project Constitution

## Core Development Principles

1. **Test-First Development (TDD)**: Write tests before implementation. Minimum 80% coverage required.
2. **Text-Based I/O**: All core operations work with text streams (stdin/stdout/JSON).
3. **Clear API Contracts**: Every module has well-defined interfaces with Python type hints.
4. **Semantic Versioning**: Follow MAJOR.MINOR.PATCH versioning with commitizen automation.
5. **Code Quality**: Adhere to SOLID, DRY, KISS, YAGNI principles. Use ruff for linting/formatting.

## Commit Message Standards

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Test additions/modifications
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

## Python Environment Setup with UV

**For Agents/Contributors**: To set up the PageReader development environment using [uv](https://github.com/astral-sh/uv):

### Prerequisites
- Python 3.13+
- Windows 11

### Setup Steps

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/AidanInceer/PageReader.git
   cd PageReader
   ```

3. **Create a virtual environment and install dependencies**:
   ```bash
   # Create a virtual environment
   uv venv
   
   # Activate the virtual environment
   # On Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # On Windows CMD:
   .venv\Scripts\activate.bat
   
   # Install all dependencies (including dev dependencies)
   uv pip install -e ".[dev]"
   ```

4. **Verify installation**:
   ```bash
   # Check Python version
   python --version  # Should be 3.13+
   
   # Run tests to verify setup
   pytest tests/
   
   # Check that the CLI works
   pagereader --version
   ```

5. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Key Dependencies
- **Core**: Pillow, NumPy, Pandas, requests, beautifulsoup4, piper-tts, pywinauto, colorama
- **Dev/Test**: pytest, pytest-cov, ruff, pre-commit, commitizen, pyinstaller

### Quick Command Reference
```bash
# Update all dependencies
uv pip install --upgrade -e ".[dev]"

# Add a new dependency
uv pip install <package-name>

# Run linting
ruff check .

# Run formatting
ruff format .

# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Development Workflow

1. **Plan**: Define feature/task clearly
2. **Test**: Write tests first (TDD)
3. **Implement**: Write production code
4. **Verify**: Run tests and linting
5. **Commit**: Use conventional commit format
6. **Review**: Submit PR with passing CI

## Technology Stack

- **Language**: Python 3.13+
- **TTS Engine**: Piper (open-source neural TTS)
- **HTML Parsing**: BeautifulSoup4
- **Browser Detection**: pywinauto
- **Testing**: pytest with coverage
- **Linting**: ruff
- **CI/CD**: GitHub Actions

---

**Version**: 1.0.0 | **Last Updated**: 2026-01-17
