import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
) as hands:

    print("Press 'q' to quit | Hand detection active...")
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Flip + BGR to RGB
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process hand landmarks
        results = hands.process(rgb_frame)

        # Draw landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2),
                    mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

        cv2.putText(frame, "EduGesture - Week 1", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("EduGesture - Hand Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()