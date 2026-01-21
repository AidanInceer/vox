"""Build script for creating standalone vox executable using PyInstaller.

This script generates a single-file Windows executable that includes:
- Python interpreter
- All dependencies (Piper TTS, Whisper STT, BeautifulSoup, etc.)
- Application code
- TTS models

Usage:
    python build_exe.py

Output:
    dist/vox.exe - Standalone executable
"""

import os
import shutil
import sys
import time
from pathlib import Path

try:
    import PyInstaller.__main__
except ImportError:
    print("ERROR: PyInstaller not found. Install it with: pip install pyinstaller")
    sys.exit(1)


def remove_readonly(func, path, excinfo):
    """Error handler for Windows readonly files."""
    os.chmod(path, 0o777)
    func(path)


def safe_rmtree(path, max_retries=3):
    """Safely remove directory tree with retry logic for Windows."""
    for attempt in range(max_retries):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"[!] Directory locked, retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"[ERROR] Could not delete {path}")
                print(f"[ERROR] {e}")
                print(f"[!] Please close any running instances of vox.exe and try again")
                return False
        except Exception as e:
            print(f"[ERROR] Unexpected error removing {path}: {e}")
            return False
    return False


def main():
    """Build the standalone executable."""
    print("[*] Building vox standalone executable...")

    # Project paths
    project_root = Path(__file__).parent.parent  # Go up from scripts/ to project root
    src_dir = project_root / "src"
    main_script = src_dir / "main.py"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    # Verify main script exists
    if not main_script.exists():
        print(f"ERROR: Main script not found at {main_script}")
        sys.exit(1)

    # Clean previous builds
    if dist_dir.exists():
        print("[*] Cleaning previous build artifacts (dist/)...")
        if not safe_rmtree(dist_dir):
            sys.exit(1)
    if build_dir.exists():
        print("[*] Cleaning previous build artifacts (build/)...")
        if not safe_rmtree(build_dir):
            sys.exit(1)

    # PyInstaller options
    options = [
        str(main_script),  # Main entry point
        "--name=vox",  # Executable name
        "--onefile",  # Single file executable
        "--windowed",  # GUI application (no console window)
        "--noconfirm",  # Overwrite without asking
        # Add hidden imports for dynamic imports
        "--hidden-import=src",
        "--hidden-import=src.browser",
        "--hidden-import=src.browser.detector",
        "--hidden-import=src.browser.tab_info",
        "--hidden-import=src.browser.accessibility",
        "--hidden-import=src.extraction",
        "--hidden-import=src.extraction.text_extractor",
        "--hidden-import=src.extraction.html_parser",
        "--hidden-import=src.extraction.dom_walker",
        "--hidden-import=src.extraction.content_filter",
        "--hidden-import=src.extraction.url_fetcher",
        "--hidden-import=src.extraction.file_loader",
        "--hidden-import=src.tts",
        "--hidden-import=src.tts.synthesizer",
        "--hidden-import=src.tts.piper_provider",
        "--hidden-import=src.tts.playback",
        "--hidden-import=src.tts.chunking",
        "--hidden-import=src.tts.controller",
        "--hidden-import=src.stt",
        "--hidden-import=src.stt.engine",
        "--hidden-import=src.stt.recorder",
        "--hidden-import=src.stt.transcriber",
        "--hidden-import=src.stt.audio_utils",
        "--hidden-import=src.stt.ui",
        "--hidden-import=src.session",
        "--hidden-import=src.session.models",
        "--hidden-import=src.session.manager",
        "--hidden-import=src.utils",
        "--hidden-import=src.utils.errors",
        "--hidden-import=src.utils.logging",
        "--hidden-import=src.utils.migration",
        "--hidden-import=src.config",
        "--hidden-import=src.ui",
        "--hidden-import=src.ui.main_window",
        "--hidden-import=src.ui.system_tray",
        "--hidden-import=src.ui.indicator",
        "--hidden-import=src.ui.styles",
        # Third-party hidden imports
        "--hidden-import=pystray",
        "--hidden-import=pystray._win32",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=pynput",
        "--hidden-import=pynput.keyboard",
        "--hidden-import=pynput.mouse",
        "--hidden-import=pyperclip",
        # Data files
        "--collect-data=piper_tts",  # Include Piper TTS models
        "--collect-data=ttkbootstrap",  # Include ttkbootstrap themes
        # Exclude test files
        "--exclude-module=pytest",
        "--exclude-module=tests",
    ]

    # Add icon if it exists
    icon_path = project_root / "imgs" / "logo.ico"
    if icon_path.exists():
        options.extend(["--icon", str(icon_path)])

    # Build the executable
    print("[*] Running PyInstaller...")
    print(f"    Main script: {main_script}")
    print(f"    Output directory: {dist_dir}")

    try:
        PyInstaller.__main__.run(options)
        print("[OK] Build complete!")
        print(f"[OK] Executable created: {dist_dir / 'vox.exe'}")

        # Display file size
        exe_path = dist_dir / "vox.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[OK] File size: {size_mb:.2f} MB")

        print("\n[*] Test the executable:")
        print(f"    {exe_path} --help")
        print(f"    {exe_path} read --url https://example.com")

    except Exception as e:
        print(f"[ERROR] Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
