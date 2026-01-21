"""vox CLI - Main entry point and command-line interface.

This is the entry point for the vox application.
Provides bidirectional audio-text conversion: read content aloud (TTS) and transcribe voice (STT).
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from colorama import Fore, Style
from colorama import init as colorama_init

from src import config
from src.browser.detector import detect_all_browser_tabs
from src.extraction.text_extractor import ConcreteTextExtractor
from src.session.manager import SessionManager
from src.tts.chunking import ChunkSynthesizer
from src.tts.controller import PlaybackController
from src.tts.playback import AudioPlayback, get_playback
from src.tts.synthesizer import PiperSynthesizer
from src.utils.errors import BrowserDetectionError, ExtractionError, TTSError
from src.utils.logging import setup_logging

# Initialize colorama for cross-platform colored output
colorama_init(autoreset=True)

logger = logging.getLogger(__name__)


# Color helper functions
def print_status(msg: str):
    """Print a status message in cyan."""
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {msg}")


def print_success(msg: str):
    """Print a success message in green."""
    print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {msg}")


def print_error(msg: str):
    """Print an error message in red."""
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")


def print_warning(msg: str):
    """Print a warning message in yellow."""
    print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")


class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter with colored output."""

    def _format_usage(self, usage, actions, groups, prefix):
        """Format usage line with color."""
        if prefix is None:
            prefix = f"{Fore.CYAN}Usage:{Style.RESET_ALL} "
        return super()._format_usage(usage, actions, groups, prefix)

    def _format_action(self, action):
        """Format individual action with colored option strings."""
        # Get the formatted help
        help_text = super()._format_action(action)

        # Color the option strings (e.g., -h, --help)
        if action.option_strings:
            # Find and color option strings
            for opt in action.option_strings:
                help_text = help_text.replace(opt, f"{Fore.GREEN}{opt}{Style.RESET_ALL}", 1)

        return help_text

    def add_usage(self, usage, actions, groups, prefix=None):
        """Override to add colored usage."""
        if prefix is None:
            prefix = f"{Fore.CYAN}Usage:{Style.RESET_ALL} "
        super().add_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        """Format section headings with color."""
        if heading:
            # Color section headings
            heading = f"{Fore.CYAN}{heading}:{Style.RESET_ALL}"
        super().start_section(heading)


