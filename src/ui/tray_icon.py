"""
XboxConnexion - System Tray Integration
Allows the application to run smoothly in the background while working in CAD.
"""

import threading
from PIL import Image, ImageDraw
import pystray
from typing import Callable, Dict, Any, List

def create_tray_image(active_color: str = "#00d26a") -> Image.Image:
    """Draws a clean vector-style tray icon."""
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Background circle
    draw.ellipse((4, 4, 60, 60), fill='#181a20', outline=active_color, width=4)
    # Controller D-Pad cross
    draw.rectangle((26, 16, 38, 48), fill=active_color)
    draw.rectangle((16, 26, 48, 38), fill=active_color)
    # Center dot
    draw.ellipse((28, 28, 36, 36), fill='#181a20')
    return img

class SystemTrayManager:
    """Manages system tray lifecycle and context menu."""

    def __init__(self,
                 on_show_window: Callable[[], None],
                 on_select_preset: Callable[[str], None],
                 on_toggle_pause: Callable[[], bool],
                 on_exit: Callable[[], None]):
        self.on_show = on_show_window
        self.on_select_preset = on_select_preset
        self.on_toggle_pause = on_toggle_pause
        self.on_exit = on_exit

        self.icon: pystray.Icon = None
        self._presets: List[Dict[str, Any]] = []
        self._active_preset_id: str = "solidworks"
        self._is_paused = False

    def start(self, presets: List[Dict[str, Any]], active_id: str):
        self._presets = presets
        self._active_preset_id = active_id
        
        menu = self._build_menu()
        self.icon = pystray.Icon(
            "XboxConnexion",
            create_tray_image("#00d26a"),
            "XboxConnexion - 3D CAD SpaceMouse",
            menu=menu
        )
        threading.Thread(target=self.icon.run, daemon=True).start()

    def update_presets(self, presets: List[Dict[str, Any]], active_id: str):
        self._presets = presets
        self._active_preset_id = active_id
        if self.icon:
            self.icon.menu = self._build_menu()

    def update_pause_state(self, is_paused: bool):
        self._is_paused = is_paused
        if self.icon:
            self.icon.menu = self._build_menu()

    def _build_menu(self) -> pystray.Menu:
        # Build Preset Radio Submenu
        preset_items = []
        for p in self._presets:
            p_id = p.get('id', '')
            p_name = p.get('name', 'Preset')
            
            def make_handler(target_id=p_id):
                return lambda icon, item: self.on_select_preset(target_id)
            
            def make_checked(target_id=p_id):
                return lambda item: target_id == self._active_preset_id

            preset_items.append(
                pystray.MenuItem(
                    p_name,
                    make_handler(p_id),
                    checked=make_checked(p_id),
                    radio=True
                )
            )

        return pystray.Menu(
            pystray.MenuItem("Open XboxConnexion", lambda icon, item: self.on_show(), default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Active Preset", pystray.Menu(*preset_items)),
            pystray.MenuItem(
                "Resume Navigation" if self._is_paused else "Pause Navigation",
                lambda icon, item: self.on_toggle_pause()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda icon, item: self._do_exit())
        )

    def _do_exit(self):
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()

    def stop(self):
        if self.icon:
            self.icon.stop()
