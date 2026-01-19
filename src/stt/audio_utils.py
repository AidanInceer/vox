"""Audio processing utilities for silence detection and analysis."""

import logging
import warnings
from typing import Callable, Optional

import numpy as np

# Suppress numpy warnings for invalid values (NaN, inf) in audio processing
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')

logger = logging.getLogger(__name__)


def calculate_rms(audio_chunk: np.ndarray) -> float:
    """Calculate Root Mean Square (RMS) energy of audio chunk.
    
    RMS provides a measure of the audio signal's amplitude, useful for
    detecting silence vs. speech.
    
    Args:
        audio_chunk: Audio samples as numpy array
    
    Returns:
        RMS energy value (higher = louder), or 0.0 if invalid
    """
    if audio_chunk is None or len(audio_chunk) == 0:
        return 0.0
    
    try:
        # Suppress all numpy warnings during calculation
        with np.errstate(all='ignore'):
            rms = np.sqrt(np.mean(audio_chunk ** 2))
        # Check for NaN or infinite values
        if np.isnan(rms) or np.isinf(rms):
            return 0.0
        return float(rms)
    except Exception:
        return 0.0


def detect_silence(audio_chunk: np.ndarray, threshold: float = 500.0) -> bool:
    """Detect if audio chunk is silent (below threshold).
    
    Args:
        audio_chunk: Audio samples as numpy array
        threshold: RMS threshold below which audio is considered silent
    
    Returns:
        True if chunk is silent, False if audio detected
    """
    rms = calculate_rms(audio_chunk)
    return rms < threshold


class SilenceDetector:
    """Stateful silence detector for tracking consecutive silent chunks.
    
    This class maintains state across multiple audio chunks to detect
    sustained periods of silence (e.g., 5 seconds) before stopping recording.
    
    Attributes:
        silence_duration: Target silence duration in seconds
        sample_rate: Audio sample rate in Hz
        chunk_duration: Duration of each audio chunk in seconds
        silent_chunks: Count of consecutive silent chunks detected
        required_chunks: Number of chunks needed to reach silence duration
    """

    def __init__(
        self,
        silence_duration: float = 5.0,
        sample_rate: int = 16000,
        chunk_duration: float = 0.1,
        silence_threshold: float = 500.0,
    ):
        """Initialize silence detector.
        
        Args:
            silence_duration: Seconds of silence to detect (default: 5.0)
            sample_rate: Audio sample rate in Hz (default: 16000)
            chunk_duration: Duration of each chunk in seconds (default: 0.1)
            silence_threshold: RMS threshold for silence detection
        """
        self.silence_duration = silence_duration
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.silence_threshold = silence_threshold
        self._silence_callback: Optional[Callable[[bool], None]] = None
        
        # Calculate how many chunks constitute the target silence duration
        self.required_chunks = int(silence_duration / chunk_duration)
        self.silent_chunks = 0
        
        logger.debug(
            f"SilenceDetector initialized: {silence_duration}s = "
            f"{self.required_chunks} chunks of {chunk_duration}s"
        )

    def process_chunk(self, audio_chunk: np.ndarray) -> bool:
        """Process audio chunk and update silence tracking state.
        
        Args:
            audio_chunk: Audio samples from microphone
        
        Returns:
            True if silence threshold reached, False otherwise
        """
        is_silent = detect_silence(
            audio_chunk, threshold=self.silence_threshold
        )
        
        # Notify callback if state changed
        prev_silent = self.silent_chunks > 0
        
        if is_silent:
            self.silent_chunks += 1
            if self.silent_chunks % 10 == 0:  # Log every 1 second
                logger.debug(
                    f"Silence: {self.silent_chunks}/{self.required_chunks} "
                    f"chunks"
                )
            
            # Notify when silence starts (2 seconds threshold for visual feedback)
            if not prev_silent and self.silent_chunks >= 20 and self._silence_callback:
                self._silence_callback(True)
        else:
            # Reset counter if sound detected
            if self.silent_chunks > 0:
                logger.debug("Sound detected, resetting silence counter")
                if self._silence_callback:
                    self._silence_callback(False)
            self.silent_chunks = 0
        
        return self.is_silence_threshold_reached()
    
    def set_silence_callback(self, callback: Callable[[bool], None]) -> None:
        """Set callback to notify about silence state changes.
        
        Args:
            callback: Function that receives boolean (True=silent, False=sound)
        """
        self._silence_callback = callback

    def is_silence_threshold_reached(self) -> bool:
        """Check if the required silence duration has been reached.
        
        Returns:
            True if sustained silence detected, False otherwise
        """
        return self.silent_chunks >= self.required_chunks

    def reset(self) -> None:
        """Reset silence detection state."""
        logger.debug("Resetting silence detector")
        self.silent_chunks = 0

    def get_status(self) -> dict:
        """Get current silence detection status.
        
        Returns:
            Dictionary with current state information
        """
        elapsed_silence = self.silent_chunks * self.chunk_duration
        return {
            "silent_chunks": self.silent_chunks,
            "required_chunks": self.required_chunks,
            "elapsed_silence_seconds": elapsed_silence,
            "target_silence_seconds": self.silence_duration,
            "threshold_reached": self.is_silence_threshold_reached(),
        }
