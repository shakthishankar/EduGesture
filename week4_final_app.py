# week4_final_app.py
# EduGesture v1.0 - FINAL BUILD
# Fixed: ord('cal'), MediaPipe models, smooth calibration, profile sync

import cv2
import mediapipe as mp
import numpy as np
from utils import get_landmark_positions, calculate_distance
from whiteboard import Whiteboard
from config import load_config, save_config
from dashboard import Dashboard
from calibration import CalibrationPanel
import pyautogui
import time

# === Load User Profile ===
config = load_config()
print(f"[INFO] Loaded profile: {config}")

# === Initialize Components ===
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

# Whiteboard
wb = Whiteboard(1280, 720)
wb.brush_size = config["brush_size"]
wb.brush_color = tuple(config["brush_color"])

# Dashboard + Calibration
dashboard = Dashboard()
cal_panel = None
show_cal = False

# Tracking
prev_wrist_x = None
last_swipe_time = 0
hand_frame_count = 0
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

    print("\n" + "="*70)
    print("EDUGESTURE v1.0 - AI GESTURE CONTROL FOR TEACHERS")
    print("c-a-l → Open Calibration | s → Save PNG | p → Save Profile | q → Quit")
    print("c → Clear Board | l → Reload Profile | h → Hide Panel")
    print("="*70 + "\n")

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
        hand_detected = results.multi_hand_landmarks is not None

        # Update dashboard
        dashboard.update(hand_detected)

        # Overlay whiteboard
        wb_frame = wb.get_frame()
        combined_frame = cv2.addWeighted(frame, 0.5, wb_frame, 0.5, 0)

        if hand_detected:
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

            # Stabilize
            if prev_wrist_x is None:
                prev_wrist_x = wrist[0]
                hand_frame_count = 1
            else:
                hand_frame_count += 1

            # Finger count
            fingers_up = sum(1 for tip, pip in zip([8,12,16,20], [6,10,14,18]) if lm_pos[tip][1] < lm_pos[pip][1])
            if thumb_tip[0] < lm_pos[2][0]: fingers_up += 1
            pinch_dist = calculate_distance(index_tip, thumb_tip)

            # === CLASSIFY GESTURE ===
            if hand_frame_count > config["min_tracking_frames"]:
                if fingers_up == 5:
                    gesture = "OPEN_PALM"; gesture_color = (0, 255, 255); wb.last_point = None
                elif fingers_up == 0:
                    gesture = "FIST"; gesture_color = (0, 0, 255)
                    if wb.last_point is not None:
                        wb.erase_line(wb.last_point[0], wb.last_point[1], index_tip[0], index_tip[1])
                    wb.last_point = index_tip.copy()
                elif pinch_dist < config["pinch_threshold"]:
                    gesture = "PINCH"; gesture_color = (255, 0, 255); wb.last_point = None
                elif fingers_up == 1 and lm_pos[8][1] < lm_pos[6][1]:
                    gesture = "INDEX_POINT"; gesture_color = (255, 255, 0)
                    if wb.last_point is not None:
                        wb.draw_line(wb.last_point[0], wb.last_point[1], index_tip[0], index_tip[1])
                    wb.last_point = index_tip.copy()
                    drawing = True
                else:
                    wb.last_point = None; drawing = False

                # === SWIPE DETECTION ===
                if prev_wrist_x is not None:
                    dx = wrist[0] - prev_wrist_x
                    if abs(dx) > config["swipe_threshold"] and (current_time - last_swipe_time) > config["swipe_cooldown"]:
                        if dx > 0:
                            pyautogui.press('right')
                            print(f"[ACTION {time.strftime('%H:%M:%S')}] NEXT SLIDE")
                        else:
                            pyautogui.press('left')
                            print(f"[ACTION {time.strftime('%H:%M:%S')}] PREVIOUS SLIDE")
                        last_swipe_time = current_time
                prev_wrist_x = wrist[0]
            else:
                prev_wrist_x = wrist[0]

        else:
            prev_wrist_x = None
            hand_frame_count = 0
            wb.last_point = None
            drawing = False

        # === UI Overlay ===
        dashboard.draw(combined_frame)
        cv2.putText(combined_frame, f"Mode: {'DRAWING' if drawing else 'READY'}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0) if drawing else (200,200,200), 2)

        # === Keyboard Controls ===
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('c'):
            wb.clear()
            print(f"[ACTION {time.strftime('%H:%M:%S')}] WHITEBOARD CLEARED")
        elif key == ord('s'):
            fn = f"whiteboard_{time.strftime('%Y%m%d_%H%M%S')}.png"
            wb.image.save(fn)
            print(f"[SAVED] {fn}")
        elif key == ord('p'):
            save_config(config)
            print(f"[PROFILE] Saved to user_profile.json")
        elif key == ord('l'):
            config = load_config()
            wb.brush_size = config["brush_size"]
            print(f"[PROFILE] Reloaded: {config}")
        elif key == ord('c') and not show_cal:
            # Wait for 'a'
            k = cv2.waitKey(500) & 0xFF
            if k == ord('a'):
                k = cv2.waitKey(500) & 0xFF
                if k == ord('l'):
                    cal_panel = CalibrationPanel(config)
                    cal_panel.show()
                    show_cal = True
                    print("[CALIBRATION] Panel opened. Adjust sliders, press 'h' to hide.")

        # === Calibration Panel Control ===
        if show_cal and cal_panel:
            cal_key = cal_panel.update()
            if cal_key == ord('h'):
                show_cal = False
                cv2.destroyWindow("EduGesture - Calibration")
                print("[CALIBRATION] Panel closed.")

        cv2.imshow("EduGesture v1.0 - FINAL", combined_frame)

cap.release()
cv2.destroyAllWindows()
save_config(config)  # Auto-save on exit
print("[INFO] Session ended. Profile saved.")