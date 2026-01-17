---
description: "Simplified task breakdown for PageReader v1.0 MVP - URL-only with enhanced CLI"
---

# Tasks: PageReader v1.0 MVP - URL Input → TTS → Audio Output

**Scope**: URL-only reading with colorized CLI and dual packaging (PyPI + Standalone Exe)  
**Status**: Planning Phase  
**Organization**: Tasks grouped by phase with clear dependencies  

## Overview

This is a massively simplified scope compared to the original spec. We've cut:
- ❌ Browser tab detection (tab detection removed entirely)
- ❌ File path input (removed)
- ❌ Playback controls (pause/resume, speed adjustment via playback)
- ❌ Session persistence
- ❌ Tab picker UI

We're keeping:
- ✅ URL → HTML fetch → Text extraction → TTS synthesis → Audio playback
- ✅ Colorized CLI with progress indicators
- ✅ Dual packaging (PyPI + PyInstaller exe)

---

## Phase 1: Foundation (Already Complete ✅)

**Status**: All tests passing, 185 tests, code formatted and linted

- [x] T001-T007: Project setup, config, errors, logging
- [x] T008-T013: Core models and interfaces
- [x] T014-T026: Phase 3 implementation (removed for URL-only)
- [x] T027-T034: Phase 4 URL/TTS implementation (KEEP - this is now our core)

**Current State**: URL-only reading already works via CLI:
```bash
python -m src.main read --url https://example.com
```

**Next Phase**: CLI enhancement and packaging

---

## Phase 2: CLI Enhancement (Colorized + Progress)

**Goal**: Make CLI user-friendly with colors, progress indicators, and better output formatting

### CLI Improvements

- [ ] T101 Add `colorama` to pyproject.toml dependencies for cross-platform colored output
- [ ] T102 Update src/main.py to use colored output:
  - Cyan ([*]) for status messages
  - Green ([OK]) for success
  - Red ([ERROR]) for errors
  - Yellow ([!]) for warnings
- [ ] T103 Add progress indicators for long operations:
  - URL fetching: show "Fetching URL..." with elapsed time
  - TTS synthesis: show "Synthesizing speech..." with elapsed time
- [ ] T104 Improve help text and command examples:
  - Update `--help` to show usage examples
  - Add descriptions of what each option does
  - Show example: `pagereader read --url https://example.com`
- [ ] T105 Add validation and error messages:
  - Validate URL format before fetching
  - Display user-friendly error messages for common failures
  - Suggest fixes (e.g., "URL fetch failed: check internet connection")
- [ ] T106 Format and lint all CLI changes with ruff
- [ ] T107 Create tests/unit/test_cli_output.py to verify colored output and messaging

**Checkpoint**: CLI is polished and user-friendly

---

## Phase 3: Build & Packaging System

**Goal**: Enable distribution as both PyPI package and standalone executable

### PyPI Package Configuration

- [ ] T201 Update pyproject.toml with package metadata:
  - Project name, version, description
  - Author, license, keywords
  - Homepage, repository URLs
  - Entry points: `[project.scripts]` with `pagereader = src.main:main`
- [ ] T202 Create src/main.py entry point function (if not exists):
  - Ensure `main()` is callable and handles sys.exit properly
  - Verify works with: `python -m src.main read --url https://example.com`
- [ ] T203 Test local PyPI installation:
  - Run `pip install -e .` in development mode
  - Verify `pagereader --help` works globally
  - Verify `pagereader read --url https://example.com` works
- [ ] T204 Create README.md with installation instructions:
  - "Install via PyPI: `pip install pagereader`"
  - "Or download standalone exe from Releases"
  - Quick start examples

### Standalone Executable (PyInstaller)

- [ ] T301 Add PyInstaller to dev dependencies in pyproject.toml
- [ ] T302 Create build_exe.py script to generate standalone .exe:
  - Use PyInstaller to bundle Python + dependencies + app code
  - Single-file output: `dist/pagereader.exe`
  - Include all Piper TTS models in the exe
  - Icon: use simple PageReader icon
- [ ] T303 Create build instructions in docs/BUILD.md:
  - Prerequisites (Python 3.13, pip, PyInstaller)
  - Commands: `python build_exe.py`
  - Output location: `dist/pagereader.exe`
  - Verify exe works: `dist/pagereader.exe --help`
