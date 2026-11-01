"""
XboxConnexion - CAD Navigation & Input Emulation Engine
Emulates SpaceMouse 6-DoF navigation (Pan, Orbit, Zoom, Roll) in SolidWorks, CATIA, etc.
Features zero-jerk boundary wrapping (Infinite Canvas) and smart cursor restore.
"""

import ctypes
from ctypes import wintypes
import time
from typing import Dict, Any, Optional, Tuple, List

# Win32 Constants
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE       = 0x0001
MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040
MOUSEEVENTF_WHEEL      = 0x0800
WHEEL_DELTA            = 120

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

# Virtual Key Codes
VK_BACK    = 0x08
VK_TAB     = 0x09
VK_RETURN  = 0x0D
VK_SHIFT   = 0x10
VK_CONTROL = 0x11
VK_MENU    = 0x12  # Alt
VK_ESCAPE  = 0x1B
VK_SPACE   = 0x20
VK_LEFT    = 0x25
VK_UP      = 0x26
VK_RIGHT   = 0x27
VK_DOWN    = 0x28
VK_F1      = 0x70
VK_F2      = 0x71
VK_F3      = 0x72
VK_F4      = 0x73
VK_F5      = 0x74
VK_F6      = 0x75
VK_F7      = 0x76
VK_F8      = 0x77
VK_F9      = 0x78
VK_F10     = 0x79
VK_F11     = 0x7A
VK_F12     = 0x7B

# Monitor Metrics
SM_XVIRTUALSCREEN  = 76
SM_YVIRTUALSCREEN  = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79

