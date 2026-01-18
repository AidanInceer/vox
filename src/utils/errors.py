"""Custom exception classes for vox application."""


class voxException(Exception):
    """Base exception for all vox errors."""

    def __init__(self, message: str, error_code: str = None, context: dict = None):
        """Initialize exception with message, error code, and optional context.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., "TAB_NOT_FOUND")
            context: Additional contextual information (e.g., tab_id, url)
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format error message with code and context."""
        msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = "; ".join(f"{k}={v}" for k, v in self.context.items())
            msg += f" ({context_str})"
        return msg


class BrowserDetectionError(voxException):
    """Raised when browser tab detection fails."""

    pass


class TabNotFoundError(voxException):
    """Raised when specified browser tab cannot be found."""

    pass


class ExtractionError(voxException):
    """Raised when text extraction from content fails."""

    pass


class TTSError(voxException):
    """Raised when text-to-speech synthesis fails."""

    pass


class TTSInitializationError(TTSError):
    """Raised when TTS engine initialization fails."""

    pass


class AudioPlaybackError(voxException):
    """Raised when audio playback fails."""

    pass


class URLFetchError(ExtractionError):
    """Raised when fetching content from URL fails."""

    pass


class FileLoadError(ExtractionError):
    """Raised when loading local file fails."""

    pass


class SessionError(voxException):
    """Raised when session persistence operations fail."""

    pass


class SessionNotFoundError(SessionError):
    """Raised when specified session cannot be found."""

    pass


class ConfigurationError(voxException):
    """Raised when application configuration is invalid."""

    pass


class ValidationError(voxException):
    """Raised when input validation fails."""

    pass


class MicrophoneError(voxException):
    """Raised when microphone access or recording fails."""

    pass


class TranscriptionError(voxException):
    """Raised when speech-to-text transcription fails."""

    pass


class ModelLoadError(voxException):
    """Raised when STT model loading or initialization fails."""

    pass


class TimeoutError(voxException):
    """Raised when operation exceeds timeout."""

    pass
