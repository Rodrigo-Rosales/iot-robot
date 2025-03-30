import cv2
import base64
import paho.mqtt.publish as publish
import time

# Configuración MQTT
MQTT_BROKER = "IP_DE_LA_LAPTOP"  # Ej: "192.168.1.100"
MQTT_TOPIC = "robot/camera"

# Configuración de la cámara
CAMERA_WIDTH = 320  # Resolución óptima para 30 FPS
CAMERA_HEIGHT = 240
JPEG_QUALITY = 60   # Balance calidad-tamaño
TARGET_FPS = 30     # Objetivo de frames por segundo

def capture_and_send():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)  # Configura la cámara para ~30 FPS
    
    frame_interval = 1.0 / TARGET_FPS  # Intervalo entre frames (segundos)
    
    try:
        while True:
            start_time = time.time()
            
            ret, frame = cap.read()
            if ret:
                # Compresión y codificación
                _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                img_base64 = base64.b64encode(img_encoded).decode('utf-8')
                
                # Envío MQTT (QoS 0 para mínima latencia)
                publish.single(
                    MQTT_TOPIC,
                    payload=img_base64,
                    hostname=MQTT_BROKER,
                    port=1883,
                    qos=0
                )
                print(f"Imagen enviada. Tamaño: {len(img_base64)} bytes")
            
            # Control preciso de FPS
            elapsed_time = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed_time)
            time.sleep(sleep_time)  # Ajusta dinámicamente
            
    except KeyboardInterrupt:
        print("Deteniendo la cámara...")
    finally:
        cap.release()

if __name__ == "__main__":
    capture_and_send()