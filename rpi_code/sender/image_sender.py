# rpi_code/sender/image_sender.py

import socket
import pickle
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

            data = pickle.dumps(frame)
            message = struct.pack(">L", len(data)) + data
            client_socket.sendall(message)

    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido.")
    finally:
        cap.release()
        client_socket.close()