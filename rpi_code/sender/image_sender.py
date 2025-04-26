# rpi_code/sender/image_sender.py

import socket
import struct
import cv2
from config import LAPTOP_IP, PORT, FRAME_WIDTH, FRAME_HEIGHT

def send_frames():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LAPTOP_IP, PORT))

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Comprimir el frame antes de enviarlo
            _, encoded_image = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            data = encoded_image.tobytes()

            # Empaquetar tamaño + datos
            message = struct.pack(">L", len(data)) + data
            client_socket.sendall(message)

    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido.")
    finally:
        cap.release()
        client_socket.close()