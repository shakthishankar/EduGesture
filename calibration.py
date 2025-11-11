# calibration.py
import cv2
import numpy as np

class CalibrationPanel:
    def __init__(self, config):
        self.config = config
        self.window_name = "EduGesture - Calibration"
        cv2.namedWindow(self.window_name)

        # Create trackbars
        cv2.createTrackbar("Swipe Thresh", self.window_name, config["swipe_threshold"], 300, self.on_swipe)
        cv2.createTrackbar("Swipe Cooldown", self.window_name, int(config["swipe_cooldown"]*10), 30, self.on_cooldown)
        cv2.createTrackbar("Pinch Thresh", self.window_name, config["pinch_threshold"], 100, self.on_pinch)
        cv2.createTrackbar("Brush Size", self.window_name, config["brush_size"], 20, self.on_brush)

    def on_swipe(self, val):
        self.config["swipe_threshold"] = val

    def on_cooldown(self, val):
        self.config["swipe_cooldown"] = val / 10.0

    def on_pinch(self, val):
        self.config["pinch_threshold"] = val

    def on_brush(self, val):
        self.config["brush_size"] = val

    def show(self):
        panel = np.zeros((300, 500, 3), dtype=np.uint8)
        cv2.putText(panel, "CALIBRATION PANEL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(panel, "Press 'h' to hide", (10, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.imshow(self.window_name, panel)

    def update(self):
        key = cv2.waitKey(1) & 0xFF
        if key == ord('h'):
            cv2.destroyWindow(self.window_name)
        return key