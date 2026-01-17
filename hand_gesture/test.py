import cv2
import mediapipe as mp
import time

MODEL_FILE = 'gesture_recognizer.task'
MODEL_URL = '/Users/jinwonlee/Github/McHacks13/gesture_recognizer.task'

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Global variable to store the latest result
current_result = None

# Callback function to handle the result asynchronously
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global current_result
    current_result = result

# Create the options
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_FILE),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result,
    num_hands=2
)

def main():
    cap = cv2.VideoCapture(0) # 0 is usually the built-in webcam

    with GestureRecognizer.create_from_options(options) as recognizer:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Convert the image from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # Send the image to the recognizer (requires timestamp in ms)
            timestamp_ms = int(time.time() * 1000)
            recognizer.recognize_async(mp_image, timestamp_ms)

            # visualization
            # If we have a result, draw it
            if current_result and current_result.gestures:
                # Get the top gesture (highest score)
                top_gesture = current_result.gestures[0][0]
                category_name = top_gesture.category_name
                score = top_gesture.score

                # Draw the text on the frame
                text = f"Gesture: {category_name} ({score:.2f})"
                cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 255, 0), 2, cv2.LINE_AA)

                # Optional: Draw landmarks (skeleton)
                if current_result.hand_landmarks:
                    for hand_landmarks in current_result.hand_landmarks:
                        # Draw points (simple visualization)
                        for landmark in hand_landmarks:
                            h, w, _ = frame.shape
                            cx, cy = int(landmark.x * w), int(landmark.y * h)
                            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

            # Show the frame
            cv2.imshow('MediaPipe Gesture Recognition', frame)

            # Exit on pressing 'q' or 'ESC'
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()