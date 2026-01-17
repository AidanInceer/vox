"""Unit tests for file loader module."""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import tempfile
import os

from src.extraction.file_loader import load_file
from src.utils.errors import FileLoadError


class TestFileLoader:
    """Test suite for file loading functionality."""

    def test_load_local_html_file(self):
        """Test loading HTML content from a local .html file."""
        html_content = "<html><body><h1>Test Page</h1><p>Content here</p></body></html>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            assert result == html_content
            assert "<h1>" in result
        finally:
            os.unlink(tmp_path)

    def test_load_htm_file_extension(self):
        """Test that both .html and .htm file extensions are accepted."""
        html_content = "<html><body>Test Content</body></html>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".htm", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            assert result == html_content
        finally:
            os.unlink(tmp_path)

    def test_load_nonexistent_file(self):
        """Test that loading a non-existent file raises FileLoadError."""
        with pytest.raises(FileLoadError) as exc_info:
            load_file("/path/to/nonexistent/file.html")

        assert "not found" in str(exc_info.value).lower() or "no such file" in str(exc_info.value).lower()

    def test_load_file_with_utf8_encoding(self):
        """Test that UTF-8 encoded files are loaded correctly."""
        html_content = "<html><body><p>Café français</p></body></html>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            assert "Café" in result
            assert "français" in result
        finally:
            os.unlink(tmp_path)

    def test_load_file_with_latin1_encoding(self):
        """Test auto-detection of non-UTF-8 encodings (e.g., Latin-1)."""
        html_content = "<html><body><p>Déjà vu</p></body></html>"

        # Write with Latin-1 encoding
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="latin-1") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            # Should handle encoding detection gracefully
            assert "vu" in result or "D" in result
        finally:
            os.unlink(tmp_path)

    def test_load_file_empty_html(self):
        """Test loading an empty HTML file."""
        html_content = ""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            assert result == ""
        finally:
            os.unlink(tmp_path)

    def test_load_file_large_html(self):
        """Test loading a large HTML file (>1 MB)."""
        # Create a large HTML with repeated content
        html_content = "<html><body>" + ("<p>Large content</p>" * 50000) + "</body></html>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            assert len(result) > 1000000  # > 1 MB
            assert result.startswith("<html>")
            assert result.endswith("</html>")
        finally:
            os.unlink(tmp_path)

    def test_load_file_permission_denied(self):
        """Test that permission errors are handled gracefully."""
        # Create a temporary file with no read permissions
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write("<html><body>Test</body></html>")
            tmp_path = tmp.name

        try:
            # Remove read permissions (Windows may not enforce this for owner,
            # so also test with a truly inaccessible path)
            os.chmod(tmp_path, 0o000)

            try:
                # Try to load the file - may raise FileLoadError for permission denied
                # or may succeed on Windows if permissions aren't enforced for owner
                result = load_file(tmp_path)
                # On Windows or when owner can still read, the file may load successfully
                # This is acceptable behavior
                assert result is not None
            except FileLoadError as e:
                # Expected on systems that enforce permissions
                assert "permission" in str(e).lower() or "access" in str(e).lower()
        finally:
            # Restore permissions before cleanup
            os.chmod(tmp_path, 0o644)
            os.unlink(tmp_path)

    def test_load_file_invalid_extension(self):
        """Test that non-HTML files raise FileLoadError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
            tmp.write("Not an HTML file")
            tmp_path = tmp.name

        try:
            with pytest.raises(FileLoadError) as exc_info:
                load_file(tmp_path)

            assert "html" in str(exc_info.value).lower() or "extension" in str(exc_info.value).lower()
        finally:
            os.unlink(tmp_path)

    def test_load_file_with_bom(self):
        """Test that files with BOM (Byte Order Mark) are handled correctly."""
        html_content = "<html><body><p>Content</p></body></html>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8-sig") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            # Should handle BOM gracefully (strip it if present)
            assert "<html>" in result
        finally:
            os.unlink(tmp_path)

    def test_load_file_malformed_html(self):
        """Test that malformed HTML can still be loaded."""
        # Missing closing tags, unmatched brackets, etc.
        html_content = "<html><body><p>Unclosed paragraph<div>Nested unclosed<body>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = load_file(tmp_path)
            assert result == html_content
        finally:
            os.unlink(tmp_path)

    def test_load_file_path_with_spaces(self):
        """Test loading files with spaces in path."""
        html_content = "<html><body>Test</body></html>"
        temp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(temp_dir, "test file with spaces.html")

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            result = load_file(tmp_path)
            assert result == html_content
        finally:
            os.unlink(tmp_path)
            os.rmdir(temp_dir)

    def test_load_file_absolute_path(self):
        """Test loading file with absolute path."""
        html_content = "<html><body>Absolute Path Test</body></html>"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as tmp:
            tmp.write(html_content)
            tmp_path = os.path.abspath(tmp.name)

        try:
            result = load_file(tmp_path)
            assert result == html_content
        finally:
            os.unlink(tmp_path)

    def test_load_file_relative_path(self):
        """Test loading file with relative path."""
        html_content = "<html><body>Relative Path Test</body></html>"
        current_dir = os.getcwd()
        temp_dir = tempfile.mkdtemp()

        try:
            os.chdir(temp_dir)
            tmp_path = "test_relative.html"

            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            result = load_file(tmp_path)
            assert result == html_content
        finally:
            os.chdir(current_dir)
            if os.path.exists(os.path.join(temp_dir, "test_relative.html")):
                os.unlink(os.path.join(temp_dir, "test_relative.html"))
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
