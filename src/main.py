"""vox - Speech-to-text application.

This is the entry point for the vox application.
Launches the speech-to-text GUI directly.
"""

import logging

from src import config
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point for vox.
    
    Directly launches the speech-to-text GUI.
    """
    # Create default config file if it doesn't exist
    config.create_default_config()

    # Check and run config migration if needed
    from src.utils.migration import migrate_config

    try:
        migrate_config()
    except Exception:
        # Log but don't fail - migration is non-critical
        pass

    # Setup logging
    setup_logging(name="vox", level=config.LOG_LEVEL)

    # Launch the GUI
    launch_gui()


def launch_gui():
    """Launch the desktop application."""
    from src.persistence.database import VoxDatabase
    from src.ui.main_window import VoxMainWindow
    from src.voice_input.controller import VoiceInputController

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

    # Run the main window event loop
    try:
        window.run()
    finally:
        # Cleanup
        database.close()


if __name__ == "__main__":
    main()
