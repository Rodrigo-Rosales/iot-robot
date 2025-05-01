# rpi_code/app.py

from sender.image_sender import send_frames
from receiver.control_receiver import receive_control_commands
from motor_controller.motor_controller import MotorController
import threading

def receive_control_loop(motor_controller):
    """Bucle para recibir comandos de control y aplicarlos a los motores."""
    for command in receive_control_commands():
        left_pwm = command.get('left_pwm')
        right_pwm = command.get('right_pwm')

        if left_pwm is not None and right_pwm is not None:
            print(f"[RPI APP CONTROL] Recibidos PWM - Izquierda: {left_pwm}, Derecha: {right_pwm}")
            motor_controller.set_speeds(left_pwm, right_pwm)
        else:
            print("[RPI APP CONTROL] Comando PWM inválido recibido.")

if __name__ == "__main__":
    motor_controller = MotorController()

    # Iniciar el hilo para recibir comandos de control
    control_thread = threading.Thread(target=receive_control_loop, args=(motor_controller,))
    control_thread.daemon = True
    control_thread.start()

    # Iniciar el envío de frames en el hilo principal
    send_frames()

    # Limpiar GPIO al finalizar (esto puede no ejecutarse si send_frames es un bucle infinito)
    try:
        while True:
            pass  # Mantener el programa principal corriendo para que los hilos sigan activos
    except KeyboardInterrupt:
        print("[RPI APP] Deteniendo...")
    finally:
        motor_controller.cleanup()