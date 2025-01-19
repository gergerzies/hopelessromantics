import cv2
import numpy as np
import pyautogui
import mediapipe as mp

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Load the filter image (e.g., sunglasses) with an alpha channel (transparent background)
filter_img = cv2.imread("images/ANIME-BLUSH-PNG.png", cv2.IMREAD_UNCHANGED)

def apply_filter(frame, x, y, w, h):
    """Apply a filter (e.g., sunglasses) over the detected face."""
    filter_resized = cv2.resize(filter_img, (w, int(w * filter_img.shape[0] / filter_img.shape[1])))
    for i in range(filter_resized.shape[0]):
        for j in range(filter_resized.shape[1]):
            if filter_resized[i, j, 3] > 0:  # Check the alpha channel
                if 0 <= y + i < frame.shape[0] and 0 <= x + j < frame.shape[1]:
                    frame[y + i, x + j] = filter_resized[i, j, :-1]

# Define the region to capture (adjust this for your Google Meet window)
region = (100, 100, 800, 600)  # (left, top, width, height)

# Open MediaPipe Face Detection
with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
    while True:
        # Capture the screen region
        screenshot = pyautogui.screenshot(region=region)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Process the frame with MediaPipe
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Draw detections and apply filter
        if results.detections:
            for detection in results.detections:
                # Get bounding box coordinates
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                # Apply the filter
                apply_filter(frame, x, y, w, h)

                # Optional: Draw bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Google Meet with Filters", frame)

        # Exit with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
