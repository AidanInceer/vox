"""Abstract interface for text-to-speech synthesis."""

from abc import ABC, abstractmethod


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
