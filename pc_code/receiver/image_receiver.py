# pc_code/receiver/image_receiver.py

import socket
import struct
import cv2
import numpy as np
from config import HOST, PORT, FRAME_WIDTH, FRAME_HEIGHT

def receive_frames():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[INFO] Esperando conexión en {HOST}:{PORT}...")
    connection, client_address = server_socket.accept()
    print(f"[INFO] Conexión establecida con {client_address}")
    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Deshabilitar Nagle
    try:
        while True:
            size_bytes = connection.recv(4)
            if not size_bytes:
                print("[DEBUG RECEIVER] No se recibieron bytes de tamaño. Conexión terminada por el cliente.")
                break
            frame_size = struct.unpack(">L", size_bytes)[0]
            print(f"[DEBUG RECEIVER] Tamaño del frame esperado: {frame_size} bytes.")
            frame_data = b""
            bytes_recvd = 0
            while bytes_recvd < frame_size:
                remaining = frame_size - bytes_recvd
                chunk_size = min(remaining, 4096)
                part = connection.recv(chunk_size)
                if not part:
                    print(f"[DEBUG RECEIVER] No se recibieron más datos del frame ({bytes_recvd}/{frame_size} bytes). Conexión terminada por el cliente.")
                    break
                frame_data += part
                bytes_recvd += len(part)
                print(f"[DEBUG RECEIVER] Bytes recibidos del frame: {bytes_recvd}/{frame_size}")

            if len(frame_data) == frame_size:
                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None and frame.shape == (FRAME_HEIGHT, FRAME_WIDTH, 3):
                    yield frame
                    print("[DEBUG RECEIVER] Frame decodificado y enviado.")
                else:
                    print("[WARNING] Frame recibido incompleto o con dimensiones incorrectas.")
            else:
                print(f"[WARNING] No se recibieron todos los bytes del frame. Se recibieron {len(frame_data)} de {frame_size}.")
                break # Salir del bucle si no se recibió el frame completo
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