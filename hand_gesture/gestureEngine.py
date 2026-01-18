import math
import mediapipe as mp

class GestureEngine:
    def __init__(self, model_path):
        # config the gesture model
        self.mp_options = mp.tasks.vision.GestureRecognizerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
            result_callback=self.result_callback,
            num_hands=2
        )
        self.recognizer = mp.tasks.vision.GestureRecognizer.create_from_options(self.mp_options)
        self.latest_result = None

    def result_callback(self, result, image, timestamp):
        self.latest_result = result

    def process_frame(self, frame_timestamp_ms, mp_image):
        self.recognizer.recognize_async(mp_image, frame_timestamp_ms)

    def get_landmarks(self):
        if self.latest_result and self.latest_result.hand_landmarks:
            return self.latest_result.hand_landmarks
        return []
    
    def is_pinching(self, landmarks):
        """Checks if Thumb and Index finger are touching."""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        dist = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
        return dist < 0.05

    def count_fingers_up(self, landmarks):
        """Returns the number of fingers extended."""
        # https://mediapipe.readthedocs.io/en/latest/solutions/hands.html
        # check the numberings for specific finger config
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        up_count = 0
        
        # check 4 fingers (excluding thumb for simplicity in mode switching)
        for tip, pip in zip(tips, pips):
            if landmarks[tip].y < landmarks[pip].y:
                up_count += 1
                
        return up_count