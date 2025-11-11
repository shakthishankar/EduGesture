# utils.py
import numpy as np

def get_landmark_positions(hand_landmarks, img_shape):
    """Convert normalized MediaPipe landmarks to pixel coordinates."""
    h, w = img_shape[:2]
    return np.array([(lm.x * w, lm.y * h) for lm in hand_landmarks.landmark])

def calculate_distance(p1, p2):
    """Euclidean distance between two points."""
    return np.linalg.norm(np.array(p1) - np.array(p2))