# laptop_receiver.py
import cv2
import socket
import pickle
import struct
import torch
from ultralytics import YOLO

# Configuración YOLOv8
model = YOLO("best.pt")  # Tu modelo entrenado
model.conf = 0.25  # Umbral bajo para balones lejanos
model.iou = 0.45   # Balance precisión-recall

# Configuración de red
HOST = '0.0.0.0'  # Escuchar en todas las interfaces
PORT = 5000

# Inicialización socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"🖥️ Servidor escuchando en {HOST}:{PORT}")

conn, addr = server_socket.accept()
data = b""
payload_size = struct.calcsize("Q")

try:
    while True:
        # Recibir frame
        while len(data) < payload_size:
            packet = conn.recv(4*1024)  # Buffer de 4KB
            if not packet: break
            data += packet
        
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += conn.recv(4*1024)
        
        frame_data = data[:msg_size]
        data = data[msg_size:]
        
        # Deserializar
        buffer = pickle.loads(frame_data)
        frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        
        # Detección (optimizado para velocidad)
        results = model(frame, imgsz=480, stream=True)  # Usar mismo tamaño que entrenamiento
        
        # Mostrar resultados
        annotated_frame = results[0].plot()  # Frame con detecciones
        cv2.imshow("Detección en Tiempo Real", annotated_frame)
        
        # Performance metrics
        fps = 1.0 / (time.time() - start_time)
        cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    conn.close()
    cv2.destroyAllWindows()