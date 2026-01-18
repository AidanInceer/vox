# Build Instructions

This document provides instructions for building vox from source, including creating the standalone Windows executable.

---

## Prerequisites

### For Development
- Python 3.13 or higher
- pip package manager
- Git (for cloning the repository)

### For Building Standalone Executable
- All development prerequisites above
- PyInstaller 6.0 or higher (included in dev dependencies)
- Windows 11 (for building Windows executable)

---

## Setting Up Development Environment

### 1. Clone the Repository
```bash
git clone https://github.com/AidanInceer/vox.git
cd vox
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv .venv

# Activate on Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Activate on Windows Command Prompt
.venv\Scripts\activate.bat

# Activate on Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install all dependencies including dev tools
pip install -e ".[dev]"

# Or install only runtime dependencies
pip install -e .
```

### 4. Verify Installation
```bash
# Test the CLI
python -m src.main --help

# Or use the installed command
vox --help

# Run a simple test
vox read --url https://example.com
```

---

## Building the Standalone Executable

### Option 1: Using the Build Script (Recommended)

The `build_exe.py` script automates the entire build process:

```bash
# Ensure you're in the project root directory
cd vox

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install PyInstaller if not already installed
pip install pyinstaller

# Run the build script
python build_exe.py
```

**Output**: `dist/vox.exe`

### Option 2: Manual PyInstaller Build

For advanced users who want more control:

```bash
pyinstaller src/main.py \
    --name=vox \
    --onefile \
    --console \
    --hidden-import=src \
    --hidden-import=src.browser \
    --hidden-import=src.extraction \
    --hidden-import=src.tts \
    --hidden-import=src.session \
    --hidden-import=src.utils \
    --collect-data=piper_tts \
    --exclude-module=pytest \
    --exclude-module=tests
```

### Build Output

After a successful build, you'll find:
- **dist/vox.exe**: The standalone executable (single file)
- **build/**: Temporary build files (can be deleted)

**Expected File Size**: ~100-300 MB (includes Python runtime, dependencies, and TTS models)

---

## Testing the Executable

### Basic Functionality Test
```powershell
# Display help
.\dist\vox.exe --help

# Test URL reading (use a lightweight page for quick test)
.\dist\vox.exe read --url https://example.com

# List available voices
.\dist\vox.exe list voices
```

### Verify No Python Required
To ensure the executable is truly standalone:
1. Copy `vox.exe` to a clean directory
2. Run it from a system without Python installed
3. Or temporarily rename your Python installation directory

### Performance Test
```powershell
# Measure startup time
Measure-Command { .\dist\vox.exe --help }

# Test with a real article
.\dist\vox.exe read --url https://en.wikipedia.org/wiki/Python_(programming_language)
```

---

## Troubleshooting Build Issues

### Issue: PyInstaller Not Found
```
ERROR: PyInstaller not found
```

**Solution**:
```bash
pip install pyinstaller
```

### Issue: Module Not Found During Build
```
ModuleNotFoundError: No module named 'src.something'
```

**Solution**: Add the missing module to the hidden imports in `build_exe.py`:
```python
"--hidden-import=src.something",
```

### Issue: Build Succeeds But Executable Crashes
```
Fatal error detected
```

**Solution**:
1. Run the executable from command line to see error messages
2. Check for missing data files or DLLs
3. Use PyInstaller's verbose mode:
   ```bash
   pyinstaller --log-level=DEBUG src/main.py ...
   ```

### Issue: Antivirus Blocks Executable
```
Windows Defender quarantined vox.exe
```

**Solution**:
- This is a false positive common with PyInstaller executables
- Add an exception in Windows Security settings
- Or obtain exe from official GitHub Releases page

### Issue: Executable Size Too Large
```
vox.exe is 500+ MB
```

**Solution**: The size is expected due to:
- Python runtime (~50 MB)
- NumPy/Pandas (~100 MB)
- Piper TTS models (~50-100 MB)
- Other dependencies

To reduce size:
- Use `--exclude-module` for unused packages
- Consider UPX compression (experimental):
  ```bash
  pyinstaller ... --upx-dir=/path/to/upx
  ```

---

## Advanced Build Configuration

### Custom Icon

1. Create or obtain a `.ico` file
2. Place it in `imgs/logo.ico`
3. Rebuild - the script will automatically include it

### Including Additional Data Files

Edit `build_exe.py` to add data files:
```python
options.extend([
    "--add-data", "path/to/data;destination/path",
])
```

### Multi-File Distribution

For a smaller initial download, use directory distribution:
```python
# In build_exe.py, change:
"--onefile",  # Remove this
# to:
"--onedir",   # Add this
```

This creates a folder with multiple files instead of one large executable.

---

## Continuous Integration Builds

The GitHub Actions workflow automatically builds the executable on:
- **Release tags** (e.g., `v1.0.0`)
- **Manual workflow dispatch**

### Triggering a Build via GitHub Actions

1. Go to **Actions** tab in GitHub repository
2. Select **Release** workflow
3. Click **Run workflow**
4. Choose branch and tag
5. Wait for build completion
6. Download artifact from release page

---

## Distribution Checklist

Before distributing the executable:

- [ ] Test on clean Windows 11 system (no Python installed)
- [ ] Verify `--help` command works
- [ ] Test reading from URL
- [ ] Test reading from local file
- [ ] Verify audio playback works
- [ ] Check file size is reasonable (<500 MB)
- [ ] Run virus scan (VirusTotal)
- [ ] Create SHA256 checksum:
  ```powershell
  Get-FileHash .\dist\vox.exe -Algorithm SHA256
  ```
- [ ] Update release notes with checksum
- [ ] Test on different Windows versions (if possible)

---

## Build Automation

### Local Batch Script

Create `build.bat` for quick builds:
```batch
@echo off
echo Building vox executable...
.venv\Scripts\activate.bat
python build_exe.py
if %ERRORLEVEL% == 0 (
    echo Build successful!
    echo Location: dist\vox.exe
) else (
    echo Build failed!
)
pause
```

### PowerShell Script

Create `build.ps1`:
```powershell
Write-Host "Building vox executable..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1
python build_exe.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Location: dist\vox.exe"
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}
```

---

## Performance Optimization

### Reducing Build Time
- Use `--exclude-module` liberally for unused packages
- Enable parallel compilation (PyInstaller 5.0+)
- Use SSD for faster I/O

### Reducing Executable Size
- Profile imports: `python -X importtime -c "import src.main"`
- Remove unused dependencies from `pyproject.toml`
- Use lazy imports where possible

---

## Platform-Specific Notes

### Windows
- Works on Windows 10 and 11
- Requires Visual C++ Redistributable (usually pre-installed)
- UAC may prompt on first run (normal for new executables)

### Linux/macOS (Future)
Currently Windows-only, but Linux/macOS builds are planned for v2.0+:
- Follow similar process with platform-specific PyInstaller options
- May require platform-specific TTS alternatives

---

## Support

For build issues:
- Check [GitHub Issues](https://github.com/AidanInceer/vox/issues)
- Review [INSTALLATION.md](../INSTALLATION.md) for troubleshooting
- Consult [PyInstaller documentation](https://pyinstaller.org/en/stable/)

---

**Last Updated**: 2026-01-17  
**Version**: 1.0.0
