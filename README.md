# 🎮 XboxConnexion — 3D SpaceMouse CAD Controller

**XboxConnexion** turns your standard **Xbox One / Xbox Series X|S / Xbox 360 controller** into a dedicated **6-Degrees-of-Freedom (6-DoF) SpaceMouse** for professional CAD applications including **Dassault Systèmes SOLIDWORKS** and **CATIA (V5 / 3DEXPERIENCE)**, as well as Autodesk Fusion 360, Inventor, and Blender.

---

## ✨ Key Features

1. **6-DoF CAD Viewport Navigation**:
   - **Right Thumbstick**: Orbit / Rotate (MMB drag in SolidWorks, MMB + RMB drag in CATIA).
   - **Left Thumbstick**: Pan / Translate (Ctrl + MMB in SolidWorks, MMB drag in CATIA).
   - **Analog Triggers (LT / RT)**: Ultra-smooth analog Zoom In & Zoom Out.
   - **Bumpers (LB / RB)**: Roll Clockwise / Counter-Clockwise.
2. **Instant Preset Switching on Controller**:
   - Dedicated physical button on your Xbox gamepad (Default: **`Back / View`** button) instantly cycles between presets (**SolidWorks ↔ CATIA ↔ Fusion ↔ Blender**).
   - **Haptic Rumble Feedback**: Controller buzzes with distinct confirmation patterns (1 pulse for SolidWorks, 2 pulses for CATIA).
   - **Floating OSD Toast Notification**: A sleek, non-intrusive on-screen banner appears for 1.5 seconds showing the active preset without stealing window focus from CAD.
3. **Infinite Canvas (Zero-Jerk Boundary Wrapping)**:
   - Eliminates mouse border collision! Automatically teleports the virtual mouse drag before it reaches monitor boundaries so you can continuously spin models 360° indefinitely.
4. **Smart Work-Point (Cursor Auto-Restore)**:
   - When you release the thumbstick, your cursor seamlessly returns to the exact model face / vertex where you were working.
5. **Precision Sketching Mode**:
   - Hold down **Left Stick Click (LS)** to reduce sensitivity by 50% for microscopic adjustments and delicate sketching.
6. **Modern Dark GUI (CustomTkinter)**:
   - **Live Controller Vector Diagram**: Real-time animated thumbsticks, analog trigger gauges, and glowing buttons.
   - **Quick Tuning**: Instant sliders for Orbit Speed, Pan Speed, Zoom Speed, and Drift Deadzones.
   - **Preset Editor**: Dynamic curve selector (Exponential Precision, Smoothstep, Linear), axis inversions, and button shortcuts.
   - **System Tray Integration**: Runs quietly in the background with quick preset selection from the Windows tray.
   - **Auto-CAD Window Focus**: Automatically switches presets when you alt-tab between `SLDWORKS.exe` and `CNEXT.exe` / `CATIA.exe`.

---

## 🚀 Quick Start

### 1. Requirements
- Windows 10 or 11
- Python 3.10+
- Any Xbox 360, Xbox One, or Xbox Series X/S controller (USB or Bluetooth)

### 2. Launching the App
Double-click:
```bat
run.bat
```
Or run silently without a console window:
```bat
pythonw run.pyw
```

---

## 🕹️ Default CAD Presets

### 🔵 SolidWorks Preset (`SLDWORKS.exe`)
| Control | SolidWorks Action | Emulation Method |
| :--- | :--- | :--- |
| **Right Stick** | **Orbit / Rotate** | Middle Mouse Button (`MMB`) Drag |
| **Left Stick** | **Pan / Translate** | `Ctrl` + `MMB` Drag |
| **Right Trigger (RT)** | **Zoom In** | Smooth Mouse Wheel Forward |
| **Left Trigger (LT)** | **Zoom Out** | Smooth Mouse Wheel Backward |
| **Right / Left Bumpers** | **Roll CW / CCW** | `Alt` + `MMB` Drag |
| **Back / View Button** | **Cycle Next Preset** | Haptic Pulse + OSD Notification |
| **Start / Menu Button** | **Pause / Resume** | Suspends / Resumes CAD emulation |
| **Left Stick Click (LS)** | **Precision Mode** | Halves movement speed while held |
| **Right Stick Click (RS)**| **Zoom to Fit** | Key `F` |
| **Y Button** | **Isometric View** | `Ctrl + 7` |
| **X Button** | **Normal To View** | `Ctrl + 8` |
| **A Button** | **Zoom to Fit** | Key `F` |
| **B Button** | **Escape / Deselect** | `Escape` |
| **D-Pad (Up/Down/Left/Right)** | **Orthogonal Views** | `Ctrl + 5` (Top), `Ctrl + 6` (Bottom), `Ctrl + 3` (Left), `Ctrl + 4` (Right) |

