# laptop_receiver.py
import socket
import pickle
import struct
import cv2
import time

HOST = '0.0.0.0'  # Escucha en todas las interfaces
PORT = 5000

def main():
    # Configuración del socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🖥️ Servidor escuchando en {HOST}:{PORT}...")
        conn, addr = s.accept()
        
        data = b""
        payload_size = struct.calcsize("Q")
        
        try:
            while True:
                # Reconstruye el tamaño del frame
                while len(data) < payload_size:
                    packet = conn.recv(4 * 1024)  # Buffer de 4KB
                    if not packet: break
                    data += packet
                
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                
                # Reconstruye los datos del frame
                while len(data) < msg_size:
                    data += conn.recv(4 * 1024)
                
                frame_data = data[:msg_size]
                data = data[msg_size:]
                
                # Deserializa y muestra el frame
                frame = pickle.loads(frame_data)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                
                cv2.imshow("Video desde RPi", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()