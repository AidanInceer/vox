"""Custom exception classes for the vox application.

This module defines the exception hierarchy used throughout the vox
application. All custom exceptions inherit from voxException (legacy base)
or VoxError (for the 004-hotkey-voice-input feature).

Exception Hierarchy:
    voxException (base)
    ├── BrowserDetectionError
    ├── TabNotFoundError
    ├── ExtractionError
    │   ├── URLFetchError
    │   └── FileLoadError
    ├── TTSError
    │   └── TTSInitializationError
    ├── AudioPlaybackError
    ├── SessionError
    │   └── SessionNotFoundError
    ├── ConfigurationError
    ├── ValidationError
    ├── MicrophoneError
    ├── TranscriptionError
    ├── ModelLoadError
    ├── TimeoutError
    └── VoxError (hotkey voice input feature)
        ├── HotkeyError
        │   ├── HotkeyAlreadyRegisteredError
        │   └── HotkeyInvalidFormatError
        ├── RecordingError
        ├── PasteError
        └── DatabaseError
"""


class voxException(Exception):
    """Base exception for all vox errors.

    Provides a structured exception with error codes and contextual information
    for better debugging and error handling throughout the application.

    Attributes:
        message: Human-readable error description.
        error_code: Machine-readable error code for programmatic handling.
        context: Dictionary of additional contextual information.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict | None = None,
    ):
        """Initialize exception with message, error code, and optional context.

        Args:
            message: Human-readable error message describing what went wrong.
            error_code: Machine-readable error code (e.g., "TAB_NOT_FOUND").
                Defaults to the class name if not provided.
            context: Additional contextual information as key-value pairs
                (e.g., {"tab_id": 123, "url": "https://example.com"}).
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format error message with code and context.

        Returns:
            Formatted string containing the error code, message, and any
            context information in the format:
            [ERROR_CODE] Message (key=value; ...).
        """
        msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = "; ".join(f"{k}={v}" for k, v in self.context.items())
            msg += f" ({context_str})"
        return msg


class BrowserDetectionError(voxException):
    """Raised when browser tab detection fails.

    Indicates that the application could not detect or communicate with
    a supported browser to retrieve the active tab information.
    """

    pass


class TabNotFoundError(voxException):
    """Raised when the specified browser tab cannot be found.

    The requested tab ID does not exist or is no longer available.
    """

    pass


class ExtractionError(voxException):
    """Raised when text extraction from content fails.

    Base exception for content extraction operations. Subclasses provide
    more specific error types for URL fetching and file loading.
    """

    pass


class TTSError(voxException):
    """Raised when text-to-speech synthesis fails.

    Indicates a failure during speech synthesis operations.
    """

    pass


class TTSInitializationError(TTSError):
    """Raised when TTS engine initialization fails.

    The TTS engine could not be started, typically due to missing
    dependencies or system configuration issues.
    """

    pass


class AudioPlaybackError(voxException):
    """Raised when audio playback fails.

    The system could not play the generated audio, possibly due to
    audio device issues or format incompatibility.
    """

    pass


class URLFetchError(ExtractionError):
    """Raised when fetching content from a URL fails.

    Network errors, invalid URLs, or HTTP errors prevent content retrieval.
    """

    pass


class FileLoadError(ExtractionError):
    """Raised when loading a local file fails.

    The file could not be read due to permissions, missing file, or
    encoding issues.
    """

    pass


class SessionError(voxException):
    """Raised when session persistence operations fail.

    Base exception for session-related errors during save/load operations.
    """

    pass


class SessionNotFoundError(SessionError):
    """Raised when the specified session cannot be found.

    The requested session ID does not exist in storage.
    """

    pass


class ConfigurationError(voxException):
    """Raised when application configuration is invalid.

    Configuration files are missing, malformed, or contain invalid values.
    """

    pass


class ValidationError(voxException):
    """Raised when input validation fails.

    User input or data does not meet the required format or constraints.
    """

    pass


class MicrophoneError(voxException):
    """Raised when microphone access or recording fails.

    The microphone could not be accessed (permissions, device not found)
    or recording operations failed.
    """

    pass


class TranscriptionError(voxException):
    """Raised when speech-to-text transcription fails.

    The STT engine could not process the audio or returned an error.
    """

    pass


class ModelLoadError(voxException):
    """Raised when STT model loading or initialization fails.

    The speech recognition model could not be loaded, typically due to
    missing model files or insufficient memory.
    """

    pass


class TimeoutError(voxException):
    """Raised when an operation exceeds its timeout.

    The operation took longer than the allowed time limit.
    """

    pass


# ============================================================================
# 004-hotkey-voice-input: Hotkey Voice Input Feature Errors
# ============================================================================


class VoxError(voxException):
    """Base exception for hotkey voice input feature errors.

    All exceptions specific to the 004-hotkey-voice-input feature inherit
    from this class for easy catching of feature-specific errors.
    """

    pass


class HotkeyError(VoxError):
    """Raised when hotkey registration or listening fails.

    Base exception for hotkey-related errors. Subclasses provide specific
    error types for registration conflicts and format issues.
    """

    pass


class HotkeyAlreadyRegisteredError(HotkeyError):
    """Raised when attempting to register an already registered hotkey.

    The specified hotkey combination is already in use by this application.
    Unregister the existing hotkey before registering a new callback.
    """

    pass


class HotkeyInvalidFormatError(HotkeyError):
    """Raised when a hotkey string format is invalid.

    The hotkey string could not be parsed. Valid formats include:
    - '<ctrl>+<alt>+space'
    - 'ctrl+alt+a'
    - '<shift>+f1'
    """

    pass


class RecordingError(VoxError):
    """Raised when audio recording operations fail.

    Recording could not start, was interrupted, or failed to capture audio.
    """

    pass


class PasteError(VoxError):
    """Raised when clipboard or paste simulation fails.

    The clipboard could not be accessed or the Ctrl+V keystroke simulation
    failed. May occur if clipboard is locked by another application.
    """

    pass


class DatabaseError(VoxError):
    """Raised when database operations fail.

    SQLite operations failed, typically due to connection issues, schema
    problems, or constraint violations.
    """

    pass
