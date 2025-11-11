
# EduGesture - AI-Powered Gesture Control for Teachers

## Week 2: 5 Core Gestures Implemented
- OPEN_PALM → PAUSE
- FIST → STOP
- SWIPE_RIGHT → NEXT SLIDE
- SWIPE_LEFT → PREVIOUS SLIDE
- PINCH → ZOOM IN/OUT

**Features**:
- Real-time classification using heuristic logic
- On-screen visual feedback with color coding
- Console logging with timestamps
- Swipe cooldown to prevent double triggers
- Single-hand focus (teacher's dominant hand)

**Run**:
```bash
venv\Scripts\activate
python week2_gesture_recognition.py

## Week 3: Slide Control + Virtual Whiteboard
- **INDEX POINT** → Draw with finger
- **FIST** → Erase
- **SWIPE** → Next/Prev in PowerPoint or Google Slides
- **'c'** → Clear board

**Run**:
```bash
python week3_control_whiteboard.py