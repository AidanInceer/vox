"""Visual feedback utilities for STT recording and transcription."""

import sys
import threading
import time
from datetime import datetime
from typing import Optional

import numpy as np
from colorama import Fore, Style

from src.stt.audio_utils import calculate_rms


class RecordingIndicator:
    """Animated recording indicator with duration counter and audio levels.

    Provides real-time visual feedback during voice recording:
    - Pulsing red dot indicator
    - Recording duration counter
    - Audio level bars
    - Device name display
    - Silence detection feedback
    """

    def __init__(
        self,
        device_name: str,
        show_audio_levels: bool = True,
    ):
        """Initialize recording indicator.

        Args:
            device_name: Name of the microphone being used
            show_audio_levels: Whether to show audio level bars
        """
        self.device_name = device_name
        self.show_audio_levels = show_audio_levels
        self.is_running = False
        self.start_time: Optional[float] = None
        self.current_rms: float = 0.0
        self.is_silent = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the animated indicator."""
        if self.is_running:
            return

        self.is_running = True
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the animated indicator."""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        # Clear the line completely (wider clear to handle long device names)
        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

    def update_audio_level(self, audio_chunk) -> None:
        """Update the audio level from current chunk.

        Args:
            audio_chunk: Audio samples as numpy array
        """
        self.current_rms = calculate_rms(audio_chunk)

    def update_silence_status(self, is_silent: bool) -> None:
        """Update silence detection status.

        Args:
            is_silent: Whether silence is currently detected
        """
        self.is_silent = is_silent

    def _animate(self) -> None:
        """Animation loop (runs in separate thread)."""
        indicator_frames = ["🔴", "🟠", "🔴", "⚫"]
        frame_idx = 0

        while self.is_running:
            if self.start_time is None:
                time.sleep(0.1)
                continue

            # Calculate duration
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            duration_str = f"{minutes:02d}:{seconds:02d}"

            # Get indicator symbol
            if self.is_silent:
                indicator = "⚫"  # Dim when silent
                color = Fore.WHITE
            else:
                indicator = indicator_frames[frame_idx % len(indicator_frames)]
                color = Fore.RED

            # Build status line
            status_parts = [
                f"{color}{indicator}{Style.RESET_ALL}",
                f"{Fore.CYAN}Recording{Style.RESET_ALL}",
                f"{Fore.YELLOW}{duration_str}{Style.RESET_ALL}",
            ]

            # Add audio level bars if enabled
            if self.show_audio_levels:
                level_bars = self._get_audio_level_bars()
                status_parts.append(level_bars)

            # Add device name (truncate if too long)
            device_display = self.device_name
            if len(device_display) > 30:
                device_display = device_display[:27] + "..."
            status_parts.append(f"{Fore.WHITE}[{device_display}]{Style.RESET_ALL}")

            # Write status line
            status_line = " | ".join(status_parts)
            sys.stdout.write(f"\r{status_line}")
            sys.stdout.flush()

            frame_idx += 1
            time.sleep(0.25)  # Update 4 times per second

    def _get_audio_level_bars(self) -> str:
        """Generate audio level visualization bars.

        Returns:
            String with colored bars representing audio level
        """
        # Normalize RMS to 0-10 scale (typical RMS range is 0-5000)
        # Handle NaN/invalid values by defaulting to 0
        if np.isnan(self.current_rms) or np.isinf(self.current_rms):
            normalized = 0
        else:
            normalized = min(int(self.current_rms / 500), 10)

        # Choose color based on level
        if normalized < 3:
            color = Fore.GREEN
        elif normalized < 7:
            color = Fore.YELLOW
        else:
            color = Fore.RED

        bars = "█" * normalized + "░" * (10 - normalized)
        return f"{color}{bars}{Style.RESET_ALL}"


