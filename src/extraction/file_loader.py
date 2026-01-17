"""File loader module for reading HTML content from local files."""

import os
from pathlib import Path

import chardet

from src.utils.errors import FileLoadError


def load_file(file_path: str) -> str:
    """
    Load HTML content from a local file.

    Args:
        file_path: Path to the HTML file (.html or .htm)

    Returns:
        str: The HTML content of the file

    Raises:
        FileLoadError: If the file cannot be loaded or has invalid extension

    Examples:
        >>> html = load_file("page.html")
        >>> "<html>" in html
        True
    """
    try:
        # Validate file extension
        path = Path(file_path)
        if path.suffix.lower() not in [".html", ".htm"]:
            raise FileLoadError(f"Invalid file extension '{path.suffix}'. Expected .html or .htm")

        # Check if file exists
        if not path.exists():
            raise FileLoadError(f"File not found: {file_path}")

        # Check read permissions
        if not os.access(file_path, os.R_OK):
            raise FileLoadError(f"Permission denied: cannot read file {file_path}")

        # Read file with encoding detection
        with open(file_path, "rb") as f:
            raw_data = f.read()

        # Detect encoding
        detected = chardet.detect(raw_data)
        encoding = detected.get("encoding", "utf-8") if detected else "utf-8"

        # Fallback to UTF-8 if detection fails
        if not encoding:
            encoding = "utf-8"

        # Try to decode with detected encoding
        try:
            content = raw_data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            # Fall back to UTF-8 with error handling
            try:
                content = raw_data.decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                # Last resort: UTF-8 with ignore errors
                content = raw_data.decode("utf-8", errors="ignore")

        return content

    except FileLoadError:
        raise
    except PermissionError as e:
        raise FileLoadError(f"Permission denied when reading {file_path}") from e
    except FileNotFoundError as e:
        raise FileLoadError(f"File not found: {file_path}") from e
    except IsADirectoryError as e:
        raise FileLoadError(f"Path is a directory, not a file: {file_path}") from e
    except Exception as e:
        raise FileLoadError(f"Failed to load file {file_path}: {str(e)}") from e
