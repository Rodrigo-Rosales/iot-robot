import paho.mqtt.client as mqtt
import base64
import numpy as np
import cv2
import json
import requests  # Para Roboflow (se usará después)
import time
frame_count = 0
start_time = time.time()

def on_message(client, userdata, msg):
    global frame_count
    frame_count += 1
    if frame_count % 30 == 0:
        fps = frame_count / (time.time() - start_time)
        print(f"FPS recibidos: {fps:.2f}")
    # ... resto del código ...

# Configuración MQTT
MQTT_BROKER = "localhost"
MQTT_TOPIC = "robot/camera"

# Configuración de visualización
WINDOW_NAME = "Video from RPi"

def on_message(client, userdata, msg):
    try:
        # Decodificar imagen
        img_base64 = msg.payload.decode('utf-8')
        img_bytes = base64.b64decode(img_base64)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Mostrar imagen (opcional, para debug)
        cv2.imshow(WINDOW_NAME, img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            client.disconnect()
        
        # --- Aquí se integrará Roboflow después ---
        # processed_img = process_with_roboflow(img)
        
    except Exception as e:
        print(f"Error: {e}")

def setup_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883)
    client.subscribe(MQTT_TOPIC)
    return client

if __name__ == "__main__":
    print("Esperando imágenes... (Presiona 'q' para salir)")
    client = setup_mqtt()
    client.loop_forever()