"""Configuration management and application constants."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

# Application metadata
APP_NAME: Final[str] = "vox"
APP_VERSION: Final[str] = "3.0.0"
APP_DESCRIPTION: Final[str] = "Desktop bidirectional audio-text conversion with TTS and STT"

# Directories
BASE_DIR: Final[Path] = Path(__file__).parent.parent.parent
SRC_DIR: Final[Path] = BASE_DIR / "src"
TESTS_DIR: Final[Path] = BASE_DIR / "tests"
DATA_DIR: Final[Path] = BASE_DIR / "data"
CACHE_DIR: Final[Path] = DATA_DIR / "cache"
LOGS_DIR: Final[Path] = BASE_DIR / "logs"
SESSION_STORAGE_DIR: Final[Path] = Path(os.getenv("APPDATA", ".")) / "vox" / "sessions"
STT_MODEL_CACHE: Final[Path] = Path(os.getenv("APPDATA", ".")) / "vox" / "models"
USER_CONFIG_DIR: Final[Path] = Path(os.getenv("APPDATA", ".")) / "vox"
USER_CONFIG_FILE: Final[Path] = USER_CONFIG_DIR / "config.json"

# Ensure necessary directories exist
for directory in [DATA_DIR, CACHE_DIR, LOGS_DIR, SESSION_STORAGE_DIR, STT_MODEL_CACHE, USER_CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# TTS Configuration
DEFAULT_TTS_PROVIDER: Final[str] = "piper"  # Options: "piper", future: "azure", "google"
DEFAULT_TTS_VOICE: Final[str] = "en_US-libritts-high"
DEFAULT_TTS_SPEED: Final[float] = 1.0
TTS_CACHE_ENABLED: Final[bool] = True
TTS_CACHE_TTL_HOURS: Final[int] = 24

# STT Configuration
DEFAULT_STT_MODEL: Final[str] = "medium"  # Options: "tiny", "base", "small", "medium", "large"
SILENCE_DURATION: Final[float] = 5.0  # seconds of silence before auto-stop
SAMPLE_RATE: Final[int] = 16000  # Hz - required for Whisper model

# Browser Detection
SUPPORTED_BROWSERS: Final[list[str]] = ["chrome", "edge", "firefox", "opera", "brave"]
BROWSER_TAB_DETECTION_TIMEOUT: Final[float] = 5.0  # seconds
BROWSER_WINDOW_CLASS_NAMES: Final[dict] = {
    "chrome": "Chrome_WidgetWin_1",
    "edge": "Chrome_WidgetWin_1",
    "firefox": "MozillaWindowClass",
    "opera": "OperaWindowClass",
    "brave": "Chrome_WidgetWin_1",
}

# Text Extraction
TEXT_EXTRACTION_TIMEOUT: Final[float] = 3.0  # seconds
MIN_TEXT_LENGTH: Final[int] = 10  # minimum characters to attempt synthesis
MAX_TEXT_LENGTH: Final[int] = 100000  # maximum characters to process

# Audio Playback
DEFAULT_PLAYBACK_VOLUME: Final[float] = 1.0  # 0.0 - 1.0
MIN_PLAYBACK_SPEED: Final[float] = 0.5
MAX_PLAYBACK_SPEED: Final[float] = 2.0
AUDIO_DEVICE_INDEX: Final[int] = -1  # -1 = default device

# Chunking Configuration
DEFAULT_CHUNK_SIZE: Final[int] = 150  # words per chunk
MAX_BUFFER_SIZE: Final[int] = 10  # maximum chunks in buffer

# Performance Targets
PERFORMANCE_TARGETS: Final[dict] = {
    "text_extraction_seconds": 3.0,
    "tts_synthesis_seconds": 5.0,
    "tab_detection_seconds": 2.0,
    "session_resume_seconds": 1.0,
}

# Memory & Resource Limits
MAX_MEMORY_MB: Final[int] = 300
MAX_CACHE_SIZE_MB: Final[int] = 500

# Logging
LOG_LEVEL: Final[str] = os.getenv("VOX_LOG_LEVEL", "INFO")
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE_SIZE_MB: Final[int] = 10
LOG_BACKUP_COUNT: Final[int] = 5

# Feature Flags
ENABLE_SESSION_PERSISTENCE: Final[bool] = True
ENABLE_CACHE: Final[bool] = True
ENABLE_ERROR_REPORTING: Final[bool] = False

# Development
DEBUG: Final[bool] = os.getenv("VOX_DEBUG", "false").lower() == "true"
TEST_MODE: Final[bool] = os.getenv("VOX_TEST", "false").lower() == "true"


# User Configuration Management

VALID_STT_MODELS: Final[list[str]] = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]

DEFAULT_USER_CONFIG: Final[dict[str, Any]] = {
    "stt": {
        "default_model": DEFAULT_STT_MODEL,
        "silence_duration": SILENCE_DURATION,
    },
    "tts": {
        "default_voice": DEFAULT_TTS_VOICE,
        "default_speed": DEFAULT_TTS_SPEED,
    },
}


def load_user_config() -> dict[str, Any]:
    """Load user configuration from config.json.

    Returns:
        User configuration dictionary. Returns default config if file doesn't exist
        or if loading fails.
    """
    if not USER_CONFIG_FILE.exists():
        logger.debug(f"Config file not found at {USER_CONFIG_FILE}, using defaults")
        return DEFAULT_USER_CONFIG.copy()

    try:
        with USER_CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info(f"Loaded user config from {USER_CONFIG_FILE}")
        return config
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in config file: {e}, using defaults")
        return DEFAULT_USER_CONFIG.copy()
    except Exception as e:
        logger.error(f"Failed to load config file: {e}, using defaults")
        return DEFAULT_USER_CONFIG.copy()


def save_user_config(config: dict[str, Any]) -> bool:
    """Save user configuration to config.json.

    Args:
        config: Configuration dictionary to save

    Returns:
        True if save successful, False otherwise
    """
    try:
        # Validate STT model if present
        if "stt" in config and "default_model" in config["stt"]:
            model = config["stt"]["default_model"]
            if model not in VALID_STT_MODELS:
                logger.error(f"Invalid STT model '{model}', valid options: {VALID_STT_MODELS}")
                return False

        # Write config with pretty formatting
        with USER_CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Saved user config to {USER_CONFIG_FILE}")
        return True

    except Exception as e:
        logger.error(f"Failed to save config file: {e}")
        return False


def get_stt_default_model() -> str:
    """Get the default STT model from user config.

    Returns:
        Model name string (e.g., "medium")
    """
    config = load_user_config()
    return config.get("stt", {}).get("default_model", DEFAULT_STT_MODEL)


def set_stt_default_model(model: str) -> bool:
    """Set the default STT model in user config.

    Args:
        model: Model name (e.g., "medium")

    Returns:
        True if successful, False otherwise
    """
    if model not in VALID_STT_MODELS:
        logger.error(f"Invalid STT model '{model}', valid options: {VALID_STT_MODELS}")
        return False

    config = load_user_config()
    if "stt" not in config:
        config["stt"] = {}
    config["stt"]["default_model"] = model

    return save_user_config(config)


def create_default_config() -> bool:
    """Create default config.json file if it doesn't exist.

    Returns:
        True if created successfully or already exists, False on error
    """
    if USER_CONFIG_FILE.exists():
        logger.debug("Config file already exists")
        return True

    return save_user_config(DEFAULT_USER_CONFIG)
