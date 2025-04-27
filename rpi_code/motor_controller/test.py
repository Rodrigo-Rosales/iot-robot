# rpi_code/motor_controller/test.py

import RPi.GPIO as GPIO
import time
import sys
import tty
import termios
from math import ceil

class MotorController:
    def __init__(self):
        # Configuración de pines (BCM)
        self.ENA = 13   # GPIO 12 (PWM0) o GPIO 13 (PWM1)
        self.IN1 = 19   # GPIO 5 o # GPIO 19
        self.IN2 = 26   # GPIO 6 o GPIO 26
        
        # Configuración motores
        self.PWM_FREQ = 1000
        self.MIN_PWM = 25    # Mínimo para que gire
        self.MAX_PWM = 100
        self.ACCELERATION = 5  # Incremento de velocidad por paso
        
        # Estado actual
        self.current_speed = 0
        self.current_direction = 1  # 1=adelante, -1=atrás
        self.pwm = None
        
        self.setup()
    
    def setup(self):
        """Inicializa GPIO y PWM"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        
        self.pwm = GPIO.PWM(self.ENA, self.PWM_FREQ)
        self.pwm.start(0)
    
    def set_motor(self, speed=None, direction=None):
        """Control preciso del motor con aceleración suave"""
        if speed is not None:
            self.current_speed = max(self.MIN_PWM, min(self.MAX_PWM, speed))
        if direction is not None:
            self.current_direction = 1 if direction > 0 else -1
        
        # Aplicar cambios
        GPIO.output(self.IN1, self.current_direction == 1)
        GPIO.output(self.IN2, self.current_direction != 1)
        self.pwm.ChangeDutyCycle(self.current_speed)
        
        self.display_status()
    
    def smooth_acceleration(self, target_speed):
        """Aceleración/desaceleración progresiva"""
        step = self.ACCELERATION if target_speed > self.current_speed else -self.ACCELERATION
        for speed in range(self.current_speed, target_speed, step):
            self.set_motor(speed=speed)
            time.sleep(0.1)
        self.set_motor(speed=target_speed)
    
    def stop_motor(self):
        """Detención suave del motor"""
        self.smooth_acceleration(0)
        print("Motor detenido")
    
    def display_status(self):
        """Muestra estado actual del motor"""
        dir_icon = "▲" if self.current_direction == 1 else "▼"
        print(f"\rMotor: {dir_icon} {self.current_speed}%", end="", flush=True)
    
    def cleanup(self):
        """Limpieza de GPIO"""
        self.stop_motor()
        self.pwm.stop()
        GPIO.cleanup()
        print("\nSistema apagado correctamente")

def get_key():
    """Captura tecla presionada"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main_control_loop():
    """Bucle principal de control mejorado"""
    motor = MotorController()
    
    print("\nCONTROL AVANZADO DE MOTOR")
    print("-----------------------")
    print("Flechas: Control dirección y velocidad")
    print("[+]/[-]: Ajuste fino de velocidad")
    print("[Space]: Detención suave")
    print("[Q]: Salir\n")
    
    try:
        while True:
            key = get_key()
            
            # Secuencias especiales (flechas)
            if key == '\x1b':
                key += sys.stdin.read(2)
            
            # Comandos
            if key == '\x1b[A':  # Flecha arriba
                motor.set_motor(direction=1)
            elif key == '\x1b[B':  # Flecha abajo
                motor.set_motor(direction=-1)
            elif key == '\x1b[C':  # Flecha derecha
                new_speed = min(motor.current_speed + 10, motor.MAX_PWM)
                motor.smooth_acceleration(new_speed)
            elif key == '\x1b[D':  # Flecha izquierda
                new_speed = max(motor.current_speed - 10, motor.MIN_PWM)
                motor.smooth_acceleration(new_speed)
            elif key == '+':
                new_speed = min(motor.current_speed + 5, motor.MAX_PWM)
                motor.set_motor(speed=new_speed)
            elif key == '-':
                new_speed = max(motor.current_speed - 5, motor.MIN_PWM)
                motor.set_motor(speed=new_speed)
            elif key == ' ':
                motor.stop_motor()
            elif key.lower() == 'q':
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        motor.cleanup()

if __name__ == "__main__":
    main_control_loop()