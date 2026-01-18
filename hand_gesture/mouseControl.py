import collections
import time
import pyautogui

from utils import Utils

class MouseController:
    def __init__(self, smooting_factor, margin, cam_w, cam_h, screen_w, screen_h, key_zoom_in, key_zoom_out, key_swipe_left, key_swipe_right):
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
        self.key_zoom_out = key_zoom_out
        self.key_swipe_left = key_swipe_left
        self.key_swipe_right = key_swipe_right
        self.pinch_start_time = 0
        self.is_scrolling = False
        self.last_scroll_y = 0
        self.count = 0

        self.zoom_anchor = None

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
        if self.prev_y is None:
            self.prev_y = current_y
            return

        delta = self.prev_y - current_y

        if abs(delta) > 5:  # pixels, not normalized
            scroll_clicks = int(delta / 8)
            pyautogui.scroll(scroll_clicks)
            self.prev_y = current_y


    def perform_zoom(self, current_dist):
        """
        Anchor-Based Zoom (Virtual Notches).
        - Establishes a start point (anchor) when you first pinch.
        - Fires a zoom key ONLY when you move a specific 'step' distance from the anchor.
        - Updates the anchor after every step to keep it synced.
        """
        # 1. ESTABLISH ANCHOR
        # If this is the first frame of a pinch, save the distance as zero-point.
        if self.zoom_anchor is None:
            self.zoom_anchor = current_dist
            return None

        # 2. CALCULATE DEVIATION FROM ANCHOR
        diff = current_dist - self.zoom_anchor

        # 3. DEFINE STEP SIZE (Sensitivity)
        # 0.02 means you have to move hands by 2% of screen width to trigger one zoom click.
        # Lower = Faster/More Sensitive. Higher = Slower/More Stable.
        STEP_SIZE = 0.026

        if diff > STEP_SIZE:
            pyautogui.hotkey(*self.key_zoom_in)
            print(f"Zoom Out (Dist: {current_dist:.3f})")
            
            self.zoom_anchor += STEP_SIZE
            return "Zoom Out"

        elif diff < -STEP_SIZE:
            pyautogui.hotkey(*self.key_zoom_out)
            print(f"Zoom In (Dist: {current_dist:.3f})")
            
            # Slide the anchor backward
            self.zoom_anchor -= STEP_SIZE
            return "Zoom In"

        return None

    def perform_swipe(self, current_x, current_y):
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

        # Swipe UP (Mission Control / App Switcher)
        elif current_y < self.cam_h * 0.2:
            # On MacOS, Mission Control is usually 'ctrl', 'up'
            pyautogui.hotkey('ctrl', 'up')
            self.last_swipe_time = time.time()
            return "Swipe Up (Mission Control)"
        
        return None