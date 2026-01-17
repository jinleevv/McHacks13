import cv2
import json
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ----------------------------
# Gesture Utilities
# ----------------------------
GESTURE_FILE = "gestures.json"

def load_gestures():
    try:
        with open(GESTURE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_gestures(data):
    with open(GESTURE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def normalize_landmarks(landmarks):
    coords = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])

    # Wrist as origin
    coords -= coords[0]

    # Scale normalization
    scale = np.max(np.linalg.norm(coords, axis=1))
    if scale > 0:
        coords /= scale

    return coords.flatten()

def recognize_gesture(landmarks, gestures, threshold=0.28):
    if not gestures:
        return None

    current = normalize_landmarks(landmarks)
    best_name = None
    best_score = float("inf")

    for name, ref in gestures.items():
        ref = np.array(ref)
        score = np.linalg.norm(current - ref)
        if score < best_score:
            best_score = score
            best_name = name

    return best_name if best_score < threshold else None

# ----------------------------
# MediaPipe Setup
# ----------------------------
model_path = "hand_landmarker.task"

BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

landmarker = HandLandmarker.create_from_options(options)

# ----------------------------
# Camera
# ----------------------------
cap = cv2.VideoCapture(0)
gestures = load_gestures()
recognition_enabled = True
timestamp = 0
recognized_name = ""

print("Controls:")
print("  S - Save gesture")
print("  R - Toggle recognition")
print("  ESC - Quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = landmarker.detect_for_video(mp_image, timestamp)
    timestamp += 1

    if result.hand_landmarks:
        landmarks = result.hand_landmarks[0]

        # Draw landmarks
        h, w, _ = frame.shape
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # Recognition
        if recognition_enabled:
            name = recognize_gesture(landmarks, gestures)
            if name:
                recognized_name = name

    # UI text
    cv2.putText(frame, f"Gesture: {recognized_name}",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 255), 2)

    cv2.putText(frame, "[S] Save  [R] Recognize ON/OFF  [ESC] Quit",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Hand Gesture Recorder + Recognizer", frame)

    key = cv2.waitKey(1) & 0xFF

    # Save gesture
    if key == ord('s') and result.hand_landmarks:
        name = input("Enter gesture name: ")
        gestures[name] = normalize_landmarks(result.hand_landmarks[0]).tolist()
        save_gestures(gestures)
        print(f"Saved gesture '{name}'")

    # Toggle recognition
    if key == ord('r'):
        recognition_enabled = not recognition_enabled
        recognized_name = ""

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
