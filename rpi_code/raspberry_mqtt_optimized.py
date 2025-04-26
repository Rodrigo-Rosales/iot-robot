# raspberry_mqtt_optimized.py
import cv2
import numpy as np
import paho.mqtt.client as mqtt
import time

# Config
BROKER_IP = "192.168.1.100"
TOPIC = "camera/stream"
FPS = 25
IMGSZ = (480, 480)  # Balance calidad-rendimiento

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER_IP)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMGSZ[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMGSZ[1])
cap.set(cv2.CAP_PROP_FPS, FPS)

# Compresión optimizada
encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]  # Calidad media-alta

try:
    while True:
        ret, frame = cap.read()
        if not ret: continue
        
        # Reducción de tamaño SIN base64 (envío binario directo)
        _, jpeg = cv2.imencode('.jpg', frame, encode_params)
        
        # Publicación asíncrona (non-blocking)
        client.publish(TOPIC, jpeg.tobytes(), qos=1)
        
        time.sleep(1/FPS)  # Control FPS preciso

finally:
    cap.release()
    client.disconnect()