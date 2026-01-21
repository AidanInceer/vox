"""System tray manager for Vox application.

Provides system tray icon functionality using pystray, allowing the app
to minimize to tray and provide quick access via tray menu.
"""

import threading
from pathlib import Path
from typing import Callable, Optional

# pystray must be imported after PIL
import pystray
from PIL import Image


class SystemTrayManager:
    """Manages the system tray icon for Vox application.

    Provides:
    - Tray icon with Vox branding
    - Right-click menu with Show/Hide/Exit options
    - Minimize to tray on window close
    - Restore from tray on click/menu action

    Attributes:
        _icon: The pystray Icon instance.
        _on_show: Callback when user clicks Show.
        _on_hide: Callback when user clicks Hide.
        _on_exit: Callback when user clicks Exit.
        _is_visible: Whether the main window is visible.
    """

    def __init__(
        self,
        on_show: Optional[Callable[[], None]] = None,
        on_hide: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the system tray manager.

        Args:
            on_show: Callback when Show is selected from tray menu.
            on_hide: Callback when Hide is selected from tray menu.
            on_exit: Callback when Exit is selected from tray menu.
        """
        self._on_show = on_show
        self._on_hide = on_hide
        self._on_exit = on_exit
        self._is_visible = True
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def create_icon(self) -> pystray.Icon:
        """Create and return the pystray Icon.

        Returns:
            Configured pystray.Icon instance.
        """
        image = self._load_icon_image()
        menu = self.create_menu()

        self._icon = pystray.Icon(
            name="vox",
            icon=image,
            title="Vox - Audio-Text Converter",
            menu=menu,
        )

        return self._icon

    def create_menu(self) -> pystray.Menu:
        """Create the tray menu with Show/Hide/Exit options.

        Returns:
            pystray.Menu with configured menu items.
        """
        return pystray.Menu(
            pystray.MenuItem(
                "Show Vox",
                self._handle_show,
                default=True,  # Double-click action
            ),
            pystray.MenuItem(
                "Hide",
                self._handle_hide,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Exit",
                self._handle_exit,
            ),
        )

    def start(self) -> None:
        """Start the system tray icon in a background thread."""
        if self._icon is None:
            self.create_icon()

        self._thread = threading.Thread(target=self._run_icon, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop and remove the system tray icon."""
        if self._icon:
            self._icon.stop()
            self._icon = None

    def update_menu_state(self, is_visible: bool) -> None:
        """Update the tray menu based on window visibility.

        Args:
            is_visible: Whether the main window is currently visible.
        """
        self._is_visible = is_visible

    def show_notification(self, title: str, message: str) -> None:
        """Show a system notification from the tray.

        Args:
            title: Notification title.
            message: Notification message.
        """
        if self._icon:
            self._icon.notify(message, title)

    def _run_icon(self) -> None:
        """Run the icon event loop (called in background thread)."""
        if self._icon:
            self._icon.run()

    def _load_icon_image(self) -> Image.Image:
        """Load the tray icon image.

        Returns:
            PIL Image for the tray icon.
        """
        # Try to load custom icon first
        icon_paths = [
            Path("build/resources/vox.ico"),
            Path("imgs/vox.ico"),
            Path("imgs/icon.ico"),
        ]

        for path in icon_paths:
            if path.exists():
                return Image.open(path)

        # Fallback: Create a simple colored square icon
        return self._create_fallback_icon()

    def _create_fallback_icon(self) -> Image.Image:
        """Create a simple fallback icon if no icon file exists.

        Returns:
            PIL Image with a simple Vox icon.
        """
        # Create a 64x64 image with Vox primary color
        size = 64
        color = (69, 130, 236)  # #4582ec - primary blue

        image = Image.new("RGB", (size, size), color)

        # Draw a simple "V" shape in white
        from PIL import ImageDraw

        draw = ImageDraw.Draw(image)

        # V shape points
        margin = 12
        points = [
            (margin, margin),  # Top-left
            (size // 2, size - margin),  # Bottom-center
            (size - margin, margin),  # Top-right
        ]

        draw.line(points[:2], fill="white", width=6)
        draw.line(points[1:], fill="white", width=6)

        return image

    def _handle_show(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Handle Show menu item click.

        Args:
            icon: The pystray Icon instance.
            item: The clicked menu item.
        """
        self._is_visible = True
        if self._on_show:
            self._on_show()

    def _handle_hide(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Handle Hide menu item click.

        Args:
            icon: The pystray Icon instance.
            item: The clicked menu item.
        """
        self._is_visible = False
        if self._on_hide:
            self._on_hide()

    def _handle_exit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Handle Exit menu item click.

        Args:
            icon: The pystray Icon instance.
            item: The clicked menu item.
        """
        self.stop()
        if self._on_exit:
            self._on_exit()
