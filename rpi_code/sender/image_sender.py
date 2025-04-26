# rpi_code/sender/image_sender.py

import socket
import cv2
import struct
from config import SERVER_IP, SERVER_PORT, FRAME_WIDTH, FRAME_HEIGHT, JPEG_QUALITY

# Inicializar la cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Inicializar socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Comprimir frame a JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        result, encoded_image = cv2.imencode('.jpg', frame, encode_param)
        data = encoded_image.tobytes()

        # Enviar longitud y luego datos
        client_socket.sendall(struct.pack(">L", len(data)) + data)

except KeyboardInterrupt:
    print("Interrupción del programa (sender).")
finally:
    cap.release()
    client_socket.close()