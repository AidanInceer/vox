"""Persistence module for settings and transcription history storage.

This module provides SQLite-based storage for user settings and
transcription history records.
"""

from src.persistence.database import VoxDatabase
from src.persistence.models import AppState, TranscriptionRecord, UserSettings

__all__ = ["VoxDatabase", "AppState", "TranscriptionRecord", "UserSettings"]
