# pc_code/detection/detector.py

from ultralytics import YOLO
import cv2
import time
import torch
from config import MODEL_PATH, CONFIDENCE_THRESHOLD, FRAME_WIDTH, FRAME_HEIGHT

class Detector:
    def __init__(self):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        print(f"[DETECTOR] Usando dispositivo: {self.device}")
        self.model = YOLO(MODEL_PATH).to(self.device)

        self.frame_center_x = FRAME_WIDTH // 2
        self.frame_center_y = FRAME_HEIGHT // 2
        self.area_near_threshold = 30000
        self.area_far_threshold = 5000
        self.margin_x = 50

    def detect(self, frame):
        start_time_total = time.time()

        # Convertir el frame de OpenCV (BGR) a RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor_frame = torch.from_numpy(rgb_frame).permute(2, 0, 1).float().unsqueeze(0).to(self.device)

        # Normalizar el tensor al rango 0.0-1.0
        normalized_tensor = tensor_frame / 255.0

        # Realizar la predicción
        results = self.model.predict(source=normalized_tensor, conf=CONFIDENCE_THRESHOLD, save=False, verbose=False)
        inference_time = time.time() - start_time_total
        annotated = results[0].plot()  # Annotated frame (RGB)

        boxes = results[0].boxes
        error_x = None
        error_y = None
        area = None
        bbox_info = None

        if boxes:
            best_box = None
            max_confidence = -1
            for box in boxes:
                confidence = box.conf[0].item()
                if confidence > max_confidence:
                    max_confidence = confidence
                    best_box = box

            if best_box is not None:
                x1, y1, x2, y2 = map(int, best_box.xyxy[0].tolist())
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

                # Dibujar bbox (esto es opcional porque .plot() ya lo hace)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # FPS (calculado al final de la función detect)
        fps = 1.0 / (time.time() - start_time_total)
        cv2.putText(annotated, f"FPS (detect): {fps:.1f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        print(f"[DETECTOR] Tiempo de inferencia: {inference_time:.3f} segundos")

        # Convertir de nuevo a BGR para OpenCV
        bgr_annotated = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

        yield bgr_annotated, error_x, error_y, area, bbox_info