class POINT(ctypes.Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

class RECT(ctypes.Structure):
    _fields_ = [('left', wintypes.LONG), ('top', wintypes.LONG), ('right', wintypes.LONG), ('bottom', wintypes.LONG)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_size_t),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_size_t),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ('uMsg', wintypes.DWORD),
        ('wParamL', wintypes.WORD),
        ('wParamH', wintypes.WORD),
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT), ('hi', HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [('type', wintypes.DWORD), ('u', INPUT_UNION)]

user32 = ctypes.windll.user32
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT

KEY_MAP = {
    'ctrl': VK_CONTROL,
    'control': VK_CONTROL,
    'shift': VK_SHIFT,
    'alt': VK_MENU,
    'escape': VK_ESCAPE,
    'esc': VK_ESCAPE,
    'space': VK_SPACE,
    'f': ord('F'),
    'z': ord('Z'),
    'y': ord('Y'),
    'x': ord('X'),
    'a': ord('A'),
    'b': ord('B'),
    'c': ord('C'),
    '0': ord('0'),
    '1': ord('1'),
    '2': ord('2'),
    '3': ord('3'),
    '4': ord('4'),
    '5': ord('5'),
    '6': ord('6'),
    '7': ord('7'),
    '8': ord('8'),
    '9': ord('9'),
    'f1': VK_F1,
    'f2': VK_F2,
    'f3': VK_F3,
    'f4': VK_F4,
    'f5': VK_F5,
    'f6': VK_F6,
    'f7': VK_F7,
    'f8': VK_F8,
    'f9': VK_F9,
    'f10': VK_F10,
    'f11': VK_F11,
    'f12': VK_F12,
}

class CADEmulator:
    """Handles high precision injection of mouse and keyboard events into CAD applications."""

    def __init__(self):
        # Anchor and tracking state
        self.anchor_x = 0
        self.anchor_y = 0
        self.is_navigating = False
        self.current_mode: Optional[str] = None  # 'pan', 'orbit', 'zoom', 'roll'
        
        # Currently held physical states by emulator
        self.held_mmb = False
        self.held_rmb = False
        self.held_ctrl = False
        self.held_shift = False
        self.held_alt = False
        
        # Sub-pixel accumulators for ultra-smooth motion
        self.accum_x = 0.0
        self.accum_y = 0.0
        self.accum_zoom = 0.0
        
        # Bounds margin for wrapping
        self.boundary_margin = 35

    def get_cursor_pos(self) -> Tuple[int, int]:
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)

    def set_cursor_pos(self, x: int, y: int):
        user32.SetCursorPos(int(x), int(y))

    def get_screen_bounds(self) -> Tuple[int, int, int, int]:
        """Returns virtual screen boundaries (left, top, right, bottom)."""
        left = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        top = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
        w = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
        h = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
        return (left, top, left + w, top + h)

    def _send_inputs(self, inputs: List[INPUT]):
        n = len(inputs)
        if n == 0:
            return
        arr = (INPUT * n)(*inputs)
        user32.SendInput(n, arr, ctypes.sizeof(INPUT))

    def _create_mouse_input(self, flags: int, dx: int = 0, dy: int = 0, data: int = 0) -> INPUT:
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.u.mi.dx = dx
        inp.u.mi.dy = dy
        inp.u.mi.mouseData = data
        inp.u.mi.dwFlags = flags
        inp.u.mi.time = 0
        inp.u.mi.dwExtraInfo = 0
        return inp

    def _create_key_input(self, vk: int, keyup: bool = False) -> INPUT:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.u.ki.wVk = vk
        inp.u.ki.wScan = 0
        inp.u.ki.dwFlags = KEYEVENTF_KEYUP if keyup else 0
        inp.u.ki.time = 0
        inp.u.ki.dwExtraInfo = 0
        return inp

    def send_key_combination(self, combo: List[str]):
        """Sends a complete key combo press and release, e.g. ['ctrl', '7']."""
        vks = [KEY_MAP.get(k.lower().strip(), 0) for k in combo]
        vks = [v for v in vks if v != 0]
        if not vks:
            return

        presses = [self._create_key_input(v, keyup=False) for v in vks]
        releases = [self._create_key_input(v, keyup=True) for v in reversed(vks)]
        self._send_inputs(presses)
        time.sleep(0.01)
        self._send_inputs(releases)

    def _set_keys_and_buttons(self, ctrl: bool = False, shift: bool = False, alt: bool = False,
                               mmb: bool = False, rmb: bool = False):
        """Diffs desired state vs held state and sends minimal input events."""
        inputs = []
        
        # Key modifiers
        if ctrl and not self.held_ctrl:
            inputs.append(self._create_key_input(VK_CONTROL, keyup=False))
            self.held_ctrl = True
        elif not ctrl and self.held_ctrl:
            inputs.append(self._create_key_input(VK_CONTROL, keyup=True))
            self.held_ctrl = False

        if shift and not self.held_shift:
            inputs.append(self._create_key_input(VK_SHIFT, keyup=False))
            self.held_shift = True
        elif not shift and self.held_shift:
            inputs.append(self._create_key_input(VK_SHIFT, keyup=True))
            self.held_shift = False

        if alt and not self.held_alt:
            inputs.append(self._create_key_input(VK_MENU, keyup=False))
            self.held_alt = True
        elif not alt and self.held_alt:
            inputs.append(self._create_key_input(VK_MENU, keyup=True))
            self.held_alt = False

        # Mouse buttons
        if mmb and not self.held_mmb:
            inputs.append(self._create_mouse_input(MOUSEEVENTF_MIDDLEDOWN))
            self.held_mmb = True
        elif not mmb and self.held_mmb:
            inputs.append(self._create_mouse_input(MOUSEEVENTF_MIDDLEUP))
            self.held_mmb = False

        if rmb and not self.held_rmb:
            inputs.append(self._create_mouse_input(MOUSEEVENTF_RIGHTDOWN))
            self.held_rmb = True
        elif not rmb and self.held_rmb:
            inputs.append(self._create_mouse_input(MOUSEEVENTF_RIGHTUP))
            self.held_rmb = False

        if inputs:
            self._send_inputs(inputs)

    def release_all_navigation(self, restore_anchor: bool = False):
        """Safely releases all held mouse buttons and modifiers."""
        if not self.is_navigating and not (self.held_mmb or self.held_rmb or self.held_ctrl or self.held_shift or self.held_alt):
            return

        self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=False, rmb=False)
        
        if restore_anchor and self.is_navigating:
            self.set_cursor_pos(self.anchor_x, self.anchor_y)

        self.is_navigating = False
        self.current_mode = None
        self.accum_x = 0.0
        self.accum_y = 0.0
        self.accum_zoom = 0.0

    def check_boundary_and_recenter(self, boundary_wrap: bool):
        """Prevents cursor from getting stuck on screen border during continuous drags."""
        if not boundary_wrap:
            return

        cur_x, cur_y = self.get_cursor_pos()
        b_left, b_top, b_right, b_bottom = self.get_screen_bounds()

        near_edge = (
            cur_x <= b_left + self.boundary_margin or
            cur_x >= b_right - self.boundary_margin or
            cur_y <= b_top + self.boundary_margin or
            cur_y >= b_bottom - self.boundary_margin
        )

        if near_edge:
            # Save current held state
            saved_ctrl = self.held_ctrl
            saved_shift = self.held_shift
            saved_alt = self.held_alt
            saved_mmb = self.held_mmb
            saved_rmb = self.held_rmb

            # Release buttons momentarily
            self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=False, rmb=False)
            
            # Teleport cursor back to anchor position
            self.set_cursor_pos(self.anchor_x, self.anchor_y)
            
            # Re-engage drag state seamlessly
            self._set_keys_and_buttons(
                ctrl=saved_ctrl,
                shift=saved_shift,
                alt=saved_alt,
                mmb=saved_mmb,
                rmb=saved_rmb
            )

    def start_navigation_if_needed(self):
        """Latches anchor position when navigation begins from rest."""
        if not self.is_navigating:
            self.anchor_x, self.anchor_y = self.get_cursor_pos()
            self.is_navigating = True
            self.accum_x = 0.0
            self.accum_y = 0.0

    def process_navigation(self,
                           orbit_delta: Tuple[float, float],
                           pan_delta: Tuple[float, float],
                           zoom_val: float,
                           roll_val: float,
                           preset: Dict[str, Any]):
        """Processes live 6-DoF deltas according to the active CAD preset."""
        boundary_wrap = preset.get('boundary_wrap', True)
        restore_cursor = preset.get('restore_cursor_on_release', True)
        cad_type = preset.get('cad_type', 'solidworks').lower()
        zoom_mode = preset.get('zoom_mode', 'wheel')

        has_orbit = (abs(orbit_delta[0]) > 0.001 or abs(orbit_delta[1]) > 0.001)
        has_pan = (abs(pan_delta[0]) > 0.001 or abs(pan_delta[1]) > 0.001)
        has_zoom = (abs(zoom_val) > 0.001)
        has_roll = (abs(roll_val) > 0.001)

        # Handle release
        if not (has_orbit or has_pan or has_zoom or has_roll):
            if self.is_navigating:
                self.release_all_navigation(restore_anchor=restore_cursor)
            return

        self.start_navigation_if_needed()

        # Priority resolution: Orbit vs Pan vs Roll
        # If user is using both sticks, dominant stick wins
        orbit_mag = abs(orbit_delta[0]) + abs(orbit_delta[1])
        pan_mag = abs(pan_delta[0]) + abs(pan_delta[1])

        # 1. ORBIT / ROTATE
        if has_orbit and orbit_mag >= pan_mag:
            if self.current_mode != 'orbit':
                # Transition to Orbit
                self.release_all_navigation(restore_anchor=False)
                self.start_navigation_if_needed()
                self.current_mode = 'orbit'
                
                if cad_type == 'solidworks':
                    # SolidWorks Orbit: Hold MMB
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=True, rmb=False)
                elif cad_type == 'catia':
                    # CATIA Orbit: Hold MMB + RMB
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=True, rmb=True)
                elif cad_type == 'fusion':
                    # Fusion 360 Orbit: Hold Shift + MMB
                    self._set_keys_and_buttons(ctrl=False, shift=True, alt=False, mmb=True, rmb=False)
                elif cad_type == 'blender':
                    # Blender Orbit: Hold MMB
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=True, rmb=False)
                else:
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=True, rmb=False)

            self._move_mouse_accumulated(orbit_delta[0], orbit_delta[1])
            self.check_boundary_and_recenter(boundary_wrap)

        # 2. PAN / TRANSLATE
        elif has_pan and pan_mag > orbit_mag:
            if self.current_mode != 'pan':
                # Transition to Pan
                self.release_all_navigation(restore_anchor=False)
                self.start_navigation_if_needed()
                self.current_mode = 'pan'
                
                if cad_type == 'solidworks':
                    # SolidWorks Pan: Hold Ctrl + MMB
                    self._set_keys_and_buttons(ctrl=True, shift=False, alt=False, mmb=True, rmb=False)
                elif cad_type == 'catia':
                    # CATIA Pan: Hold MMB
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=True, rmb=False)
                elif cad_type == 'fusion':
                    # Fusion 360 Pan: Hold MMB
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=False, mmb=True, rmb=False)
                elif cad_type == 'blender':
                    # Blender Pan: Hold Shift + MMB
                    self._set_keys_and_buttons(ctrl=False, shift=True, alt=False, mmb=True, rmb=False)
                else:
                    self._set_keys_and_buttons(ctrl=True, shift=False, alt=False, mmb=True, rmb=False)

            self._move_mouse_accumulated(pan_delta[0], pan_delta[1])
            self.check_boundary_and_recenter(boundary_wrap)

        # 3. ROLL
        elif has_roll:
            if self.current_mode != 'roll':
                self.release_all_navigation(restore_anchor=False)
                self.start_navigation_if_needed()
                self.current_mode = 'roll'
                if cad_type == 'solidworks':
                    # SolidWorks Roll: Alt + MMB
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=True, mmb=True, rmb=False)
                else:
                    self._set_keys_and_buttons(ctrl=False, shift=False, alt=True, mmb=True, rmb=False)

            self._move_mouse_accumulated(roll_val, 0)
            self.check_boundary_and_recenter(boundary_wrap)

        # 4. ZOOM (Can occur in tandem with wheel zoom)
        if has_zoom:
            if zoom_mode == 'wheel':
                # Mouse wheel zoom works seamlessly in Solidworks, CATIA, Fusion
                self.accum_zoom += zoom_val * 45.0  # Wheel scaling
                steps = int(self.accum_zoom)
                if steps != 0:
                    self.accum_zoom -= steps
                    # Windows wheel event: dwData = steps * WHEEL_DELTA
                    inp = self._create_mouse_input(MOUSEEVENTF_WHEEL, data=steps * WHEEL_DELTA)
                    self._send_inputs([inp])
            elif zoom_mode == 'drag_shift':
                # Drag zoom (SolidWorks Shift+MMB)
                if not self.held_mmb:
                    self._set_keys_and_buttons(ctrl=False, shift=True, alt=False, mmb=True, rmb=False)
                self._move_mouse_accumulated(0, -zoom_val * 20.0)
            elif zoom_mode == 'drag_catia':
                # Classic CATIA drag zoom: MMB hold + RMB click
                if self.current_mode != 'zoom_catia':
                    self.release_all_navigation(restore_anchor=False)
                    self.start_navigation_if_needed()
                    self.current_mode = 'zoom_catia'
                    # Hold MMB, tap RMB
                    self._set_keys_and_buttons(mmb=True, rmb=False)
                    time.sleep(0.005)
                    self._send_inputs([
                        self._create_mouse_input(MOUSEEVENTF_RIGHTDOWN),
                        self._create_mouse_input(MOUSEEVENTF_RIGHTUP)
                    ])
                self._move_mouse_accumulated(0, -zoom_val * 20.0)
                self.check_boundary_and_recenter(boundary_wrap)

    def _move_mouse_accumulated(self, dx: float, dy: float):
        """Accumulates fractional pixel delta and sends integer mouse move packets."""
        self.accum_x += dx
        self.accum_y += dy
        
        step_x = int(self.accum_x)
        step_y = int(self.accum_y)
        
        if step_x != 0 or step_y != 0:
            self.accum_x -= step_x
            self.accum_y -= step_y
            inp = self._create_mouse_input(MOUSEEVENTF_MOVE, dx=step_x, dy=step_y)
            self._send_inputs([inp])

    def trigger_action(self, action_id: str, preset: Dict[str, Any]):
        """Executes a discrete CAD shortcut action."""
        cad_type = preset.get('cad_type', 'solidworks').lower()
        
        # SolidWorks standard shortcuts
        if cad_type == 'solidworks':
            if action_id == 'fit_view':
                self.send_key_combination(['f'])
            elif action_id == 'isometric':
                self.send_key_combination(['ctrl', '7'])
            elif action_id == 'normal_to':
                self.send_key_combination(['ctrl', '8'])
            elif action_id == 'top_view':
                self.send_key_combination(['ctrl', '5'])
            elif action_id == 'bottom_view':
                self.send_key_combination(['ctrl', '6'])
            elif action_id == 'front_view':
                self.send_key_combination(['ctrl', '1'])
            elif action_id == 'back_view':
                self.send_key_combination(['ctrl', '2'])
            elif action_id == 'left_view':
                self.send_key_combination(['ctrl', '3'])
            elif action_id == 'right_view':
                self.send_key_combination(['ctrl', '4'])
            elif action_id == 'escape':
                self.send_key_combination(['escape'])
            elif action_id == 'undo':
                self.send_key_combination(['ctrl', 'z'])
            elif action_id == 'redo':
                self.send_key_combination(['ctrl', 'y'])

        # CATIA standard shortcuts
        elif cad_type == 'catia':
            if action_id == 'fit_view':
                # Fit All In shortcut / reframe
                self.send_key_combination(['ctrl', 'shift', '0'])
            elif action_id == 'isometric':
                self.send_key_combination(['ctrl', 'shift', '7'])
            elif action_id == 'top_view':
                self.send_key_combination(['ctrl', 'shift', '5'])
            elif action_id == 'bottom_view':
                self.send_key_combination(['ctrl', 'shift', '6'])
            elif action_id == 'front_view':
                self.send_key_combination(['ctrl', 'shift', '1'])
            elif action_id == 'back_view':
                self.send_key_combination(['ctrl', 'shift', '2'])
            elif action_id == 'left_view':
                self.send_key_combination(['ctrl', 'shift', '3'])
            elif action_id == 'right_view':
                self.send_key_combination(['ctrl', 'shift', '4'])
            elif action_id == 'escape':
                self.send_key_combination(['escape'])
            elif action_id == 'undo':
                self.send_key_combination(['ctrl', 'z'])
            elif action_id == 'redo':
                self.send_key_combination(['ctrl', 'y'])

        # Generic / Fusion / Blender shortcuts
        else:
            if action_id == 'fit_view':
                self.send_key_combination(['f'])
            elif action_id == 'isometric':
                self.send_key_combination(['ctrl', '7'])
            elif action_id == 'escape':
                self.send_key_combination(['escape'])
            elif action_id == 'undo':
                self.send_key_combination(['ctrl', 'z'])
            elif action_id == 'redo':
                self.send_key_combination(['ctrl', 'y'])
