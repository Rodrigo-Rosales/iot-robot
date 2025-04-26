# rpi_code/sender.py

import socket
import cv2
import struct
import pickle
from config import LAPTOP_IP, PORT, FRAME_WIDTH, FRAME_HEIGHT

def main():
    # Conectarse al socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LAPTOP_IP, PORT))

    # Capturar video
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Serializar la imagen
            data = pickle.dumps(frame)
            # Enviar el tamaño primero
            message = struct.pack(">L", len(data)) + data
            client_socket.sendall(message)

    except KeyboardInterrupt:
        print("\n[INFO] Finalizando envío...")
    finally:
        cap.release()
        client_socket.close()

if __name__ == "__main__":
    main()