import cv2
import base64
import paho.mqtt.client as mqtt
import time

# ================= CONFIGURACIÓN =================
MQTT_BROKER = "192.168.18.2"   # IP de la laptop
MQTT_TOPIC_CAMERA = "robot/camera"
CAMERA_RESOLUTION = (320, 240)  # Resolución optimizada
JPEG_QUALITY = 70               # Balance calidad-tamaño (1-100)
TARGET_FPS = 30                 # Objetivo de frames por segundo

# ================= SETUP INICIAL =================
def setup_camera():
    """Configura la cámara con parámetros optimizados."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    return cap

def setup_mqtt():
    """Configura el cliente MQTT."""
    client = mqtt.Client()
    client.connect(MQTT_BROKER, port=1883, keepalive=60)
    return client

# ================= FUNCIONES PRINCIPALES =================
def capture_and_stream(client, camera):
    """Captura y envía frames continuamente vía MQTT."""
    frame_interval = 1.0 / TARGET_FPS
    
    try:
        while True:
            start_time = time.time()
            
            # 1. Captura del frame
            ret, frame = camera.read()
            if not ret:
                print("Error: No se pudo capturar frame")
                continue

            # 2. Codificación en JPEG y Base64
            _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            img_base64 = base64.b64encode(img_encoded).decode('utf-8')

            # 3. Publicación MQTT
            client.publish(MQTT_TOPIC_CAMERA, img_base64, qos=0)
            print(f"Frame enviado | Tamaño: {len(img_base64)} bytes", end='\r')

            # 4. Control de FPS
            elapsed = time.time() - start_time
            time.sleep(max(0, frame_interval - elapsed))
            
    except KeyboardInterrupt:
        print("\nDeteniendo transmisión...")
    finally:
        camera.release()
        client.disconnect()
        print("Recursos liberados correctamente.")

# ================= EJECUCIÓN =================
if __name__ == "__main__":
    camera = setup_camera()
    mqtt_client = setup_mqtt()
    
    try:
        capture_and_stream(mqtt_client, camera)
    finally:
        camera.release()
        mqtt_client.disconnect()