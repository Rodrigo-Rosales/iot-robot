import paho.mqtt.client as mqtt
import base64
import numpy as np
import cv2
import os
import threading
from collections import deque
import time

# Configuración
MQTT_BROKER = "localhost"
MQTT_TOPIC = "robot/camera"
OUTPUT_DIR = "capturas_roboflow"
BUFFER_SIZE = 3  # Frames en buffer

# Variables globales
frame_buffer = deque(maxlen=BUFFER_SIZE)
save_flag = False
lock = threading.Lock()

def on_message(client, userdata, msg):
    try:
        img_data = base64.b64decode(msg.payload)
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        with lock:
            frame_buffer.append(img)
            
    except Exception as e:
        print(f"Error procesando imagen: {str(e)}")

def save_current_frame():
    global save_flag
    while True:
        if save_flag and frame_buffer:
            with lock:
                frame = frame_buffer[-1]  # Toma el frame más reciente
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{OUTPUT_DIR}/captura_{timestamp}.jpg"
                
                if not cv2.imwrite(filename, frame):
                    print(f"Error guardando {filename}")
                else:
                    print(f"Imagen guardada: {filename}")
                    
            save_flag = False
        time.sleep(0.01)

def setup():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883)
    client.subscribe(MQTT_TOPIC)
    
    # Hilo para guardar imágenes
    saver_thread = threading.Thread(target=save_current_frame, daemon=True)
    saver_thread.start()
    
    return client

if __name__ == "__main__":
    client = setup()
    client.loop_start()
    
    print("Sistema listo. Presione:")
    print("  [s] Guardar imagen actual")
    print("  [q] Salir")
    
    try:
        while True:
            key = cv2.waitKey(100) & 0xFF
            
            if key == ord('s'):
                if frame_buffer:
                    save_flag = True
                else:
                    print("No hay frames disponibles")
                    
            elif key == ord('q'):
                break
                
            # Mostrar vista previa
            if frame_buffer:
                cv2.imshow("Vista Previa (Último Frame)", frame_buffer[-1])
                
    finally:
        client.loop_stop()
        cv2.destroyAllWindows()
        print("Sistema detenido")