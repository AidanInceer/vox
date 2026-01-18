# Project Rebranding Checklist Contract

**Feature**: Project Rebranding  
**Date**: January 18, 2026  
**Purpose**: Systematic checklist for renaming project from "vox" to new name

## Naming Decision

**Current Name**: vox  
**New Name**: **vox**  
**CLI Command**: **vox**

**Decision Status**: ✅ **APPROVED** - Name selected and ready for implementation

**Rationale**: Concise, voice-focused (Latin "vox" = voice), available on PyPI/GitHub, professional tone

## Phase 1: Name Selection & Validation

### Pre-Implementation Checklist

- [x] **Select name from research.md candidates** - **vox** selected
- [x] **Verify PyPI availability**: Available on PyPI
- [x] **Verify GitHub availability**: Available on GitHub
- [x] **Trademark search**: No USPTO conflicts (common Latin word)
- [x] **Team approval**: Approved by stakeholders

**Gate**: ✅ Ready to proceed to Phase 2

## Phase 2: Codebase Refactoring

### 2.1 Python Package Structure

- [ ] **pyproject.toml**: Update `[project].name` field
  ```toml
  # Before
  name = "vox"
  
  # After
  name = "vox"
  ```

- [ ] **pyproject.toml**: Update `[project.scripts]` entry point
  ```toml
  # Before
  vox = "src.main:main"
  
  # After
  vox = "src.main:main"
  ```

- [ ] **pyproject.toml**: Update URLs section
  ```toml
  [project.urls]
  Homepage = "https://github.com/AidanInceer/vox"
  Repository = "https://github.com/AidanInceer/vox"
  Documentation = "https://github.com/AidanInceer/vox/blob/main/README.md"
  Issues = "https://github.com/AidanInceer/vox/issues"
  ```

- [ ] **pyproject.toml**: Update description field
  ```toml
  description = "Bidirectional audio-text conversion tool with TTS and STT"
  ```

- [ ] **pyproject.toml**: Update keywords
  ```toml
  keywords = ["text-to-speech", "speech-to-text", "accessibility", "transcription", "audio"]
  ```

- [ ] **src/__init__.py**: Update `__version__` and package metadata
  ```python
  __version__ = "2.0.0"  # MAJOR bump for breaking change
  __name__ = "vox"
  ```

- [ ] **src/config.py**: Update application constants
  ```python
  # Before
  APP_NAME = "vox"
  APP_VERSION = "1.1.0"
  
  # After
  APP_NAME = "vox"
  APP_VERSION = "2.0.0"
  ```

### 2.2 CLI Help Text & Messages

- [ ] **src/main.py**: Update CLI parser description
  ```python
  parser = argparse.ArgumentParser(
      prog="vox",
      description="vox - Bidirectional audio-text conversion CLI"
  )
  ```

- [ ] **src/main.py**: Update version string display
  ```python
  parser.add_argument("--version", action="version", version=f"vox {APP_VERSION}")
  ```

- [ ] **src/main.py**: Search and replace display strings
  - Find: `"vox"`, `"vox"`
  - Replace with: `"vox"`, `"vox"`

- [ ] **All print statements**: Update banner/status messages
  ```python
  # Before
  print("vox v1.1.0")
  
  # After
  print("vox v2.0.0")
  ```

### 2.3 Documentation Files

- [ ] **README.md**: Replace all instances of "vox" with "vox"
  - Title/heading
  - Installation commands (`pip install vox`)
  - Usage examples (`vox read --url...`)
  - Links to repository
  - Logo alt text (if logo updated)

- [ ] **CHANGELOG.md**: Add entry for v2.0.0 rebranding
  ```markdown
  ## [2.0.0] - 2026-01-XX
  
  ### BREAKING CHANGES
  - Project renamed from vox to vox
  - CLI command changed from `vox` to `vox`
  - PyPI package renamed to `vox`
  
  ### Added
  - Speech-to-text (STT) functionality
  - Comprehensive developer documentation
  ```

