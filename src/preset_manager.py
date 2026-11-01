"""
XboxConnexion - Preset Manager
Loads, saves, and manages profiles for SolidWorks, CATIA, Fusion 360, and custom CAD apps.
"""

import json
import os
import copy
from typing import Dict, Any, List, Optional

CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
PRESETS_FILE = os.path.join(CONFIG_DIR, 'presets.json')
SETTINGS_FILE = os.path.join(CONFIG_DIR, 'settings.json')

DEFAULT_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "solidworks",
        "name": "SolidWorks",
        "cad_type": "solidworks",
        "description": "Dassault Systèmes SOLIDWORKS 3D CAD",
        "app_process": "SLDWORKS.exe",
        "left_stick": "pan",
        "right_stick": "orbit",
        "triggers": "zoom",
        "bumpers": "roll",
        "sensitivity_orbit": 1.25,
        "sensitivity_pan": 1.0,
        "sensitivity_zoom": 1.35,
        "sensitivity_roll": 0.8,
        "deadzone_stick": 0.12,
        "deadzone_trigger": 0.08,
        "curve": "exponential",
        "curve_exponent": 2.1,
        "invert_orbit_x": False,
        "invert_orbit_y": False,
        "invert_pan_x": False,
        "invert_pan_y": True,
        "invert_zoom": False,
        "boundary_wrap": True,
        "restore_cursor_on_release": True,
        "zoom_mode": "wheel",
        "button_mappings": {
            "a": "fit_view",
            "b": "escape",
            "x": "normal_to",
            "y": "isometric",
            "dpad_up": "top_view",
            "dpad_down": "bottom_view",
            "dpad_left": "left_view",
            "dpad_right": "right_view",
            "ls_click": "precision_mode",
            "rs_click": "fit_view",
            "start": "toggle_pause",
            "back": "cycle_preset"
        }
    },
    {
        "id": "catia",
        "name": "CATIA V5 / 3DX",
        "cad_type": "catia",
        "description": "Dassault Systèmes CATIA V5 & 3DEXPERIENCE",
        "app_process": "CNEXT.exe",
        "left_stick": "pan",
        "right_stick": "orbit",
        "triggers": "zoom",
        "bumpers": "roll",
        "sensitivity_orbit": 1.25,
        "sensitivity_pan": 1.0,
        "sensitivity_zoom": 1.35,
        "sensitivity_roll": 0.8,
        "deadzone_stick": 0.12,
        "deadzone_trigger": 0.08,
        "curve": "exponential",
        "curve_exponent": 2.1,
        "invert_orbit_x": False,
        "invert_orbit_y": False,
        "invert_pan_x": False,
        "invert_pan_y": True,
        "invert_zoom": False,
        "boundary_wrap": True,
        "restore_cursor_on_release": True,
        "zoom_mode": "wheel",
        "button_mappings": {
            "a": "fit_view",
            "b": "escape",
            "x": "fit_view",
            "y": "isometric",
            "dpad_up": "top_view",
            "dpad_down": "bottom_view",
            "dpad_left": "left_view",
            "dpad_right": "right_view",
            "ls_click": "precision_mode",
            "rs_click": "fit_view",
            "start": "toggle_pause",
            "back": "cycle_preset"
        }
    },
    {
        "id": "fusion",
        "name": "Autodesk Fusion & Inventor",
        "cad_type": "fusion",
        "description": "Autodesk Fusion 360 & Inventor CAD",
        "app_process": "Fusion360.exe",
        "left_stick": "pan",
        "right_stick": "orbit",
        "triggers": "zoom",
        "bumpers": "roll",
        "sensitivity_orbit": 1.2,
        "sensitivity_pan": 1.0,
        "sensitivity_zoom": 1.3,
        "sensitivity_roll": 0.8,
        "deadzone_stick": 0.12,
        "deadzone_trigger": 0.08,
        "curve": "exponential",
        "curve_exponent": 2.1,
        "invert_orbit_x": False,
        "invert_orbit_y": False,
        "invert_pan_x": False,
        "invert_pan_y": True,
        "invert_zoom": False,
        "boundary_wrap": True,
        "restore_cursor_on_release": True,
        "zoom_mode": "wheel",
        "button_mappings": {
            "a": "fit_view",
            "b": "escape",
            "x": "fit_view",
            "y": "isometric",
            "dpad_up": "top_view",
            "dpad_down": "bottom_view",
            "dpad_left": "left_view",
            "dpad_right": "right_view",
            "ls_click": "precision_mode",
            "rs_click": "fit_view",
            "start": "toggle_pause",
            "back": "cycle_preset"
        }
    },
    {
        "id": "blender",
        "name": "Blender & FreeCAD",
        "cad_type": "blender",
        "description": "Blender 3D & FreeCAD Open Source Modeling",
        "app_process": "blender.exe",
        "left_stick": "pan",
        "right_stick": "orbit",
        "triggers": "zoom",
        "bumpers": "roll",
        "sensitivity_orbit": 1.2,
        "sensitivity_pan": 1.0,
        "sensitivity_zoom": 1.3,
        "sensitivity_roll": 0.8,
        "deadzone_stick": 0.12,
        "deadzone_trigger": 0.08,
        "curve": "exponential",
        "curve_exponent": 2.1,
        "invert_orbit_x": False,
        "invert_orbit_y": False,
        "invert_pan_x": False,
        "invert_pan_y": True,
        "invert_zoom": False,
        "boundary_wrap": True,
        "restore_cursor_on_release": True,
        "zoom_mode": "wheel",
        "button_mappings": {
            "a": "fit_view",
            "b": "escape",
            "x": "fit_view",
            "y": "isometric",
            "dpad_up": "top_view",
            "dpad_down": "bottom_view",
            "dpad_left": "left_view",
            "dpad_right": "right_view",
            "ls_click": "precision_mode",
            "rs_click": "fit_view",
            "start": "toggle_pause",
            "back": "cycle_preset"
        }
    }
]

