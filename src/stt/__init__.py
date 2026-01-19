"""Speech-to-Text (STT) module for vox.

This module provides voice recording and transcription capabilities using
Whisper models via the faster-whisper library. Key components:

- engine.py: Whisper model loading and transcription
- recorder.py: Microphone audio capture
- transcriber.py: Main orchestration coordinator
- audio_utils.py: Audio processing and silence detection
- ui.py: Visual feedback and formatting utilities

Example usage:
    from src.stt.transcriber import Transcriber

    transcriber = Transcriber(model="medium", silence_duration=5.0)
    result = transcriber.transcribe(output_file="transcript.txt")
    print(result)
"""

__all__ = ["STTEngine", "MicrophoneRecorder", "Transcriber"]
