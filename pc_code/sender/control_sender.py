# pc_code/sender/control_sender.py

import socket
import struct
import json
from config import RASPBERRY_PI_IP, RASPBERRY_PI_PORT_CONTROL

def send_control_command(left_pwm, right_pwm):
    """Envía los comandos PWM a la Raspberry Pi."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((RASPBERRY_PI_IP, RASPBERRY_PI_PORT_CONTROL))
        command = {'left_pwm': left_pwm, 'right_pwm': right_pwm}
        command_json = json.dumps(command).encode('utf-8')
        client_socket.sendall(struct.pack(">L", len(command_json)) + command_json)
        client_socket.close()
    except Exception as e:
        print(f"[ERROR CONTROL SENDER] No se pudo enviar el comando de control: {e}")

if __name__ == "__main__":
    # Ejemplo de prueba (no se ejecutará al ser importado)
    print("[CONTROL SENDER TEST] Enviando comando de prueba...")
    send_control_command(50, -50)
    print("[CONTROL SENDER TEST] Comando de prueba enviado.")