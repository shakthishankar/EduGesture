# config.py
import json
import os

DEFAULT_CONFIG = {
    "swipe_threshold": 100,
    "swipe_cooldown": 0.8,
    "pinch_threshold": 45,
    "min_tracking_frames": 3,
    "brush_size": 5,
    "brush_color": [255, 255, 0]
}

CONFIG_FILE = "user_profile.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)