- [ ] T304 Test standalone exe on clean Windows system:
  - Verify no Python installation required
  - Verify `pagereader.exe read --url https://example.com` works
  - Verify audio plays correctly
  - Measure exe file size
- [ ] T305 Create GitHub Actions workflow for automated exe generation:
  - Trigger on releases or manual workflow_dispatch
  - Generate .exe artifact
  - Upload to GitHub Releases

### Documentation & Release

- [ ] T401 Create INSTALLATION.md with two paths:
  - Path A: "For Developers" (PyPI + source code)
  - Path B: "For End Users" (Standalone exe, no Python required)
- [ ] T402 Create CHANGELOG.md documenting v1.0.0 features and known limitations
- [ ] T403 Update README.md with:
  - Feature summary (URL → audio reading)
  - Installation instructions (both methods)
  - Usage examples
  - Troubleshooting section
  - Known limitations (URL-only, no browser tabs, offline Piper TTS)

**Checkpoint**: Application ready for distribution

---

## Phase 4: Testing & Validation

- [ ] T501 Run full test suite: `pytest tests/ --cov=src --cov-report=term-missing`
  - Verify ≥80% coverage maintained
  - All 185 tests passing
- [ ] T502 Manual end-to-end test:
  - Install via `pip install -e .`
  - Run: `pagereader read --url https://en.wikipedia.org/wiki/Python_(programming_language)`
  - Verify text extraction, synthesis, audio playback all work
- [ ] T503 Test standalone exe:
  - Copy `dist/pagereader.exe` to clean directory
  - Run: `pagereader.exe read --url https://example.com`
  - Verify works without Python installed
- [ ] T504 Performance validation:
  - Simple URL: <5 seconds total (fetch + extract + synth + play)
  - Complex URL: <30 seconds total
  - Memory usage: <500 MB during synthesis
- [ ] T505 Create tests/integration/test_end_to_end.py with real URL tests

**Checkpoint**: Application fully tested and ready for v1.0 release

---

## Removed Tasks (Deferred to v2+)

The following are intentionally removed from v1.0 scope:

- ❌ Browser tab detection (T035-T039)
- ❌ File path input (removed from T031)
- ❌ Tab picker UI (removed from Phase 5)
- ❌ Playback controls (pause/resume/skip) - will use OS volume controls
- ❌ Speed adjustment via app (users adjust system audio)
- ❌ Session persistence (save/resume reading) - future feature
- ❌ Advanced extraction settings - future feature
- ❌ Multiple TTS voices - future feature (currently locked to en_US-libritts-high)

These can be added in v1.1 or v2.0 based on user feedback.

---

## Success Criteria for v1.0

- ✅ URL-only reading works reliably
- ✅ CLI is colorized and shows progress
- ✅ PyPI package installable and functional
- ✅ Standalone exe works on Windows without Python
- ✅ All tests passing (≥80% coverage)
- ✅ Documentation complete (README, INSTALLATION, BUILD)
- ✅ E2E test passes on real URL (Wikipedia)

---

## Timeline Estimate

| Phase | Tasks | Est. Time | Notes |
|-------|-------|-----------|-------|
| 1 | Foundation | ✅ Done | Already complete |
| 2 | CLI Enhancement | 4-6 hours | Colorization, validation, error handling |
| 3 | Packaging | 6-8 hours | PyPI setup, PyInstaller config, GitHub Actions |
| 4 | Testing | 2-3 hours | Full test suite, manual validation |
| **Total** | **All** | **~14-18 hours** | Can be done in 1-2 development days |

---

## Dependency Graph

```
Phase 1 (✅ Complete)
  ↓
Phase 2 (CLI Enhancement) 
  ↓
Phase 3 (Packaging)
  ↓
Phase 4 (Testing & Release)
```

All tasks in each phase should complete before moving to the next.

---

## Next Steps

1. Review this simplified task list ✅
2. Approve scope changes (URL-only, no browser tabs, no file input)
3. Begin Phase 2 (CLI enhancement with colorama)
4. Build standalone exe in Phase 3
5. Release v1.0 with both PyPI and exe distribution methods
