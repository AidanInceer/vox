"""Structured logging configuration for vox."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from src import config


class ColoredFormatter(logging.Formatter):
    """Logging formatter with color support for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color codes."""
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    name: str = "vox",
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> logging.Logger:
    """Configure logging for vox application.

    Args:
        name: Logger name (usually module name or "vox" for root)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               If None, uses config.LOG_LEVEL
        log_file: Path to log file. If None, uses config.LOGS_DIR / f"{name}.log"
        enable_console: Whether to add console handler
        enable_file: Whether to add file handler

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level
    if level is None:
        level = config.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Use colored formatter for console
        formatter = ColoredFormatter(config.LOG_FORMAT)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if enable_file:
        if log_file is None:
            log_file = config.LOGS_DIR / f"{name}.log"

        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.LOG_FILE_SIZE_MB * 1024 * 1024,
            backupCount=config.LOG_BACKUP_COUNT,
        )
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Use standard formatter for file (no colors)
        formatter = logging.Formatter(config.LOG_FORMAT)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to avoid duplicate logs
    if name != "vox":
        logger.propagate = False

    return logger


# Root logger for vox
_root_logger = setup_logging("vox")


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance for the module
    """
    return logging.getLogger(f"vox.{name}")