def main():
    """Main entry point for vox CLI."""
    # Create default config file if it doesn't exist
    config.create_default_config()

    # Check and run config migration if needed
    from src.utils.migration import migrate_config

    try:
        migration_result = migrate_config()
        if migration_result["migrated"]:
            print_success("Migrated configuration from vox to vox")
            print_status(f"Backup saved to: {migration_result['backup_path']}")
    except Exception as e:
        # Log but don't fail - migration is non-critical
        pass

    parser = create_parser()
    args = parser.parse_args()

    # Handle version flag
    if hasattr(args, "version") and args.version:
        print(f"vox v{config.APP_VERSION}")
        sys.exit(0)

    # Setup logging
    log_level = "DEBUG" if args.verbose else config.LOG_LEVEL
    setup_logging(name="vox", level=log_level)

    # Dispatch to appropriate command
    try:
        if args.command == "read":
            command_read(args)
        elif args.command == "transcribe":
            command_transcribe(args)
        elif args.command == "list":
            command_list(args)
        elif args.command == "list-sessions":
            command_list_sessions(args)
        elif args.command == "resume":
            command_resume(args)
        elif args.command == "delete-session":
            command_delete_session(args)
        elif args.command == "config":
            command_config(args)
        elif args.command == "gui":
            command_gui(args)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print_warning("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        print_error(str(e))
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.

    Returns:
        ArgumentParser with all commands and options defined
    """
    # Create colored description with ASCII art header
    description = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════╗
║                            vox v{config.APP_VERSION}                              ║
║       Bidirectional audio-text conversion: TTS and STT            ║
╚═══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}🎤 Speech-to-Text:{Style.RESET_ALL}
  Record your voice and get accurate text transcription

{Fore.YELLOW}🔊 Text-to-Speech:{Style.RESET_ALL}
  Read web pages and browser tabs aloud with AI TTS

{Fore.YELLOW}📚 Session Management:{Style.RESET_ALL}
  Save reading sessions and resume later from where you left off

{Fore.YELLOW}🎮 Interactive Controls:{Style.RESET_ALL}
  Control playback with keyboard shortcuts during audio playback
"""

    epilog = f"""
{Fore.CYAN}═══════════════════════════════════════════════════════════════════
📖 Examples:
═══════════════════════════════════════════════════════════════════{Style.RESET_ALL}

  {Fore.GREEN}# Transcribe your voice to text{Style.RESET_ALL}
  vox transcribe

  {Fore.GREEN}# Save transcription to file{Style.RESET_ALL}
  vox transcribe --output transcript.txt

  {Fore.GREEN}# Read from a URL{Style.RESET_ALL}
  vox read --url https://example.com

  {Fore.GREEN}# Save a reading session{Style.RESET_ALL}
  vox read --url https://example.com --save-session my-article

  {Fore.GREEN}# List saved sessions{Style.RESET_ALL}
  vox list-sessions

  {Fore.GREEN}# Resume a session{Style.RESET_ALL}
  vox resume my-article

  {Fore.GREEN}# Read from a local file{Style.RESET_ALL}
  vox read --file article.html

  {Fore.GREEN}# Read with custom voice and speed{Style.RESET_ALL}
  vox read --url https://example.com --voice en_US-libritts-high --speed 1.5

  {Fore.GREEN}# Save audio to file{Style.RESET_ALL}
  vox read --url https://example.com --output audio.wav

  {Fore.GREEN}# List all open browser tabs{Style.RESET_ALL}
  vox list tabs

  {Fore.GREEN}# List available voices{Style.RESET_ALL}
  vox list voices

{Fore.CYAN}═══════════════════════════════════════════════════════════════════{Style.RESET_ALL}
💡 For more help on a specific command: {Fore.YELLOW}vox <command> --help{Style.RESET_ALL}
"""

    parser = argparse.ArgumentParser(
        prog="vox",
        description=description,
        epilog=epilog,
        formatter_class=ColoredHelpFormatter,
        add_help=False,  # We'll add custom help
    )

    # Add custom help argument with color
    parser.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message and exit"
    )

    # Global options
    parser.add_argument("-v", "--version", action="store_true", help="Show version and exit")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # READ command
    read_parser = subparsers.add_parser(
        "read",
        help=f"{Fore.YELLOW}Read content aloud{Style.RESET_ALL}",
        description=f"{Fore.CYAN}Read content from a URL, file, or browser tab using text-to-speech{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )
    read_group = read_parser.add_mutually_exclusive_group(required=True)
    read_group.add_argument("--tab", metavar="TAB_ID", help="Read a specific browser tab by ID")
    read_group.add_argument("--url", metavar="URL", help="Read content from a URL (http:// or https://)")
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

    # Session management
    read_parser.add_argument(
        "--save-session", metavar="NAME", help="Save this reading session with a name for later resume"
    )

    # TRANSCRIBE command
    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help=f"{Fore.YELLOW}Transcribe voice to text{Style.RESET_ALL}",
        description=f"{Fore.CYAN}Record your voice and convert it to text using speech-to-text{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )
    transcribe_parser.add_argument(
        "--output",
        metavar="FILE",
        help="Save transcription to a file (default: print to stdout)",
    )
    transcribe_parser.add_argument(
        "--model",
        default=None,  # Will use saved default from config
        help=f"Whisper model size: tiny, base, small, medium, large (default: saved preference or {config.DEFAULT_STT_MODEL})",
    )
    transcribe_parser.add_argument(
        "--set-default-model",
        action="store_true",
        help="Save the specified --model as the new default for future transcriptions",
    )

    # LIST command
    list_parser = subparsers.add_parser(
        "list",
        help=f"{Fore.YELLOW}List available items{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )
    list_subcommands = list_parser.add_subparsers(dest="list_type", help="What to list")

    list_subcommands.add_parser("tabs", help="List all open browser tabs")
    list_subcommands.add_parser("voices", help="List available TTS voices")

    # SESSION MANAGEMENT commands
    list_sessions_parser = subparsers.add_parser(
        "list-sessions",
        help=f"{Fore.YELLOW}List all saved reading sessions{Style.RESET_ALL}",
        description=f"{Fore.CYAN}Display all saved reading sessions with their progress{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )

    resume_parser = subparsers.add_parser(
        "resume",
        help=f"{Fore.YELLOW}Resume a saved reading session{Style.RESET_ALL}",
        description=f"{Fore.CYAN}Resume playback from a previously saved session{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )
    resume_parser.add_argument("session_name", help="Name of the session to resume")
    resume_parser.add_argument(
        "--voice",
        default="en_US-libritts-high",
        help="Voice to use for synthesis (default: en_US-libritts-high)",
    )
    resume_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (0.5-2.0, default: 1.0)")

    delete_session_parser = subparsers.add_parser(
        "delete-session",
        help=f"{Fore.YELLOW}Delete a saved reading session{Style.RESET_ALL}",
        description=f"{Fore.CYAN}Permanently delete a saved session{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )
    delete_session_parser.add_argument("session_name", help="Name of the session to delete")

    # CONFIG command
    config_parser = subparsers.add_parser(
        "config",
        help=f"{Fore.YELLOW}Show or manage configuration{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )
    config_parser.add_argument(
        "--show-stt",
        action="store_true",
        help="Show STT configuration settings",
    )

    # GUI command - Desktop application with hotkey voice input
    gui_parser = subparsers.add_parser(
        "gui",
        help=f"{Fore.YELLOW}Launch desktop app with hotkey voice input{Style.RESET_ALL}",
        description=f"{Fore.CYAN}Launch the Vox desktop application with global hotkey voice input{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
    )
    gui_parser.add_argument(
        "--minimized",
        action="store_true",
        help="Start minimized (hidden, hotkey still works)",
    )

    return parser


def command_read(args):
    """Handle the 'read' command.

    Args:
        args: Parsed command-line arguments
    """
    # Validate inputs
    if not any([args.tab, args.url, args.file, args.active]):
        print_error("One of --tab, --url, --file, or --active must be provided")
        sys.exit(1)

    if args.speed and not (config.MIN_PLAYBACK_SPEED <= args.speed <= config.MAX_PLAYBACK_SPEED):
        print_error(f"Speed must be between {config.MIN_PLAYBACK_SPEED} and {config.MAX_PLAYBACK_SPEED}")
        sys.exit(1)

    # Step 1: Get content
    start_time = time.time()
    print_status("Retrieving content...")
    content = _get_content(args)
    elapsed = time.time() - start_time

    if not content:
        print_error("Could not retrieve content")
        sys.exit(1)

    print_success(f"Retrieved {len(content)} characters ({elapsed:.2f}s)")

    # Get URL for session saving
    url = args.url or args.file or args.tab or "active-tab"

    # Step 2: Save session if requested
    if args.save_session:
        try:
            print_status(f"Saving session '{args.save_session}'...")
            manager = SessionManager()
            session_id = manager.save_session(
                session_name=args.save_session,
                url=url,
                extracted_text=content,
                playback_position=0,
                tts_settings={"voice": args.voice, "speed": args.speed},
            )
            print_success(f"Session saved (ID: {session_id})")
        except ValueError as e:
            print_error(f"Failed to save session: {e}")
            sys.exit(1)

    # Step 3: Synthesize to speech with chunking for faster feedback
    start_time = time.time()

    # Check if we should use chunking (for longer content)
    word_count = len(content.split())
    use_chunking = word_count > 200  # Use chunking for articles >200 words

    if use_chunking:
        print_status(f"Preparing text chunks ({word_count} words)...")
        try:
            voice = args.voice or config.DEFAULT_TTS_VOICE
            speed = args.speed or config.DEFAULT_TTS_SPEED

            # Create chunk synthesizer
            chunk_synth = ChunkSynthesizer(voice=voice, speed=speed)

            # Prepare chunks
            chunk_synth.prepare_chunks(content)
            chunk_count = chunk_synth.get_chunk_count()
            print_success(f"Split into {chunk_count} chunks")

            # Synthesize first chunk immediately
            print_status("Synthesizing first chunk (this should be fast)...")
            first_chunk_start = time.time()
            chunk_synth.synthesize_first_chunk()
            first_chunk_elapsed = time.time() - first_chunk_start
            print_success(f"First chunk ready ({first_chunk_elapsed:.2f}s)")

            # Start background synthesis of remaining chunks
            if chunk_count > 1:
                print_status(f"Synthesizing remaining {chunk_count - 1} chunks in background...")
                chunk_synth.start_background_synthesis(num_workers=2)

            elapsed = time.time() - start_time
            print_success(f"Synthesis pipeline started ({elapsed:.2f}s)")

        except Exception as e:
            print_error(f"Failed to initialize chunked synthesis: {e}")
            print_warning("Falling back to standard synthesis...")
            use_chunking = False

    # Fall back to standard synthesis if not using chunking or if chunking failed
    if not use_chunking:
        print_status("Synthesizing speech...")
        try:
            voice = args.voice or config.DEFAULT_TTS_VOICE
            speed = args.speed or config.DEFAULT_TTS_SPEED
            synthesizer = PiperSynthesizer(voice=voice)
            audio_bytes = synthesizer.synthesize(content, speed=speed)
            elapsed = time.time() - start_time
            print_success(f"Generated {len(audio_bytes)} bytes of audio ({elapsed:.2f}s)")
        except TTSError as e:
            print_error(f"Failed to synthesize speech: {e}")
            sys.exit(1)

    # Step 4: Handle output
    if args.output:
        # For file output, we need complete audio
        if use_chunking:
            print_status("Waiting for all chunks to synthesize for file output...")
            # Wait for all chunks to complete
            import time as time_module

            while True:
                status = chunk_synth.get_buffer_status()
                completed = sum(1 for c in chunk_synth.chunks if c.synthesis_status.value == "completed")
                if completed >= chunk_count:
                    break
                print(f"\r⏳ Synthesizing: {completed}/{chunk_count} chunks complete", end="", flush=True)
                time_module.sleep(0.5)
            print("\r" + " " * 60 + "\r", end="", flush=True)

            # Combine all chunks into single audio file
            print_status("Combining chunks into single file...")
            all_audio = b"".join([c.audio_data for c in chunk_synth.chunks if c.audio_data])
            _save_audio(all_audio, args.output)
            chunk_synth.stop()
        else:
            _save_audio(audio_bytes, args.output)
    elif not args.no_play:
        if use_chunking:
            _play_audio_interactive_chunked(chunk_synth, session_name=args.save_session if args.save_session else None)
            chunk_synth.stop()  # Clean up after playback
        else:
            _play_audio_interactive(audio_bytes, session_name=args.save_session if args.save_session else None)

    # Exit successfully
    sys.exit(0)


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
        print_warning("Use 'list tabs' or 'list voices'")


def command_config(args):
    """Handle the 'config' command.

    Args:
        args: Parsed command-line arguments
    """
    if args.show_stt:
        # Show STT configuration
        user_config = config.load_user_config()
        default_model = config.get_stt_default_model()

        print(f"\n{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}STT Configuration{Style.RESET_ALL}"
            + " " * 32
            + f"{Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}╠{'═' * 50}╣{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Default Model:{Style.RESET_ALL} {default_model:28s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Silence Duration:{Style.RESET_ALL} {config.SILENCE_DURATION}s{' ' * 26} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Sample Rate:{Style.RESET_ALL} {config.SAMPLE_RATE}Hz{' ' * 24} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Model Cache:{Style.RESET_ALL} {str(config.STT_MODEL_CACHE):24s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Config File:{Style.RESET_ALL} {str(config.USER_CONFIG_FILE):24s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}╠{'═' * 50}╣{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Available Models:{Style.RESET_ALL}"
            + " " * 30
            + f"{Fore.CYAN}║{Style.RESET_ALL}"
        )
        for model in config.VALID_STT_MODELS:
            marker = "→" if model == default_model else " "
            print(
                f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{marker}{Style.RESET_ALL} {model:44s} {Fore.CYAN}║{Style.RESET_ALL}"
            )
        print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")

        print(
            f"{Fore.WHITE}💡 Tip:{Style.RESET_ALL} Set default model with: vox transcribe --model <name> --set-default-model\n"
        )
    else:
        # Show general configuration
        print(f"\n{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}vox Configuration{Style.RESET_ALL}"
            + " " * 30
            + f"{Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}╠{'═' * 50}╣{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}TTS Provider:{Style.RESET_ALL} {config.DEFAULT_TTS_PROVIDER:30s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Default Voice:{Style.RESET_ALL} {config.DEFAULT_TTS_VOICE:29s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Default Speed:{Style.RESET_ALL} {str(config.DEFAULT_TTS_SPEED):29s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Cache Enabled:{Style.RESET_ALL} {str(config.TTS_CACHE_ENABLED):29s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}STT Model:{Style.RESET_ALL} {config.get_stt_default_model():33s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Config Directory:{Style.RESET_ALL} {str(config.USER_CONFIG_DIR):25s} {Fore.CYAN}║{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")

        print(f"{Fore.WHITE}💡 Tip:{Style.RESET_ALL} Use --show-stt to see detailed STT configuration\n")


def command_gui(args):
    """Handle the 'gui' command - launch desktop application.

    Args:
        args: Parsed command-line arguments
    """
    from src.persistence.database import VoxDatabase
    from src.ui.main_window import VoxMainWindow
    from src.voice_input.controller import VoiceInputController

    print_status("Starting Vox Desktop Application...")

    # Initialize database
    database = VoxDatabase()

    # Initialize controller
    controller = VoiceInputController(database=database)

    # Create and configure main window
    window = VoxMainWindow(
        controller=controller,
        database=database,
    )

    # Start the controller (registers hotkeys)
    controller.start()

    print_success("Application started")
    print_status(f"Hotkey: {database.get_setting('hotkey', '<ctrl>+<alt>+space')}")
    print_status("Press the hotkey to start voice input")

    # Hide window if --minimized flag
    if args.minimized:
        window.hide()
        print_status("Running minimized - use hotkey to activate")

    # Run the main window event loop
    try:
        window.run()
    finally:
        # Cleanup
        database.close()
        print_status("Application closed")


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
            # Validate URL format
            if not args.url.startswith(("http://", "https://")):
                print_error(f"Invalid URL format: {args.url}")
                print_warning("URL must start with http:// or https://")
                return ""
            print(f"  Fetching from: {args.url}")
            return extractor.extract_from_url(args.url)

        elif args.file:
            # Load from file
            file_path = Path(args.file)
            if not file_path.exists():
                print_error(f"File not found: {args.file}")
                return ""
            print(f"  Loading from: {args.file}")
            return extractor.extract_from_file(args.file)

        elif args.active:
            # Get active tab
            print("  Reading active browser tab")
            # TODO: Detect and read active tab
            print_warning("Active tab detection not yet implemented")
            return ""

    except ExtractionError as e:
        print_error(str(e))
        if "Connection" in str(e) or "Network" in str(e):
            print_warning("Check your internet connection and try again")
        return ""

    return ""


def _list_tabs():
    """List all open browser tabs."""
    try:
        print(f"\n{Fore.CYAN}📑 Open Browser Tabs:{Style.RESET_ALL}\n")

        tabs = detect_all_browser_tabs()

        if not tabs:
            print_warning("No browser tabs detected")
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
        print_error(f"Failed to detect tabs: {e}")
        sys.exit(1)


def _list_voices():
    """List available TTS voices."""
    print(f"\n{Fore.CYAN}🎙️  Available TTS Voices:{Style.RESET_ALL}\n")

    synthesizer = PiperSynthesizer()
    voices = synthesizer.get_voices()

    for voice in voices:
        print(f"  • {voice}")

    print()


def _play_audio(audio_bytes: bytes):
    """Play audio bytes without interactive controls.

    Args:
        audio_bytes: Audio data to play
    """
    try:
        print_status("Playing audio...")
        playback = get_playback()
        playback.play_audio(audio_bytes)
        print_success("Audio playback complete")
    except Exception as e:
        print_error(f"Failed to play audio: {e}")
        print_warning("Check your audio device settings")
        sys.exit(1)


def _play_audio_interactive(audio_bytes: bytes, session_name: Optional[str] = None):
    """Play audio with interactive keyboard controls.

    Args:
        audio_bytes: Audio data to play
        session_name: Optional session name for saving playback position
    """
    try:
        print_status("Starting interactive playback...")
        print()
        print(f"{Fore.CYAN}🎮 Keyboard Controls:{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}SPACE{Style.RESET_ALL}  Pause/Resume")
        print(f"  {Fore.YELLOW}→{Style.RESET_ALL}      Seek forward 5 seconds")
        print(f"  {Fore.YELLOW}←{Style.RESET_ALL}      Seek backward 5 seconds")
        print(f"  {Fore.YELLOW}Q{Style.RESET_ALL}      Quit playback")
        print()
        print(f"{Fore.CYAN}💡 Note:{Style.RESET_ALL} Speed control not available during playback.")
        print("   Use --speed flag when starting (e.g., --speed 1.5)")
        print()

        # Create audio playback instance
        audio_playback = AudioPlayback()

        # Create controller
        controller = PlaybackController(audio_playback)

        # Start playback (this blocks until playback completes or user quits)
        controller.start(audio_bytes=audio_bytes, chunks=[])

        # Save playback position if session provided
        if session_name and controller.state.current_position_ms > 0:
            try:
                manager = SessionManager()
                # Update the session's playback position
                manager.update_session_position(session_name, controller.state.current_position_ms)
                logger.info(f"Saved playback position: {controller.state.current_position_ms}ms")
            except Exception as e:
                logger.warning(f"Failed to save playback position: {e}")

        print_success("Audio playback complete")

    except Exception as e:
        print_error(f"Failed to play audio: {e}")
        print_warning("Check your audio device settings")
        sys.exit(1)


def _play_audio_interactive_chunked(chunk_synthesizer: ChunkSynthesizer, session_name: Optional[str] = None):
    """Play audio with interactive keyboard controls using streaming chunks.

    Args:
        chunk_synthesizer: ChunkSynthesizer instance with prepared chunks
        session_name: Optional session name for saving playback position
    """
    try:
        print_status("Starting streaming playback...")
        print()
        print(f"{Fore.CYAN}🎮 Keyboard Controls:{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}SPACE{Style.RESET_ALL}  Pause/Resume")
        print(f"  {Fore.YELLOW}→{Style.RESET_ALL}      Seek forward 5 seconds (within current chunk)")
        print(f"  {Fore.YELLOW}←{Style.RESET_ALL}      Seek backward 5 seconds (within current chunk)")
        print(f"  {Fore.YELLOW}Q{Style.RESET_ALL}      Quit playback")
        print()
        print(f"{Fore.CYAN}💡 Note:{Style.RESET_ALL} Speed control not available during playback.")
        print("   Use --speed flag when starting (e.g., --speed 1.5)")
        print()

        # Create audio playback instance
        audio_playback = AudioPlayback()

        # Create controller
        controller = PlaybackController(audio_playback)

        # Start playback with chunk synthesizer (this blocks until playback completes or user quits)
        controller.start(chunk_synthesizer=chunk_synthesizer)

        # Save playback position if session provided
        if session_name and controller.state.current_position_ms > 0:
            try:
                manager = SessionManager()
                # Update the session's playback position
                manager.update_session_position(session_name, controller.state.current_position_ms)
                logger.info(f"Saved playback position: {controller.state.current_position_ms}ms")
            except Exception as e:
                logger.warning(f"Failed to save playback position: {e}")

        print_success("Audio playback complete")

    except Exception as e:
        print_error(f"Failed to play audio: {e}")
        print_warning("Check your audio device settings")
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
        print_success(f"Audio saved to: {output_path}")
    except Exception as e:
        print_error(f"Failed to save audio: {e}")
        print_warning("Check file path and permissions")
        sys.exit(1)


def command_list_sessions(args):
    """Handle the 'list-sessions' command.

    Args:
        args: Parsed command-line arguments
    """
    try:
        manager = SessionManager()
        sessions = manager.list_sessions()

        if not sessions:
            print_warning("No saved sessions found")
            print("\nTo save a session, use: vox read --url <URL> --save-session <NAME>")
            return

        print(f"\n{Fore.CYAN}📚 Saved Reading Sessions:{Style.RESET_ALL}\n")

        # Sort by last accessed (most recent first)
        sessions.sort(key=lambda s: s["last_accessed"], reverse=True)

        for session in sessions:
            # Format session name in cyan
            name = f"{Fore.CYAN}{session['session_name']}{Style.RESET_ALL}"

            # Progress indicator
            progress = session["progress_percent"]
            if progress >= 100:
                progress_str = f"{Fore.GREEN}✓ Complete{Style.RESET_ALL}"
            elif progress > 0:
                progress_str = f"{Fore.YELLOW}{progress:.1f}%{Style.RESET_ALL}"
            else:
                progress_str = f"{Fore.WHITE}0%{Style.RESET_ALL}"

            # Display session info
            print(f"  {name}")
            print(f"    URL: {session['url']}")
            print(
                f"    Progress: {progress_str} ({session['playback_position']:,} / {session['total_characters']:,} chars)"
            )
            print(f"    Last accessed: {session['last_accessed']}")
            print()

        print(f"Total: {len(sessions)} session(s)")
        print("\nTo resume a session, use: vox resume <session-name>")

    except Exception as e:
        print_error(f"Failed to list sessions: {e}")
        sys.exit(1)


def command_resume(args):
    """Handle the 'resume' command.

    Args:
        args: Parsed command-line arguments
    """
    try:
        print_status(f"Resuming session '{args.session_name}'...")
        manager = SessionManager()

        # Load session
        text, position = manager.resume_session(args.session_name)

        if not text:
            print_error("Session has no content to resume")
            sys.exit(1)

        # Calculate progress
        progress_percent = (position / len(text)) * 100 if len(text) > 0 else 0

        print_success(f"Loaded session at position {position:,} / {len(text):,} chars ({progress_percent:.1f}%)")

        # Get the text from the position forward
        remaining_text = text[position:]

        if not remaining_text:
            print_warning("Session is already complete!")
            return

        print_status(f"Synthesizing {len(remaining_text):,} characters...")

        # Synthesize from resume position
        voice = args.voice or config.DEFAULT_TTS_VOICE
        speed = args.speed or config.DEFAULT_TTS_SPEED
        synthesizer = PiperSynthesizer(voice=voice)
        audio_bytes = synthesizer.synthesize(remaining_text, speed=speed)

        print_success(f"Generated {len(audio_bytes)} bytes of audio")

        # Play audio with interactive controls
        _play_audio_interactive(audio_bytes, session_name=args.session_name)

    except ValueError as e:
        print_error(f"Session not found: {e}")
        print("\nAvailable sessions:")
        command_list_sessions(args)
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to resume session: {e}")
        sys.exit(1)


def command_delete_session(args):
    """Handle the 'delete-session' command.

    Args:
        args: Parsed command-line arguments
    """
    try:
        print_status(f"Deleting session '{args.session_name}'...")
        manager = SessionManager()
        manager.delete_session(args.session_name)
        print_success(f"Session '{args.session_name}' deleted")
    except ValueError as e:
        print_error(f"Session not found: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to delete session: {e}")
        sys.exit(1)


def command_transcribe(args):
    """Handle the 'transcribe' command.

    Args:
        args: Parsed command-line arguments
    """
    from pathlib import Path

    from src.stt.transcriber import Transcriber
    from src.stt.ui import format_device_list, format_error_box
    from src.utils.errors import MicrophoneError, ModelLoadError, TranscriptionError

    try:
        # Handle --set-default-model flag
        if args.set_default_model:
            if not args.model:
                print_error("--set-default-model requires --model to be specified")
                sys.exit(1)

            if config.set_stt_default_model(args.model):
                print_success(f"Set default STT model to: {args.model}")
            else:
                print_error(f"Invalid model '{args.model}'. Valid options: {', '.join(config.VALID_STT_MODELS)}")
                sys.exit(1)

        # Initialize transcriber once (uses saved default if args.model is None)
        if args.model:
            print_status(f"Initializing speech-to-text with model: {args.model}")
        else:
            default_model = config.get_stt_default_model()
            print_status(f"Initializing speech-to-text with default model: {default_model}")

        transcriber = Transcriber(model_name=args.model)

        # Loop to allow retries
        while True:
            try:
                # Prepare output path if specified
                output_path = Path(args.output) if args.output else None

                # Run transcription
                text = transcriber.transcribe(output_file=output_path)

                print_success("Transcription complete!")

                # Ask if user wants to record again
                print()
                response = input(f"{Fore.CYAN}?{Style.RESET_ALL} Record again? (y/N): ").strip().lower()

                if response in ["y", "yes"]:
                    print()  # Add blank line before next recording
                    continue
                elif response in ["", "n", "no"]:
                    break
                else:
                    print_warning(f"Unknown response '{response}', exiting...")
                    break

            except KeyboardInterrupt:
                print()
                print_warning("Recording cancelled by user")
                break

    except MicrophoneError as e:
        error_box = format_error_box(
            error_type="Microphone Error",
            message=e.message,
            suggestions=[
                "Check that a microphone is connected",
                "Verify microphone permissions in Windows Settings (Privacy & security > Microphone)",
                "Ensure no other application is using the microphone",
            ],
        )
        print(f"\n{error_box}\n")
        print(format_device_list())
        logger.error(f"Microphone error: {e}")
        sys.exit(1)

    except ModelLoadError as e:
        error_box = format_error_box(
            error_type="Model Loading Error",
            message=e.message,
            suggestions=[
                f"Check internet connection (first download of '{args.model or config.get_stt_default_model()}' model)",
                f"Verify cache directory exists: {config.STT_MODEL_CACHE}",
                "Try a smaller model: vox transcribe --model tiny",
            ],
        )
        print(f"\n{error_box}\n")
        logger.error(f"Model load error: {e}")
        sys.exit(1)

    except TranscriptionError as e:
        error_box = format_error_box(
            error_type="Transcription Error",
            message=e.message,
            suggestions=[
                "Ensure you spoke clearly during recording",
                "Check microphone input volume in Windows settings",
                "Try recording again with less background noise",
                "Try a larger model for better accuracy: vox transcribe --model large",
            ],
        )
        print(f"\n{error_box}\n")
        logger.error(f"Transcription error: {e}")
        sys.exit(1)

    except Exception as e:
        error_box = format_error_box(
            error_type="Unexpected Error",
            message=str(e),
            suggestions=[
                "Check log files for details",
                "Report this issue if it persists",
            ],
        )
        print(f"\n{error_box}\n")
        logger.exception("Unexpected error in transcribe command")
        sys.exit(1)


if __name__ == "__main__":
    main()
