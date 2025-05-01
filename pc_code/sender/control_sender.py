# pc_code/sender/control_sender.py

import socket
import struct
import json
from config import RASPBERRY_PI_IP, RASPBERRY_PI_PORT_CONTROL

class ControlSender:
    def __init__(self):
        self.client_socket = None
        self.connected = False

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Deshabilitar Nagle
            self.client_socket.connect((RASPBERRY_PI_IP, RASPBERRY_PI_PORT_CONTROL))
            self.connected = True
            print("[CONTROL SENDER] Conexión establecida para comandos de control.")
            return True
        except Exception as e:
            print(f"[ERROR CONTROL SENDER] No se pudo conectar para comandos de control: {e}")
            return False

    def send_control_command(self, left_pwm, right_pwm):
        if not self.connected:
            if not self.connect():
                return False
        try:
            command = {'left_pwm': left_pwm, 'right_pwm': right_pwm}
            command_json = json.dumps(command).encode('utf-8')
            self.client_socket.sendall(struct.pack(">L", len(command_json)) + command_json)
            return True
        except Exception as e:
            print(f"[ERROR CONTROL SENDER] Error al enviar comando de control: {e}")
            self.connected = False  # Considerar la conexión perdida
            return False

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            self.connected = False
            print("[CONTROL SENDER] Conexión para comandos de control cerrada.")

# Ejemplo de cómo usar esta clase en tu app.py (tendrás que modificar tu bucle principal)
if __name__ == "__main__":
    sender = ControlSender()
    if sender.connect():
        print("[CONTROL SENDER TEST] Enviando comando de prueba...")
        sender.send_control_command(50, -50)
        print("[CONTROL SENDER TEST] Comando de prueba enviado.")
        sender.close()