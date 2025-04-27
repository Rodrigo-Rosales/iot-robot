# rpi_code/motor_controllerd/app.py

from motor_controller import MotorController
import time

# Inicialización
motor = MotorController()

try:
    # Ejemplo de movimientos
    print("Avanzando...")
    motor.move_forward(60)  # 60% de velocidad
    time.sleep(3)
    
    # print("Girando a la derecha...")
    # motor.turn_right(40)
    # time.sleep(1.5)
    
    # print("Detención suave...")
    # motor.smooth_stop()
    
    # print("Movimiento complejo...")
    # motor.set_speeds(70, 30)  # Motor izquierdo más rápido
    # time.sleep(1)
    
finally:
    motor.cleanup()