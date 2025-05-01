# pc_code/detection/detector.py

from ultralytics import YOLO
import cv2
import time
from config import MODEL_PATH, CONFIDENCE_THRESHOLD, FRAME_WIDTH, FRAME_HEIGHT

class Detector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
        self.frame_center_x = FRAME_WIDTH // 2
        self.frame_center_y = FRAME_HEIGHT // 2
        self.area_near_threshold = 30000
        self.area_far_threshold = 5000
        self.margin_x = 50

    def detect(self, frame):
        start_time = time.time()
        results = self.model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, save=False, verbose=False)
        annotated = results[0].plot()

        boxes = results[0].boxes
        error_x = None
        error_y = None
        area = None
        bbox_info = None

        if boxes:
            best_box = max(boxes, key=lambda b: b.conf[0].item())
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2
            width = x2 - x1
            height = y2 - y1
            area = width * height
            error_x = x_center - self.frame_center_x
            error_y = y_center - self.frame_center_y
            bbox_info = {
                'x_center': x_center,
                'y_center': y_center,
                'width': width,
                'height': height,
                'area': area,
                'error_x': error_x,
                'error_y': error_y
            }

            # Dibujar bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # FPS
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        yield annotated, error_x, error_y, area, bbox_info