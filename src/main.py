"""PageReader CLI - Main entry point and command-line interface.

This is the entry point for the PageReader application.
Provides commands for reading browser tabs, URLs, and files aloud.
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
    """Main entry point for PageReader CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle version flag
    if hasattr(args, 'version') and args.version:
        print("PageReader v1.0.0")
        sys.exit(0)

    # Setup logging
    log_level = "DEBUG" if args.verbose else config.LOG_LEVEL
    setup_logging(name="pagereader", level=log_level)

    # Dispatch to appropriate command
    try:
        if args.command == "read":
            command_read(args)
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
║                          PageReader v1.0.0                        ║
║          Read web pages and browser tabs aloud with AI TTS        ║
╚═══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}📚 Session Management:{Style.RESET_ALL}
  Save reading sessions and resume later from where you left off
  
{Fore.YELLOW}🎮 Interactive Controls:{Style.RESET_ALL}
  Control playback with keyboard shortcuts during audio playback
"""

    epilog = f"""
{Fore.CYAN}═══════════════════════════════════════════════════════════════════
📖 Examples:
═══════════════════════════════════════════════════════════════════{Style.RESET_ALL}

  {Fore.GREEN}# Read from a URL{Style.RESET_ALL}
  pagereader read --url https://example.com

  {Fore.GREEN}# Save a reading session{Style.RESET_ALL}
  pagereader read --url https://example.com --save-session my-article

  {Fore.GREEN}# List saved sessions{Style.RESET_ALL}
  pagereader list-sessions

  {Fore.GREEN}# Resume a session{Style.RESET_ALL}
  pagereader resume my-article

  {Fore.GREEN}# Read from a local file{Style.RESET_ALL}
  pagereader read --file article.html

  {Fore.GREEN}# Read with custom voice and speed{Style.RESET_ALL}
  pagereader read --url https://example.com --voice en_US-libritts-high --speed 1.5

  {Fore.GREEN}# Save audio to file{Style.RESET_ALL}
  pagereader read --url https://example.com --output audio.wav

  {Fore.GREEN}# List all open browser tabs{Style.RESET_ALL}
  pagereader list tabs

  {Fore.GREEN}# List available voices{Style.RESET_ALL}
  pagereader list voices

{Fore.CYAN}═══════════════════════════════════════════════════════════════════{Style.RESET_ALL}
💡 For more help on a specific command: {Fore.YELLOW}pagereader <command> --help{Style.RESET_ALL}
"""

    parser = argparse.ArgumentParser(
        prog="pagereader",
        description=description,
        epilog=epilog,
        formatter_class=ColoredHelpFormatter,
        add_help=False,  # We'll add custom help
    )

    # Add custom help argument with color
    parser.add_argument(
        "-h", "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit"
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
    read_group.add_argument(
        "--url", metavar="URL", help="Read content from a URL (http:// or https://)"
    )
    read_group.add_argument("--file", metavar="FILE_PATH", help="Read content from a local HTML file")
    read_group.add_argument(
        "--active", action="store_true", help="Read the currently active browser tab"
    )

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
        "--save-session",
        metavar="NAME",
        help="Save this reading session with a name for later resume"
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
        help=f"{Fore.YELLOW}Show configuration{Style.RESET_ALL}",
        formatter_class=ColoredHelpFormatter,
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
                tts_settings={"voice": args.voice, "speed": args.speed}
            )
            print_success(f"Session saved (ID: {session_id})")
        except ValueError as e:
            print_error(f"Failed to save session: {e}")
            sys.exit(1)

    # Step 3: Synthesize to speech
    start_time = time.time()
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
        _save_audio(audio_bytes, args.output)
    elif not args.no_play:
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
        print(f"   Use --speed flag when starting (e.g., --speed 1.5)")
        print()
        
        # Create audio playback instance
        audio_playback = AudioPlayback()
        
        # Create controller
        controller = PlaybackController(audio_playback)
        
        # Start playback (this blocks until playback completes or user quits)
        controller.start(audio_bytes, [])
        
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
            print("\nTo save a session, use: pagereader read --url <URL> --save-session <NAME>")
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
            print(f"    Progress: {progress_str} ({session['playback_position']:,} / {session['total_characters']:,} chars)")
            print(f"    Last accessed: {session['last_accessed']}")
            print()

        print(f"Total: {len(sessions)} session(s)")
        print(f"\nTo resume a session, use: pagereader resume <session-name>")

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


if __name__ == "__main__":
    main()
