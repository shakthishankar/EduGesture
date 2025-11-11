# dashboard.py
import time
import cv2

class Dashboard:
    def __init__(self):
        self.fps = 0.0
        self.detection_rate = 0.0
        self.frame_count = 0
        self.detected_count = 0
        self.start_time = time.time()

    def update(self, detected):
        self.frame_count += 1
        if detected:
            self.detected_count += 1
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.fps = self.frame_count / elapsed
            self.detection_rate = (self.detected_count / self.frame_count) * 100

    def draw(self, frame):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (w-300, 10), (w-10, 140), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        stats = [
            f"FPS: {self.fps:.1f}",
            f"Detection: {self.detection_rate:.1f}%",
            f"Frames: {self.frame_count}",
            f"Detected: {self.detected_count}"
        ]
        for i, txt in enumerate(stats):
            cv2.putText(frame, txt, (w-290, 40 + i*25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)