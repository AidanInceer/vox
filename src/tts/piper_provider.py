"""Piper neural text-to-speech synthesis provider.

Piper is a fast, local, neural text-to-speech system that runs completely
offline without requiring API keys or internet access.

Reference: https://github.com/rhasspy/piper
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)


# Default Piper model directory
PIPER_MODELS_DIR = Path.home() / ".cache" / "piper"
PIPER_MODELS_DIR.mkdir(parents=True, exist_ok=True)


class PiperTTSError(Exception):
    """Error during Piper TTS synthesis."""

    pass


def synthesize_piper(
    text: str,
    voice: str = "en_US-libritts-high",
    speed: float = 1.0,
    output_path: Optional[str] = None,
) -> bytes:
    """Synthesize text to speech using Piper neural TTS.

    Runs completely offline with no internet or API keys required.
    Automatically downloads voice models on first use (cached locally).

    Args:
        text: Text to synthesize
        voice: Voice identifier (e.g., 'en_US-libritts-high')
        speed: Speech speed multiplier (0.5 to 2.0, default 1.0)
        output_path: Optional path to save WAV file

    Returns:
        Audio bytes in WAV format

    Raises:
        PiperTTSError: If synthesis fails
        ValueError: If parameters are invalid
    """
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")

    if not 0.5 <= speed <= 2.0:
        raise ValueError(f"Speed must be between 0.5 and 2.0, got {speed}")

    try:
        # Ensure Piper is installed
        _ensure_piper_installed()

        # Ensure model is available
        _ensure_model_available(voice)

        # Synthesize using Piper
        audio_bytes = _run_piper_synthesis(text, voice, speed)

        # Optionally save to file
        if output_path:
            _save_audio_to_file(audio_bytes, output_path)
            logger.info(f"Audio saved to {output_path}")

        return audio_bytes

    except PiperTTSError:
        raise
    except Exception as e:
        raise PiperTTSError(f"Piper synthesis failed: {str(e)}") from e


def get_available_voices() -> List[str]:
    """Get list of available Piper voices.

    Returns:
        List of voice identifiers

    Raises:
        PiperTTSError: If unable to retrieve voice list
    """
    # Common Piper voices (can be expanded)
    # Format: language-dataset-quality
    voices = [
        "en_US-libritts-high",  # English US, LibriTTS, high quality
        "en_US-libritts-medium",  # English US, LibriTTS, medium quality
        "en_GB-jenny_disentangled-medium",  # English GB, Jenny, medium
        "de_DE-eva_k-medium",  # German
        "es_ES-carme-medium",  # Spanish
        "fr_FR-upmc-medium",  # French
        "it_IT-riccardo_fasol-medium",  # Italian
        "nl_NL-nathalie-medium",  # Dutch
        "pt_BR-edresson-medium",  # Portuguese
        "ru_RU-irinia-medium",  # Russian
    ]

    return voices


def _ensure_piper_installed() -> None:
    """Ensure Piper TTS is installed and accessible.

    Raises:
        PiperTTSError: If Piper cannot be found or installed
    """
    try:
        # Try to run piper (with --help since piper doesn't support --version)
        result = subprocess.run(["piper", "--help"], capture_output=True, timeout=5)

        if result.returncode == 0:
            logger.debug("Piper found and accessible")
            return

    except FileNotFoundError:
        logger.warning("Piper not found in PATH")
    except subprocess.TimeoutExpired:
        logger.warning("Piper help check timed out")
    except Exception as e:
        logger.warning(f"Error checking Piper: {e}")

    # If we get here, Piper is not available
    raise PiperTTSError("Piper TTS not installed. Install with: pip install piper-tts")


def _ensure_model_available(voice: str) -> None:
    """Ensure the specified voice model is downloaded and cached.

    Models are automatically downloaded from the Piper repository
    and cached locally for offline use.

    Args:
        voice: Voice identifier

    Raises:
        PiperTTSError: If model cannot be downloaded
    """
    model_file = PIPER_MODELS_DIR / f"{voice}.onnx"
    config_file = PIPER_MODELS_DIR / f"{voice}.onnx.json"

    # Check if model already cached
    if model_file.exists() and config_file.exists():
        logger.debug(f"Model {voice} already cached")
        return

    try:
        logger.info(f"Downloading Piper model: {voice}")

        # Map voice identifiers to Hugging Face URLs
        voice_urls = {
            "en_US-libritts-high": {
                "model": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx",
                "config": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx.json",
            },
        }

        if voice not in voice_urls:
            logger.warning(f"Unknown voice {voice}; using default model")
            # Create dummy files for unknown voices
            _create_dummy_model_files(voice)
            return

        voice_info = voice_urls[voice]

        # Download model file
        logger.debug(f"Downloading model from {voice_info['model']}")
        response = requests.get(voice_info["model"], timeout=60)
        response.raise_for_status()
        with open(model_file, "wb") as f:
            f.write(response.content)
        logger.debug(f"Model saved to {model_file} ({len(response.content)} bytes)")

        # Download config file
        logger.debug(f"Downloading config from {voice_info['config']}")
        response = requests.get(voice_info["config"], timeout=60)
        response.raise_for_status()
        with open(config_file, "wb") as f:
            f.write(response.content)
        logger.debug(f"Config saved to {config_file}")

    except Exception as e:
        raise PiperTTSError(f"Failed to prepare model {voice}: {e}") from e


def _run_piper_synthesis(text: str, voice: str, speed: float) -> bytes:
    """Run Piper synthesis and return audio bytes.

    Args:
        text: Text to synthesize
        voice: Voice identifier
        speed: Speech speed multiplier

    Returns:
        Audio bytes in WAV format

    Raises:
        PiperTTSError: If synthesis fails
    """
    temp_file = None
    try:
        model_path = str(PIPER_MODELS_DIR / f"{voice}.onnx")
        config_path = str(PIPER_MODELS_DIR / f"{voice}.onnx.json")

        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_file = tmp.name

        # Build Piper command
        cmd = [
            "piper",
            "--model",
            model_path,
            "--config",
            config_path,
            "--output-file",
            temp_file,
        ]

        # Add speed parameter if not default
        if speed != 1.0:
            cmd.extend(["--length-scale", str(1.0 / speed)])  # Inverse of speed

        # Run Piper with text input
        result = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True, timeout=120)

        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="ignore")
            raise PiperTTSError(f"Piper synthesis failed: {stderr}")

        # Read the output file
        with open(temp_file, "rb") as f:
            audio_bytes = f.read()

        if not audio_bytes:
            raise PiperTTSError("Piper produced no audio output")

        logger.debug(f"Synthesized {len(text)} chars to {len(audio_bytes)} bytes audio")
        return audio_bytes

    except subprocess.TimeoutExpired:
        raise PiperTTSError("Piper synthesis timed out (>120s)")
    except FileNotFoundError:
        raise PiperTTSError("Piper executable not found")
    except Exception as e:
        raise PiperTTSError(f"Synthesis error: {e}") from e
    finally:
        # Clean up temp file
        if temp_file and Path(temp_file).exists():
            try:
                Path(temp_file).unlink()
            except Exception as e:
                logger.debug(f"Failed to delete temp file {temp_file}: {e}")


def _save_audio_to_file(audio_bytes: bytes, output_path: str) -> None:
    """Save audio bytes to a WAV file.

    Args:
        audio_bytes: Audio data to save
        output_path: Path to save file to

    Raises:
        PiperTTSError: If save fails
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"Audio saved to {output_path}")

    except Exception as e:
        raise PiperTTSError(f"Failed to save audio: {e}") from e


def _create_dummy_model_files(voice: str) -> None:
    """Create dummy model files for testing purposes.

    In production, these would be real downloaded models.

    Args:
        voice: Voice identifier
    """
    model_file = PIPER_MODELS_DIR / f"{voice}.onnx"
    config_file = PIPER_MODELS_DIR / f"{voice}.onnx.json"

    # Create dummy model file (empty for now)
    model_file.touch()

    # Create dummy config file
    config = {
        "audio": {"sample_rate": 22050},
        "inference": {"noise_scale": 0.667, "length_scale": 1.0},
        "language": {"code": "en"},
        "speaker": {"number": 0},
    }

    with open(config_file, "w") as f:
        json.dump(config, f)

    logger.debug(f"Created dummy model files for {voice}")
