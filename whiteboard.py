# whiteboard.py
from PIL import Image, ImageDraw
import numpy as np

class Whiteboard:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), (30, 30, 30))
        self.draw = ImageDraw.Draw(self.image)
        self.last_point = None
        self.brush_size = 5
        self.brush_color = (255, 255, 0)

    def draw_line(self, x1, y1, x2, y2):
        self.draw.line([(x1, y1), (x2, y2)], fill=self.brush_color, width=self.brush_size)

    def erase_line(self, x1, y1, x2, y2):
        self.draw.line([(x1, y1), (x2, y2)], fill=(30, 30, 30), width=self.brush_size * 3)

    def get_frame(self):
        return np.array(self.image)

    def clear(self):
        self.image = Image.new("RGB", (self.width, self.height), (30, 30, 30))
        self.draw = ImageDraw.Draw(self.image)
        self.last_point = None