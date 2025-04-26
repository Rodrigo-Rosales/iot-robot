import cv2
import numpy as np
import base64
import time
from inference_sdk import InferenceHTTPClient

# Configuración de Roboflow
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="jjVaPG6AhMyJS4GocOpG"
)
MODEL_ID = "basketball-1zhpe/1"

# Parámetros de la cámara
CAMERA_INDEX = 0  # Cambia a 1 si tienes otra cámara
RESOLUTION = (320, 240)  # Tamaño de imagen
MAX_FPS = 15  # Control de FPS

# Historial de tracking
tracking_history = []

def analyze_movement(current_pos):
    """Analiza el movimiento con base en la posición previa"""
    if not tracking_history:
        tracking_history.append(current_pos)
        return "Calculando..."
    
    prev_pos = tracking_history[-1]
    dx, dy = current_pos['x'] - prev_pos['x'], current_pos['y'] - prev_pos['y']

    movement = []
    if abs(dx) > 5:
        movement.append("IZQ" if dx < 0 else "DER")
    if abs(dy) > 5:
        movement.append("ARR" if dy < 0 else "ABA")

    tracking_history.append(current_pos)
    return " ".join(movement) if movement else "ESTABLE"

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION[1])

    last_frame_time = time.time()

    while True:
        elapsed = time.time() - last_frame_time
        frame_delay = 1.0 / MAX_FPS
        if elapsed < frame_delay:
            time.sleep(frame_delay - elapsed)
            continue
        
        last_frame_time = time.time()

        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo capturar frame")
            continue

        # Redimensionar imagen
        frame_resized = cv2.resize(frame, RESOLUTION)

        try:
            # Convertir a base64 para Roboflow
            _, img_encoded = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 60])
            result = CLIENT.infer(
                base64.b64encode(img_encoded).decode('utf-8'),
                model_id=MODEL_ID
            )

            # Dibujar detecciones
            if result and 'predictions' in result and result['predictions']:
                best_pred = max(result['predictions'], key=lambda x: x['confidence'])
                x, y = int(best_pred['x']), int(best_pred['y'])
                w, h = int(best_pred['width']), int(best_pred['height'])
                movement = analyze_movement({'x': x, 'y': y})

                cv2.rectangle(frame_resized, (x-w//2, y-h//2), (x+w//2, y+h//2), (0, 255, 0), 2)
                cv2.putText(frame_resized, f"Conf: {best_pred['confidence']:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 1)
                cv2.putText(frame_resized, f"Mov: {movement}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 1)

            # Mostrar resultado
            cv2.imshow("Detección en Tiempo Real", frame_resized)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error en procesamiento: {e}")
            time.sleep(0.1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
