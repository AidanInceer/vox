"""Voice input controller module for orchestrating the voice-to-text flow.

This module provides the main integration controller that coordinates
hotkey listening, recording, transcription, and pasting operations.
"""

from src.voice_input.controller import VoiceInputController

__all__ = ["VoiceInputController"]
