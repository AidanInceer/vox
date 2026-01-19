"""Whisper-based speech-to-text engine for vox."""

import logging
import os
from pathlib import Path
from typing import Optional

# Suppress huggingface_hub symlink warning on Windows
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from faster_whisper import WhisperModel

from src.config import DEFAULT_STT_MODEL, STT_MODEL_CACHE
from src.utils.errors import ModelLoadError, TranscriptionError

logger = logging.getLogger(__name__)


class STTEngine:
    """Wrapper for faster-whisper model handling and transcription.
    
    This class manages Whisper model lifecycle (loading, caching) and provides
    a simple interface for transcribing audio files to text.
    
    Attributes:
        model_name: Whisper model size (tiny, base, small, medium, large)
        model: Loaded WhisperModel instance
        model_path: Path to cached model files
    """

    def __init__(self, model_name: str = DEFAULT_STT_MODEL):
        """Initialize STT engine with specified Whisper model.
        
        Args:
            model_name: Model size identifier (default: "medium")
        
        Raises:
            ModelLoadError: If model loading fails
        """
        self.model_name = model_name
        self.model_path = STT_MODEL_CACHE
        self.model: Optional[WhisperModel] = None
        
        logger.info(f"Initializing STT engine with model: {model_name}")
        self._load_model()

    def _check_model_cache(self) -> bool:
        """Check if model files exist in cache directory.
        
        Returns:
            True if model is cached, False otherwise
        """
        model_dir = self.model_path / self.model_name
        return model_dir.exists() and any(model_dir.iterdir())

    def _load_model(self) -> None:
        """Load Whisper model from cache or download if necessary.
        
        Raises:
            ModelLoadError: If model loading fails
        """
        from src.stt.ui import ProgressIndicator
        
        try:
            # Ensure cache directory exists
            self.model_path.mkdir(parents=True, exist_ok=True)
            
            # Estimate model size for user feedback
            model_sizes = {
                "tiny": "75 MB",
                "base": "142 MB",
                "small": "466 MB",
                "medium": "1.5 GB",
                "large": "2.9 GB",
            }
            size_str = model_sizes.get(self.model_name, "unknown size")
            
            # Show progress indicator
            if self._check_model_cache():
                progress = ProgressIndicator(
                    message=f"Loading {self.model_name} model from cache...",
                    show_spinner=True,
                )
            else:
                progress = ProgressIndicator(
                    message=f"Downloading {self.model_name} model ({size_str})...",
                    show_spinner=True,
                )
            
            progress.start()
            
            # Load model with CTranslate2 backend for speed
            self.model = WhisperModel(
                self.model_name,
                device="cpu",
                compute_type="int8",
                download_root=str(self.model_path),
            )
            
            progress.stop(success=True)
            
        except Exception as e:
            error_msg = (
                f"Failed to load Whisper model '{self.model_name}': "
                f"{str(e)}"
            )
            logger.error(error_msg)
            raise ModelLoadError(
                error_msg,
                error_code="MODEL_LOAD_FAILED",
                context={
                    "model_name": self.model_name,
                    "cache_path": str(self.model_path),
                },
            ) from e

    def transcribe_audio(self, audio_path: Path, language: str = "en") -> str:
        """Transcribe audio file to text using Whisper model.
        
        Args:
            audio_path: Path to WAV audio file (16kHz, mono, 16-bit PCM)
            language: Language code for transcription (default: "en")
        
        Returns:
            Transcribed text as a single string
        
        Raises:
            TranscriptionError: If transcription fails
        """
        if not audio_path.exists():
            raise TranscriptionError(
                f"Audio file not found: {audio_path}",
                error_code="AUDIO_FILE_NOT_FOUND",
                context={"audio_path": str(audio_path)},
            )
        
        if self.model is None:
            raise TranscriptionError(
                "Model not loaded",
                error_code="MODEL_NOT_LOADED",
            )
        
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Transcribe with language specification and beam search
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language,
                beam_size=5,
                vad_filter=True,  # Voice activity detection to filter silence
            )
            
            # Extract text from segments
            text = self._extract_text(segments)
            
            logger.info(
                f"Transcription complete: {len(text)} characters, "
                f"language: {info.language}, "
                f"probability: {info.language_probability:.2f}"
            )
            
            return text
            
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(error_msg)
            raise TranscriptionError(
                error_msg,
                error_code="TRANSCRIPTION_FAILED",
                context={"audio_path": str(audio_path)},
            ) from e

    def _extract_text(self, segments) -> str:
        """Extract and concatenate text from transcription segments.
        
        Args:
            segments: Iterator of segment objects from faster-whisper
        
        Returns:
            Combined text from all segments
        """
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())
        
        # Join with spaces, ensuring no double spaces
        full_text = " ".join(text_parts)
        return full_text.strip()

    def get_model_info(self) -> dict:
        """Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "model_name": self.model_name,
            "model_path": str(self.model_path),
            "is_loaded": self.model is not None,
            "is_cached": self._check_model_cache(),
        }