---

### 🟢 CATIA V5 / 3DEXPERIENCE Preset (`CNEXT.exe`)
| Control | CATIA Action | Emulation Method |
| :--- | :--- | :--- |
| **Right Stick** | **Orbit / Rotate** | `MMB` + `RMB` Drag |
| **Left Stick** | **Pan / Translate** | `MMB` Drag |
| **Triggers (RT / LT)** | **Zoom In / Out** | Mouse Wheel or Classic CATIA Drag |
| **Bumpers (RB / LB)** | **Roll / Reframe** | View orientation |
| **Back / View Button** | **Cycle Next Preset** | Haptic Pulse + OSD Notification |
| **Start / Menu Button** | **Pause / Resume** | Suspends / Resumes CAD emulation |
| **Left Stick Click (LS)** | **Precision Mode** | Halves movement speed while held |
| **Right Stick Click (RS)**| **Fit All In** | `Ctrl + Shift + 0` |
| **Y Button** | **Isometric View** | `Ctrl + Shift + 7` |
| **X Button** | **Fit All In** | Reframe |
| **A Button** | **Fit / Center** | Reframe |
| **B Button** | **Escape** | `Escape` |
| **D-Pad** | **Standard Views** | Top, Bottom, Left, Right |

---

## 🛠️ Tuning & Customization

Inside the **XboxConnexion** interface:
- **Preset Selector Bar**: Click any preset button (`[ SolidWorks ]`, `[ CATIA V5 / 3DX ]`, etc.) to switch instantly.
- **Preset Switch Button Selection**: In the *App Settings* tab, you can customize which physical controller button cycles presets (`Back`, `Guide`, `Start`, `LS Click`, `RS Click`, `LB`, `RB`).
- **Dynamic Curves**:
  - `Exponential (Precision)`: Subtle micro-movements near center for fine sketch editing, ramping up to rapid rotation when fully deflected.
  - `Smoothstep`: S-curve dampening.
  - `Linear`: 1:1 proportional response.
- **Boundary Wrapping**: Prevents cursor from stopping at screen borders on multi-monitor setups.
- **Zoom Mode Selection**: Choose between Mouse Wheel zoom and classic CAD drag zoom.

---

## 📂 Project Structure

```
XboxConnexion/
├── config/
│   ├── presets.json           # Active & customizable CAD profiles
│   └── settings.json          # User preferences (rumble, OSD, cycle key)
├── src/
│   ├── xinput.py              # Windows XInput ctypes interface (rumble, polling)
│   ├── cad_emulator.py        # Win32 SendInput 6-DoF navigation & infinite canvas
│   ├── preset_manager.py      # Profile management (SolidWorks, CATIA, Fusion)
│   ├── controller_manager.py  # Background polling & preset switch handler
│   ├── toast_hud.py           # Click-through floating OSD notification overlay
│   ├── app_detector.py        # Active CAD foreground process auto-detection
│   └── ui/
│       ├── controller_canvas.py # Live vector gamepad with animated sticks/buttons
│       ├── preset_editor.py     # Preset fine-tuning sliders & shortcut binder
│       ├── tray_icon.py         # System tray icon with context menu
│       └── main_window.py       # CustomTkinter dark CAD GUI
├── run.bat                    # Windows 1-click batch launcher
├── run.pyw                    # Windowless Python background launcher
├── requirements.txt           # Python dependencies
└── README.md                  # Manual & documentation
```
