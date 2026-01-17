import cv2
import mediapipe as mp
import time

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index Finger
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle Finger
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring Finger
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Wrist to Pinky Base
]

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# UPDATE THIS PATH to point to your actual .task file
MODEL_PATH = '/Users/jinwonlee/Github/McHacks13/hand_gesture/gesture_recognizer.task'

current_result = None

def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global current_result
    current_result = result

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result,
    num_hands=2  # Detect up to 2 hands
)

def main():
    cap = cv2.VideoCapture(0)

    with GestureRecognizer.create_from_options(options) as recognizer:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue

            # MediaPipe needs RGB, OpenCV uses BGR
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # Run detection
            timestamp_ms = int(time.time() * 1000)
            recognizer.recognize_async(mp_image, timestamp_ms)

            # draw the skeleton
            if current_result and current_result.hand_landmarks:
                height, width, _ = frame.shape
                
                # Loop through every detected hand
                for hand_landmarks in current_result.hand_landmarks:
                    
                    # 1. Convert normalized (0-1) landmarks to pixel (x,y) coordinates
                    points = []
                    for lm in hand_landmarks:
                        cx, cy = int(lm.x * width), int(lm.y * height)
                        points.append((cx, cy))

                    # 2. Draw Lines (The Skeleton)
                    for start_idx, end_idx in HAND_CONNECTIONS:
                        if start_idx < len(points) and end_idx < len(points):
                            # Draw a white line with thickness 2
                            cv2.line(frame, points[start_idx], points[end_idx], (255, 255, 255), 2)

                    # 3. Draw Dots (The Joints)
                    for point in points:
                        # Draw a blue dot
                        cv2.circle(frame, point, 5, (255, 0, 0), -1)

            # Draw Gesture Name (if any)
            if current_result and current_result.gestures:
                top_gesture = current_result.gestures[0][0]
                text = f"{top_gesture.category_name} ({top_gesture.score:.2f})"
                cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow('Gesture Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()