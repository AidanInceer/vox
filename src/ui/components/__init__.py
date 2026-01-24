"""UI components module for Vox application.

This module contains reusable UI components extracted from main_window.py
following the Single Responsibility Principle.
"""

from src.ui.components.card import FluentCard
from src.ui.components.empty_state import EmptyState
from src.ui.components.history_item import HistoryItemCard
from src.ui.components.keycap import KeyCapLabel
from src.ui.components.model_slider import ModelSlider
from src.ui.components.speed_slider import SpeedSlider
from src.ui.components.theme_toggle import ThemeToggle

__all__: list[str] = [
    "FluentCard",
    "EmptyState",
    "HistoryItemCard",
    "KeyCapLabel",
    "ModelSlider",
    "SpeedSlider",
    "ThemeToggle",
]
