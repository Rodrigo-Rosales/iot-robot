# rpi_code/receiver/control_receiver.py

import socket
import struct
import json
from config import RASPBERRY_PI_IP_CONTROL_RECEIVER, RASPBERRY_PI_PORT_CONTROL

def receive_control_commands():
    """
    Establishes a TCP server to receive control commands (PWM values)
    from the laptop and yields them as a dictionary over a persistent connection.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((RASPBERRY_PI_IP_CONTROL_RECEIVER, RASPBERRY_PI_PORT_CONTROL))
    server_socket.listen(1)
    print(f"[RPI RECEIVER] Esperando comandos en {RASPBERRY_PI_IP_CONTROL_RECEIVER}:{RASPBERRY_PI_PORT_CONTROL}...")

    connection, client_address = server_socket.accept()
    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Deshabilitar Nagle
    print(f"[RPI RECEIVER] Conexión establecida con {client_address}")
    try:
        data = b''
        payload_size = struct.calcsize(">L")
        while True:
            while len(data) < payload_size:
                packet = connection.recv(4096)
                if not packet:
                    return  # Connection closed by the client
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]

            while len(data) < msg_size:
                packet = connection.recv(4096)
                if not packet:
                    return  # Connection closed by the client
                data += packet

            command_data = data[:msg_size]
            data = data[msg_size:]

            try:
                command = json.loads(command_data.decode('utf-8'))
                left_pwm = command.get('left_pwm')
                right_pwm = command.get('right_pwm')

                if left_pwm is not None and right_pwm is not None:
                    yield {'left_pwm': left_pwm, 'right_pwm': right_pwm}
                else:
                    print("[RPI RECEIVER] Comando inválido recibido.")

            except json.JSONDecodeError as e:
                print(f"[RPI RECEIVER] Error al decodificar JSON: {e}")
            except Exception as e:
                print(f"[RPI RECEIVER] Error al procesar el comando: {e}")

    except KeyboardInterrupt:
        print("[RPI RECEIVER] Recepción de comandos detenida por el usuario.")
    finally:
        connection.close()
        server_socket.close()

if __name__ == "__main__":
    # This part is for testing the receiver independently
    from motor_controller.motor_controller import MotorController
    motor_controller = MotorController()
    try:
        for command in receive_control_commands():
            print(f"[RPI RECEIVER TEST] Received command: {command}")
            motor_controller.set_speeds(command['left_pwm'], command['right_pwm'])
    except Exception as e:
        print(f"[RPI RECEIVER TEST] Error: {e}")
    finally:
        motor_controller.cleanup()