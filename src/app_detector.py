"""
XboxConnexion - Foreground CAD Application Detector
Detects when the user switches to SolidWorks, CATIA, Fusion 360, etc., to auto-select presets.
"""

import ctypes
from ctypes import wintypes
import os
import time
import threading
from typing import Callable, Optional

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

class AppDetector:
    """Monitors the active foreground window to detect CAD application switches."""

    def __init__(self, on_cad_focus_callback: Optional[Callable[[str], None]] = None):
        self.callback = on_cad_focus_callback
        self.enabled = True
        self._running = False
        self._last_process = ""
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def get_foreground_process_name(self) -> Optional[str]:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == 0:
            return None
            
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_process:
            return None

        buf = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(1024)
        res = kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size))
        kernel32.CloseHandle(h_process)
        if res:
            return os.path.basename(buf.value).lower()
        return None

    def _monitor_loop(self):
        while self._running:
            if self.enabled and self.callback:
                try:
                    proc = self.get_foreground_process_name()
                    if proc and proc != self._last_process:
                        self._last_process = proc
                        self.callback(proc)
                except Exception:
                    pass
            time.sleep(0.5)
