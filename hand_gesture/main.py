import time
import cv2
import mediapipe as mp
import pyautogui

from gestureEngine import GestureEngine
from mouseControl import MouseController
from utils import Utils

CAM_W, CAM_H = 640, 480
SCREEN_W, SCREEN_H = pyautogui.size()

# Performance Tuners
pyautogui.PAUSE = 0           # Remove lag
SMOOTHING_FACTOR = 2          # Lower = faster, Higher = smoother
MARGIN = 100                  # Box margin for mouse movement
SCROLL_SENSITIVITY = 35       # Pixels per scroll step
ZOOM_THRESHOLD = 0.05         # Threshold to detect pinch open/close
SWIPE_THRESHOLD = 50          # Pixels needed to trigger a swipe

# MacOS:
KEY_ZOOM_IN = 'command', '+'
KEY_ZOOM_OUT = 'command', '-'
KEY_SWIPE_LEFT = 'ctrl', 'left'
KEY_SWIPE_RIGHT = 'ctrl', 'right'


def main():
    engine = GestureEngine(model_path="./gesture_recognizer.task")
    mouse = MouseController(smooting_factor=SMOOTHING_FACTOR, margin=MARGIN, cam_w=CAM_W, cam_h=CAM_H, screen_w=SCREEN_W, screen_h=SCREEN_H, key_zoom_in=KEY_ZOOM_IN, key_swipe_left=KEY_SWIPE_LEFT, key_swipe_right=KEY_SWIPE_RIGHT)
    cap = cv2.VideoCapture(0)
    cap.set(3, CAM_W)
    cap.set(4, CAM_H)

    print("--- STARTING SMART TRACKPAD ---")
    print("1 Finger:  Move Cursor (Pinch to Click)")
    print("2 Fingers: Scroll (Move Up/Down) OR Zoom (Pinch In/Out)")
    print("3+ Fingers: Swipe (Move Left/Right)")

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success: continue

            # Pre-process
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Async Recognition
            engine.process_frame(int(time.time() * 1000), mp_image)
            
            # Logic Layer
            landmarks = engine.get_landmarks()
            status_text = "Idle"
            
            h, w, _ = frame.shape

            if landmarks:
                # Detect Mode
                fingers_up = engine.count_fingers_up(landmarks)
                
                # Get coordinates for key points (in pixels)
                index_x = landmarks[8].x * CAM_W
                index_y = landmarks[8].y * CAM_W

                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                middle_tip = landmarks[12]

                # cursor mode
                if fingers_up <= 1:
                    status_text = "Cursor Mode"
                    mouse.move_cursor(index_x, index_y)
                    
                    dist = Utils.calc_distance(index_tip, thumb_tip)
                    if dist < 0.05:
                        mouse.left_click()
                        cv2.circle(frame, (int(index_x), int(index_y)), 15, (0, 255, 0), -1)

                # scroll & zoom modde
                elif fingers_up == 2:
                    # Calculate distance between Index and Middle finger
                    im_dist = Utils.calc_distance(index_tip, middle_tip)
                    
                    # perform zoom
                    zoom_action = mouse.perform_zoom(im_dist)
                    
                    if zoom_action:
                        status_text = zoom_action
                    else:
                        # scroll action
                        avg_y = (index_tip.y + middle_tip.y) / 2 * CAM_H
                        mouse.perform_scroll(avg_y)
                        status_text = "Scroll Mode"

                # swipe
                elif fingers_up >= 3:
                    hand_x = landmarks[0].x * CAM_W
                    hand_y = landmarks[0].y * CAM_H
                    action = mouse.perform_swipe(hand_x,hand_y)
                    if action:
                        status_text = action
                    else:
                        status_text = "Swipe Mode (Move to Edges)"

                # visualization for hand gesture
                for lm in landmarks:
                    cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 5, (255, 0, 0), -1)

            # draw status box
            cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), -1)
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # draw active area box
            cv2.rectangle(frame, (MARGIN, MARGIN), (CAM_W - MARGIN, CAM_H - MARGIN), (255, 255, 255), 1)

            cv2.imshow("Smart Air Trackpad", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()