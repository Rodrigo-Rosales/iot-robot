# pc_code/receiver/image_receiver.py

import socket
import struct
import cv2
import numpy as np
from config import PC_IP, PC_PORT_VIDEO, FRAME_WIDTH, FRAME_HEIGHT

def receive_frames():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((PC_IP, PC_PORT_VIDEO))
    server_socket.listen(1)
    print(f"[INFO] Esperando conexión en {PC_IP}:{PC_PORT_VIDEO}...")
    connection, client_address = server_socket.accept()
    print(f"[INFO] Conexión establecida con {client_address}")
    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Deshabilitar Nagle
    try:
        while True:
            size_bytes = connection.recv(4)
            if not size_bytes:
                break
            frame_size = struct.unpack(">L", size_bytes)[0]
            frame_data = b""
            while len(frame_data) < frame_size:
                part = connection.recv(4096)
                if not part:
                    break
                data += part  # Corregido: acumular en 'data'
            if data:
                frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None and frame.shape == (FRAME_HEIGHT, FRAME_WIDTH, 3):
                    yield frame
                else:
                    print("[WARNING] Frame recibido incompleto o con dimensiones incorrectas.")
    except Exception as e:
        print(f"[ERROR RECEIVER] Error en la conexión: {e}")
    finally:
        connection.close()
        server_socket.close()

if __name__ == '__main__':
    for frame in receive_frames():
        cv2.imshow("Received Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()