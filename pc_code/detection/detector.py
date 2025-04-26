# pc_code/detection/detector.py

from ultralytics import YOLO
import cv2
from config import MODEL_PATH, CONFIDENCE_THRESHOLD

class Detector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)

    def detect(self, frame):
        results = self.model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, save=False, verbose=False)
        annotated = results[0].plot()
        return annotated, results[0]