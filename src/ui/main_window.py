"""
XboxConnexion - Main Window Interface
Modern CustomTkinter GUI featuring real-time controller vector visualization,
one-click preset switching, fine-tuning sliders, and CAD configuration.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, Optional

from .controller_canvas import ControllerCanvas
from .preset_editor import PresetEditor
from .tray_icon import SystemTrayManager
from ..preset_manager import PresetManager
from ..controller_manager import ControllerManager

class MainWindow(ctk.CTk):
    """Main application window for XboxConnexion."""

    def __init__(self,
                 controller_manager: ControllerManager,
                 preset_manager: PresetManager,
                 tray_manager: Optional[SystemTrayManager] = None):
        super().__init__()

        self.cm = controller_manager
        self.pm = preset_manager
        self.tray = tray_manager

        # Window Configuration
        self.title("XboxConnexion - 3D SpaceMouse CAD Controller")
        self.geometry("980x740")
        self.minsize(880, 680)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#12141a")

        # Handle window close (minimize to tray or quit)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Wire controller callbacks
        self.cm.on_state_update = self._on_controller_state
        self.cm.on_connection_change = self._on_connection_change
        self.cm.on_preset_change = self._on_preset_switched

        # Build UI layout
        self._build_top_bar()
        self._build_preset_bar()
        self._build_tabs()

        # Initial data sync
        self._sync_active_preset()
        self._update_connection_display(self.cm.device.is_connected)

    def _build_top_bar(self):
        """Builds branding, connection pill, battery, and master toggle."""
        top_bar = ctk.CTkFrame(self, fg_color="#1a1d26", corner_radius=0, height=65)
        top_bar.pack(fill="x", side="top")

        # Left branding
        f_brand = ctk.CTkFrame(top_bar, fg_color="transparent")
        f_brand.pack(side="left", padx=20, pady=10)

        lbl_logo = ctk.CTkLabel(
            f_brand,
            text="🎮 XboxConnexion",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        lbl_logo.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            f_brand,
            text="6-DoF SpaceMouse Emulator for SolidWorks & CATIA",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#00d26a"
        )
        lbl_sub.pack(anchor="w")

        # Right status controls
        f_status = ctk.CTkFrame(top_bar, fg_color="transparent")
        f_status.pack(side="right", padx=20, pady=10)

        # Controller connection pill
        self.pill_conn = ctk.CTkLabel(
            f_status,
            text="● Disconnected",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#382024",
            text_color="#e06c75",
            corner_radius=12,
            padx=12,
            pady=4
        )
        self.pill_conn.pack(side="left", padx=8)

        # Battery indicator
        self.lbl_battery = ctk.CTkLabel(
            f_status,
            text="🔋 --",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8a90a0"
        )
        self.lbl_battery.pack(side="left", padx=8)

        # Master navigation active switch
        self.sw_master = ctk.CTkSwitch(
            f_status,
            text="Navigation Active",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._on_toggle_master_switch
        )
        self.sw_master.select()
        self.sw_master.pack(side="left", padx=12)

    def _build_preset_bar(self):
        """Builds prominent preset switcher bar."""
        p_bar = ctk.CTkFrame(self, fg_color="#181a22", corner_radius=10)
        p_bar.pack(fill="x", padx=15, pady=(12, 6))

        ctk.CTkLabel(
            p_bar,
            text="ACTIVE CAD PRESET:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#8a90a0"
        ).pack(side="left", padx=(15, 10), pady=12)

        # Preset segmented buttons
        preset_names = [p.get("name", "Preset") for p in self.pm.presets]
        self.seg_presets = ctk.CTkSegmentedButton(
            p_bar,
            values=preset_names,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._on_preset_segment_selected,
            selected_color="#00bcd4",
            selected_hover_color="#00acc1"
        )
        self.seg_presets.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # Controller Cycle Button Indicator
        cycle_btn_name = self.pm.settings.get("cycle_button", "back").upper()
        self.btn_cycle = ctk.CTkButton(
            p_bar,
            text=f"⟳ Next Preset (🎮 {cycle_btn_name})",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#272b38",
            hover_color="#333849",
            text_color="#00d26a",
            width=190,
            command=self._on_cycle_button_clicked
        )
        self.btn_cycle.pack(side="right", padx=15, pady=10)

    def _build_tabs(self):
        """Builds main tabview."""
        self.tabs = ctk.CTkTabview(self, fg_color="#181a22", corner_radius=12)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=(6, 15))

        tab_monitor = self.tabs.add("🎮 Controller Visualizer & Live Monitor")
        tab_preset = self.tabs.add("⚙️ Preset Editor & Tuning")
        tab_settings = self.tabs.add("🛠️ App Settings & Automation")

        self._build_monitor_tab(tab_monitor)
        self._build_preset_tab(tab_preset)
        self._build_settings_tab(tab_settings)

    def _build_monitor_tab(self, parent):
        """Builds live visualizer and quick controls."""
        parent.columnconfigure(0, weight=6)
        parent.columnconfigure(1, weight=5)
        parent.rowconfigure(0, weight=1)

        # Left: Controller vector canvas card
        left_card = ctk.CTkFrame(parent, fg_color="#14161c", corner_radius=10)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        ctk.CTkLabel(
            left_card,
            text="Live Xbox Gamepad Input Feed",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#00d26a"
        ).pack(anchor="w", padx=15, pady=(10, 4))

        self.canvas = ControllerCanvas(left_card, width=500, height=340)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=5)

        # Quick Live stick metrics text
        self.lbl_stick_metrics = ctk.CTkLabel(
            left_card,
            text="Left Stick (Pan): X: +0.00  Y: +0.00   |   Right Stick (Orbit): X: +0.00  Y: +0.00",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#8a90a0"
        )
        self.lbl_stick_metrics.pack(anchor="center", pady=(0, 10))

        # Right: Quick tuning & Active Preset summary
        right_card = ctk.CTkFrame(parent, fg_color="#14161c", corner_radius=10)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        ctk.CTkLabel(
            right_card,
            text="⚡ Quick Sensitivity Adjustment",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#00bcd4"
        ).pack(anchor="w", padx=15, pady=(12, 6))

        # Quick Orbit Slider
        f_q_orbit = ctk.CTkFrame(right_card, fg_color="transparent")
        f_q_orbit.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(f_q_orbit, text="Orbit Speed:", width=110, anchor="w").pack(side="left")
        self.q_slider_orbit = ctk.CTkSlider(f_q_orbit, from_=0.2, to=3.0, number_of_steps=28, command=self._on_q_orbit)
        self.q_slider_orbit.pack(side="left", fill="x", expand=True, padx=5)
        self.lbl_q_orbit = ctk.CTkLabel(f_q_orbit, text="1.25x", width=40)
        self.lbl_q_orbit.pack(side="right")

        # Quick Pan Slider
        f_q_pan = ctk.CTkFrame(right_card, fg_color="transparent")
        f_q_pan.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(f_q_pan, text="Pan Speed:", width=110, anchor="w").pack(side="left")
        self.q_slider_pan = ctk.CTkSlider(f_q_pan, from_=0.2, to=3.0, number_of_steps=28, command=self._on_q_pan)
        self.q_slider_pan.pack(side="left", fill="x", expand=True, padx=5)
        self.lbl_q_pan = ctk.CTkLabel(f_q_pan, text="1.00x", width=40)
        self.lbl_q_pan.pack(side="right")

        # Quick Zoom Slider
        f_q_zoom = ctk.CTkFrame(right_card, fg_color="transparent")
        f_q_zoom.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(f_q_zoom, text="Zoom Speed:", width=110, anchor="w").pack(side="left")
        self.q_slider_zoom = ctk.CTkSlider(f_q_zoom, from_=0.2, to=3.0, number_of_steps=28, command=self._on_q_zoom)
        self.q_slider_zoom.pack(side="left", fill="x", expand=True, padx=5)
        self.lbl_q_zoom = ctk.CTkLabel(f_q_zoom, text="1.35x", width=40)
        self.lbl_q_zoom.pack(side="right")

        # CAD Controls cheat sheet card
        self.f_cheat = ctk.CTkFrame(right_card, fg_color="#1c1f28", corner_radius=8)
        self.f_cheat.pack(fill="both", expand=True, padx=15, pady=12)

        self.lbl_cheat_title = ctk.CTkLabel(
            self.f_cheat,
            text="🎮 Navigation Scheme: SolidWorks",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#00d26a"
        )
        self.lbl_cheat_title.pack(anchor="w", padx=12, pady=(10, 6))

        self.lbl_cheat_body = ctk.CTkLabel(
            self.f_cheat,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#c5cbd6",
            justify="left"
        )
        self.lbl_cheat_body.pack(anchor="w", padx=12, pady=(0, 10))

    def _build_preset_tab(self, parent):
        """Builds preset editor tab."""
        self.preset_editor = PresetEditor(parent, on_save_callback=self._on_preset_saved)
        self.preset_editor.pack(fill="both", expand=True, padx=5, pady=5)

    def _build_settings_tab(self, parent):
        """Builds app settings & automation tab."""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Preset Switch Button Selection Card
        btn_card = ctk.CTkFrame(scroll, fg_color="#21242d", corner_radius=10)
        btn_card.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            btn_card,
            text="🎮 Preset Switch Button on Xbox Controller",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#00bcd4"
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            btn_card,
            text="Choose which physical controller button cycles through SolidWorks, CATIA, etc.:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8a90a0"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        f_sw_btn = ctk.CTkFrame(btn_card, fg_color="transparent")
        f_sw_btn.pack(fill="x", padx=15, pady=(0, 15))

        self.opt_cycle_btn = ctk.CTkOptionMenu(
            f_sw_btn,
            values=[
                "Back / View (Recommended)",
                "Xbox Guide Button",
                "Start / Menu Button",
                "Left Stick Click (LS)",
                "Right Stick Click (RS)",
                "Left Bumper (LB)",
                "Right Bumper (RB)"
            ],
            command=self._on_change_cycle_button
        )
        self.opt_cycle_btn.pack(side="left")

        # Set initial value
        cur_btn = self.pm.settings.get("cycle_button", "back")
        btn_to_opt = {
            "back": "Back / View (Recommended)",
            "guide": "Xbox Guide Button",
            "start": "Start / Menu Button",
            "ls_click": "Left Stick Click (LS)",
            "rs_click": "Right Stick Click (RS)",
            "lb": "Left Bumper (LB)",
            "rb": "Right Bumper (RB)"
        }
        self.opt_cycle_btn.set(btn_to_opt.get(cur_btn, "Back / View (Recommended)"))

        # 2. Haptics & Feedback Card
        haptics_card = ctk.CTkFrame(scroll, fg_color="#21242d", corner_radius=10)
        haptics_card.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            haptics_card,
            text="📳 Haptic Rumble & OSD Feedback",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#00d26a"
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # Rumble switch
        self.sw_rumble = ctk.CTkSwitch(
            haptics_card,
            text="Vibrate controller on preset switch (1 pulse: SolidWorks, 2 pulses: CATIA)",
            command=self._on_save_app_settings
        )
        if self.pm.settings.get("haptic_rumble_enabled", True):
            self.sw_rumble.select()
        self.sw_rumble.pack(anchor="w", padx=15, pady=6)

        # OSD Toast HUD switch
        self.sw_osd = ctk.CTkSwitch(
            haptics_card,
            text="Show floating On-Screen Display (OSD) notification when switching presets",
            command=self._on_save_app_settings
        )
        if self.pm.settings.get("osd_toast_enabled", True):
            self.sw_osd.select()
        self.sw_osd.pack(anchor="w", padx=15, pady=6)

        # Rumble intensity slider
        f_rint = ctk.CTkFrame(haptics_card, fg_color="transparent")
        f_rint.pack(fill="x", padx=15, pady=(8, 15))
        ctk.CTkLabel(f_rint, text="Rumble Motor Intensity:", width=160, anchor="w").pack(side="left")
        self.slider_rint = ctk.CTkSlider(f_rint, from_=0.1, to=1.0, number_of_steps=18, command=self._on_rint_change)
        self.slider_rint.set(self.pm.settings.get("haptic_rumble_intensity", 0.6))
        self.slider_rint.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_rint_val = ctk.CTkLabel(f_rint, text=f"{int(self.slider_rint.get()*100)}%", width=45)
        self.lbl_rint_val.pack(side="right")

        # 3. Automation & System Card
        auto_card = ctk.CTkFrame(scroll, fg_color="#21242d", corner_radius=10)
        auto_card.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            auto_card,
            text="🤖 Automation & Background Running",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ff9800"
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # Auto switch CAD window
        self.sw_auto_cad = ctk.CTkSwitch(
            auto_card,
            text="Auto-switch preset when focusing SolidWorks (SLDWORKS.exe) or CATIA (CNEXT.exe)",
            command=self._on_save_app_settings
        )
        if self.pm.settings.get("auto_switch_cad_window", True):
            self.sw_auto_cad.select()
        self.sw_auto_cad.pack(anchor="w", padx=15, pady=6)

        # Minimize to tray on close
        self.sw_tray = ctk.CTkSwitch(
            auto_card,
            text="Minimize to system tray when closing window (keeps running in background)",
            command=self._on_save_app_settings
        )
        if self.pm.settings.get("minimize_to_tray_on_close", True):
            self.sw_tray.select()
        self.sw_tray.pack(anchor="w", padx=15, pady=(6, 15))

        # 4. Factory Reset Card
        rst_card = ctk.CTkFrame(scroll, fg_color="#21242d", corner_radius=10)
        rst_card.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            rst_card,
            text="⚠️ Factory Defaults",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#e06c75"
        ).pack(anchor="w", padx=15, pady=(12, 6))

        btn_rst = ctk.CTkButton(
            rst_card,
            text="Reset All Presets & Settings to Factory Defaults",
            fg_color="#382024",
            hover_color="#4d2c32",
            text_color="#e06c75",
            command=self._on_factory_reset
        )
        btn_rst.pack(anchor="w", padx=15, pady=(0, 15))

    # --- UI Sync & Handlers ---

    def _sync_active_preset(self):
        """Updates UI displays to match active preset."""
        preset = self.pm.get_active_preset()
        name = preset.get("name", "Preset")
        cad_type = preset.get("cad_type", "solidworks").lower()

        # Update Segmented Button
        self.seg_presets.set(name)

        # Update Quick Tuning Sliders
        sens_orbit = preset.get("sensitivity_orbit", 1.25)
        self.q_slider_orbit.set(sens_orbit)
        self.lbl_q_orbit.configure(text=f"{sens_orbit:.2f}x")

        sens_pan = preset.get("sensitivity_pan", 1.0)
        self.q_slider_pan.set(sens_pan)
        self.lbl_q_pan.configure(text=f"{sens_pan:.2f}x")

        sens_zoom = preset.get("sensitivity_zoom", 1.35)
        self.q_slider_zoom.set(sens_zoom)
        self.lbl_q_zoom.configure(text=f"{sens_zoom:.2f}x")

        # Update Preset Editor Frame
        self.preset_editor.load_preset(preset)

        # Update Cheat Sheet
        self.lbl_cheat_title.configure(text=f"🎮 Navigation Scheme: {name}")
        if cad_type == 'solidworks':
            cheat = (
                "• Orbit / Rotate: Right Analog Stick (MMB Drag)\n"
                "• Pan / Translate: Left Analog Stick (Ctrl + MMB Drag)\n"
                "• Zoom: Triggers RT (In) / LT (Out) (Mouse Wheel)\n"
                "• Roll: Bumpers RB (CW) / LB (CCW) (Alt + MMB)\n"
                "• Y Button: Isometric View (Ctrl+7)   |   X: Normal To (Ctrl+8)\n"
                "• A Button: Zoom to Fit (F)            |   B: Escape\n"
                "• D-Pad: Top (Up) • Bottom (Down) • Left (Left) • Right (Right)\n"
                "• Left Stick Click (Hold): Precision Mode (50% speed for sketching)"
            )
        elif cad_type == 'catia':
            cheat = (
                "• Pan / Translate: Left Analog Stick (MMB Drag)\n"
                "• Orbit / Rotate: Right Analog Stick (MMB + RMB Drag)\n"
                "• Zoom: Triggers RT (In) / LT (Out) (MMB+RMB Drag or Wheel)\n"
                "• Roll: Bumpers RB / LB\n"
                "• Y Button: Isometric View            |   X: Fit All In\n"
                "• A Button: Fit / Reframe             |   B: Escape\n"
                "• D-Pad: Standard Orthogonal Views\n"
                "• Left Stick Click (Hold): Precision Mode (50% speed for sketching)"
            )
        else:
            cheat = (
                "• Orbit: Right Analog Stick\n"
                "• Pan: Left Analog Stick\n"
                "• Zoom: Triggers RT (In) / LT (Out)\n"
                "• Roll: Bumpers RB / LB\n"
                "• A: Fit View   |   Y: Isometric   |   B: Escape"
            )
        self.lbl_cheat_body.configure(text=cheat)

        # Update Tray if running
        if self.tray:
            self.tray.update_presets(self.pm.presets, preset.get("id", ""))

    def _on_controller_state(self, state: Dict[str, Any]):
        """Called ~100Hz from controller background thread."""
        # Update Canvas vector
        self.canvas.update_state(state)
        
        # Update metrics label
        lx = state.get('lx', 0.0)
        ly = state.get('ly', 0.0)
        rx = state.get('rx', 0.0)
        ry = state.get('ry', 0.0)
        self.lbl_stick_metrics.configure(
            text=f"Left Stick (Pan): X: {lx:+.2f}  Y: {ly:+.2f}   |   Right Stick (Orbit): X: {rx:+.2f}  Y: {ry:+.2f}"
        )

    def _on_connection_change(self, is_connected: bool):
        """Called when controller connects/disconnects."""
        self.after(0, lambda: self._update_connection_display(is_connected))

    def _update_connection_display(self, is_connected: bool):
        if is_connected:
            self.pill_conn.configure(
                text="● Controller Connected",
                fg_color="#183324",
                text_color="#00d26a"
            )
            # Query battery
            bat = self.cm.device.get_battery()
            lvl = bat.get('level', 'unknown').capitalize()
            typ = bat.get('type', 'unknown').capitalize()
            self.lbl_battery.configure(text=f"🔋 Battery: {lvl} ({typ})")
        else:
            self.pill_conn.configure(
                text="● No Controller Detected",
                fg_color="#382024",
                text_color="#e06c75"
            )
            self.lbl_battery.configure(text="🔋 --")

    def _on_preset_switched(self, new_preset: Dict[str, Any]):
        """Called when preset is changed via the physical Xbox button."""
        self.after(0, self._sync_active_preset)

    def _on_preset_segment_selected(self, preset_name: str):
        """Called when user clicks preset in segmented bar."""
        for p in self.pm.presets:
            if p.get("name") == preset_name:
                self.pm.set_active_preset_by_id(p.get("id"))
                self._sync_active_preset()
                if self.pm.settings.get("haptic_rumble_enabled", True):
                    self.cm.device.pulse_rumble(pulses=1, intensity=0.4, duration_s=0.08)
                break

    def _on_cycle_button_clicked(self):
        """Manual next preset cycle button."""
        self.cm.cycle_preset()

    def _on_toggle_master_switch(self):
        val = bool(self.sw_master.get())
        if val == self.cm.is_paused:
            self.cm.toggle_pause()

    def _on_q_orbit(self, val: float):
        self.lbl_q_orbit.configure(text=f"{val:.2f}x")
        preset = self.pm.get_active_preset()
        preset['sensitivity_orbit'] = round(val, 2)
        self.pm.save_presets()
        self.preset_editor.slider_orbit.set(val)
        self.preset_editor.lbl_orbit_val.configure(text=f"{val:.2f}x")

    def _on_q_pan(self, val: float):
        self.lbl_q_pan.configure(text=f"{val:.2f}x")
        preset = self.pm.get_active_preset()
        preset['sensitivity_pan'] = round(val, 2)
        self.pm.save_presets()
        self.preset_editor.slider_pan.set(val)
        self.preset_editor.lbl_pan_val.configure(text=f"{val:.2f}x")

    def _on_q_zoom(self, val: float):
        self.lbl_q_zoom.configure(text=f"{val:.2f}x")
        preset = self.pm.get_active_preset()
        preset['sensitivity_zoom'] = round(val, 2)
        self.pm.save_presets()
        self.preset_editor.slider_zoom.set(val)
        self.preset_editor.lbl_zoom_val.configure(text=f"{val:.2f}x")

    def _on_preset_saved(self, updated_preset: Dict[str, Any]):
        self.pm.update_preset(updated_preset.get('id', ''), updated_preset)
        self._sync_active_preset()

    def _on_change_cycle_button(self, val: str):
        opt_to_btn = {
            "Back / View (Recommended)": "back",
            "Xbox Guide Button": "guide",
            "Start / Menu Button": "start",
            "Left Stick Click (LS)": "ls_click",
            "Right Stick Click (RS)": "rs_click",
            "Left Bumper (LB)": "lb",
            "Right Bumper (RB)": "rb"
        }
        btn_key = opt_to_btn.get(val, "back")
        self.pm.settings["cycle_button"] = btn_key
        self.pm.save_settings()
        self.btn_cycle.configure(text=f"⟳ Next Preset (🎮 {btn_key.upper()})")

    def _on_rint_change(self, val: float):
        self.lbl_rint_val.configure(text=f"{int(val*100)}%")
        self.pm.settings["haptic_rumble_intensity"] = round(val, 2)
        self.pm.save_settings()

    def _on_save_app_settings(self):
        self.pm.settings["haptic_rumble_enabled"] = bool(self.sw_rumble.get())
        self.pm.settings["osd_toast_enabled"] = bool(self.sw_osd.get())
        self.pm.settings["auto_switch_cad_window"] = bool(self.sw_auto_cad.get())
        self.pm.settings["minimize_to_tray_on_close"] = bool(self.sw_tray.get())
        self.pm.save_settings()

    def _on_factory_reset(self):
        self.pm.reset_to_defaults()
        self._sync_active_preset()

    def _on_close(self):
        """Handles close event (minimize to tray or exit)."""
        if self.pm.settings.get("minimize_to_tray_on_close", True) and self.tray:
            self.withdraw()
        else:
            self.quit()
