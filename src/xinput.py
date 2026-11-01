"""
XboxConnexion - Low-level XInput Wrapper
Direct ctypes access to Windows XInput API for zero-latency gamepad polling and haptics.
"""

import ctypes
from ctypes import wintypes
import time
from typing import Optional, Tuple, Dict, Any

# XInput Button Constants
XINPUT_GAMEPAD_DPAD_UP        = 0x0001
XINPUT_GAMEPAD_DPAD_DOWN      = 0x0002
XINPUT_GAMEPAD_DPAD_LEFT      = 0x0004
XINPUT_GAMEPAD_DPAD_RIGHT     = 0x0008
XINPUT_GAMEPAD_START          = 0x0010
XINPUT_GAMEPAD_BACK           = 0x0020
XINPUT_GAMEPAD_LEFT_THUMB     = 0x0040
XINPUT_GAMEPAD_RIGHT_THUMB    = 0x0080
XINPUT_GAMEPAD_LEFT_SHOULDER  = 0x0100
XINPUT_GAMEPAD_RIGHT_SHOULDER = 0x0200
XINPUT_GAMEPAD_GUIDE          = 0x0400  # Exposed by XInputGetStateEx (ordinal 100)
XINPUT_GAMEPAD_A              = 0x1000
XINPUT_GAMEPAD_B              = 0x2000
XINPUT_GAMEPAD_X              = 0x4000
XINPUT_GAMEPAD_Y              = 0x8000

# Thumbstick default deadzones
XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE  = 7849
XINPUT_GAMEPAD_RIGHT_THUMB_DEADZONE = 8689
XINPUT_GAMEPAD_TRIGGER_THRESHOLD    = 30

ERROR_SUCCESS = 0
ERROR_DEVICE_NOT_CONNECTED = 1167

class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ('wButtons', wintypes.WORD),
        ('bLeftTrigger', wintypes.BYTE),
        ('bRightTrigger', wintypes.BYTE),
        ('sThumbLX', wintypes.SHORT),
        ('sThumbLY', wintypes.SHORT),
        ('sThumbRX', wintypes.SHORT),
        ('sThumbRY', wintypes.SHORT),
    ]

class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ('dwPacketNumber', wintypes.DWORD),
        ('Gamepad', XINPUT_GAMEPAD),
    ]

class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [
        ('wLeftMotorSpeed', wintypes.WORD),
        ('wRightMotorSpeed', wintypes.WORD),
    ]

class XINPUT_BATTERY_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BatteryType', wintypes.BYTE),
        ('BatteryLevel', wintypes.BYTE),
    ]

BATTERY_DEVTYPE_GAMEPAD = 0x00
BATTERY_TYPE_DISCONNECTED = 0x00
BATTERY_TYPE_WIRED = 0x01
BATTERY_TYPE_ALKALINE = 0x02
BATTERY_TYPE_NIMH = 0x03
BATTERY_TYPE_UNKNOWN = 0xFF

BATTERY_LEVEL_EMPTY = 0x00
BATTERY_LEVEL_LOW = 0x01
BATTERY_LEVEL_MEDIUM = 0x02
BATTERY_LEVEL_FULL = 0x03

