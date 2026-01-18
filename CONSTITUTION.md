# PageReader Constitution

## Core Principles

1. **Test-First Development**: Write tests before implementation. Minimum 80% coverage required.
2. **Text-Based I/O**: Core operations work with text streams (stdin/stdout/JSON).
3. **Clear API Contracts**: Every module has well-defined interfaces with type hints.
4. **Semantic Versioning**: MAJOR.MINOR.PATCH format. Use commitizen for automated versioning.
5. **Code Quality**: Follow SOLID, DRY, KISS, YAGNI principles. Use ruff for linting/formatting.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `test`: Test additions/modifications
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

### 2.3 Commitizen Tool
Use Commitizen for interactive commit creation:

```bash
# Interactive commit prompt
cz commit

# Version bump (maintainers only)
cz bump

# Generate changelog
cz changelog
```

---

## 3. Development Workflow

### 3.1 Branch Strategy
- **Main Branch**: `main` (protected, requires PR approval)
- **Feature Branches**: `NNN-feature-name` (e.g., `001-web-reader-ai`)
- **Hotfix Branches**: `hotfix/description` (for urgent production fixes)

### 3.2 Pull Request Process
1. Create feature branch from `main`
2. Implement changes following TDD (tests first, then code)
3. Run `ruff format .` and `ruff check --fix` before commit
4. Write conventional commit messages
5. Ensure all tests pass: `pytest tests/ --cov=src --cov-fail-under=80`
6. Push branch and open PR against `main`
7. Wait for CI checks to pass (linting, tests, coverage)
8. Request review from maintainers
9. Address review feedback
10. Merge to `main` (squash or merge commit)

### 3.3 Release Process
1. **Version Bump**: Merge commits to `main` trigger auto-version bump (GitHub Actions)
2. **Changelog**: Changelog is automatically updated on version bump
3. **Tagging**: Create release tag manually or via `cz bump` locally
4. **Distribution**: Tag push triggers release workflow (PyPI + standalone exe)

---

## 4. Testing Requirements

### 4.1 Coverage Targets
- **Overall**: ≥80% line coverage across all modules
- **Critical Paths**: ≥95% coverage for:
  - `src/extraction/` (text extraction accuracy is critical)
  - `src/tts/` (speech synthesis must be reliable)
  - `src/browser/` (tab detection must work consistently)

### 4.2 Test Organization
```
tests/
├── unit/              # Isolated component tests
├── integration/       # Component interaction tests
├── contract/          # External API boundary tests
├── performance/       # Benchmarks and profiling
└── fixtures/          # Test data and mocks
```

### 4.3 Test Naming Convention
- **Files**: `test_<module_name>.py` (e.g., `test_text_extractor.py`)
- **Classes**: `Test<ClassName>` (e.g., `TestTextExtractor`)
- **Functions**: `test_<behavior>` (e.g., `test_extract_paragraph_text`)

### 4.4 Test Markers
Use pytest markers to categorize tests:
- `@pytest.mark.unit`: Unit tests (fast, isolated)
- `@pytest.mark.integration`: Integration tests (slower, requires dependencies)
- `@pytest.mark.contract`: Contract tests (external API boundaries)
- `@pytest.mark.performance`: Performance benchmarks

---

## 5. Code Review Guidelines

### 5.1 Review Checklist
- [ ] Tests written before implementation (TDD)
- [ ] All tests pass
- [ ] Coverage ≥80% (≥95% for critical paths)
- [ ] Ruff linting passes (no errors)
- [ ] Code follows SOLID principles
- [ ] No code duplication (DRY)
- [ ] Simple, readable code (KISS)
- [ ] Conventional commit messages
- [ ] Documentation updated (if needed)
- [ ] No breaking changes without major version bump

## Development Standards

- **Language**: Python 3.13+
- **Testing**: pytest with ≥80% coverage
- **Linting**: ruff for formatting and linting
- **CI/CD**: GitHub Actions for automated testing and releases

---

**Version**: 1.0.0 | **Last Updated**: 2026-01-17
