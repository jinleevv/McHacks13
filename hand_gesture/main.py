import time
import cv2
import mediapipe as mp
import pyautogui
import threading

# Your custom modules
from gestureEngine import GestureEngine
from mouseControl import MouseController
from utils import Utils
from flask import Flask, Response

# --- CONFIGURATION ---
CAM_W, CAM_H = 640, 480
SCREEN_W, SCREEN_H = pyautogui.size()

# Performance Tuners
pyautogui.PAUSE = 0
SMOOTHING_FACTOR = 2
MARGIN = 100
SCROLL_SENSITIVITY = 35
ZOOM_THRESHOLD = 0.05
SWIPE_THRESHOLD = 50

# Key Mappings
KEY_ZOOM_IN = ('command', '+')  # Adjusted for tuple unpacking if needed
KEY_ZOOM_OUT = ('command', '-')
KEY_SWIPE_LEFT = ('ctrl', 'left')
KEY_SWIPE_RIGHT = ('ctrl', 'right')

# --- FLASK SETUP ---
app = Flask(__name__)

# --- GLOBAL STATE ---
output_frame = None
lock = threading.Lock()


def run_gesture_logic():
    """
    Background thread that handles Camera, Gesture Recognition,
    Mouse Control, and Drawing.
    """
    global output_frame, lock

    # Initialize Logic Components
    # Note: Ensure paths to .task files are correct relative to where you run this script
    engine = GestureEngine(model_path="./gesture_recognizer.task")
    mouse = MouseController(
        smooting_factor=SMOOTHING_FACTOR,
        margin=MARGIN,
        cam_w=CAM_W,
        cam_h=CAM_H,
        screen_w=SCREEN_W,
        screen_h=SCREEN_H,
        key_zoom_in=KEY_ZOOM_IN,
        key_swipe_left=KEY_SWIPE_LEFT,
        key_swipe_right=KEY_SWIPE_RIGHT
    )

    cap = cv2.VideoCapture(0)
    cap.set(3, CAM_W)
    cap.set(4, CAM_H)

    print("--- STARTING SMART TRACKPAD (BACKGROUND) ---")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        # 1. Pre-process
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # 2. Async Recognition
        engine.process_frame(int(time.time() * 1000), mp_image)

        # 3. Logic Layer
        landmarks = engine.get_landmarks()
        status_text = "Idle"
        h, w, _ = frame.shape

        if landmarks:
            fingers_up = engine.count_fingers_up(landmarks)

            # Key points
            index_x = landmarks[8].x * CAM_W
            index_y = landmarks[8].y * CAM_W  # Note: check if this should be CAM_H or CAM_W (usually y * H)

            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]

            # --- Cursor Mode ---
            if fingers_up <= 1:
                status_text = "Cursor Mode"
                mouse.move_cursor(index_x, index_y)

                dist = Utils.calc_distance(index_tip, thumb_tip)
                if dist < 0.05:
                    mouse.left_click()
                    cv2.circle(frame, (int(index_x), int(index_y)), 15, (0, 255, 0), -1)

            # --- Scroll & Zoom Mode ---
            elif fingers_up == 2:
                im_dist = Utils.calc_distance(index_tip, middle_tip)
                zoom_action = mouse.perform_zoom(im_dist)

                if zoom_action:
                    status_text = zoom_action
                else:
                    avg_y = (index_tip.y + middle_tip.y) / 2 * CAM_H
                    mouse.perform_scroll(avg_y)
                    status_text = "Scroll Mode"

            # --- Swipe Mode ---
            elif fingers_up >= 3:
                hand_x = landmarks[0].x * CAM_W
                hand_y = landmarks[0].y * CAM_H
                action = mouse.perform_swipe(hand_x, hand_y)
                if action:
                    status_text = action
                else:
                    status_text = "Swipe Mode"

            # --- Visualization ---
            for lm in landmarks:
                cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 5, (255, 0, 0), -1)

        # 4. Draw UI
        cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), -1)
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.rectangle(frame, (MARGIN, MARGIN), (CAM_W - MARGIN, CAM_H - MARGIN), (255, 255, 255), 1)

        # 5. Update Global Frame for Flask
        with lock:
            output_frame = frame.copy()

    cap.release()


def generate_frames():
    """Generator function for Flask to stream video."""
    global output_frame, lock

    while True:
        with lock:
            if output_frame is None:
                continue

            # Encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue

        # Yield the output frame in the byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

        # Adding a tiny sleep prevents the generator from hogging CPU if no new frame is ready
        time.sleep(0.01)


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/")
def index():
    return """
    <html>
        <head><title>Gesture Test</title></head>
        <body>
            <h1>Gesture Control Backend is Running!</h1>
            <p>If you see this text, the Flask server is up.</p>
            <p>Below is the raw video feed that Electron will see:</p>
            <img src="/video_feed" width="640" height="480" style="border: 2px solid black;">
        </body>
    </html>
    """


if __name__ == "__main__":
    # Start the Gesture Logic in a separate daemon thread
    t = threading.Thread(target=run_gesture_logic)
    t.daemon = True  # Ensures thread dies when main program exits
    t.start()

    # Start Flask Server
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)