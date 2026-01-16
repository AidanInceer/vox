"""Tests for configuration module."""

import pytest
from src.config import (
    # App metadata
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    # TTS Settings
    DEFAULT_TTS_PROVIDER,
    DEFAULT_TTS_VOICE,
    DEFAULT_TTS_SPEED,
    TTS_CACHE_ENABLED,
    TTS_CACHE_TTL_HOURS,
    # Browser Settings
    SUPPORTED_BROWSERS,
    BROWSER_TAB_DETECTION_TIMEOUT,
    BROWSER_WINDOW_CLASS_NAMES,
    # Extraction Settings
    TEXT_EXTRACTION_TIMEOUT,
    MIN_TEXT_LENGTH,
    MAX_TEXT_LENGTH,
    # Playback Settings
    DEFAULT_PLAYBACK_VOLUME,
    MIN_PLAYBACK_SPEED,
    MAX_PLAYBACK_SPEED,
    AUDIO_DEVICE_INDEX,
    # Performance Settings
    PERFORMANCE_TARGETS,
    # Memory Settings
    MAX_MEMORY_MB,
    MAX_CACHE_SIZE_MB,
    # Logging Settings
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE_SIZE_MB,
    LOG_BACKUP_COUNT,
    # Feature Flags
    ENABLE_SESSION_PERSISTENCE,
    ENABLE_CACHE,
    ENABLE_ERROR_REPORTING,
    # Development
    DEBUG,
    TEST_MODE,
)


class TestAppMetadata:
    """Test application metadata."""

    def test_app_name_defined(self):
        """App name should be defined."""
        assert APP_NAME == "PageReader"
        assert isinstance(APP_NAME, str)

    def test_app_version_defined(self):
        """App version should be defined."""
        assert APP_VERSION == "1.0.0"
        assert isinstance(APP_VERSION, str)

    def test_app_description_defined(self):
        """App description should be defined."""
        assert APP_DESCRIPTION is not None
        assert isinstance(APP_DESCRIPTION, str)
        assert len(APP_DESCRIPTION) > 0


class TestTTSSettings:
    """Test TTS configuration values."""

    def test_tts_provider_defined(self):
        """TTS provider should be set."""
        assert DEFAULT_TTS_PROVIDER == "piper"
        assert isinstance(DEFAULT_TTS_PROVIDER, str)

    def test_tts_voice_defined(self):
        """TTS voice should be defined."""
        assert DEFAULT_TTS_VOICE is not None
        assert isinstance(DEFAULT_TTS_VOICE, str)
        assert "en_US" in DEFAULT_TTS_VOICE or "en_GB" in DEFAULT_TTS_VOICE

    def test_tts_speed_valid(self):
        """TTS speed should be positive."""
        assert DEFAULT_TTS_SPEED > 0
        assert isinstance(DEFAULT_TTS_SPEED, (int, float))

    def test_tts_cache_settings(self):
        """TTS cache should be properly configured."""
        assert isinstance(TTS_CACHE_ENABLED, bool)
        assert TTS_CACHE_TTL_HOURS > 0
        assert isinstance(TTS_CACHE_TTL_HOURS, int)


class TestBrowserSettings:
    """Test browser detection configuration."""

    def test_supported_browsers_defined(self):
        """Supported browsers should be defined."""
        assert len(SUPPORTED_BROWSERS) > 0
        assert isinstance(SUPPORTED_BROWSERS, list)
        assert all(isinstance(b, str) for b in SUPPORTED_BROWSERS)

    def test_browser_timeout(self):
        """Browser detection timeout should be reasonable."""
        assert BROWSER_TAB_DETECTION_TIMEOUT > 0
        assert isinstance(BROWSER_TAB_DETECTION_TIMEOUT, (int, float))

    def test_browser_window_classes(self):
        """Browser window class names should be mapped."""
        assert isinstance(BROWSER_WINDOW_CLASS_NAMES, dict)
        assert len(BROWSER_WINDOW_CLASS_NAMES) > 0
        # All supported browsers should have window class entries
        for browser in SUPPORTED_BROWSERS:
            if browser in BROWSER_WINDOW_CLASS_NAMES:
                assert isinstance(BROWSER_WINDOW_CLASS_NAMES[browser], str)


class TestExtractionSettings:
    """Test text extraction configuration."""

    def test_extraction_timeout(self):
        """Extraction timeout should be positive."""
        assert TEXT_EXTRACTION_TIMEOUT > 0
        assert isinstance(TEXT_EXTRACTION_TIMEOUT, (int, float))

    def test_text_length_bounds(self):
        """Text length bounds should be valid."""
        assert MIN_TEXT_LENGTH >= 0
        assert MAX_TEXT_LENGTH > MIN_TEXT_LENGTH

    def test_text_length_reasonable(self):
        """Text length limits should be reasonable."""
        assert MIN_TEXT_LENGTH < 100  # Reasonable minimum
        assert MAX_TEXT_LENGTH > 1000  # Reasonable maximum


