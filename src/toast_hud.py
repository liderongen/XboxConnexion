"""
XboxConnexion - On-Screen Display (OSD) Toast HUD
Floating, non-intrusive notification overlay that appears when switching presets.
Uses WS_EX_NOACTIVATE so it never steals focus from CAD applications.
"""

import tkinter as tk
import ctypes
from ctypes import wintypes
import threading
import time

GWL_EXSTYLE       = -20
WS_EX_NOACTIVATE  = 0x08000000
WS_EX_TOOLWINDOW  = 0x00000080
WS_EX_TOPMOST     = 0x00000008
WS_EX_TRANSPARENT = 0x00000020

class ToastHUD:
    """Non-activating transparent overlay for preset switch notifications."""

    def __init__(self):
        self._root = None
        self._window = None
        self._label_title = None
        self._label_sub = None
        self._frame = None
        self._hide_timer = None
        self._is_ready = False
        self._queue = []
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        self._root = tk.Tk()
        self._root.withdraw()

        self._window = tk.Toplevel(self._root)
        self._window.withdraw()
        self._window.overrideredirect(True)
        self._window.attributes('-topmost', True)
        self._window.attributes('-alpha', 0.92)

        # Style frame
        self._frame = tk.Frame(
            self._window,
            bg='#181a20',
            highlightbackground='#00d26a',
            highlightthickness=2,
            padx=20,
            pady=10
        )
        self._frame.pack(fill='both', expand=True)

        self._label_title = tk.Label(
            self._frame,
            text="",
            font=("Segoe UI", 13, "bold"),
            fg="#ffffff",
            bg="#181a20"
        )
        self._label_title.pack(anchor="center")

        self._label_sub = tk.Label(
            self._frame,
            text="",
            font=("Segoe UI", 9),
            fg="#9da5b4",
            bg="#181a20"
        )
        self._label_sub.pack(anchor="center", pady=(2, 0))

        self._window.update_idletasks()
        
        # Apply Windows extended style
        hwnd = ctypes.windll.user32.GetParent(self._window.winfo_id())
        if hwnd == 0:
            hwnd = self._window.winfo_id()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd,
            GWL_EXSTYLE,
            style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST
        )

        self._is_ready = True
        self._root.mainloop()

    def show(self, title: str, subtitle: str = "", accent_color: str = "#00d26a", duration_s: float = 1.6):
        """Displays toast overlay with given title, subtitle and accent."""
        if not self._is_ready or not self._root:
            return

        def _do_show():
            if self._hide_timer:
                self._hide_timer.cancel()

            self._label_title.config(text=f"🎮  {title}")
            self._label_sub.config(text=subtitle)
            self._frame.config(highlightbackground=accent_color)

            # Center near top of primary monitor
            width = 380
            height = 68
            screen_w = self._root.winfo_screenwidth()
            pos_x = (screen_w - width) // 2
            pos_y = 60

            self._window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
            self._window.deiconify()
            self._window.lift()

            # Timer to auto-hide
            self._hide_timer = threading.Timer(duration_s, self._hide)
            self._hide_timer.start()

        self._root.after(0, _do_show)

    def _hide(self):
        if self._window and self._root:
            self._root.after(0, self._window.withdraw)
