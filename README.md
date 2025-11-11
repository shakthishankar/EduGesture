# EduGesture v1.0  
**AI-Powered Gesture Control for Teachers**  
**Phase 1: Complete** (Nov 12, 2025)

[![Phase 1 Complete](https://img.shields.io/badge/Phase%201-Complete-success?style=for-the-badge)](https://github.com/shakthishankar/EduGesture)

Hands-free classroom tool: Control slides, draw on virtual whiteboard, calibrate in real-time—all via webcam gestures. No external hardware needed.

---

## Features (Phase 1)
- **Real-time Hand Tracking**: MediaPipe for 21 landmarks (95%+ accuracy in ideal light).
- **5 Core Gestures**: 
  - Index Point → Draw (yellow lines).
  - Fist → Erase.
  - Swipe Right/Left → Next/Prev Slide (PowerPoint/Google Slides).
  - Open Palm → Pause.
  - Pinch → Zoom.
- **Virtual Whiteboard**: Draw/erase mid-air; save as PNG (`s` key).
- **Live Calibration Panel**: Adjust thresholds (`c-a-l` to open, `h` to hide).
- **Accuracy Dashboard**: FPS + detection % overlay.
- **User Profiles**: Save/load settings (`p` to save, `l` to reload).
- **Standalone .exe**: Runs without Python (`dist/EduGesture.exe`).

---

## Quick Start
1. **Download**: [EduGesture.exe](https://github.com/shakthishankar/EduGesture/releases/download/v1.0.0/EduGesture.exe) (or clone repo).
2. **Run**: Double-click `.exe` (or `python week4_final_app.py`).
3. **Test**: Open PowerPoint (F5 for slideshow), point/swipe/draw.

**Controls**:
| Key | Action |
|-----|--------|
| `c-a-l` | Open Calibration (sliders for swipe/pinch/brush) |
| `h` | Hide Panel |
| `c` | Clear Board |
| `s` | Save PNG |
| `p` | Save Profile |
| `l` | Reload Profile |
| `q` | Quit |

---

## Build from Source
```bash
# Install deps
pip install -r requirements.txt

# Run
python week4_final_app.py

# Build .exe
pyinstaller week4_final_app.spec
