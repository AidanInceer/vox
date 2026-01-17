"""Abstract interface and concrete implementations for text-to-speech synthesis."""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from src.tts.piper_provider import get_available_voices, synthesize_piper
from src.utils.errors import TTSError

logger = logging.getLogger(__name__)


# Cache directory for synthesized audio
TTS_CACHE_DIR = Path.home() / ".cache" / "pagereader" / "tts"
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class Synthesizer(ABC):
    """Abstract base class for text-to-speech synthesis.

    Implementations:
        - PiperSynthesizer: Open-source neural TTS via Piper
        - (Future) AzureSynthesizer: Cloud-based TTS via Azure
        - (Future) GoogleSynthesizer: Cloud-based TTS via Google Cloud
    """

    @abstractmethod
    def synthesize(self, text: str, speed: float = 1.0) -> bytes:
        """Synthesize text to speech audio bytes.

        Args:
            text: Text to synthesize
            speed: Speech speed multiplier (0.5x to 2.0x)

        Returns:
            Audio bytes in WAV format

        Raises:
            TTSError: If synthesis fails
            ValidationError: If text is empty or invalid
            TimeoutError: If synthesis exceeds timeout
        """
        pass

    @abstractmethod
    def get_voices(self) -> list[str]:
        """Get list of available voices for this synthesizer.

        Returns:
            List of voice identifiers available in this TTS engine
        """
        pass

    @abstractmethod
    def set_voice(self, voice: str) -> None:
        """Set the voice to use for synthesis.

        Args:
            voice: Voice identifier from get_voices()

        Raises:
            ValidationError: If voice is not available
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if TTS engine is available and functional.

        Returns:
            True if TTS engine is initialized and ready to use
        """
        pass


class PiperSynthesizer(Synthesizer):
    """Concrete synthesizer implementation using Piper neural TTS.

    Features:
    - Runs completely offline (no API keys or internet required)
    - High-quality neural voices
    - Fast synthesis with configurable speed
    - Caches synthesized audio to avoid re-synthesis
    """

    def __init__(self, voice: str = "en_US-libritts-high", use_cache: bool = True):
        """Initialize Piper synthesizer.

        Args:
            voice: Default voice to use for synthesis
            use_cache: Whether to cache synthesized audio
        """
        self.voice = voice
        self.use_cache = use_cache
        self._available_voices = get_available_voices()

        # Validate voice
        if voice not in self._available_voices:
            logger.warning(f"Voice {voice} not in available list, continuing anyway")

    def synthesize(self, text: str, speed: float = 1.0) -> bytes:
        """Synthesize text to speech using Piper.

        Args:
            text: Text to synthesize
            speed: Speech speed multiplier (0.5 to 2.0)

        Returns:
            Audio bytes in WAV format

        Raises:
            TTSError: If synthesis fails
        """
        if not text or not isinstance(text, str):
            raise TTSError("Text must be a non-empty string")

        if not 0.5 <= speed <= 2.0:
            raise TTSError(f"Speed must be 0.5-2.0, got {speed}")

        try:
            # Check cache first
            if self.use_cache:
                cached_audio = self._get_cached_audio(text, speed)
                if cached_audio:
                    logger.debug("Using cached audio for text (cache hit)")
                    return cached_audio

            # Synthesize new audio
            logger.info(f"Synthesizing audio: {len(text)} chars with {self.voice}")
            audio_bytes = synthesize_piper(text, voice=self.voice, speed=speed)

            # Cache the result
            if self.use_cache:
                self._cache_audio(text, speed, audio_bytes)

            return audio_bytes

        except TTSError:
            raise
        except Exception as e:
            raise TTSError(f"Piper synthesis failed: {str(e)}") from e

    def get_voices(self) -> List[str]:
        """Get list of available Piper voices.

        Returns:
            List of voice identifiers
        """
        return self._available_voices.copy()

    def set_voice(self, voice: str) -> None:
        """Set the voice to use for synthesis.

        Args:
            voice: Voice identifier

        Raises:
            TTSError: If voice is not available
        """
        if voice not in self._available_voices:
            raise TTSError(f"Voice '{voice}' not available. Available: {', '.join(self._available_voices[:3])}...")

        self.voice = voice
        logger.info(f"Voice set to {voice}")

    def is_available(self) -> bool:
        """Check if Piper TTS is available and functional.

        Returns:
            True if Piper is installed and can synthesize
        """
        try:
            # Try a quick synthesis to verify it works
            test_audio = synthesize_piper("test", voice=self.voice)
            return bool(test_audio)
        except Exception as e:
            logger.warning(f"Piper availability check failed: {e}")
            return False

    def _get_cache_key(self, text: str, speed: float) -> str:
        """Generate cache key for text and speed combination.

        Args:
            text: Text to synthesize
            speed: Speed parameter

        Returns:
            Cache key string
        """
        cache_input = f"{text}|{speed}|{self.voice}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    def _get_cached_audio(self, text: str, speed: float) -> Optional[bytes]:
        """Get audio from cache if available.

        Args:
            text: Text to synthesize
            speed: Speed parameter

        Returns:
            Cached audio bytes, or None if not in cache
        """
        try:
            cache_key = self._get_cache_key(text, speed)
            cache_file = TTS_CACHE_DIR / f"{cache_key}.wav"

            if cache_file.exists():
                with open(cache_file, "rb") as f:
                    audio = f.read()
                logger.debug(f"Cache hit for key {cache_key}")
                return audio

            return None

        except Exception as e:
            logger.debug(f"Cache lookup failed: {e}")
            return None

    def _cache_audio(self, text: str, speed: float, audio_bytes: bytes) -> None:
        """Cache synthesized audio.

        Args:
            text: Original text
            speed: Speed parameter
            audio_bytes: Audio data to cache
        """
        try:
            cache_key = self._get_cache_key(text, speed)
            cache_file = TTS_CACHE_DIR / f"{cache_key}.wav"

            # Also save metadata
            metadata = {
                "text": text[:200],  # First 200 chars only
                "speed": speed,
                "voice": self.voice,
                "length_chars": len(text),
            }

            with open(cache_file, "wb") as f:
                f.write(audio_bytes)

            metadata_file = TTS_CACHE_DIR / f"{cache_key}.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f)

            logger.debug(f"Cached audio: {cache_key}")

        except Exception as e:
            logger.warning(f"Failed to cache audio: {e}")

    def clear_cache(self) -> None:
        """Clear the synthesis cache.

        This removes all cached audio files.
        """
        try:
            for cache_file in TTS_CACHE_DIR.glob("*.wav"):
                cache_file.unlink()
            for metadata_file in TTS_CACHE_DIR.glob("*.json"):
                metadata_file.unlink()

            logger.info("Cleared TTS cache")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
