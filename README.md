### Quick Start Guide
1. Install all the dependencies:
- `pip install -r requirements.txt`
2. Navigate to the backend and start the server:
- `cd backend/`
- `python main.py`
3. Navigate to the frontend and launch the frontend:
- `cd ../frontend/`
- `yarn install` to install the node packages
- `yarn run start` to start electron

### Inspiration
Jarvis from Iron Man was our chief inspiration. Tony Stark (Iron Man) uses J.A.R.V.I.S to interact with holograms. This sparked our idea to explore hands-free interaction with everyday devices. Real life problems such as not wanting to touch our laptops during a cooking session highlighted a practical need for gesture-based control. 
### What it does
Our version of Jarvis allows for control over your screen through hand gesture detection. 
Users can navigate around their system without the need of a mouse or trackpad.
### How we built it
We built our system using MediaPipe, Google’s AI-powered hand and gesture tracking framework. The gesture processing pipeline was integrated with Flask for backend communication and Electron to deliver a responsive desktop interface. Together, these technologies allowed us to create a real-time interactive control system.
### Challenges we ran into
MediaPipe’s file structure and APIs have undergone recent changes, making many existing tutorials outdated. Adapting to these updates required extensive debugging and experimentation. Additionally, designing an intuitive gesture system that balanced accuracy, responsiveness, and usability involved significant trial and error.
### Accomplishments that we're proud of
We successfully built a fully functional application that is usable in real-world scenarios today. Achieving smooth real-time tracking and system interaction within a limited development timeframe was a major achievement for our team.
### What we learned
This project introduced our team to several new technologies and concepts. We gained hands-on experience with Google’s computer vision tools, real-time gesture recognition, and vision processing pipelines. We also learned how to integrate Flask and Electron to create full-stack desktop applications.
### What's next for Jarvis?
Moving forward, we plan to focus on customization and personalization. Every user interacts with their system differently, so allowing users to define custom gestures and map them to specific actions will be a key feature. We also aim to improve recognition accuracy and provide gesture fine-tuning to better adapt to individual user preferences.
