import cv2
import numpy as np
import base64
import paho.mqtt.client as mqtt
from inference_sdk import InferenceHTTPClient
from collections import deque
import threading
import time

# ================= CONFIGURACIÓN =================
MQTT_BROKER = "192.168.18.2"  # IP de la Raspberry
MQTT_TOPIC = "robot/camera"
MAX_FPS = 15
RESOLUTION = (320, 240)

# Configuración de Roboflow
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="jjVaPG6AhMyJS4GocOpG"
)
MODEL_ID = "basketball-1zhpe/1"

# Variables de estado
frame_buffer = deque(maxlen=1)
lock = threading.Lock()
tracking_history = deque(maxlen=5)  
last_frame_time = time.time()

def on_message(client, userdata, msg):
    """Procesa la imagen recibida desde MQTT."""
    try:
        img_data = base64.b64decode(msg.payload)
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is not None:
            img = cv2.resize(img, RESOLUTION)
            with lock:
                frame_buffer.clear()
                frame_buffer.append(img)
    except Exception as e:
        print(f"Error al procesar imagen MQTT: {e}")

def analyze_movement(current_pos):
    """Analiza el movimiento con base en las últimas posiciones registradas."""
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

def process_frames():
    """Procesa los frames en tiempo real y muestra las detecciones."""
    global last_frame_time
    
    while True:
        elapsed = time.time() - last_frame_time
        frame_delay = 1.0 / MAX_FPS
        if elapsed < frame_delay:
            time.sleep(frame_delay - elapsed)
            continue
        
        last_frame_time = time.time()
        if not frame_buffer:
            continue
        
        try:
            with lock:
                img = frame_buffer[-1].copy()
            
            _, img_encoded = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 60])
            result = CLIENT.infer(
                base64.b64encode(img_encoded).decode('utf-8'),
                model_id=MODEL_ID
            )
            
            if result and 'predictions' in result and result['predictions']:
                best_pred = max(result['predictions'], key=lambda x: x['confidence'])
                x, y = int(best_pred['x']), int(best_pred['y'])
                w, h = int(best_pred['width']), int(best_pred['height'])
                movement = analyze_movement({'x': x, 'y': y})

                # Dibujar detección
                cv2.rectangle(img, (x-w//2, y-h//2), (x+w//2, y+h//2), (0, 255, 0), 2)
                cv2.putText(img, f"Conf: {best_pred['confidence']:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 1)
                cv2.putText(img, f"Mov: {movement}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 1)

            # Mostrar frame
            cv2.imshow("Deteccion Baloncesto", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error en procesamiento: {e}")

def main():
    print("Iniciando sistema de detección...")

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, keepalive=60)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()

    processing_thread = threading.Thread(target=process_frames, daemon=True)
    processing_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo sistema...")
    finally:
        cv2.destroyAllWindows()
        client.disconnect()

if __name__ == "__main__":
    main()
