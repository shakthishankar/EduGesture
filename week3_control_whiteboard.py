# week3_control_whiteboard.py
# EduGesture - Week 3: Slide Control + Virtual Whiteboard
# Fixed: last_point array ambiguity, stable drawing/erasing, real slide control

import cv2
import mediapipe as mp
import numpy as np
from utils import get_landmark_positions, calculate_distance
from whiteboard import Whiteboard
import pyautogui
import time

# === Initialize MediaPipe ===
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# === PyAutoGUI Settings ===
pyautogui.FAILSAFE = True  # Move mouse to top-left to emergency stop
pyautogui.PAUSE = 0.01     # Fast response

# === Gesture to Action Mapping ===
GESTURE_ACTIONS = {
    "OPEN_PALM": "PAUSE",
    "FIST": "ERASE",
    "SWIPE_RIGHT": "NEXT SLIDE",
    "SWIPE_LEFT": "PREVIOUS SLIDE",
    "PINCH": "ZOOM",
    "INDEX_POINT": "DRAW"
}

# === Global Tracking Variables ===
prev_wrist_x = None
last_swipe_time = 0
swipe_threshold = 100      # pixels
swipe_cooldown = 0.8       # seconds
hand_frame_count = 0
min_tracking_frames = 3    # Wait for stable hand

# === Whiteboard Canvas ===
wb = Whiteboard(1280, 720)
drawing = False

# === Webcam Setup ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    print("\n" + "="*60)
    print("EduGesture - Week 3: SLIDE CONTROL + VIRTUAL WHITEBOARD")
    print("INDEX POINT → Draw | FIST → Erase | SWIPE → Next/Prev")
    print("Press 'c' to Clear | 's' to Save PNG | 'q' to Quit")
    print("="*60 + "\n")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        current_time = time.time()
        gesture = "UNKNOWN"
        gesture_color = (255, 255, 255)

        # === Overlay: Webcam + Whiteboard (50/50 blend) ===
        wb_frame = wb.get_frame()
        combined_frame = cv2.addWeighted(frame, 0.5, wb_frame, 0.5, 0)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(
                combined_frame, hand, mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            lm_pos = get_landmark_positions(hand, frame.shape)
            wrist = lm_pos[0]
            index_tip = lm_pos[8]
            thumb_tip = lm_pos[4]

            # === Stabilize hand tracking ===
            if prev_wrist_x is None:
                prev_wrist_x = wrist[0]
                hand_frame_count = 1
            else:
                hand_frame_count += 1

            # === Count fingers up ===
            fingers_up = 0
            finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
            finger_pips = [6, 10, 14, 18]
            for tip, pip in zip(finger_tips, finger_pips):
                if lm_pos[tip][1] < lm_pos[pip][1]:
                    fingers_up += 1
            if thumb_tip[0] < lm_pos[2][0]:  # Thumb left of PIP
                fingers_up += 1

            pinch_dist = calculate_distance(index_tip, thumb_tip)

            # === CLASSIFY GESTURE (Only after stable frames) ===
            if hand_frame_count > min_tracking_frames:
                if fingers_up == 5:
                    gesture = "OPEN_PALM"
                    gesture_color = (0, 255, 255)
                    drawing = False
                    wb.last_point = None  # Reset drawing

                elif fingers_up == 0:
                    gesture = "FIST"
                    gesture_color = (0, 0, 255)
                    # ERASE MODE
                    if wb.last_point is not None:
                        x1, y1 = wb.last_point
                        x2, y2 = index_tip
                        wb.erase_line(x1, y1, x2, y2)
                    wb.last_point = index_tip.copy()  # Store as list
                    drawing = False

                elif pinch_dist < 45:
                    gesture = "PINCH"
                    gesture_color = (255, 0, 255)
                    drawing = False
                    wb.last_point = None

                elif fingers_up == 1 and lm_pos[8][1] < lm_pos[6][1]:
                    gesture = "INDEX_POINT"
                    gesture_color = (255, 255, 0)
                    # DRAW MODE
                    if wb.last_point is not None:
                        x1, y1 = wb.last_point
                        x2, y2 = index_tip
                        wb.draw_line(x1, y1, x2, y2)
                    wb.last_point = index_tip.copy()
                    drawing = True

                else:
                    wb.last_point = None
                    drawing = False

                # === SWIPE DETECTION (Wrist motion) ===
                if prev_wrist_x is not None:
                    dx = wrist[0] - prev_wrist_x
                    if abs(dx) > swipe_threshold and (current_time - last_swipe_time) > swipe_cooldown:
                        if dx > 0:
                            gesture = "SWIPE_RIGHT"
                            pyautogui.press('right')
                            print(f"[ACTION {time.strftime('%H:%M:%S')}] NEXT SLIDE")
                        else:
                            gesture = "SWIPE_LEFT"
                            pyautogui.press('left')
                            print(f"[ACTION {time.strftime('%H:%M:%S')}] PREVIOUS SLIDE")
                        last_swipe_time = current_time
                prev_wrist_x = wrist[0]

            else:
                prev_wrist_x = wrist[0]

            # === Log non-drawing gestures ===
            if gesture in ["OPEN_PALM", "FIST", "PINCH"]:
                print(f"[LOG {time.strftime('%H:%M:%S')}] {GESTURE_ACTIONS[gesture]}")

        else:
            prev_wrist_x = None
            hand_frame_count = 0
            wb.last_point = None
            drawing = False

        # === On-Screen UI ===
        cv2.putText(combined_frame, "EduGesture - Week 3", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(combined_frame, f"Mode: {'DRAWING' if drawing else 'READY'}",
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 255, 0) if drawing else (200, 200, 200), 2)

        instructions = [
            "INDEX POINT → Draw (Yellow)",
            "FIST → Erase",
            "SWIPE → Next/Prev Slide",
            "Press 'c' → Clear | 's' → Save PNG"
        ]
        for i, txt in enumerate(instructions):
            cv2.putText(combined_frame, txt, (10, 120 + i*30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # === Keyboard Controls ===
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            wb.clear()
            print(f"[ACTION {time.strftime('%H:%M:%S')}] WHITEBOARD CLEARED")
        elif key == ord('s'):
            filename = f"whiteboard_{time.strftime('%Y%m%d_%H%M%S')}.png"
            wb.image.save(filename)
            print(f"[SAVED] {filename}")

        cv2.imshow("EduGesture - Week 3: Control + Whiteboard", combined_frame)

cap.release()
cv2.destroyAllWindows()