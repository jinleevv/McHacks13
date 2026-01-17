import collections
import time
import pyautogui

from utils import Utils

class MouseController:
    def __init__(self, smooting_factor, margin, cam_w, cam_h, screen_w, screen_h, key_zoom_in, key_swipe_left, key_swipe_right):
        self.cursor_history = collections.deque(maxlen=smooting_factor)
        self.last_swipe_time = 0
        self.last_zoom_time = 0
        # To track previous state for relative scroll/zoom
        self.prev_y = None 
        self.prev_dist = None

        self.margin = margin
        self.cam_w = cam_w
        self.cam_h = cam_h
        
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.key_zoom_in = key_zoom_in
        self.key_swipe_left = key_swipe_left
        self.key_swipe_right = key_swipe_right

    def move_cursor(self, x, y):
        """Smooths coordinates and moves the mouse."""
        # map camera coords to screen coords
        clamped_x = max(self.margin, min(x, self.cam_w - self.margin))
        clamped_y = max(self.margin, min(y, self.cam_h - self.margin))
        
        target_x = Utils.map_range(clamped_x, self.margin, self.cam_w - self.margin, 0, self.screen_w)
        target_y = Utils.map_range(clamped_y, self.margin, self.cam_h - self.margin, 0, self.screen_h)

        self.cursor_history.append((target_x, target_y))
        avg_x = sum(p[0] for p in self.cursor_history) / len(self.cursor_history)
        avg_y = sum(p[1] for p in self.cursor_history) / len(self.cursor_history)

        pyautogui.moveTo(avg_x, avg_y, _pause=False)

        # reset scroll memory when moving cursor
        self.prev_y = None
        self.prev_dist = None

    def left_click(self):
        pyautogui.click(_pause=False)

    def perform_scroll(self, current_y):
        """Scrolls based on vertical movement of fingers."""
        if self.prev_y is None:
            self.prev_y = current_y
            return

        # scroll direction
        delta = self.prev_y - current_y 
        
        # only scroll if movement is significant
        if abs(delta) > 5:
            # multiplier for speed
            scroll_clicks = int(delta / 5) 
            pyautogui.scroll(scroll_clicks * 2) 
            self.prev_y = current_y

    def perform_zoom(self, current_dist):
        """Zooms based on fingers spreading (in) or closing (out)."""
        if self.prev_dist is None:
            self.prev_dist = current_dist
            return

        # Debounce zoom to prevent spamming keys
        if time.time() - self.last_zoom_time < 0.2:
            return

        delta = current_dist - self.prev_dist

        if delta > 0.04: # Spreading -> Zoom In
            pyautogui.hotkey(*self.key_zoom_in)
            self.prev_dist = current_dist
            self.last_zoom_time = time.time()
            return "Zoom In"
        elif delta < -0.04: # Pinching -> Zoom Out
            pyautogui.hotkey(*self.key_zoom_in)
            self.prev_dist = current_dist
            self.last_zoom_time = time.time()
            return "Zoom Out"
        
        return None

    def perform_swipe(self, current_x):
        """Triggers left/right desktop switch."""
        # Debounce swipes (don't swipe 10 times in 1 second)
        if time.time() - self.last_swipe_time < 1.0:
            return None

        if current_x < self.cam_w * 0.2: 
            pyautogui.hotkey(*self.key_swipe_left)
            self.last_swipe_time = time.time()
            return "Swipe Left"
        elif current_x > self.cam_w * 0.8:
            pyautogui.hotkey(*self.key_swipe_right)
            self.last_swipe_time = time.time()
            return "Swipe Right"
        
        return None