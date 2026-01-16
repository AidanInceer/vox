"""Unit tests for custom exception classes."""

import pytest

from src.utils.errors import (
    AudioPlaybackError,
    BrowserDetectionError,
    ConfigurationError,
    ExtractionError,
    FileLoadError,
    PageReaderException,
    SessionError,
    SessionNotFoundError,
    TabNotFoundError,
    TTSError,
    TTSInitializationError,
    TimeoutError,
    URLFetchError,
    ValidationError,
)


class TestPageReaderExceptionBase:
    """Tests for base PageReaderException class."""
    
    def test_exception_with_message_only(self):
        """Test exception instantiation with message only."""
        exc = PageReaderException("Something went wrong")
        assert str(exc) == "[PageReaderException] Something went wrong"
        assert exc.error_code == "PageReaderException"
        assert exc.context == {}
    
    def test_exception_with_error_code(self):
        """Test exception with custom error code."""
        exc = PageReaderException("Failed to connect", error_code="CONNECTION_FAILED")
        assert "[CONNECTION_FAILED]" in str(exc)
        assert exc.error_code == "CONNECTION_FAILED"
    
    def test_exception_with_context(self):
        """Test exception with contextual information."""
        context = {"url": "https://example.com", "status": 404}
        exc = PageReaderException("Invalid response", context=context)
        error_str = str(exc)
        assert "url=https://example.com" in error_str
        assert "status=404" in error_str
    
    def test_exception_is_subclassed_properly(self):
        """Test that exception inherits from Exception."""
        exc = PageReaderException("Test")
        assert isinstance(exc, Exception)
        with pytest.raises(PageReaderException):
            raise exc


class TestSpecificExceptionClasses:
    """Tests for specific exception subclasses."""
    
    def test_browser_detection_error(self):
        """Test BrowserDetectionError instantiation."""
        exc = BrowserDetectionError("Could not detect Chrome")
        assert "BrowserDetectionError" in str(exc)
    
    def test_tab_not_found_error(self):
        """Test TabNotFoundError instantiation."""
        exc = TabNotFoundError("Tab with ID xyz not found", context={"tab_id": "xyz"})
        assert "tab_id=xyz" in str(exc)
    
    def test_extraction_error(self):
        """Test ExtractionError instantiation."""
        exc = ExtractionError("Failed to parse HTML")
        assert "ExtractionError" in str(exc)
    
    def test_tts_error(self):
        """Test TTSError instantiation."""
        exc = TTSError("TTS engine failed")
        assert "TTSError" in str(exc)
    
    def test_tts_initialization_error(self):
        """Test TTSInitializationError is subclass of TTSError."""
        exc = TTSInitializationError("Could not initialize Piper")
        assert isinstance(exc, TTSError)
    
    def test_audio_playback_error(self):
        """Test AudioPlaybackError instantiation."""
        exc = AudioPlaybackError("No audio device available")
        assert "AudioPlaybackError" in str(exc)
    
    def test_url_fetch_error(self):
        """Test URLFetchError is subclass of ExtractionError."""
        exc = URLFetchError("Failed to fetch URL", context={"url": "https://example.com"})
        assert isinstance(exc, ExtractionError)
    
    def test_file_load_error(self):
        """Test FileLoadError is subclass of ExtractionError."""
        exc = FileLoadError("File not found", context={"file": "/path/to/file.html"})
        assert isinstance(exc, ExtractionError)
    
    def test_session_error(self):
        """Test SessionError instantiation."""
        exc = SessionError("Failed to save session")
        assert "SessionError" in str(exc)
    
    def test_session_not_found_error(self):
        """Test SessionNotFoundError is subclass of SessionError."""
        exc = SessionNotFoundError("Session abc123 not found")
        assert isinstance(exc, SessionError)
    
    def test_configuration_error(self):
        """Test ConfigurationError instantiation."""
        exc = ConfigurationError("Invalid configuration value")
        assert "ConfigurationError" in str(exc)
    
    def test_validation_error(self):
        """Test ValidationError instantiation."""
        exc = ValidationError("Invalid input")
        assert "ValidationError" in str(exc)
    
    def test_timeout_error(self):
        """Test TimeoutError instantiation."""
        exc = TimeoutError("Operation timed out", context={"timeout_seconds": 5.0})
        assert "TimeoutError" in str(exc)
        assert "timeout_seconds=5.0" in str(exc)


class TestExceptionRaisingAndCatching:
    """Tests for raising and catching exceptions."""
    
    def test_raise_and_catch_base_exception(self):
        """Test raising and catching base PageReaderException."""
        with pytest.raises(PageReaderException):
            raise PageReaderException("Test error")
    
    def test_raise_and_catch_specific_exception(self):
        """Test raising and catching specific exception."""
        with pytest.raises(TabNotFoundError):
            raise TabNotFoundError("Tab not found")
    
    def test_catch_parent_catches_child(self):
        """Test that parent exception class catches child exceptions."""
        with pytest.raises(PageReaderException):
            raise TabNotFoundError("Specific error caught as parent")
    
    def test_exception_with_all_parameters(self):
        """Test exception with all parameters."""
        exc = PageReaderException(
            message="Complete error",
            error_code="COMPLETE_ERROR",
            context={"key1": "value1", "key2": 42}
        )
        error_str = str(exc)
        assert "Complete error" in error_str
        assert "[COMPLETE_ERROR]" in error_str
        assert "key1=value1" in error_str
        assert "key2=42" in error_str
