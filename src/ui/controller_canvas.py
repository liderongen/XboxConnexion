"""
XboxConnexion - Controller Vector Canvas Widget
Renders a real-time vector diagram of an Xbox controller with animated sticks,
triggers, and glowing buttons for instant feedback.
"""

import tkinter as tk
from typing import Dict, Any

class ControllerCanvas(tk.Canvas):
    """Custom Tkinter Canvas providing live visualization of Xbox controller state."""

    def __init__(self, parent, width: int = 500, height: int = 300, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg='#181a20',
            highlightthickness=0,
            **kwargs
        )
        self.w = width
        self.h = height
        self.cx = width / 2
        self.cy = height / 2 + 10

        # Elements to update dynamically
        self.ls_dot = None
        self.rs_dot = None
        self.lt_bar = None
        self.rt_bar = None
        self.btn_elements: Dict[str, Any] = {}
        
        self._init_graphics()

    def _init_graphics(self):
        """Draws controller base shape and initial components."""
        self.delete("all")

        # Controller Body Outline (ergonomic stylized gamepad)
        # Main shell
        shell_points = [
            self.cx - 150, self.cy - 70,   # Top Left
            self.cx - 60,  self.cy - 75,   # Top Center-Left
            self.cx + 60,  self.cy - 75,   # Top Center-Right
            self.cx + 150, self.cy - 70,   # Top Right
            self.cx + 190, self.cy + 30,   # Right Grip Outer
            self.cx + 160, self.cy + 115,  # Right Grip Bottom
            self.cx + 115, self.cy + 105,  # Right Grip Inner
            self.cx + 50,  self.cy + 45,   # Bottom Inset Right
            self.cx - 50,  self.cy + 45,   # Bottom Inset Left
            self.cx - 115, self.cy + 105,  # Left Grip Inner
            self.cx - 160, self.cy + 115,  # Left Grip Bottom
            self.cx - 190, self.cy + 30,   # Left Grip Outer
        ]
        self.create_polygon(shell_points, fill='#232630', outline='#353a47', width=3, smooth=True)

        # Triggers Indicators (top corners)
        # LT
        self.create_rectangle(self.cx - 170, self.cy - 110, self.cx - 130, self.cy - 80,
                              fill='#1d1f27', outline='#353a47', width=2)
        self.create_text(self.cx - 150, self.cy - 95, text="LT (Zoom -)", fill='#8a90a0', font=("Segoe UI", 8, "bold"))
        self.lt_bar = self.create_rectangle(self.cx - 170, self.cy - 80, self.cx - 130, self.cy - 80,
                                            fill='#00d26a', outline='')

        # RT
        self.create_rectangle(self.cx + 130, self.cy - 110, self.cx + 170, self.cy - 80,
                              fill='#1d1f27', outline='#353a47', width=2)
        self.create_text(self.cx + 150, self.cy - 95, text="RT (Zoom +)", fill='#8a90a0', font=("Segoe UI", 8, "bold"))
        self.rt_bar = self.create_rectangle(self.cx + 130, self.cy - 80, self.cx + 170, self.cy - 80,
                                            fill='#00d26a', outline='')

        # Bumpers (LB, RB)
        self.btn_elements['lb'] = self.create_rectangle(
            self.cx - 120, self.cy - 75, self.cx - 65, self.cy - 60,
            fill='#2e323e', outline='#444a5b', width=2
        )
        self.create_text(self.cx - 92, self.cy - 67, text="LB (Roll)", fill='#c5cbd6', font=("Segoe UI", 8, "bold"))

        self.btn_elements['rb'] = self.create_rectangle(
            self.cx + 65, self.cy - 75, self.cx + 120, self.cy - 60,
            fill='#2e323e', outline='#444a5b', width=2
        )
        self.create_text(self.cx + 92, self.cy - 67, text="RB (Roll)", fill='#c5cbd6', font=("Segoe UI", 8, "bold"))

        # Xbox Center Guide Logo
        self.create_oval(self.cx - 16, self.cy - 48, self.cx + 16, self.cy - 16,
                         fill='#181a20', outline='#00d26a', width=2)
        self.create_text(self.cx, self.cy - 32, text="X", fill='#00d26a', font=("Segoe UI", 12, "bold"))

        # Back / View Button (Preset Switch!)
        self.btn_elements['back'] = self.create_oval(
            self.cx - 45, self.cy - 35, self.cx - 27, self.cy - 17,
            fill='#2e323e', outline='#444a5b', width=2
        )
        self.create_text(self.cx - 36, self.cy - 42, text="PRESET ⟳", fill='#00bcd4', font=("Segoe UI", 7, "bold"))

        # Start / Menu Button (Pause)
        self.btn_elements['start'] = self.create_oval(
            self.cx + 27, self.cy - 35, self.cx + 45, self.cy - 17,
            fill='#2e323e', outline='#444a5b', width=2
        )
        self.create_text(self.cx + 36, self.cy - 42, text="PAUSE ⏸", fill='#ff9800', font=("Segoe UI", 7, "bold"))

        # Left Thumbstick (Pan) - Center around (cx - 85, cy - 15)
        self.ls_base_x = self.cx - 85
        self.ls_base_y = self.cy - 15
        self.create_oval(self.ls_base_x - 30, self.ls_base_y - 30,
                         self.ls_base_x + 30, self.ls_base_y + 30,
                         fill='#1a1c23', outline='#353a47', width=2)
        self.create_text(self.ls_base_x, self.ls_base_y + 38, text="LS: PAN ↔", fill='#00bcd4', font=("Segoe UI", 8, "bold"))
        self.ls_dot = self.create_oval(self.ls_base_x - 16, self.ls_base_y - 16,
                                       self.ls_base_x + 16, self.ls_base_y + 16,
                                       fill='#3a4050', outline='#00bcd4', width=2)

        # Right Thumbstick (Orbit) - Center around (cx + 55, cy + 25)
        self.rs_base_x = self.cx + 55
        self.rs_base_y = self.cy + 25
        self.create_oval(self.rs_base_x - 30, self.rs_base_y - 30,
                         self.rs_base_x + 30, self.rs_base_y + 30,
                         fill='#1a1c23', outline='#353a47', width=2)
        self.create_text(self.rs_base_x, self.rs_base_y + 38, text="RS: ORBIT ⟲", fill='#00d26a', font=("Segoe UI", 8, "bold"))
        self.rs_dot = self.create_oval(self.rs_base_x - 16, self.rs_base_y - 16,
                                       self.rs_base_x + 16, self.rs_base_y + 16,
                                       fill='#3a4050', outline='#00d26a', width=2)

        # D-Pad (Views) - Center around (cx - 45, cy + 30)
        dp_cx = self.cx - 45
        dp_cy = self.cy + 30
        
        # Up
        self.btn_elements['dpad_up'] = self.create_rectangle(
            dp_cx - 8, dp_cy - 24, dp_cx + 8, dp_cy - 8,
            fill='#2e323e', outline='#444a5b'
        )
        # Down
        self.btn_elements['dpad_down'] = self.create_rectangle(
            dp_cx - 8, dp_cy + 8, dp_cx + 8, dp_cy + 24,
            fill='#2e323e', outline='#444a5b'
        )
        # Left
        self.btn_elements['dpad_left'] = self.create_rectangle(
            dp_cx - 24, dp_cy - 8, dp_cx - 8, dp_cy + 8,
            fill='#2e323e', outline='#444a5b'
        )
        # Right
        self.btn_elements['dpad_right'] = self.create_rectangle(
            dp_cx + 8, dp_cy - 8, dp_cx + 24, dp_cy + 8,
            fill='#2e323e', outline='#444a5b'
        )
        # Center
        self.create_rectangle(dp_cx - 8, dp_cy - 8, dp_cx + 8, dp_cy + 8, fill='#232630', outline='')
        self.create_text(dp_cx, dp_cy + 35, text="Views", fill='#8a90a0', font=("Segoe UI", 7, "bold"))

        # Action Buttons (A, B, X, Y) - Center around (cx + 105, cy - 15)
        ab_cx = self.cx + 105
        ab_cy = self.cy - 15

        # Y (Yellow) - Top
        self.btn_elements['y'] = self.create_oval(
            ab_cx - 10, ab_cy - 28, ab_cx + 10, ab_cy - 8,
            fill='#3a3620', outline='#e5c07b', width=2
        )
        self.create_text(ab_cx, ab_cy - 18, text="Y", fill='#f1c40f', font=("Segoe UI", 9, "bold"))

        # A (Green) - Bottom
        self.btn_elements['a'] = self.create_oval(
            ab_cx - 10, ab_cy + 8, ab_cx + 10, ab_cy + 28,
            fill='#1e3328', outline='#00d26a', width=2
        )
        self.create_text(ab_cx, ab_cy + 18, text="A", fill='#00d26a', font=("Segoe UI", 9, "bold"))

        # X (Blue) - Left
        self.btn_elements['x'] = self.create_oval(
            ab_cx - 28, ab_cy - 10, ab_cx - 8, ab_cy + 10,
            fill='#1e2a38', outline='#61afef', width=2
        )
        self.create_text(ab_cx - 18, ab_cy, text="X", fill='#61afef', font=("Segoe UI", 9, "bold"))

        # B (Red) - Right
        self.btn_elements['b'] = self.create_oval(
            ab_cx + 8, ab_cy - 10, ab_cx + 28, ab_cy + 10,
            fill='#382024', outline='#e06c75', width=2
        )
        self.create_text(ab_cx + 18, ab_cy, text="B", fill='#e06c75', font=("Segoe UI", 9, "bold"))

    def update_state(self, state: Dict[str, Any]):
        """Updates canvas components with live controller input values."""
        # 1. Update Left Thumbstick
        lx = state.get('lx', 0.0)
        ly = state.get('ly', 0.0)
        max_stick_deflection = 14.0
        cur_lx = self.ls_base_x + (lx * max_stick_deflection)
        cur_ly = self.ls_base_y - (ly * max_stick_deflection)
        self.coords(self.ls_dot,
                    cur_lx - 16, cur_ly - 16,
                    cur_lx + 16, cur_ly + 16)
        
        # Stick click color feedback
        btns = state.get('buttons', {})
        if btns.get('ls_click', False):
            self.itemconfig(self.ls_dot, fill='#00bcd4')
        else:
            self.itemconfig(self.ls_dot, fill='#3a4050')

        # 2. Update Right Thumbstick
        rx = state.get('rx', 0.0)
        ry = state.get('ry', 0.0)
        cur_rx = self.rs_base_x + (rx * max_stick_deflection)
        cur_ry = self.rs_base_y - (ry * max_stick_deflection)
        self.coords(self.rs_dot,
                    cur_rx - 16, cur_ry - 16,
                    cur_rx + 16, cur_ry + 16)
        
        if btns.get('rs_click', False):
            self.itemconfig(self.rs_dot, fill='#00d26a')
        else:
            self.itemconfig(self.rs_dot, fill='#3a4050')

        # 3. Update Triggers
        lt = state.get('lt', 0.0)
        rt = state.get('rt', 0.0)
        # LT bar heights
        lt_h = int(lt * 30)
        self.coords(self.lt_bar, self.cx - 170, self.cy - 80 - lt_h, self.cx - 130, self.cy - 80)
        
        rt_h = int(rt * 30)
        self.coords(self.rt_bar, self.cx + 130, self.cy - 80 - rt_h, self.cx + 170, self.cy - 80)

        # 4. Update Buttons
        for btn_key, canvas_id in self.btn_elements.items():
            is_down = btns.get(btn_key, False)
            if btn_key == 'back':
                # Preset switch button glowing cyan on press
                self.itemconfig(canvas_id, fill='#00bcd4' if is_down else '#2e323e')
            elif btn_key == 'start':
                self.itemconfig(canvas_id, fill='#ff9800' if is_down else '#2e323e')
            elif btn_key in ['lb', 'rb']:
                self.itemconfig(canvas_id, fill='#00d26a' if is_down else '#2e323e')
            elif btn_key.startswith('dpad'):
                self.itemconfig(canvas_id, fill='#00bcd4' if is_down else '#2e323e')
            elif btn_key == 'a':
                self.itemconfig(canvas_id, fill='#00d26a' if is_down else '#1e3328')
            elif btn_key == 'b':
                self.itemconfig(canvas_id, fill='#e06c75' if is_down else '#382024')
            elif btn_key == 'x':
                self.itemconfig(canvas_id, fill='#61afef' if is_down else '#1e2a38')
            elif btn_key == 'y':
                self.itemconfig(canvas_id, fill='#f1c40f' if is_down else '#3a3620')
