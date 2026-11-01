"""
XboxConnexion - Controller Manager
High-speed background polling loop that processes analog sticks, curves, deadzones,
handles the preset switch button with haptic feedback, and feeds CAD emulation.
"""

import time
import math
import threading
from typing import Dict, Any, Optional, Callable

from .xinput import XInputDevice
from .cad_emulator import CADEmulator
from .preset_manager import PresetManager
from .toast_hud import ToastHUD

class ControllerManager:
    """Coordinates controller input, presets, haptics, and CAD viewport manipulation."""

    def __init__(self,
                 preset_manager: PresetManager,
                 cad_emulator: CADEmulator,
                 toast_hud: Optional[ToastHUD] = None):
        self.pm = preset_manager
        self.emulator = cad_emulator
        self.toast = toast_hud
        self.device = XInputDevice(controller_id=0)

        self.is_running = False
        self.is_paused = False
        self._thread = None
        
        # State tracking for edge detection
        self.prev_buttons: Dict[str, bool] = {}
        self.last_connected = False
        
        # Callback hooks for GUI updates
        self.on_state_update: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_connection_change: Optional[Callable[[bool], None]] = None
        self.on_preset_change: Optional[Callable[[Dict[str, Any]], None]] = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        self.emulator.release_all_navigation(restore_anchor=False)

    def toggle_pause(self) -> bool:
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.emulator.release_all_navigation(restore_anchor=False)
            if self.toast:
                self.toast.show("Navigation Paused", "Controller input suspended", accent_color="#ff9800")
        else:
            if self.toast:
                self.toast.show("Navigation Resumed", "SpaceMouse mode active", accent_color="#00d26a")
        return self.is_paused

    def cycle_preset(self):
        """Cycles to the next preset, fires haptic pulse and OSD toast notification."""
        new_preset = self.pm.cycle_next_preset()
        name = new_preset.get('name', 'Preset')
        cad_type = new_preset.get('cad_type', 'solidworks').lower()
        desc = new_preset.get('description', '')

        # Haptic Rumble confirmation
        if self.pm.settings.get('haptic_rumble_enabled', True):
            intensity = self.pm.settings.get('haptic_rumble_intensity', 0.6)
            pulses = 1 if cad_type == 'solidworks' else (2 if cad_type == 'catia' else 3)
            self.device.pulse_rumble(pulses=pulses, intensity=intensity, duration_s=0.1)

        # OSD Toast Notification
        if self.toast and self.pm.settings.get('osd_toast_enabled', True):
            accent = "#00d26a" if cad_type == 'solidworks' else ("#00bcd4" if cad_type == 'catia' else "#ff9800")
            subtitle = f"Active: {desc} (Orbit: RS | Pan: LS | Zoom: Triggers)"
            self.toast.show(f"Preset: {name}", subtitle, accent_color=accent)

        # Notify UI
        if self.on_preset_change:
            self.on_preset_change(new_preset)

    def _apply_deadzone_and_curve(self,
                                   raw_x: float,
                                   raw_y: float,
                                   deadzone: float,
                                   curve_type: str,
                                   exponent: float,
                                   sensitivity: float,
                                   invert_x: bool,
                                   invert_y: bool) -> tuple[float, float]:
        """Calculates deadzone-normalized, curved analog stick coordinates."""
        mag = math.sqrt(raw_x * raw_x + raw_y * raw_y)
        if mag <= deadzone:
            return (0.0, 0.0)

        # Normalize to 0.0 .. 1.0 above deadzone
        norm_mag = min(1.0, (mag - deadzone) / (1.0 - deadzone))
        norm_x = raw_x / mag
        norm_y = raw_y / mag

        # Response curve
        if curve_type == 'exponential':
            curved_mag = math.pow(norm_mag, exponent)
        elif curve_type == 'smoothstep':
            curved_mag = norm_mag * norm_mag * (3.0 - 2.0 * norm_mag)
        else: # linear
            curved_mag = norm_mag

        final_speed = curved_mag * sensitivity * 16.0  # Base pixel multiplier
        dx = norm_x * final_speed * (-1.0 if invert_x else 1.0)
        dy = norm_y * final_speed * (-1.0 if invert_y else 1.0)
        return (dx, dy)

    def _loop(self):
        """High-frequency polling loop (~100 Hz)."""
        dt = 0.01
        while self.is_running:
            start_time = time.perf_counter()
            data = self.device.poll()

            # Handle connection state changes
            is_connected = (data is not None)
            if is_connected != self.last_connected:
                self.last_connected = is_connected
                if self.on_connection_change:
                    self.on_connection_change(is_connected)
                if not is_connected:
                    self.emulator.release_all_navigation(restore_anchor=False)

            if not is_connected or self.is_paused:
                time.sleep(0.015)
                continue

            preset = self.pm.get_active_preset()
            buttons = data['buttons']
            
            # --- Detect Button Press Edges ---
            cycle_btn_name = self.pm.settings.get('cycle_button', 'back')
            for btn_name, is_down in buttons.items():
                was_down = self.prev_buttons.get(btn_name, False)
                if is_down and not was_down:
                    # Button was just pressed!
                    # 1. Preset Switch Button
                    if btn_name == cycle_btn_name:
                        self.cycle_preset()
                        continue

                    # 2. Toggle Pause
                    if btn_name == 'start':
                        # Default start button action
                        mapping = preset.get('button_mappings', {}).get(btn_name)
                        if mapping == 'toggle_pause':
                            self.toggle_pause()
                            continue

                    # 3. Mapped CAD action
                    mapping = preset.get('button_mappings', {}).get(btn_name)
                    if mapping and mapping not in ['cycle_preset', 'toggle_pause', 'precision_mode']:
                        self.emulator.trigger_action(mapping, preset)

            self.prev_buttons = buttons.copy()

            # --- Check Precision Mode (Stick modifier) ---
            # Holding left stick click reduces speed by 50%
            is_precision = buttons.get('ls_click', False) and (
                preset.get('button_mappings', {}).get('ls_click') == 'precision_mode'
            )
            precision_mult = 0.45 if is_precision else 1.0

            # --- Process Stick Inputs ---
            dz_stick = preset.get('deadzone_stick', 0.12)
            dz_trigger = preset.get('deadzone_trigger', 0.08)
            curve = preset.get('curve', 'exponential')
            exponent = preset.get('curve_exponent', 2.1)

            # Left Stick (Default: Pan)
            ls_action = preset.get('left_stick', 'pan')
            sens_pan = preset.get('sensitivity_pan', 1.0) * precision_mult
            pan_dx, pan_dy = self._apply_deadzone_and_curve(
                data['lx'], data['ly'],
                dz_stick, curve, exponent, sens_pan,
                preset.get('invert_pan_x', False),
                preset.get('invert_pan_y', True)
            )

            # Right Stick (Default: Orbit)
            rs_action = preset.get('right_stick', 'orbit')
            sens_orbit = preset.get('sensitivity_orbit', 1.25) * precision_mult
            orbit_dx, orbit_dy = self._apply_deadzone_and_curve(
                data['rx'], data['ry'],
                dz_stick, curve, exponent, sens_orbit,
                preset.get('invert_orbit_x', False),
                preset.get('invert_orbit_y', False)
            )

            # Triggers (Default: Zoom)
            # RT zooms in, LT zooms out
            lt = data['lt']
            rt = data['rt']
            zoom_val = 0.0
            if rt > dz_trigger:
                zoom_val += (rt - dz_trigger) / (1.0 - dz_trigger)
            if lt > dz_trigger:
                zoom_val -= (lt - dz_trigger) / (1.0 - dz_trigger)

            sens_zoom = preset.get('sensitivity_zoom', 1.35) * precision_mult
            if preset.get('invert_zoom', False):
                zoom_val = -zoom_val
            zoom_val *= sens_zoom

            # Bumpers (Default: Roll)
            roll_val = 0.0
            sens_roll = preset.get('sensitivity_roll', 0.8) * precision_mult
            if buttons.get('lb', False):
                roll_val -= sens_roll * 10.0
            if buttons.get('rb', False):
                roll_val += sens_roll * 10.0

            # Dispatch 6-DoF navigation to CAD emulator
            self.emulator.process_navigation(
                orbit_delta=(orbit_dx, orbit_dy),
                pan_delta=(pan_dx, pan_dy),
                zoom_val=zoom_val,
                roll_val=roll_val,
                preset=preset
            )

            # Notify GUI live monitor
            if self.on_state_update:
                self.on_state_update({
                    'connected': True,
                    'lx': data['lx'],
                    'ly': data['ly'],
                    'rx': data['rx'],
                    'ry': data['ry'],
                    'lt': data['lt'],
                    'rt': data['rt'],
                    'buttons': buttons,
                    'is_precision': is_precision,
                })

            # Maintain ~100Hz loop
            elapsed = time.perf_counter() - start_time
            sleep_time = max(0.001, dt - elapsed)
            time.sleep(sleep_time)
