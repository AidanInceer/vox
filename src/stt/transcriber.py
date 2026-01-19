"""Main transcription orchestrator coordinating recording and STT."""

import logging
import tempfile
import time
from pathlib import Path
from typing import Optional

from colorama import Fore, Style

from src.config import DEFAULT_STT_MODEL, SAMPLE_RATE, SILENCE_DURATION
from src.stt.audio_utils import SilenceDetector
from src.stt.engine import STTEngine
from src.stt.recorder import MicrophoneRecorder
from src.stt.ui import RecordingIndicator, ProgressIndicator, format_transcription_result
from src.utils.errors import TranscriptionError

logger = logging.getLogger(__name__)


class Transcriber:
    """Orchestrates voice recording and transcription workflow.
    
    This class coordinates the complete speech-to-text pipeline:
    1. Record audio from microphone (with Enter or silence stop)
    2. Save recording to temporary WAV file
    3. Transcribe audio using Whisper model
    4. Display and optionally save transcription result
    
    Attributes:
        model_name: Whisper model size to use
        silence_duration: Seconds of silence before auto-stop
        engine: STT engine instance
        recorder: Microphone recorder instance
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        sample_rate: int = SAMPLE_RATE,
    ):
        """Initialize transcriber with model and recording settings.
        
        Args:
            model_name: Whisper model size or None to use saved default
            sample_rate: Audio sample rate in Hz (default: 16000)
        """
        # Use saved default model if none specified
        if model_name is None:
            from src.config import get_stt_default_model
            model_name = get_stt_default_model()
        
        self.model_name = model_name
        self.sample_rate = sample_rate
        
        logger.info(f"Initializing Transcriber: model={model_name}")
        
        # Initialize STT engine
        self.engine = STTEngine(model_name=model_name)
        
        # Initialize recorder (will be created fresh for each transcription)
        self.recorder: Optional[MicrophoneRecorder] = None

    def transcribe(
        self,
        output_file: Optional[Path] = None,
        language: str = "en",
    ) -> str:
        """Execute complete transcription workflow.
        
        This is the main entry point that:
        1. Records audio from microphone
        2. Transcribes to text
        3. Displays result
        4. Saves to file if requested
        
        Args:
            output_file: Optional path to save transcription
            language: Language code for transcription (default: "en")
        
        Returns:
            Transcribed text
        
        Raises:
            TranscriptionError: If transcription pipeline fails
        """
        try:
            # Show keyboard shortcuts hint
            print(f"\n{Fore.WHITE}💡 Tip:{Style.RESET_ALL} Press {Fore.YELLOW}Enter{Style.RESET_ALL} to stop recording\n")
            
            # Step 1: Record audio with visual feedback
            audio_data, duration = self._record_audio()
            
            # Step 2: Process recording (save and transcribe)
            text = self._process_recording(audio_data, language, duration)
            
            # Step 3: Display result with formatting
            self._display_result(text, duration)
            
            # Step 4: Save to file if requested
            if output_file:
                self._save_result(text, output_file)
            
            return text
            
        except Exception as e:
            if isinstance(e, (TranscriptionError, Exception)):
                logger.error(f"Transcription failed: {str(e)}")
                raise
            raise TranscriptionError(
                f"Transcription pipeline failed: {str(e)}",
                error_code="TRANSCRIPTION_PIPELINE_FAILED",
            ) from e

    def _record_audio(self) -> tuple["np.ndarray", float]:
        """Record audio from microphone with Enter key stop.
        
        Returns:
            Tuple of (audio samples, duration in seconds)
        """
        # Create fresh recorder without silence detection
        self.recorder = MicrophoneRecorder(
            sample_rate=self.sample_rate,
            channels=1,
            silence_detector=None,
        )
        
        # Get device info for visual feedback
        device_info = self.recorder.get_device_info()
        logger.info(f"Recording from: {device_info['device_name']}")
        
        # Create and start visual indicator
        indicator = RecordingIndicator(
            device_name=device_info['device_name'],
            show_audio_levels=True,
        )
        indicator.start()
        
        # Start recording
        start_time = time.time()
        self.recorder.start_recording()
        
        # Set callback to update visual indicator
        self.recorder.set_audio_callback(lambda chunk: indicator.update_audio_level(chunk))
        
        # Wait for Enter key
        self.recorder.wait_for_enter()
        
        # Stop recording and indicator
        audio_data = self.recorder.stop_recording()
        duration = time.time() - start_time
        indicator.stop()
        
        return audio_data, duration

    def _process_recording(self, audio_data: "np.ndarray", language: str, duration: float) -> str:
        """Save recording to WAV and transcribe to text.
        
        Args:
            audio_data: Recorded audio samples
            language: Language code for transcription
            duration: Recording duration in seconds
        
        Returns:
            Transcribed text
        """
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Save audio to WAV
            if self.recorder:
                self.recorder.save_wav(audio_data, tmp_path)
            else:
                raise TranscriptionError(
                    "Recorder not initialized",
                    error_code="RECORDER_NOT_INITIALIZED",
                )
            
            # Show progress indicator
            progress = ProgressIndicator(
                message=f"Transcribing with {self.model_name} model...",
                show_spinner=True,
            )
            progress.start()
            
            # Transcribe WAV file
            text = self.engine.transcribe_audio(tmp_path, language=language)
            
            progress.stop(success=True)
            
            return text
            
        finally:
            # Clean up temporary file
            if tmp_path.exists():
                tmp_path.unlink()
                logger.debug(f"Cleaned up temporary file: {tmp_path}")

    def _display_result(self, text: str, duration: float) -> None:
        """Display transcription result to terminal with formatting.
        
        Args:
            text: Transcribed text to display
            duration: Recording duration in seconds
        """
        # Use formatted output from ui module
        formatted = format_transcription_result(
            text=text,
            duration=duration,
            model_name=self.model_name,
            confidence=None,  # TODO: Extract from Whisper segments if available
        )
        print(f"\n{formatted}\n")

    def _save_result(self, text: str, output_file: Path) -> None:
        """Save transcription to file.
        
        Args:
            text: Transcribed text
            output_file: Path to output file
        """
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(text, encoding="utf-8")
            print(f"✅ Saved to: {output_file}")
            logger.info(f"Transcription saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            print(f"⚠️  Warning: Could not save to file: {e}")

    def get_model_info(self) -> dict:
        """Get information about the transcription setup.
        
        Returns:
            Dictionary with configuration details
        """
        return {
            "model_name": self.model_name,
            "silence_duration": self.silence_duration,
            "sample_rate": self.sample_rate,
            "engine_info": self.engine.get_model_info() if self.engine else None,
            "recorder_info": self.recorder.get_device_info() if self.recorder else None,
        }