- [ ] **docs/BUILD.md**: Update build instructions with new name
- [ ] **docs/ARCHITECTURE.md** (new file): Use new name throughout
- [ ] **.agents** (new file): Use new name in project metadata
- [ ] **claude.md** (new file): Use new name in guidelines
- [ ] **CONTRIBUTING.md** (if exists): Update project name references

### 2.4 Configuration & Data Directories

- [ ] **Session directory migration**: Update `src/config.py`
  ```python
  # Before
  DATA_DIR = Path(os.getenv("APPDATA")) / "vox"
  
  # After
  DATA_DIR = Path(os.getenv("APPDATA")) / "vox"
  
  # Add migration logic (one-time)
  OLD_DATA_DIR = Path(os.getenv("APPDATA")) / "vox"
  if OLD_DATA_DIR.exists() and not DATA_DIR.exists():
      shutil.copytree(OLD_DATA_DIR, DATA_DIR)
      logger.info(f"Migrated data from vox to {DATA_DIR}")
  ```

- [ ] **Session files**: Update metadata in existing sessions (if applicable)

### 2.5 Test Files

- [ ] **tests/**: Search for "vox" in all test files
- [ ] **tests/**: Update test docstrings referencing old name
- [ ] **tests/**: Update test fixture paths if they include "vox"
- [ ] **tests/**: Update CLI invocation tests
  ```python
  # Before
  result = subprocess.run(["vox", "--version"])
  
  # After
  result = subprocess.run(["vox", "--version"])
  ```

### 2.6 Build & Packaging

- [ ] **scripts/build_exe.py**: Update executable name
  ```python
  # Before
  name="vox"
  
  # After
  name="vox"
  ```

- [ ] **vox.spec** (PyInstaller spec): Rename file to `vox.spec`
- [ ] **vox.spec**: Update name fields inside spec file

- [ ] **setup.py** (if exists): Update name fields

### 2.7 Git & GitHub

- [ ] **Repository rename**: GitHub Settings → Rename repository to "vox"
- [ ] **Local git remote update**:
  ```bash
  git remote set-url origin https://github.com/AidanInceer/vox.git
  ```

- [ ] **.github/**: Update workflow files referencing "vox"
- [ ] **GitHub Actions**: Update any hardcoded package names
- [ ] **GitHub repo description**: Update to reflect STT capability
- [ ] **GitHub topics**: Add "speech-to-text", "transcription" tags

### 2.8 Comments & Docstrings

- [ ] **Module docstrings**: Update references to "vox"
  ```python
  # Before
  """vox CLI - Main entry point"""
  
  # After
  """vox CLI - Main entry point"""
  ```

- [ ] **Inline comments**: Search for "vox" in comments
- [ ] **TODO comments**: Update any references to old name

## Phase 3: External References

### 3.1 PyPI

- [ ] **Register new package name** on PyPI (requires PyPI account)
- [ ] **Upload v2.0.0** under new name
- [ ] **Mark old package as deprecated**: Add deprecation notice to vox PyPI page
  ```
  ## DEPRECATED
  
  This package has been renamed to `vox`. Please update your installation:
  
      pip uninstall vox
      pip install vox
  
  All future updates will be published under the new name.
  ```

### 3.2 Documentation Sites (if applicable)

- [ ] **ReadTheDocs** (if used): Update project name and URLs
- [ ] **GitHub Wiki** (if used): Update all pages
- [ ] **External documentation** (if hosted separately): Update domain/URLs

### 3.3 Social/Community

- [ ] **GitHub repo social image**: Update with new name/logo
- [ ] **Announcement**: Post migration notice (GitHub Discussions, Twitter, Reddit if applicable)
- [ ] **Old links**: Add redirects or deprecation notices

## Phase 4: Testing & Validation

### 4.1 Automated Tests

- [ ] **Run full test suite**: `pytest tests/ --cov=src`
- [ ] **Verify ≥80% coverage**: Check coverage report
- [ ] **Test CLI commands**: Manually test `vox --help`
- [ ] **Test installation**: Fresh virtual environment
  ```bash
  python -m venv test_env
  test_env\Scripts\activate
  pip install -e .
  vox --version
  ```

### 4.2 Manual Testing

- [ ] **Test PyPI installation**: `pip install vox` from clean environment
- [ ] **Test executable**: Run `vox.exe` on Windows
- [ ] **Test TTS commands**: Verify existing functionality not broken
- [ ] **Test session migration**: Verify old vox sessions accessible
- [ ] **Test help text**: All commands show updated name

### 4.3 Documentation Validation

- [ ] **Verify all links**: Check README, docs for broken links
- [ ] **Test examples**: Run all command examples from README
- [ ] **Spell check**: Grep for "vox" or "vox" typos
  ```bash
  grep -r "vox" . --exclude-dir=.git --exclude-dir=specs/001-* --exclude-dir=specs/002-*
  ```

## Phase 5: Release & Communication

### 5.1 Version Bump

- [ ] **commitizen bump**: Run `cz bump` to update to v2.0.0
- [ ] **Git tag**: Create and push tag `v2.0.0`
- [ ] **GitHub Release**: Create release with notes about rebranding

### 5.2 Announcement

- [ ] **README badge**: Update any badges referencing old name
- [ ] **Migration guide**: Add section to README explaining upgrade path
  ```markdown
  ## Upgrading from vox 1.x
  
  vox has been renamed to vox to reflect expanded STT capabilities.
  
  1. Uninstall old package: `pip uninstall vox`
  2. Install new package: `pip install vox`
  3. Update CLI commands: `vox` → `vox`
  4. Your saved sessions will be automatically migrated on first run
  ```

- [ ] **CHANGELOG entry**: Finalize v2.0.0 release notes
- [ ] **Deprecation timeline**: Document support end date for old package

## Rollback Plan

If critical issues discovered post-rename:

1. **Hotfix release**: Patch under old name (v1.1.1) with critical fixes
2. **Delay migration**: Keep old package active for 1+ additional release cycles
3. **Communication**: Announce extended transition period
4. **Dual maintenance**: Support both names temporarily (symlink/alias)

## Validation Criteria

| Criterion | Method | Pass Condition |
|-----------|--------|----------------|
| No references to old name | `grep -r "vox"` | Zero matches in src/, excluding specs/ |
| PyPI package accessible | `pip install vox` | Successful installation |
| CLI command works | `vox --version` | Displays v2.0.0 |
| Tests pass | `pytest tests/` | 100% pass, ≥80% coverage |
| Sessions migrate | Run after rename | Old sessions accessible |
| Documentation accurate | Manual review | All examples work, no broken links |

## Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Name Selection & Validation | ~~1-3 days~~ COMPLETE | Stakeholder availability |
| Codebase Refactoring | 2-4 hours | Name finalized |
| Testing & Validation | 2-3 hours | Refactoring complete |
| Release & Communication | 1 hour | All tests passing |
| **Total** | **2-4 hours** | Name approved |

## Notes

- **Breaking Change**: Users must update CLI commands and package name
- **Semantic Versioning**: MAJOR bump (1.x → 2.0) required per constitution
- **Backward Compatibility**: Session migration maintains user data continuity
- **Deprecation Period**: Recommend 6-month window before removing old PyPI package

**Status**: ✅ **READY FOR IMPLEMENTATION** - Name "vox" approved  
**Checklist Progress**: 6 / 66 items (Phase 1 complete, Phase 2-5 pending)

---

**Next Actions**:
1. ~~Select final name from research.md candidates~~ ✅ COMPLETE: vox
2. ~~Validate name availability (PyPI, GitHub, trademark)~~ ✅ COMPLETE
3. ~~Get stakeholder approval~~ ✅ COMPLETE
4. Proceed to Phase 2 refactoring
