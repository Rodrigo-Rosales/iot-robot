# pc_code/detection/detector.py

from ultralytics import YOLO
import cv2
import time
from pc_code.config import MODEL_PATH, CONFIDENCE_THRESHOLD, FRAME_WIDTH

class Detector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
        self.frame_center_x = FRAME_WIDTH // 2
        self.area_near_threshold = 30000
        self.area_far_threshold = 5000
        self.margin_x = 50

    def get_instruction(self, x_center, area):
        if area > self.area_near_threshold:
            return "RETROCEDER"
        elif area < self.area_far_threshold:
            return "AVANZAR"
        elif x_center < self.frame_center_x - self.margin_x:
            return "GIRAR IZQUIERDA"
        elif x_center > self.frame_center_x + self.margin_x:
            return "GIRAR DERECHA"
        else:
            return "ADELANTE RECTO"

    def detect(self, frame):
        start_time = time.time()
        results = self.model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, save=False, verbose=False)
        annotated = results[0].plot()

        boxes = results[0].boxes
        instruction = None

        if boxes:
            best_box = max(boxes, key=lambda b: b.conf[0].item())
            x1, y1, x2, y2 = map(int, best_box.xyxy[0])
            x_center = (x1 + x2) // 2
            area = (x2 - x1) * (y2 - y1)
            instruction = self.get_instruction(x_center, area)

            # Dibujar bbox e instrucción
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, instruction, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

        # FPS
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return annotated, instruction