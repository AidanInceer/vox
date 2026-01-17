"""PageReader CLI - Main entry point and command-line interface.

This is the entry point for the PageReader application.
Provides commands for reading browser tabs, URLs, and files aloud.
"""

import argparse
import logging
import sys
from pathlib import Path

from src.browser.detector import detect_all_browser_tabs
from src import config
from src.extraction.text_extractor import ConcreteTextExtractor
from src.tts.playback import get_playback
from src.tts.synthesizer import PiperSynthesizer
from src.utils.errors import BrowserDetectionError, ExtractionError, TTSError
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point for PageReader CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else config.LOG_LEVEL
    setup_logging(name="pagereader", level=log_level)

    # Dispatch to appropriate command
    try:
        if args.command == "read":
            command_read(args)
        elif args.command == "list":
            command_list(args)
        elif args.command == "config":
            command_config(args)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.

    Returns:
        ArgumentParser with all commands and options defined
    """
    parser = argparse.ArgumentParser(
        prog="pagereader",
        description="Read web pages and browser tabs aloud using AI text-to-speech",
    )

    # Global options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # READ command
    read_parser = subparsers.add_parser("read", help="Read content aloud")
    read_group = read_parser.add_mutually_exclusive_group(required=True)
    read_group.add_argument("--tab", metavar="TAB_ID", help="Read a specific browser tab by ID")
    read_group.add_argument("--url", metavar="URL", help="Read content from a URL")
    read_group.add_argument("--file", metavar="FILE_PATH", help="Read content from a local HTML file")
    read_group.add_argument("--active", action="store_true", help="Read the currently active browser tab")

    # TTS options
    read_parser.add_argument(
        "--voice",
        default="en_US-libritts-high",
        help="Voice to use for synthesis (default: en_US-libritts-high)",
    )
    read_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (0.5-2.0, default: 1.0)")
    read_parser.add_argument("--no-play", action="store_true", help="Generate audio but do not play it")
    read_parser.add_argument("--output", metavar="FILE", help="Save audio to a file instead of playing")

    # LIST command
    list_parser = subparsers.add_parser("list", help="List available items")
    list_subcommands = list_parser.add_subparsers(dest="list_type", help="What to list")

    list_subcommands.add_parser("tabs", help="List all open browser tabs")
    list_subcommands.add_parser("voices", help="List available TTS voices")

    # CONFIG command
    config_parser = subparsers.add_parser("config", help="Show configuration")

    return parser


def command_read(args):
    """Handle the 'read' command.

    Args:
        args: Parsed command-line arguments
    """
    # Validate inputs
    if not any([args.tab, args.url, args.file, args.active]):
        print("Error: One of --tab, --url, --file, or --active must be provided")
        sys.exit(1)

    if args.speed and not (config.MIN_PLAYBACK_SPEED <= args.speed <= config.MAX_PLAYBACK_SPEED):
        print(f"Error: Speed must be between {config.MIN_PLAYBACK_SPEED} and {config.MAX_PLAYBACK_SPEED}")
        sys.exit(1)

    # Step 1: Get content
    print("[*] Retrieving content...")
    content = _get_content(args)

    if not content:
        print("Error: Could not retrieve content")
        sys.exit(1)

    print(f"[OK] Retrieved {len(content)} characters")

    # Step 2: Synthesize to speech
    print("[*] Synthesizing speech...")
    try:
        voice = args.voice or config.DEFAULT_TTS_VOICE
        speed = args.speed or config.DEFAULT_TTS_SPEED
        synthesizer = PiperSynthesizer(voice=voice)
        audio_bytes = synthesizer.synthesize(content, speed=speed)
        print(f"[OK] Generated {len(audio_bytes)} bytes of audio")
    except TTSError as e:
        print(f"Error: Failed to synthesize speech: {e}")
        sys.exit(1)

    # Step 3: Handle output
    if args.output:
        _save_audio(audio_bytes, args.output)
    elif not args.no_play:
        _play_audio(audio_bytes)


def command_list(args):
    """Handle the 'list' command.

    Args:
        args: Parsed command-line arguments
    """
    if args.list_type == "tabs":
        _list_tabs()
    elif args.list_type == "voices":
        _list_voices()
    else:
        print("Use 'list tabs' or 'list voices'")


def command_config(args):
    """Handle the 'config' command.

    Args:
        args: Parsed command-line arguments
    """
    print("\nPageReader Configuration:")
    print(f"  TTS Provider: {config.DEFAULT_TTS_PROVIDER}")
    print(f"  Default Voice: {config.DEFAULT_TTS_VOICE}")
    print(f"  Default Speed: {config.DEFAULT_TTS_SPEED}")
    print(f"  Cache Synthesis: {config.TTS_CACHE_ENABLED}")


def _get_content(args) -> str:
    """Get content from specified source.

    Args:
        args: Parsed arguments with tab/url/file/active options

    Returns:
        Content text, or empty string if retrieval failed
    """
    extractor = ConcreteTextExtractor()

    try:
        if args.tab:
            # Get specific tab by ID
            print(f"  Reading tab: {args.tab}")
            return extractor.extract(args.tab)

        elif args.url:
            # Fetch from URL
            print(f"  Fetching from: {args.url}")
            return extractor.extract_from_url(args.url)

        elif args.file:
            # Load from file
            print(f"  Loading from: {args.file}")
            return extractor.extract_from_file(args.file)

        elif args.active:
            # Get active tab
            print("  Reading active browser tab")
            # TODO: Detect and read active tab
            print("  (Active tab detection not yet implemented)")
            return ""

    except ExtractionError as e:
        print(f"  Error: {e}")
        return ""

    return ""


def _list_tabs():
    """List all open browser tabs."""
    try:
        print("\n📑 Open Browser Tabs:\n")

        tabs = detect_all_browser_tabs()

        if not tabs:
            print("  No browser tabs detected")
            return

        # Group by browser
        by_browser = {}
        for tab in tabs:
            if tab.browser_name not in by_browser:
                by_browser[tab.browser_name] = []
            by_browser[tab.browser_name].append(tab)

        # Display grouped
        for browser, browser_tabs in sorted(by_browser.items()):
            print(f"  {browser.upper()} ({len(browser_tabs)} tabs)")
            for tab in browser_tabs:
                print(f"    [{tab.tab_id}] {tab.title}")
                print(f"         {tab.url}")

        print()

    except BrowserDetectionError as e:
        print(f"Error: Failed to detect tabs: {e}")
        sys.exit(1)


def _list_voices():
    """List available TTS voices."""
    print("\n🎙️  Available TTS Voices:\n")

    synthesizer = PiperSynthesizer()
    voices = synthesizer.get_voices()

    for voice in voices:
        print(f"  • {voice}")

    print()


def _play_audio(audio_bytes: bytes):
    """Play audio bytes.

    Args:
        audio_bytes: Audio data to play
    """
    try:
        print("🔊 Playing audio...")
        playback = get_playback()
        playback.play_audio(audio_bytes)
        print("✓ Audio playback complete")
    except Exception as e:
        print(f"Error: Failed to play audio: {e}")
        sys.exit(1)


def _save_audio(audio_bytes: bytes, output_path: str):
    """Save audio to a file.

    Args:
        audio_bytes: Audio data to save
        output_path: Path to save file to
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"✓ Audio saved to: {output_path}")
    except Exception as e:
        print(f"Error: Failed to save audio: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