class ProgressIndicator:
    """Progress indicator for model loading and transcription.

    Shows spinner animation with status message and optional progress info.
    """

    def __init__(self, message: str, show_spinner: bool = True):
        """Initialize progress indicator.

        Args:
            message: Status message to display
            show_spinner: Whether to show animated spinner
        """
        self.message = message
        self.show_spinner = show_spinner
        self.is_running = False
        self.additional_info = ""
        self._thread: Optional[threading.Thread] = None
        self.start_time: Optional[float] = None

    def start(self) -> None:
        """Start the progress indicator."""
        if self.is_running:
            return

        self.is_running = True
        self.start_time = time.time()
        if self.show_spinner:
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
        else:
            print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {self.message}")

    def stop(self, success: bool = True) -> float:
        """Stop the progress indicator.

        Args:
            success: Whether the operation succeeded

        Returns:
            Elapsed time in seconds
        """
        elapsed = time.time() - self.start_time if self.start_time else 0

        self.is_running = False
        if self._thread:
            self._thread.join(timeout=0.5)

        # Clear the line
        sys.stdout.write("\r" + " " * 100 + "\r")
        sys.stdout.flush()

        # Show completion message
        if success:
            symbol = f"{Fore.GREEN}✓{Style.RESET_ALL}"
        else:
            symbol = f"{Fore.RED}✗{Style.RESET_ALL}"

        print(f"{symbol} {self.message} {Fore.WHITE}(completed in {elapsed:.1f}s){Style.RESET_ALL}")

        return elapsed

    def update_info(self, info: str) -> None:
        """Update additional information shown in progress.

        Args:
            info: Additional information string
        """
        self.additional_info = info

    def _animate(self) -> None:
        """Animation loop (runs in separate thread)."""
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame_idx = 0

        while self.is_running:
            spinner = spinner_frames[frame_idx % len(spinner_frames)]

            # Build status line
            status = f"{Fore.CYAN}{spinner}{Style.RESET_ALL} {self.message}"
            if self.additional_info:
                status += f" {Fore.WHITE}({self.additional_info}){Style.RESET_ALL}"

            sys.stdout.write(f"\r{status}")
            sys.stdout.flush()

            frame_idx += 1
            time.sleep(0.1)


def format_transcription_result(
    text: str,
    duration: float,
    model_name: str,
    confidence: Optional[float] = None,
) -> str:
    """Format transcription result with metadata and styling.

    Args:
        text: Transcribed text
        duration: Audio duration in seconds
        model_name: Whisper model used
        confidence: Optional confidence score (0-1)

    Returns:
        Formatted string with colored box and metadata
    """
    # Calculate text stats
    word_count = len(text.split())
    char_count = len(text)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build header
    header = f"{Fore.CYAN}╔{'═' * 68}╗{Style.RESET_ALL}"
    title = f"{Fore.CYAN}║{Fore.GREEN} 📝 Transcription Result{' ' * 43}{Fore.CYAN}║{Style.RESET_ALL}"
    divider = f"{Fore.CYAN}╠{'═' * 68}╣{Style.RESET_ALL}"

    # Build metadata (without borders first, we'll add them after padding)
    meta_line1 = f" {Fore.WHITE}Words:{Style.RESET_ALL} {word_count} | {Fore.WHITE}Characters:{Style.RESET_ALL} {char_count} | {Fore.WHITE}Duration:{Style.RESET_ALL} {duration:.1f}s"
    meta_line2 = (
        f" {Fore.WHITE}Model:{Style.RESET_ALL} {model_name} | {Fore.WHITE}Transcribed:{Style.RESET_ALL} {timestamp}"
    )

    # Helper function to strip color codes and calculate visible length
    def visible_length(s: str) -> int:
        import re

        # Remove ANSI color codes
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        return len(ansi_escape.sub("", s))

    # Pad metadata lines to 66 chars (leaves room for borders)
    meta_lines = []
    for line in [meta_line1, meta_line2]:
        visible = visible_length(line)
        padding_needed = 66 - visible
        padded = line + " " * padding_needed
        meta_lines.append(f"{Fore.CYAN}║{Style.RESET_ALL}{padded} {Fore.CYAN}║{Style.RESET_ALL}")

    if confidence is not None:
        confidence_pct = confidence * 100
        conf_color = Fore.GREEN if confidence > 0.8 else Fore.YELLOW
        conf_line = f" {Fore.WHITE}Confidence:{Style.RESET_ALL} {conf_color}{confidence_pct:.1f}%{Style.RESET_ALL}"
        visible = visible_length(conf_line)
        padding_needed = 66 - visible
        padded = conf_line + " " * padding_needed
        meta_lines.append(f"{Fore.CYAN}║{Style.RESET_ALL}{padded} {Fore.CYAN}║{Style.RESET_ALL}")

    # Build text content (wrap at 66 chars)
    text_lines = []
    words = text.split()
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= 66:
            current_line += word + " "
        else:
            if current_line:
                text_lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        text_lines.append(current_line.strip())

    # Format text lines
    formatted_text = []
    for line in text_lines:
        padding = 66 - len(line)
        formatted_text.append(f"{Fore.CYAN}║{Style.RESET_ALL} {line}{' ' * padding} {Fore.CYAN}║{Style.RESET_ALL}")

    # Build footer
    footer = f"{Fore.CYAN}╚{'═' * 68}╝{Style.RESET_ALL}"

    # Combine all parts
    result = "\n".join([header, title, divider] + meta_lines + [divider] + formatted_text + [footer])

    return result