class XInputDevice:
    """Manages low-level XInput controller communication."""
    
    def __init__(self, controller_id: int = 0):
        self.controller_id = controller_id
        self._dll = None
        self._get_state_func = None
        self._set_state_func = None
        self._get_battery_func = None
        self._is_connected = False
        self._last_packet_number = -1
        self._init_dll()

    def _init_dll(self):
        # Try loading xinput dlls in order of preference
        dll_names = ['xinput1_4.dll', 'xinput1_3.dll', 'xinput9_1_0.dll']
        for name in dll_names:
            try:
                self._dll = ctypes.windll.LoadLibrary(name)
                # Try getting secret ordinal 100 (XInputGetStateEx) which supports the Xbox Guide button
                try:
                    self._get_state_func = self._dll[100]
                except Exception:
                    self._get_state_func = getattr(self._dll, 'XInputGetState', None)
                
                self._set_state_func = getattr(self._dll, 'XInputSetState', None)
                self._get_battery_func = getattr(self._dll, 'XInputGetBatteryInformation', None)
                break
            except Exception:
                continue

        if not self._dll or not self._get_state_func:
            print("[XInput] Warning: Failed to load Windows XInput library.")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def poll(self) -> Optional[Dict[str, Any]]:
        """Polls current controller state. Returns None if disconnected."""
        if not self._get_state_func:
            return None

        state = XINPUT_STATE()
        res = self._get_state_func(self.controller_id, ctypes.byref(state))
        if res == ERROR_SUCCESS:
            self._is_connected = True
            gp = state.Gamepad
            
            # Button states
            btns = gp.wButtons
            buttons = {
                'dpad_up': bool(btns & XINPUT_GAMEPAD_DPAD_UP),
                'dpad_down': bool(btns & XINPUT_GAMEPAD_DPAD_DOWN),
                'dpad_left': bool(btns & XINPUT_GAMEPAD_DPAD_LEFT),
                'dpad_right': bool(btns & XINPUT_GAMEPAD_DPAD_RIGHT),
                'start': bool(btns & XINPUT_GAMEPAD_START),
                'back': bool(btns & XINPUT_GAMEPAD_BACK),
                'ls_click': bool(btns & XINPUT_GAMEPAD_LEFT_THUMB),
                'rs_click': bool(btns & XINPUT_GAMEPAD_RIGHT_THUMB),
                'lb': bool(btns & XINPUT_GAMEPAD_LEFT_SHOULDER),
                'rb': bool(btns & XINPUT_GAMEPAD_RIGHT_SHOULDER),
                'guide': bool(btns & XINPUT_GAMEPAD_GUIDE),
                'a': bool(btns & XINPUT_GAMEPAD_A),
                'b': bool(btns & XINPUT_GAMEPAD_B),
                'x': bool(btns & XINPUT_GAMEPAD_X),
                'y': bool(btns & XINPUT_GAMEPAD_Y),
            }

            # Raw trigger values: 0 to 255 -> normalize to 0.0 .. 1.0
            lt = gp.bLeftTrigger / 255.0
            rt = gp.bRightTrigger / 255.0

            # Raw thumbstick values: -32768 to 32767 -> normalize to -1.0 .. 1.0
            lx = max(-1.0, gp.sThumbLX / 32767.0)
            ly = max(-1.0, gp.sThumbLY / 32767.0)
            rx = max(-1.0, gp.sThumbRX / 32767.0)
            ry = max(-1.0, gp.sThumbRY / 32767.0)

            return {
                'connected': True,
                'packet': state.dwPacketNumber,
                'lx': lx,
                'ly': ly,
                'rx': rx,
                'ry': ry,
                'lt': lt,
                'rt': rt,
                'buttons': buttons,
            }
        else:
            self._is_connected = False
            return None

    def set_vibration(self, left_speed: float, right_speed: float):
        """Sets rumble motor speeds (0.0 to 1.0)."""
        if not self._set_state_func or not self._is_connected:
            return
        w_left = int(max(0.0, min(1.0, left_speed)) * 65535)
        w_right = int(max(0.0, min(1.0, right_speed)) * 65535)
        vib = XINPUT_VIBRATION(w_left, w_right)
        try:
            self._set_state_func(self.controller_id, ctypes.byref(vib))
        except Exception:
            pass

    def pulse_rumble(self, pulses: int = 1, intensity: float = 0.5, duration_s: float = 0.12):
        """Generates haptic pulses (used for preset switching confirmation)."""
        import threading
        def _pulse():
            for i in range(pulses):
                self.set_vibration(intensity, intensity)
                time.sleep(duration_s)
                self.set_vibration(0, 0)
                if i < pulses - 1:
                    time.sleep(0.08)
        threading.Thread(target=_pulse, daemon=True).start()

    def get_battery(self) -> Dict[str, Any]:
        """Returns battery information."""
        if not self._get_battery_func or not self._is_connected:
            return {'type': 'unknown', 'level': 'unknown'}
        bat = XINPUT_BATTERY_INFORMATION()
        res = self._get_battery_func(self.controller_id, BATTERY_DEVTYPE_GAMEPAD, ctypes.byref(bat))
        if res == ERROR_SUCCESS:
            type_str = {
                BATTERY_TYPE_DISCONNECTED: 'disconnected',
                BATTERY_TYPE_WIRED: 'wired',
                BATTERY_TYPE_ALKALINE: 'alkaline',
                BATTERY_TYPE_NIMH: 'nimh',
                BATTERY_TYPE_UNKNOWN: 'unknown'
            }.get(bat.BatteryType, 'unknown')

            level_str = {
                BATTERY_LEVEL_EMPTY: 'empty',
                BATTERY_LEVEL_LOW: 'low',
                BATTERY_LEVEL_MEDIUM: 'medium',
                BATTERY_LEVEL_FULL: 'full'
            }.get(bat.BatteryLevel, 'unknown')

            return {'type': type_str, 'level': level_str}
        return {'type': 'unknown', 'level': 'unknown'}
