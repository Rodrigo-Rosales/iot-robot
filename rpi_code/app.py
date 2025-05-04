# rpi_code/app.py

import threading
from sender.image_sender import send_frames
from receiver.control_receiver import receive_control_commands
from motor_controller.motor_controller import MotorController
import signal
import sys

motor_controller = None  # Declarar como variable global para acceder en el handler

def signal_handler(sig, frame):
    print("[APP RPI] Recibiendo señal de terminación...")
    if motor_controller:
        print("[APP RPI] Deteniendo motores suavemente...")
        motor_controller.detener_suave()
        motor_controller.cleanup()
    sys.exit(0)

def main():
    global motor_controller
    motor_controller = MotorController()

    # Configurar el handler para la señal de interrupción (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Iniciar el receptor de comandos de control en un hilo
    control_thread = threading.Thread(target=control_loop, args=(motor_controller,))
    control_thread.daemon = True
    control_thread.start()

    # Iniciar el envío de frames en el hilo principal
    send_frames()

    # Mantener el hilo principal activo para que el handler de señales funcione
    try:
        while True:
            pass
    except KeyboardInterrupt:
        # Esta excepción será capturada por el signal handler
        pass

def control_loop(motor_controller):
    for command in receive_control_commands():
        print(f"[APP RPI] Recibido comando: {command}")
        motor_controller.set_speeds(command['left_pwm'], command['right_pwm'])

if __name__ == "__main__":
    main()