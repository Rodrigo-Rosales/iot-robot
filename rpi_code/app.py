# rpi_code/app.py

import threading
from sender.image_sender import send_frames
from receiver.control_receiver import receive_control_commands
from motor_controller.motor_controller import MotorController

def main():
    motor_controller = MotorController()

    # Iniciar el receptor de comandos de control en un hilo
    control_thread = threading.Thread(target=control_loop, args=(motor_controller,))
    control_thread.daemon = True
    control_thread.start()

    # Iniciar el envío de frames en el hilo principal
    send_frames()

def control_loop(motor_controller):
    for command in receive_control_commands():
        print(f"[APP RPI] Recibido comando: {command}")
        motor_controller.set_speeds(command['left_pwm'], command['right_pwm'])

if __name__ == "__main__":
    main()