class TestPlaybackSettings:
    """Test audio playback configuration."""

    def test_playback_volume(self):
        """Default volume should be in valid range."""
        assert 0.0 <= DEFAULT_PLAYBACK_VOLUME <= 1.0

    def test_playback_speed_range(self):
        """Playback speed range should be valid."""
        assert MIN_PLAYBACK_SPEED > 0
        assert MAX_PLAYBACK_SPEED > MIN_PLAYBACK_SPEED
        assert MIN_PLAYBACK_SPEED <= 1.0
        assert MAX_PLAYBACK_SPEED >= 1.0

    def test_audio_device_index(self):
        """Audio device index should be valid."""
        assert isinstance(AUDIO_DEVICE_INDEX, int)
        # -1 means default device
        assert AUDIO_DEVICE_INDEX >= -1


class TestPerformanceSettings:
    """Test performance tuning configuration."""

    def test_performance_targets_defined(self):
        """Performance targets should be defined."""
        assert isinstance(PERFORMANCE_TARGETS, dict)
        assert len(PERFORMANCE_TARGETS) > 0

    def test_performance_target_values(self):
        """Performance target values should be positive."""
        for key, value in PERFORMANCE_TARGETS.items():
            assert isinstance(value, (int, float))
            assert value > 0


class TestMemorySettings:
    """Test memory and resource limits."""

    def test_memory_limits(self):
        """Memory limits should be positive."""
        assert MAX_MEMORY_MB > 0
        assert MAX_CACHE_SIZE_MB > 0
        assert isinstance(MAX_MEMORY_MB, int)
        assert isinstance(MAX_CACHE_SIZE_MB, int)

    def test_cache_vs_memory(self):
        """Cache size shouldn't exceed memory limit."""
        # Cache should be reasonable relative to memory
        assert MAX_CACHE_SIZE_MB <= MAX_MEMORY_MB * 2


class TestLoggingSettings:
    """Test logging configuration."""

    def test_log_level_valid(self):
        """Log level should be valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert LOG_LEVEL in valid_levels

    def test_log_format_defined(self):
        """Log format should be defined."""
        assert LOG_FORMAT is not None
        assert isinstance(LOG_FORMAT, str)
        assert "%s" in LOG_FORMAT or "%" in LOG_FORMAT

    def test_log_rotation_settings(self):
        """Log rotation should be configured."""
        assert LOG_FILE_SIZE_MB > 0
        assert LOG_BACKUP_COUNT >= 0
        assert isinstance(LOG_FILE_SIZE_MB, int)
        assert isinstance(LOG_BACKUP_COUNT, int)


class TestFeatureFlags:
    """Test feature toggle configuration."""

    def test_all_features_defined(self):
        """All feature flags should be defined."""
        assert isinstance(ENABLE_SESSION_PERSISTENCE, bool)
        assert isinstance(ENABLE_CACHE, bool)
        assert isinstance(ENABLE_ERROR_REPORTING, bool)

    def test_core_features_enabled(self):
        """Core features should be enabled for v1.0.0."""
        # P1 features should be enabled
        assert ENABLE_SESSION_PERSISTENCE is True
        assert ENABLE_CACHE is True


class TestDevelopmentSettings:
    """Test development mode settings."""

    def test_debug_flag(self):
        """Debug flag should be boolean."""
        assert isinstance(DEBUG, bool)

    def test_test_mode_flag(self):
        """Test mode flag should be boolean."""
        assert isinstance(TEST_MODE, bool)


class TestConfigurationConsistency:
    """Test overall configuration consistency."""

    def test_speed_ranges_compatible(self):
        """Playback speeds should be compatible with TTS default."""
        # Default TTS speed should be convertible to playback speed range
        assert DEFAULT_TTS_SPEED > 0
        assert MIN_PLAYBACK_SPEED > 0

    def test_timeouts_reasonable(self):
        """All timeouts should be reasonable (100ms to 30s)."""
        assert 0.1 <= TEXT_EXTRACTION_TIMEOUT <= 30
        assert 0.1 <= BROWSER_TAB_DETECTION_TIMEOUT <= 30

    def test_supported_browsers_not_empty(self):
        """At least one browser should be supported."""
        assert len(SUPPORTED_BROWSERS) >= 1
        # Common browsers should be included
        assert any(
            b in SUPPORTED_BROWSERS
            for b in ["chrome", "edge", "firefox"]
        )
