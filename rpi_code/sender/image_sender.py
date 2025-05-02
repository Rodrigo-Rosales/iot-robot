# rpi_code/sender/image_sender.py

import socket
import cv2
import struct
import time
from config import SERVER_IP, SERVER_PORT, FRAME_WIDTH, FRAME_HEIGHT, JPEG_QUALITY, FPS_SEND

def send_frames():
    # Inicializar la cámara
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Intenta reducir el buffer de la cámara

    # Inicializar socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Deshabilitar Nagle
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"[RPI VIDEO SENDER] Error al conectar: {e}")
        return

    try:
        while True:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            # Comprimir frame a JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
            result, encoded_image = cv2.imencode('.jpg', frame, encode_param)
            data = encoded_image.tobytes()

            # Enviar longitud y luego datos
            try:
                client_socket.sendall(struct.pack(">L", len(data)) + data)
            except Exception as e:
                print(f"[RPI VIDEO SENDER] Error al enviar frame: {e}")
                break

            time_to_send = time.time() - start_time
            sleep_time = max(0, (1 / FPS_SEND) - time_to_send)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("Interrupción del programa (sender).")
    finally:
        cap.release()
        client_socket.close()