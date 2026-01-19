"""Microphone audio recording for vox speech-to-text."""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from src.config import SAMPLE_RATE
from src.stt.audio_utils import SilenceDetector
from src.utils.errors import MicrophoneError

logger = logging.getLogger(__name__)


class MicrophoneRecorder:
    """Handles microphone audio capture with Enter key and silence detection.
    
    This class manages real-time audio recording from the default system
    microphone, providing both manual (Enter key) and automatic (silence
    detection) stopping mechanisms.
    
    Attributes:
        sample_rate: Audio sampling rate in Hz (16kHz for Whisper)
        channels: Number of audio channels (1 = mono)
        device_id: System device ID for microphone
        device_name: Human-readable device name
        audio_chunks: List of recorded audio chunks
        is_recording: Flag indicating recording state
        silence_detector: Optional silence detection for auto-stop
    """

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = 1,
        device_id: Optional[int] = None,
        silence_detector: Optional[SilenceDetector] = None,
    ):
        """Initialize microphone recorder.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 16000)
            channels: Number of channels, 1=mono (default: 1)
            device_id: Specific device ID or None for default
            silence_detector: Optional silence detector for auto-stop
        
        Raises:
            MicrophoneError: If microphone detection or setup fails
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_detector = silence_detector
        self.audio_chunks: list[np.ndarray] = []
        self.is_recording = False
        self._stream: Optional[sd.InputStream] = None
        self._stop_event = threading.Event()
        self._audio_level_callback: Optional[Callable[[np.ndarray], None]] = None
        
        # Detect and validate microphone device
        device_info = self._detect_default_device(device_id)
        self.device_id, self.device_name = device_info
        self._validate_device()
        
        logger.info(
            f"MicrophoneRecorder initialized: device={self.device_name}, "
            f"rate={sample_rate}Hz, channels={channels}"
        )

    def _detect_default_device(
        self, device_id: Optional[int]
    ) -> tuple[int, str]:
        """Detect default or specified microphone device.
        
        Args:
            device_id: Optional specific device ID
        
        Returns:
            Tuple of (device_id, device_name)
        
        Raises:
            MicrophoneError: If no input device found
        """
        try:
            if device_id is not None:
                device_info = sd.query_devices(device_id)
                return device_id, device_info["name"]
            
            # Get default input device
            default_device = sd.query_devices(kind="input")
            device_id = sd.default.device[0]  # Input device index
            
            logger.info(f"Using default microphone: {default_device['name']}")
            return device_id, default_device["name"]
            
        except Exception as e:
            error_msg = "No microphone detected. Please connect a microphone and try again."
            logger.error(f"{error_msg} Details: {str(e)}")
            raise MicrophoneError(
                error_msg,
                error_code="NO_MICROPHONE_DETECTED",
                context={"system_error": str(e)},
            ) from e

    def _validate_device(self) -> None:
        """Validate that the selected device supports recording.
        
        Raises:
            MicrophoneError: If device validation fails
        """
        try:
            device_info = sd.query_devices(self.device_id)
            
            if device_info["max_input_channels"] < self.channels:
                raise MicrophoneError(
                    f"Device '{self.device_name}' does not support {self.channels} input channels",
                    error_code="UNSUPPORTED_CHANNEL_CONFIG",
                    context={
                        "device": self.device_name,
                        "requested_channels": self.channels,
                        "max_channels": device_info["max_input_channels"],
                    },
                )
            
            logger.debug(f"Device validation passed: {device_info}")
            
        except MicrophoneError:
            raise
        except Exception as e:
            raise MicrophoneError(
                f"Failed to validate microphone device: {str(e)}",
                error_code="DEVICE_VALIDATION_FAILED",
                context={"device_id": self.device_id},
            ) from e

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """Callback function for sounddevice stream to process audio chunks.
        
        Args:
            indata: Input audio data from microphone
            frames: Number of frames in chunk
            time_info: Time information dict
            status: Stream status flags
        """
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        # Store audio chunk (copy to avoid buffer reuse issues)
        audio_chunk = indata.copy()
        self.audio_chunks.append(audio_chunk)
        
        # Notify callback for visual feedback
        if self._audio_level_callback:
            self._audio_level_callback(audio_chunk)
        
        # Check for silence if detector is enabled
        if self.silence_detector:
            if self.silence_detector.process_chunk(audio_chunk.flatten()):
                logger.info("Silence threshold reached, stopping recording")
                self._stop_event.set()
    
    def set_audio_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """Set callback function to receive audio chunks for visual feedback.
        
        Args:
            callback: Function that receives audio chunk as numpy array
        """
        self._audio_level_callback = callback

    def start_recording(self) -> None:
        """Start recording audio from microphone.
        
        Raises:
            MicrophoneError: If recording cannot start
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return
        
        try:
            # Reset state
            self.audio_chunks = []
            self._stop_event.clear()
            if self.silence_detector:
                self.silence_detector.reset()
            
            # Start audio stream with callback
            self._stream = sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                callback=self._audio_callback,
                blocksize=int(self.sample_rate * 0.1),  # 100ms chunks
            )
            
            self._stream.start()
            self.is_recording = True
            
            logger.info("Recording started")
            
        except Exception as e:
            error_msg = f"Failed to start recording: {str(e)}"
            logger.error(error_msg)
            raise MicrophoneError(
                error_msg,
                error_code="RECORDING_START_FAILED",
                context={"device": self.device_name},
            ) from e

    def stop_recording(self) -> np.ndarray:
        """Stop recording and return concatenated audio data.
        
        Returns:
            Numpy array of audio samples (int16)
        
        Raises:
            MicrophoneError: If no audio was recorded
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return np.array([], dtype=np.int16)
        
        try:
            # Stop and close stream
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            
            self.is_recording = False
            logger.info(f"Recording stopped, collected {len(self.audio_chunks)} chunks")
            
            # Concatenate all audio chunks
            if not self.audio_chunks:
                raise MicrophoneError(
                    "No audio data recorded",
                    error_code="NO_AUDIO_RECORDED",
                )
            
            audio_data = np.concatenate(self.audio_chunks, axis=0)
            duration = len(audio_data) / self.sample_rate
            
            logger.info(f"Total recording duration: {duration:.2f} seconds")
            
            return audio_data.flatten().astype(np.int16)
            
        except MicrophoneError:
            raise
        except Exception as e:
            error_msg = f"Failed to stop recording: {str(e)}"
            logger.error(error_msg)
            raise MicrophoneError(
                error_msg,
                error_code="RECORDING_STOP_FAILED",
            ) from e

    def wait_for_enter(self) -> None:
        """Block until Enter key is pressed or silence detected.
        
        This runs in the main thread and monitors both keyboard input
        and the silence detection stop event.
        """
        # Use a separate thread to monitor Enter key
        def wait_for_input():
            try:
                input()
                self._stop_event.set()
            except Exception as e:
                logger.error(f"Input monitoring error: {e}")
        
        input_thread = threading.Thread(target=wait_for_input, daemon=True)
        input_thread.start()
        
        # Wait for either Enter key or silence detection
        self._stop_event.wait()

    def save_wav(self, audio_data: np.ndarray, output_path: Path) -> None:
        """Save audio data as WAV file.
        
        Args:
            audio_data: Audio samples to save
            output_path: Path to output WAV file
        
        Raises:
            MicrophoneError: If file writing fails
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Ensure correct shape for scipy.io.wavfile
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(-1, 1)
            
            wavfile.write(output_path, self.sample_rate, audio_data)
            
            file_size = output_path.stat().st_size / 1024  # KB
            logger.info(f"Audio saved to {output_path} ({file_size:.1f} KB)")
            
        except Exception as e:
            error_msg = f"Failed to save audio file: {str(e)}"
            logger.error(error_msg)
            raise MicrophoneError(
                error_msg,
                error_code="AUDIO_SAVE_FAILED",
                context={"output_path": str(output_path)},
            ) from e

    def get_device_info(self) -> dict:
        """Get information about the recording device.
        
        Returns:
            Dictionary with device metadata
        """
        try:
            device_info = sd.query_devices(self.device_id)
            return {
                "device_id": self.device_id,
                "device_name": self.device_name,
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "max_input_channels": device_info["max_input_channels"],
                "default_samplerate": device_info["default_samplerate"],
            }
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {"device_id": self.device_id, "device_name": self.device_name}
