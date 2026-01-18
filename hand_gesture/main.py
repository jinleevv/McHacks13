import math
import os
import time
import cv2
import mediapipe as mp
import pyautogui
import threading

# Your custom modules
from gestureEngine import GestureEngine
from geminiVoiceAssistant import GeminiVoiceAssistant
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
    mouse = MouseController(smooting_factor=SMOOTHING_FACTOR, margin=MARGIN, cam_w=CAM_W, cam_h=CAM_H, screen_w=SCREEN_W, screen_h=SCREEN_H, key_zoom_in=KEY_ZOOM_IN, key_zoom_out=KEY_ZOOM_OUT, key_swipe_left=KEY_SWIPE_LEFT, key_swipe_right=KEY_SWIPE_RIGHT)
    voice_assistant = GeminiVoiceAssistant()
    cap = cv2.VideoCapture(0)
    cap.set(3, CAM_W)
    cap.set(4, CAM_H)

    print("--- STARTING SMART TRACKPAD (BACKGROUND) ---")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        # Pre-process Image (Frame)
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Process Image (Hand Recognition Model)
        engine.process_frame(int(time.time() * 1000), mp_image)

        # Handle Result
        landmarks = engine.get_landmarks()
        status_text = "Idle"
        h, w, _ = frame.shape

        if landmarks:
            hand1 = landmarks[0]
            if len(landmarks) == 2:
                hand2 = landmarks[1]
                if engine.is_pinching(hand1) and engine.is_pinching(hand2):
                    status_text = "Dual Zoom Mode"
                    x1, y1 = hand1[8].x * CAM_W, hand1[8].y * CAM_H
                    x2, y2 = hand2[8].x * CAM_W, hand2[8].y * CAM_H
                    hands_dist = math.hypot(x2 - x1, y2 - y1)
                    norm_dist = hands_dist / CAM_W
                        
                    zoom_result = mouse.perform_zoom(norm_dist)
                    if zoom_result: 
                        status_text = f"Dual: {zoom_result}"
                else:
                    mouse.zoom_anchor = None
                    status_text = "2 Hands (Open)"
                
            else: # most likely 1 hand
                
                if engine.latest_result and engine.latest_result.gestures:
                    # Get the top gesture (highest score)
                    top_gesture = engine.latest_result.gestures[0][0].category_name
                    if top_gesture == "ILoveYou":
                        voice_assistant.run()
                        engine.latest_result = None
                    elif top_gesture == "Thumb_Down":
                        os._exit(0)

                fingers_up = engine.count_fingers_up(hand1)

                #thumb_tip = hand1[4]
                index_tip = hand1[8]
                #middle_tip = hand1[12]

                index_tip_x_scaled = index_tip.x * CAM_W
                index_tip_y_scaled = index_tip.y * CAM_H

                # Cursor Mode
                if fingers_up <= 1:
                    if engine.is_pinching(hand1):
                        if mouse.pinch_start_time == 0:
                            mouse.pinch_start_time = time.time()

                        pinch_duration = time.time() - mouse.pinch_start_time

                        # vertical scroll
                        if pinch_duration > 0.4:
                            status_text = "Click & Hold: Scrolling"
                            mouse.perform_scroll(index_tip_y_scaled)
                            # Draw Scroll UI
                            cv2.circle(frame, (int(index_tip_x_scaled), int(index_tip_y_scaled)), 20, (255, 0, 0), 2)
                        else:
                            # building up to a scroll
                            status_text = "Pinching..."

                    # release pinch
                    else:
                        status_text = "Cursor Mode"
                        mouse.move_cursor(index_tip_x_scaled, index_tip_y_scaled)

                        # if was in a pinch previous frame
                        if mouse.pinch_start_time > 0:
                            pinch_duration = time.time() - mouse.pinch_start_time

                            # min click time threshold
                            # if you make it too small may click accidentally due to error in tracking
                            if pinch_duration <= 0.2:
                                mouse.left_click()
                                status_text = "Click"

                            mouse.pinch_start_time = 0
                            # reset scroll memory (if any)
                            mouse.prev_y = None  
                            mouse.scroll_anchor = None

                # Swipe Mode
                elif fingers_up >= 3:
                    hand_x = hand1[0].x * CAM_W
                    hand_y = hand1[0].y * CAM_H
                    action = mouse.perform_swipe(hand_x, hand_y)
                    if action:
                        status_text = action
                    else:
                        status_text = "Swipe Mode"


        #UI
            
        # Draw hands
        for hand_lms in landmarks:
            for lm in hand_lms:
                cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 5, (255, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), -1)
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.rectangle(frame, (MARGIN, MARGIN), (CAM_W - MARGIN, CAM_H - MARGIN), (255, 255, 255), 1)

        # Global Frame for Flask
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
    with open("index1.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Start the Gesture Logic in a separate daemon thread
    t = threading.Thread(target=run_gesture_logic)
    t.daemon = True  # Ensures thread dies when main program exits
    t.start()

    # Start Flask Server
    app.run(host="0.0.0.0", port=5174, debug=False, use_reloader=False)