def format_error_box(
    error_type: str,
    message: str,
    suggestions: Optional[list[str]] = None,
) -> str:
    """Format error message in colored box with suggestions.

    Args:
        error_type: Type of error (e.g., "Microphone Error", "Model Error")
        message: Error message text
        suggestions: Optional list of troubleshooting suggestions

    Returns:
        Formatted error box string
    """
    # Choose color based on error type
    if "microphone" in error_type.lower():
        color = Fore.RED
        icon = "🎤"
    elif "model" in error_type.lower():
        color = Fore.YELLOW
        icon = "🔧"
    elif "transcription" in error_type.lower():
        color = Fore.MAGENTA
        icon = "📝"
    else:
        color = Fore.RED
        icon = "❌"

    # Build header
    header = f"{color}╔{'═' * 68}╗{Style.RESET_ALL}"
    title = f"{color}║{Style.RESET_ALL} {icon} {Fore.RED}{error_type}{Style.RESET_ALL}"
    title_padding = 66 - len(f" {icon} {error_type}")
    title += " " * title_padding + f"{color}║{Style.RESET_ALL}"
    divider = f"{color}╠{'═' * 68}╣{Style.RESET_ALL}"

    # Format message (wrap at 66 chars)
    msg_lines = []
    words = message.split()
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= 66:
            current_line += word + " "
        else:
            if current_line:
                msg_lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        msg_lines.append(current_line.strip())

    formatted_msg = []
    for line in msg_lines:
        padding = 66 - len(line)
        formatted_msg.append(f"{color}║{Style.RESET_ALL} {line}{' ' * padding} {color}║{Style.RESET_ALL}")

    # Format suggestions if provided
    formatted_suggestions = []
    if suggestions:
        formatted_suggestions.append(divider)
        formatted_suggestions.append(
            f"{color}║{Style.RESET_ALL} {Fore.CYAN}💡 Try:{Style.RESET_ALL}" + " " * 58 + f"{color}║{Style.RESET_ALL}"
        )
        for i, suggestion in enumerate(suggestions, 1):
            # Wrap suggestion text
            suggestion_text = f"{i}. {suggestion}"
            sug_lines = []
            words = suggestion_text.split()
            current_line = ""

            for word in words:
                if len(current_line) + len(word) + 1 <= 64:
                    current_line += word + " "
                else:
                    if current_line:
                        sug_lines.append(current_line.strip())
                    current_line = "   " + word + " "  # Indent continuation

            if current_line:
                sug_lines.append(current_line.strip())

            for line in sug_lines:
                padding = 66 - len(line)
                formatted_suggestions.append(
                    f"{color}║{Style.RESET_ALL} {line}{' ' * padding} {color}║{Style.RESET_ALL}"
                )

    # Build footer
    footer = f"{color}╚{'═' * 68}╝{Style.RESET_ALL}"

    # Combine all parts
    result = "\n".join([header, title, divider] + formatted_msg + formatted_suggestions + [footer])

    return result


def list_audio_devices() -> list[dict]:
    """List all available audio input devices.

    Returns:
        List of device info dictionaries with keys:
        - id: Device index
        - name: Device name
        - channels: Max input channels
        - default: Whether it's the default device
    """
    try:
        import sounddevice as sd

        devices = []
        device_list = sd.query_devices()
        default_input = sd.default.device[0]

        for idx, device in enumerate(device_list):
            if device["max_input_channels"] > 0:  # Input device
                devices.append(
                    {
                        "id": idx,
                        "name": device["name"],
                        "channels": device["max_input_channels"],
                        "default": (idx == default_input),
                    }
                )

        return devices

    except Exception:
        return []


def format_device_list() -> str:
    """Format available audio input devices as a table.

    Returns:
        Formatted device table string
    """
    devices = list_audio_devices()

    if not devices:
        return f"{Fore.YELLOW}No audio input devices found{Style.RESET_ALL}"

    # Build table
    lines = []
    lines.append(f"\n{Fore.CYAN}Available Audio Input Devices:{Style.RESET_ALL}")
    lines.append(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    lines.append(f"{Fore.WHITE}  ID  │  Device Name                              │  Channels{Style.RESET_ALL}")
    lines.append(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")

    for device in devices:
        marker = f"{Fore.GREEN}★{Style.RESET_ALL}" if device["default"] else " "
        name = device["name"][:40]  # Truncate long names
        lines.append(f"{marker} {device['id']:2d}  │  {name:40s}  │  {device['channels']}")

    lines.append(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    lines.append(f"{Fore.GREEN}★{Style.RESET_ALL} = Default device\n")

    return "\n".join(lines)
