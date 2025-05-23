# pc_code/receiver/image_receiver.py

import socket
import struct
import cv2
import numpy as np
import time
from config import HOST, PORT, FRAME_WIDTH, FRAME_HEIGHT

def receive_frames():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[INFO] Esperando conexión en {HOST}:{PORT}...")
    connection = None
    try:
        connection, client_address = server_socket.accept()
        print(f"[INFO] Conexión establecida con {client_address}")
        if connection:
            connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            while True:
                size_bytes = connection.recv(4)
                if not size_bytes:
                    print("[DEBUG RECEIVER] No se recibieron bytes de tamaño. Conexión terminada por el cliente.")
                    break
                frame_size = struct.unpack(">L", size_bytes)[0]
                # print(f"[DEBUG RECEIVER] Tamaño del frame esperado: {frame_size} bytes.")
                
                frame_data = bytearray()
                bytes_recvd = 0
                while bytes_recvd < frame_size:
                    remaining = frame_size - bytes_recvd
                    chunk_size = min(remaining, 4096)
                    part = connection.recv(chunk_size)
                    if not part:
                        print(f"[DEBUG RECEIVER] Conexión interrumpida mientras recibíamos el frame ({bytes_recvd}/{frame_size} bytes).")
                        return  # Salir limpiamente si la conexión se corta
                    frame_data.extend(part)
                    bytes_recvd += len(part)
                    # print(f"[DEBUG RECEIVER] Bytes recibidos del frame: {bytes_recvd}/{frame_size}")

                if len(frame_data) == frame_size:
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        # print(f"[DEBUG RECEIVER] Dimensiones del frame decodificado: {frame.shape}")
                        if frame.shape == (FRAME_HEIGHT, FRAME_WIDTH, 3):
                            yield frame
                            # print("[DEBUG RECEIVER] Frame decodificado y enviado.")
                        else:
                            print(f"[WARNING] Frame decodificado pero con dimensiones incorrectas: {frame.shape}")
                    else:
                        print("[WARNING] Error al decodificar el frame.")
                else:
                    print(f"[WARNING] No se recibieron todos los bytes del frame. Se recibieron {len(frame_data)} de {frame_size}.")
        else:
            print("[WARNING] No se pudo establecer la conexión.")

    except Exception as e:
        print(f"[ERROR RECEIVER] Error en la conexión: {e}")
    finally:
        if connection:
            connection.close()
        server_socket.close()
        cv2.destroyAllWindows()  # Cierre seguro en caso de error
        print("[INFO] Conexión cerrada y ventanas destruidas.")

if __name__ == '__main__':
    while True:
        frame_generator = receive_frames()
        for frame in frame_generator:
            cv2.imshow("Received Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        print("[INFO] Reconectando en 5 segundos...")
        time.sleep(5)