DEFAULT_SETTINGS: Dict[str, Any] = {
    "active_preset_id": "solidworks",
    "cycle_button": "back",
    "auto_switch_cad_window": True,
    "haptic_rumble_enabled": True,
    "haptic_rumble_intensity": 0.6,
    "osd_toast_enabled": True,
    "minimize_to_tray_on_close": True,
    "start_minimized": False
}

class PresetManager:
    """Manages loading, saving, cycling, and configuring presets."""

    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.presets: List[Dict[str, Any]] = []
        self.settings: Dict[str, Any] = copy.deepcopy(DEFAULT_SETTINGS)
        self.active_preset_index: int = 0
        self.load()

    def load(self):
        # Load Presets
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
                    self.presets = json.load(f)
            except Exception as e:
                print(f"[PresetManager] Error loading presets: {e}. Using defaults.")
                self.presets = copy.deepcopy(DEFAULT_PRESETS)
        else:
            self.presets = copy.deepcopy(DEFAULT_PRESETS)
            self.save_presets()

        # Load Settings
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except Exception as e:
                print(f"[PresetManager] Error loading settings: {e}. Using defaults.")
        else:
            self.save_settings()

        # Set active preset index
        active_id = self.settings.get("active_preset_id", "solidworks")
        self.set_active_preset_by_id(active_id)

    def save_presets(self):
        try:
            with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=4)
        except Exception as e:
            print(f"[PresetManager] Error saving presets: {e}")

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[PresetManager] Error saving settings: {e}")

    def get_active_preset(self) -> Dict[str, Any]:
        if 0 <= self.active_preset_index < len(self.presets):
            return self.presets[self.active_preset_index]
        return self.presets[0] if self.presets else DEFAULT_PRESETS[0]

    def set_active_preset_by_id(self, preset_id: str) -> bool:
        for idx, p in enumerate(self.presets):
            if p.get("id") == preset_id:
                self.active_preset_index = idx
                self.settings["active_preset_id"] = preset_id
                self.save_settings()
                return True
        return False

    def cycle_next_preset(self) -> Dict[str, Any]:
        """Cycles to the next preset in the list and saves settings."""
        if not self.presets:
            return DEFAULT_PRESETS[0]
        self.active_preset_index = (self.active_preset_index + 1) % len(self.presets)
        new_preset = self.presets[self.active_preset_index]
        self.settings["active_preset_id"] = new_preset.get("id", "")
        self.save_settings()
        return new_preset

    def update_preset(self, preset_id: str, updated_data: Dict[str, Any]):
        for idx, p in enumerate(self.presets):
            if p.get("id") == preset_id:
                self.presets[idx].update(updated_data)
                self.save_presets()
                break

    def duplicate_preset(self, preset_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        for p in self.presets:
            if p.get("id") == preset_id:
                new_preset = copy.deepcopy(p)
                import uuid
                new_preset["id"] = f"custom_{uuid.uuid4().hex[:6]}"
                new_preset["name"] = new_name
                self.presets.append(new_preset)
                self.save_presets()
                return new_preset
        return None

    def reset_to_defaults(self):
        self.presets = copy.deepcopy(DEFAULT_PRESETS)
        self.save_presets()
        self.set_active_preset_by_id("solidworks")
