# pc_code/receiver/image_receiver.py

import socket
import struct
import numpy as np
import cv2
from config import HOST, PORT, FRAME_SKIP_ENABLED

def receive_frames():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"[INFO] Esperando conexión en {HOST}:{PORT}...")

    conn, addr = server_socket.accept()
    print(f"[INFO] Conexión establecida con {addr}")

    data = b''
    payload_size = struct.calcsize(">L")

    try:
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

            # Decodificar frame
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # FRAME SKIPPING IMPLEMENTADO
            if FRAME_SKIP_ENABLED:
                conn.setblocking(0)
                try:
                    while True:
                        next_packet = conn.recv(4096)
                        if not next_packet:
                            break
                        data += next_packet

                        while len(data) >= payload_size:
                            packed_msg_size = data[:payload_size]
                            if len(data) < payload_size + struct.unpack(">L", packed_msg_size)[0]:
                                break

                            msg_size = struct.unpack(">L", packed_msg_size)[0]
                            data = data[payload_size:]
                            frame_data = data[:msg_size]
                            data = data[msg_size:]

                            nparr = np.frombuffer(frame_data, np.uint8)
                            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                except BlockingIOError:
                    pass
                finally:
                    conn.setblocking(1)

            # 🔥 Yield del último frame listo
            yield frame

    except KeyboardInterrupt:
        print("[INFO] Interrupción manual (receiver).")
    finally:
        conn.close()
        server_socket.close()