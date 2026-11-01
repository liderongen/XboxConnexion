"""
XboxConnexion - Main Entry Point
Launches the XboxConnexion 3D SpaceMouse CAD Controller and GUI.
"""

import sys
import os

# Ensure src parent directory is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.preset_manager import PresetManager
from src.cad_emulator import CADEmulator
from src.toast_hud import ToastHUD
from src.controller_manager import ControllerManager
from src.app_detector import AppDetector
from src.ui.main_window import MainWindow
from src.ui.tray_icon import SystemTrayManager

def main():
    print("[XboxConnexion] Initializing 3D SpaceMouse CAD Controller...")

    # 1. Preset Manager
    pm = PresetManager()

    # 2. CAD Emulation Engine
    cad_emulator = CADEmulator()

    # 3. OSD Toast HUD
    toast_hud = ToastHUD() if pm.settings.get("osd_toast_enabled", True) else None

    # 4. Controller Manager
    cm = ControllerManager(preset_manager=pm, cad_emulator=cad_emulator, toast_hud=toast_hud)

    # 5. Tray Manager (Forward declaration for circular references)
    app_window = None

    def on_show_window():
        if app_window:
            app_window.after(0, lambda: (app_window.deiconify(), app_window.lift(), app_window.focus_force()))

    def on_select_preset(preset_id: str):
        if pm.set_active_preset_by_id(preset_id):
            cm.cycle_preset()

    def on_toggle_pause():
        return cm.toggle_pause()

    def on_exit():
        cm.stop()
        if app_window:
            app_window.after(0, app_window.destroy)
        sys.exit(0)

    tray = SystemTrayManager(
        on_show_window=on_show_window,
        on_select_preset=on_select_preset,
        on_toggle_pause=on_toggle_pause,
        on_exit=on_exit
    )

    # 6. GUI Main Window
    app_window = MainWindow(controller_manager=cm, preset_manager=pm, tray_manager=tray)

    # 7. CAD Application Auto-Detector
    def on_cad_window_focused(process_name: str):
        if not pm.settings.get("auto_switch_cad_window", True):
            return
        
        proc_lower = process_name.lower()
        target_preset_id = None

        if "sldworks" in proc_lower:
            target_preset_id = "solidworks"
        elif "cnext" in proc_lower or "catia" in proc_lower:
            target_preset_id = "catia"
        elif "fusion" in proc_lower or "inventor" in proc_lower:
            target_preset_id = "fusion"
        elif "blender" in proc_lower:
            target_preset_id = "blender"

        if target_preset_id and target_preset_id != pm.get_active_preset().get("id"):
            print(f"[AppDetector] CAD application active: {process_name} -> Switching preset to '{target_preset_id}'")
            if pm.set_active_preset_by_id(target_preset_id):
                active_p = pm.get_active_preset()
                if toast_hud and pm.settings.get("osd_toast_enabled", True):
                    toast_hud.show(f"Auto-Preset: {active_p.get('name')}", f"Detected {process_name}", "#00bcd4")
                if cm.on_preset_change:
                    cm.on_preset_change(active_p)

    detector = AppDetector(on_cad_focus_callback=on_cad_window_focused)

    # Start background subsystems
    cm.start()
    detector.start()
    tray.start(pm.presets, pm.get_active_preset().get("id", "solidworks"))

    print("[XboxConnexion] System ready! Starting GUI main loop...")
    try:
        app_window.mainloop()
    finally:
        cm.stop()
        detector.stop()
        tray.stop()

if __name__ == "__main__":
    main()
