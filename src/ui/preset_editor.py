"""
XboxConnexion - Preset Editor View
Provides fine-tuning of sensitivities, response curves, deadzones, axis inversions,
boundary handling, and CAD shortcut rebindings.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable

AVAILABLE_ACTIONS = [
    ("fit_view", "Zoom to Fit (Fit All In)"),
    ("isometric", "Isometric View"),
    ("normal_to", "Normal To View"),
    ("top_view", "Top View"),
    ("bottom_view", "Bottom View"),
    ("front_view", "Front View"),
    ("back_view", "Back View"),
    ("left_view", "Left View"),
    ("right_view", "Right View"),
    ("escape", "Escape / Cancel"),
    ("undo", "Undo"),
    ("redo", "Redo"),
    ("precision_mode", "Precision Mode (50% speed held)"),
    ("none", "None / Disabled"),
]

class PresetEditor(ctk.CTkScrollableFrame):
    """CustomTkinter scrollable frame for editing CAD presets."""

    def __init__(self, parent, on_save_callback: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(parent, fg_color="#181a20", **kwargs)
        self.on_save = on_save_callback
        self.current_preset: Dict[str, Any] = {}

        self._build_ui()

    def _build_ui(self):
        # 1. Header Section
        self.lbl_title = ctk.CTkLabel(
            self,
            text="Preset Configuration",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_title.pack(anchor="w", padx=15, pady=(10, 2))

        self.lbl_desc = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8a90a0"
        )
        self.lbl_desc.pack(anchor="w", padx=15, pady=(0, 15))

        # 2. Sensitivities Card
        sens_card = ctk.CTkFrame(self, fg_color="#21242d", corner_radius=10)
        sens_card.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            sens_card,
            text="🎯 Motion Sensitivities & Deadzones",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#00bcd4"
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # Orbit Speed Slider
        f_orbit = ctk.CTkFrame(sens_card, fg_color="transparent")
        f_orbit.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(f_orbit, text="Orbit / Rotate Speed:", width=160, anchor="w").pack(side="left")
        self.slider_orbit = ctk.CTkSlider(f_orbit, from_=0.2, to=3.0, number_of_steps=28, command=self._on_orbit_change)
        self.slider_orbit.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_orbit_val = ctk.CTkLabel(f_orbit, text="1.25x", width=45)
        self.lbl_orbit_val.pack(side="right")

        # Pan Speed Slider
        f_pan = ctk.CTkFrame(sens_card, fg_color="transparent")
        f_pan.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(f_pan, text="Pan / Translate Speed:", width=160, anchor="w").pack(side="left")
        self.slider_pan = ctk.CTkSlider(f_pan, from_=0.2, to=3.0, number_of_steps=28, command=self._on_pan_change)
        self.slider_pan.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_pan_val = ctk.CTkLabel(f_pan, text="1.00x", width=45)
        self.lbl_pan_val.pack(side="right")

        # Zoom Speed Slider
        f_zoom = ctk.CTkFrame(sens_card, fg_color="transparent")
        f_zoom.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(f_zoom, text="Zoom Speed (Triggers):", width=160, anchor="w").pack(side="left")
        self.slider_zoom = ctk.CTkSlider(f_zoom, from_=0.2, to=3.0, number_of_steps=28, command=self._on_zoom_change)
        self.slider_zoom.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_zoom_val = ctk.CTkLabel(f_zoom, text="1.35x", width=45)
        self.lbl_zoom_val.pack(side="right")

        # Stick Deadzone Slider
        f_dz = ctk.CTkFrame(sens_card, fg_color="transparent")
        f_dz.pack(fill="x", padx=15, pady=(4, 15))
        ctk.CTkLabel(f_dz, text="Stick Drift Deadzone:", width=160, anchor="w").pack(side="left")
        self.slider_dz = ctk.CTkSlider(f_dz, from_=0.02, to=0.30, number_of_steps=28, command=self._on_dz_change)
        self.slider_dz.pack(side="left", fill="x", expand=True, padx=10)
        self.lbl_dz_val = ctk.CTkLabel(f_dz, text="12%", width=45)
        self.lbl_dz_val.pack(side="right")

        # 3. Dynamic Curve & Inversion Card
        dyn_card = ctk.CTkFrame(self, fg_color="#21242d", corner_radius=10)
        dyn_card.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            dyn_card,
            text="📈 Stick Response Curve & Inversion",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#00d26a"
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # Curve Selector
        f_curve = ctk.CTkFrame(dyn_card, fg_color="transparent")
        f_curve.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(f_curve, text="Dynamic Curve:", width=130, anchor="w").pack(side="left")
        self.seg_curve = ctk.CTkSegmentedButton(
            f_curve,
            values=["Exponential (Precision)", "Smoothstep", "Linear"],
            command=self._on_curve_change
        )
        self.seg_curve.pack(side="left", fill="x", expand=True, padx=10)

        # Inversion Checkboxes Grid
        f_inv = ctk.CTkFrame(dyn_card, fg_color="transparent")
        f_inv.pack(fill="x", padx=15, pady=(10, 15))
        
        self.chk_inv_orbit_y = ctk.CTkCheckBox(f_inv, text="Invert Orbit Pitch (Y)", command=self._auto_save)
        self.chk_inv_orbit_y.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.chk_inv_orbit_x = ctk.CTkCheckBox(f_inv, text="Invert Orbit Yaw (X)", command=self._auto_save)
        self.chk_inv_orbit_x.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.chk_inv_pan_y = ctk.CTkCheckBox(f_inv, text="Invert Pan Y", command=self._auto_save)
        self.chk_inv_pan_y.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.chk_inv_pan_x = ctk.CTkCheckBox(f_inv, text="Invert Pan X", command=self._auto_save)
        self.chk_inv_pan_x.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.chk_inv_zoom = ctk.CTkCheckBox(f_inv, text="Invert Zoom Triggers", command=self._auto_save)
        self.chk_inv_zoom.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # 4. Viewport & Canvas Behavior Card
        vp_card = ctk.CTkFrame(self, fg_color="#21242d", corner_radius=10)
        vp_card.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            vp_card,
            text="🔄 3D Viewport & Mouse Handling",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ff9800"
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # Infinite Canvas switch
        self.sw_boundary = ctk.CTkSwitch(
            vp_card,
            text="Infinite Canvas (Zero-jerk border wrapping so cursor never jams)",
            command=self._auto_save
        )
        self.sw_boundary.pack(anchor="w", padx=15, pady=6)

        # Return cursor to start switch
        self.sw_restore = ctk.CTkSwitch(
            vp_card,
            text="Smart Work-Point: Return mouse cursor to model point on release",
            command=self._auto_save
        )
        self.sw_restore.pack(anchor="w", padx=15, pady=6)

        # Zoom Mode Option Menu
        f_zmode = ctk.CTkFrame(vp_card, fg_color="transparent")
        f_zmode.pack(fill="x", padx=15, pady=(6, 15))
        ctk.CTkLabel(f_zmode, text="Zoom Injection Mode:", width=160, anchor="w").pack(side="left")
        self.opt_zoom_mode = ctk.CTkOptionMenu(
            f_zmode,
            values=["Mouse Wheel (Default)", "Shift + MMB Drag", "Classic CATIA Drag (MMB+RMB)"],
            command=self._on_zoom_mode_change
        )
        self.opt_zoom_mode.pack(side="left", padx=10)

        # 5. Button Actions Table
        act_card = ctk.CTkFrame(self, fg_color="#21242d", corner_radius=10)
        act_card.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            act_card,
            text="🎮 Controller Button CAD Mappings",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#61afef"
        ).pack(anchor="w", padx=15, pady=(12, 10))

        self.btn_dropdowns: Dict[str, ctk.CTkOptionMenu] = {}
        mapping_labels = [
            ("y", "Y Button:"),
            ("x", "X Button:"),
            ("a", "A Button:"),
            ("b", "B Button:"),
            ("dpad_up", "D-Pad Up:"),
            ("dpad_down", "D-Pad Down:"),
            ("dpad_left", "D-Pad Left:"),
            ("dpad_right", "D-Pad Right:"),
            ("ls_click", "Left Stick Click:"),
            ("rs_click", "Right Stick Click:"),
        ]

        action_names = [label for _, label in AVAILABLE_ACTIONS]
        self.action_id_by_label = {label: aid for aid, label in AVAILABLE_ACTIONS}
        self.label_by_action_id = {aid: label for aid, label in AVAILABLE_ACTIONS}

        grid_f = ctk.CTkFrame(act_card, fg_color="transparent")
        grid_f.pack(fill="x", padx=15, pady=(0, 15))

        for idx, (btn_key, btn_text) in enumerate(mapping_labels):
            row = idx // 2
            col = (idx % 2) * 2
            ctk.CTkLabel(grid_f, text=btn_text, width=120, anchor="w").grid(row=row, column=col, padx=(10, 5), pady=4, sticky="w")
            om = ctk.CTkOptionMenu(
                grid_f,
                values=action_names,
                command=lambda val, k=btn_key: self._on_btn_mapping_change(k, val)
            )
            om.grid(row=row, column=col+1, padx=(0, 20), pady=4, sticky="w")
            self.btn_dropdowns[btn_key] = om

    def load_preset(self, preset: Dict[str, Any]):
        """Populates UI elements with the values of the selected preset."""
        self.current_preset = preset

        self.lbl_title.configure(text=f"Preset: {preset.get('name', 'Preset')}")
        self.lbl_desc.configure(text=preset.get('description', ''))

        # Sensitivities
        sens_orbit = preset.get('sensitivity_orbit', 1.25)
        self.slider_orbit.set(sens_orbit)
        self.lbl_orbit_val.configure(text=f"{sens_orbit:.2f}x")

        sens_pan = preset.get('sensitivity_pan', 1.0)
        self.slider_pan.set(sens_pan)
        self.lbl_pan_val.configure(text=f"{sens_pan:.2f}x")

        sens_zoom = preset.get('sensitivity_zoom', 1.35)
        self.slider_zoom.set(sens_zoom)
        self.lbl_zoom_val.configure(text=f"{sens_zoom:.2f}x")

        dz = preset.get('deadzone_stick', 0.12)
        self.slider_dz.set(dz)
        self.lbl_dz_val.configure(text=f"{int(dz * 100)}%")

        # Curve
        curve = preset.get('curve', 'exponential')
        curve_map = {
            'exponential': 'Exponential (Precision)',
            'smoothstep': 'Smoothstep',
            'linear': 'Linear'
        }
        self.seg_curve.set(curve_map.get(curve, 'Exponential (Precision)'))

        # Inversions
        if preset.get('invert_orbit_y', False):
            self.chk_inv_orbit_y.select()
        else:
            self.chk_inv_orbit_y.deselect()

        if preset.get('invert_orbit_x', False):
            self.chk_inv_orbit_x.select()
        else:
            self.chk_inv_orbit_x.deselect()

        if preset.get('invert_pan_y', True):
            self.chk_inv_pan_y.select()
        else:
            self.chk_inv_pan_y.deselect()

        if preset.get('invert_pan_x', False):
            self.chk_inv_pan_x.select()
        else:
            self.chk_inv_pan_x.deselect()

        if preset.get('invert_zoom', False):
            self.chk_inv_zoom.select()
        else:
            self.chk_inv_zoom.deselect()

        # Canvas & Viewport
        if preset.get('boundary_wrap', True):
            self.sw_boundary.select()
        else:
            self.sw_boundary.deselect()

        if preset.get('restore_cursor_on_release', True):
            self.sw_restore.select()
        else:
            self.sw_restore.deselect()

        # Zoom Mode
        zm = preset.get('zoom_mode', 'wheel')
        zm_display = {
            'wheel': 'Mouse Wheel (Default)',
            'drag_shift': 'Shift + MMB Drag',
            'drag_catia': 'Classic CATIA Drag (MMB+RMB)'
        }.get(zm, 'Mouse Wheel (Default)')
        self.opt_zoom_mode.set(zm_display)

        # Button Mappings
        mappings = preset.get('button_mappings', {})
        for btn_key, om in self.btn_dropdowns.items():
            action_id = mappings.get(btn_key, 'none')
            disp_label = self.label_by_action_id.get(action_id, 'None / Disabled')
            om.set(disp_label)

    def _on_orbit_change(self, val: float):
        self.lbl_orbit_val.configure(text=f"{val:.2f}x")
        self.current_preset['sensitivity_orbit'] = round(val, 2)
        self._auto_save()

    def _on_pan_change(self, val: float):
        self.lbl_pan_val.configure(text=f"{val:.2f}x")
        self.current_preset['sensitivity_pan'] = round(val, 2)
        self._auto_save()

    def _on_zoom_change(self, val: float):
        self.lbl_zoom_val.configure(text=f"{val:.2f}x")
        self.current_preset['sensitivity_zoom'] = round(val, 2)
        self._auto_save()

    def _on_dz_change(self, val: float):
        self.lbl_dz_val.configure(text=f"{int(val * 100)}%")
        self.current_preset['deadzone_stick'] = round(val, 2)
        self._auto_save()

    def _on_curve_change(self, val: str):
        rev_map = {
            'Exponential (Precision)': 'exponential',
            'Smoothstep': 'smoothstep',
            'Linear': 'linear'
        }
        self.current_preset['curve'] = rev_map.get(val, 'exponential')
        self._auto_save()

    def _on_zoom_mode_change(self, val: str):
        rev_map = {
            'Mouse Wheel (Default)': 'wheel',
            'Shift + MMB Drag': 'drag_shift',
            'Classic CATIA Drag (MMB+RMB)': 'drag_catia'
        }
        self.current_preset['zoom_mode'] = rev_map.get(val, 'wheel')
        self._auto_save()

    def _on_btn_mapping_change(self, btn_key: str, disp_val: str):
        action_id = self.action_id_by_label.get(disp_val, 'none')
        if 'button_mappings' not in self.current_preset:
            self.current_preset['button_mappings'] = {}
        self.current_preset['button_mappings'][btn_key] = action_id
        self._auto_save()

    def _auto_save(self):
        # Update checkbox states
        self.current_preset['invert_orbit_y'] = bool(self.chk_inv_orbit_y.get())
        self.current_preset['invert_orbit_x'] = bool(self.chk_inv_orbit_x.get())
        self.current_preset['invert_pan_y'] = bool(self.chk_inv_pan_y.get())
        self.current_preset['invert_pan_x'] = bool(self.chk_inv_pan_x.get())
        self.current_preset['invert_zoom'] = bool(self.chk_inv_zoom.get())

        self.current_preset['boundary_wrap'] = bool(self.sw_boundary.get())
        self.current_preset['restore_cursor_on_release'] = bool(self.sw_restore.get())

        if self.on_save:
            self.on_save(self.current_preset)
