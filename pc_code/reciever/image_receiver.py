# pc_code/receiver/image_receiver.py

import socket
import pickle
import struct

def receive_frames(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    print(f"[INFO] Esperando conexión en el puerto {port}...")
    
    conn, addr = server_socket.accept()
    print(f"[INFO] Conexión establecida con: {addr}")

    data = b''
    payload_size = struct.calcsize(">L")

    while True:
        # Leer el tamaño del paquete
        while len(data) < payload_size:
            packet = conn.recv(4096)
            if not packet:
                return
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        # Leer el frame completo
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)
        yield frame