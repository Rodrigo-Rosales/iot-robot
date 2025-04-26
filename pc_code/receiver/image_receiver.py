# pc_code/receiver/image_receiver.py

import socket
import pickle
import struct
import cv2
import numpy as np
from config import PORT

def receive_frames():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen(1)
    print(f"[INFO] Esperando conexión en el puerto {PORT}...")

    conn, addr = server_socket.accept()
    print(f"[INFO] Conexión establecida con {addr}")

    data = b''
    payload_size = struct.calcsize(">L")

    while True:
        while len(data) < payload_size:
            packet = conn.recv(4096)
            if not packet:
                return
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        # 🔥 Decodificar la imagen comprimida
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        yield frame