.PHONY: help activate test test-unit test-integration test-cov format lint clean install

# Variables
PYTHON := .venv/Scripts/python.exe
PIP := .venv/Scripts/pip.exe
PYTEST := .venv/Scripts/pytest.exe
RUFF := .venv/Scripts/ruff.exe

help:
	@echo Available commands:
	@echo   make activate      - Activate virtual environment (Windows PowerShell)
	@echo   make install       - Install project dependencies
	@echo   make test          - Run all tests
	@echo   make test-unit     - Run unit tests only
	@echo   make test-integration - Run integration tests only
	@echo   make test-cov      - Run tests with coverage report
	@echo   make format        - Format code with ruff
	@echo   make format-check  - Check code formatting without changes
	@echo   make lint          - Run linting checks with ruff
	@echo   make clean         - Clean up generated files
	@echo   make build         - Build executable with PyInstaller

activate:
	@echo To activate the virtual environment, run:
	@echo   .venv\Scripts\Activate.ps1

install:
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov ruff

test:
	$(PYTEST) tests/ -v

test-unit:
	$(PYTEST) tests/unit/ -v

test-integration:
	$(PYTEST) tests/integration/ -v

test-cov:
	$(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=term

format:
	$(RUFF) format src/ tests/

format-check:
	$(RUFF) format --check src/ tests/

lint:
	$(RUFF) check src/ tests/
	@echo Linting complete!

clean:
	@echo Cleaning up...
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist coverage.xml del /q coverage.xml
	@if exist .coverage del /q .coverage
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d"
	@echo Cleanup complete!

build:
	$(PYTHON) scripts/build_exe.py
	@echo Build complete! Check dist/ folder for executable.
