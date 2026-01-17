"""Build script for creating standalone PageReader executable using PyInstaller.

This script generates a single-file Windows executable that includes:
- Python interpreter
- All dependencies (Piper TTS, BeautifulSoup, etc.)
- Application code
- TTS models

Usage:
    python build_exe.py

Output:
    dist/pagereader.exe - Standalone executable
"""

import os
import shutil
import sys
from pathlib import Path

try:
    import PyInstaller.__main__
except ImportError:
    print("ERROR: PyInstaller not found. Install it with: pip install pyinstaller")
    sys.exit(1)


def main():
    """Build the standalone executable."""
    print("[*] Building PageReader standalone executable...")

    # Project paths
    project_root = Path(__file__).parent
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
        print("[*] Cleaning previous build artifacts...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # PyInstaller options
    options = [
        str(main_script),  # Main entry point
        "--name=pagereader",  # Executable name
        "--onefile",  # Single file executable
        "--console",  # Console application
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
        "--hidden-import=src.session",
        "--hidden-import=src.session.models",
        "--hidden-import=src.ui",
        "--hidden-import=src.utils",
        "--hidden-import=src.utils.errors",
        "--hidden-import=src.utils.logging",
        "--hidden-import=src.config",
        # Data files
        "--collect-data=piper_tts",  # Include Piper TTS models
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
        print(f"[OK] Executable created: {dist_dir / 'pagereader.exe'}")

        # Display file size
        exe_path = dist_dir / "pagereader.exe"
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
