# raspberry_sender.py
import cv2
import socket
import pickle
import struct
import time

# Configuración de red
HOST = 'IP_DE_TU_LAPTOP'  # Cambiar por la IP local de tu laptop
PORT = 5000

# Inicialización cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 640x480 es suficiente para detección
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)  # Máximo FPS para la cámara

# Configuración del socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Comprimir imagen (calidad 80% para reducir tamaño)
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        
        # Serializar y enviar
        data = pickle.dumps(buffer, protocol=2)
        message = struct.pack("Q", len(data)) + data
        client_socket.sendall(message)
        
        # Opcional: Mostrar preview local (comentar para mejor rendimiento)
        cv2.imshow("RPi Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    client_socket.close()
    cv2.destroyAllWindows()