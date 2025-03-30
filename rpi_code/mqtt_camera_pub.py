import cv2
import base64
import paho.mqtt.publish as publish
import time

# Configuración (reemplaza con la IP laptop)
MQTT_BROKER = "192.168.18.1"
MQTT_TOPIC = "robot/camera"

def capture_and_send():
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (320, 240))
                _, img_encoded = cv2.imencode('.jpg', frame)
                img_base64 = base64.b64encode(img_encoded).decode('utf-8')
                publish.single(
                    MQTT_TOPIC,
                    payload=img_base64,
                    hostname=MQTT_BROKER
                )
                print("Imagen enviada")
            time.sleep(0.1)
    except KeyboardInterrupt:
        cap.release()

if __name__ == "__main__":
    capture_and_send()