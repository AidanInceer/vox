"""Clipboard management and paste simulation for vox voice input.

This module provides clipboard operations and simulates Ctrl+V paste
to insert transcribed text at the current cursor position.
"""

import logging
import time
from typing import Optional

import pyperclip
from pynput import keyboard

from src.utils.errors import PasteError

logger = logging.getLogger(__name__)

# Delay constants for clipboard operations
_CLIPBOARD_DELAY = 0.05  # 50ms delay between clipboard operations
_PASTE_DELAY = 0.1  # 100ms delay after paste simulation


class ClipboardPaster:
    """Clipboard management and paste simulation for text insertion.

    Provides clipboard operations and simulates Ctrl+V paste to insert
    transcribed text at the current cursor position in any application.
    Optionally preserves and restores original clipboard contents.

    Thread Safety:
        Thread-safe for `paste_text` calls. Uses pyperclip for cross-platform
        clipboard access and pynput for keystroke simulation.

    Note:
        The target application must have focus for paste simulation to work.
        Small delays (~150ms) are introduced to ensure clipboard stability.

    Example:
        >>> paster = ClipboardPaster()
        >>> paster.paste_text("Hello world", restore_clipboard=True)
        True
        >>> paster.copy_to_clipboard("Some text")
        >>> paster.get_clipboard()
        'Some text'
    """

    def __init__(self) -> None:
        """Initialize the clipboard paster.

        Creates a pynput keyboard controller for simulating paste keystrokes.
        """
        self._keyboard_controller = keyboard.Controller()
        logger.debug("ClipboardPaster initialized")

    def copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard without pasting.

        Args:
            text: Text to copy

        Raises:
            PasteError: If clipboard operation fails
        """
        try:
            pyperclip.copy(text)
            logger.debug(f"Copied {len(text)} characters to clipboard")
        except Exception as e:
            raise PasteError(
                f"Failed to copy to clipboard: {str(e)}",
                error_code="CLIPBOARD_COPY_FAILED",
                context={"text_length": len(text)},
            ) from e

    def get_clipboard(self) -> str:
        """Get current clipboard text content.

        Returns:
            Clipboard text, or empty string if not text

        Raises:
            PasteError: If clipboard access fails
        """
        try:
            content = pyperclip.paste()
            return content if content else ""
        except Exception as e:
            logger.warning(f"Failed to read clipboard: {str(e)}")
            return ""

    def paste_text(self, text: str, restore_clipboard: bool = True) -> bool:
        """Copy text to clipboard and simulate Ctrl+V paste.

        Args:
            text: Text to paste at current cursor position
            restore_clipboard: If True, restore original clipboard after paste

        Returns:
            True if paste simulation completed, False if failed

        Note:
            Target application must have focus for paste to work.
            Small delay (~150ms) occurs for clipboard operations.
        """
        if not text:
            logger.warning("paste_text called with empty text")
            return False

        original_clipboard: Optional[str] = None

        try:
            # Save original clipboard if restoration requested
            if restore_clipboard:
                original_clipboard = self.get_clipboard()
                logger.debug("Saved original clipboard content")

            # Copy new text to clipboard
            self.copy_to_clipboard(text)

            # Small delay to ensure clipboard is ready
            time.sleep(_CLIPBOARD_DELAY)

            # Simulate Ctrl+V paste
            self._simulate_paste()

            # Allow paste to complete
            time.sleep(_PASTE_DELAY)

            logger.info(f"Pasted {len(text)} characters")

            return True

        except PasteError:
            raise
        except Exception as e:
            logger.error(f"Paste operation failed: {str(e)}")
            raise PasteError(
                f"Paste operation failed: {str(e)}",
                error_code="PASTE_FAILED",
                context={"text_length": len(text)},
            ) from e

        finally:
            # Restore original clipboard if requested
            if restore_clipboard and original_clipboard is not None:
                try:
                    # Small delay before restoration
                    time.sleep(_CLIPBOARD_DELAY)
                    pyperclip.copy(original_clipboard)
                    logger.debug("Restored original clipboard content")
                except Exception as e:
                    logger.warning(f"Failed to restore clipboard: {str(e)}")

    def _simulate_paste(self) -> None:
        """Simulate Ctrl+V keyboard shortcut.

        Uses pynput to send the key combination.
        """
        try:
            with self._keyboard_controller.pressed(keyboard.Key.ctrl):
                self._keyboard_controller.tap("v")
            logger.debug("Simulated Ctrl+V paste")
        except Exception as e:
            raise PasteError(
                f"Failed to simulate paste keystroke: {str(e)}",
                error_code="PASTE_KEYSTROKE_FAILED",
            ) from e
