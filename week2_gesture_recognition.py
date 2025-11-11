# week2_gesture_recognition.py
import cv2
import mediapipe as mp
import numpy as np
from utils import get_landmark_positions, calculate_distance
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Gesture mapping
GESTURE_LABELS = {
    "OPEN_PALM": "PAUSE",
    "FIST": "STOP",
    "SWIPE_RIGHT": "NEXT SLIDE",
    "SWIPE_LEFT": "PREVIOUS SLIDE",
    "PINCH": "ZOOM IN/OUT",
    "INDEX_POINT": "SELECT"
}

# === GLOBAL TRACKING VARIABLES (Declared at top) ===
prev_wrist_x = None
last_swipe_time = 0
swipe_threshold = 100   # Increased for reliability
swipe_cooldown = 0.8    # Slightly faster response
min_tracking_frames = 3  # Require stable hand for 3 frames

# Frame counter for stability
hand_frame_count = 0

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    print("\nEduGesture - Week 2: 5 Core Gestures + SWIPE FIXED")
    print("Hold gesture steady | Swipe clearly from left to right")
    print("Press 'q' to quit\n")

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

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(
                frame, hand, mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            lm_pos = get_landmark_positions(hand, frame.shape)
            wrist = lm_pos[0]
            index_tip = lm_pos[8]
            thumb_tip = lm_pos[4]
            middle_tip = lm_pos[12]

            # === Stabilize tracking ===
            if prev_wrist_x is None:
                prev_wrist_x = wrist[0]
                hand_frame_count = 1
            else:
                hand_frame_count += 1

            # === Finger state detection ===
            fingers_up = 0
            finger_tips = [8, 12, 16, 20]
            finger_pips = [6, 10, 14, 18]
            for tip, pip in zip(finger_tips, finger_pips):
                if lm_pos[tip][1] < lm_pos[pip][1]:
                    fingers_up += 1
            if thumb_tip[0] < lm_pos[2][0]:
                fingers_up += 1

            pinch_dist = calculate_distance(index_tip, thumb_tip)

            # === Gesture Classification ===
            if hand_frame_count > min_tracking_frames:
                if fingers_up == 5:
                    gesture = "OPEN_PALM"
                    gesture_color = (0, 255, 255)
                    prev_wrist_x = wrist[0]  # Update for swipe prep
                elif fingers_up == 0:
                    gesture = "FIST"
                    gesture_color = (0, 0, 255)
                    prev_wrist_x = wrist[0]
                elif pinch_dist < 45:
                    gesture = "PINCH"
                    gesture_color = (255, 0, 255)
                    prev_wrist_x = wrist[0]
                elif fingers_up == 1 and lm_pos[8][1] < lm_pos[6][1]:  # Index only
                    gesture = "INDEX_POINT"
                    gesture_color = (255, 255, 0)
                    # SWIPE DETECTION
                    if prev_wrist_x is not None:
                        dx = wrist[0] - prev_wrist_x
                        if abs(dx) > swipe_threshold and (current_time - last_swipe_time) > swipe_cooldown:
                            if dx > 0:
                                gesture = "SWIPE_RIGHT"
                                gesture_color = (0, 255, 0)
                                print(f"[LOG {time.strftime('%H:%M:%S')}] SWIPE DETECTED: NEXT SLIDE")
                            else:
                                gesture = "SWIPE_LEFT"
                                gesture_color = (255, 165, 0)
                                print(f"[LOG {time.strftime('%H:%M:%S')}] SWIPE DETECTED: PREVIOUS SLIDE")
                            last_swipe_time = current_time
                    prev_wrist_x = wrist[0]
                else:
                    prev_wrist_x = wrist[0]  # Always update
            else:
                prev_wrist_x = wrist[0]

            # === Log only final gestures ===
            if gesture != "INDEX_POINT" and gesture in GESTURE_LABELS:
                print(f"[LOG {time.strftime('%H:%M:%S')}] Gesture: {GESTURE_LABELS[gesture]}")

        else:
            prev_wrist_x = None
            hand_frame_count = 0

        # === On-Screen Display ===
        cv2.putText(frame, "EduGesture - Week 2", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, f"Gesture: {GESTURE_LABELS.get(gesture, 'UNKNOWN')}",
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, gesture_color, 3)

        instructions = [
            "5 Fingers -> PAUSE",
            "Fist -> STOP",
            "Index Point + Swipe -> NEXT/PREV",
            "Pinch -> ZOOM"
        ]
        for i, txt in enumerate(instructions):
            cv2.putText(frame, txt, (10, 120 + i*30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("EduGesture - Week 2: Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()