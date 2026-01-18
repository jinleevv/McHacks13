import math
from enum import Enum
import pyautogui

MODEL_PATH = './gesture_recognizer.task'

# Camera & Screen
CAM_W, CAM_H = 640, 480
SCREEN_W, SCREEN_H = pyautogui.size()

# Performance Tuners
pyautogui.PAUSE = 0           # Remove lag
SMOOTHING_FACTOR = 2          # Lower = faster, Higher = smoother
MARGIN = 100                  # Box margin for mouse movement
SCROLL_SENSITIVITY = 15       # Pixels per scroll step
ZOOM_THRESHOLD = 0.05         # Threshold to detect pinch open/close
SWIPE_THRESHOLD = 50          # Pixels needed to trigger a swipe

# OS Shortcuts (Adjust for Windows/Mac)
# MacOS:
KEY_ZOOM_IN = 'command', '+'
KEY_ZOOM_OUT = 'command', '-'
KEY_SWIPE_LEFT = 'ctrl', 'left'
KEY_SWIPE_RIGHT = 'ctrl', 'right'
# Windows (Uncomment if needed):
# KEY_ZOOM_IN = 'ctrl', '+'
# KEY_ZOOM_OUT = 'ctrl', '-'
# KEY_SWIPE_LEFT = 'win', 'ctrl', 'left'
# KEY_SWIPE_RIGHT = 'win', 'ctrl', 'right'

class GestureMode(Enum):
    NONE = 0
    CURSOR = 1  # 1 Finger
    SCROLL = 2  # 2 Fingers
    SWIPE = 3   # 3+ Fingers

class Utils:
    @staticmethod
    def map_range(value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def calc_distance(p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)