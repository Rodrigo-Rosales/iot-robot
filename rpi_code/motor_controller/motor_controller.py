# rpi_code/motor_controllerd/motor_controller.py

import RPi.GPIO as GPIO
import time
from config import ENA, IN1, IN2, ENB, IN3, IN4

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup([ENA, IN1, IN2, ENB, IN3, IN4], GPIO.OUT)

# Configuración PWM hardware (frecuencia recomendada: 1-10kHz)
pwm_left = GPIO.PWM(ENA, 10000)  # 10kHz para menos ruido
pwm_right = GPIO.PWM(ENB, 10000)
pwm_left.start(0)  # Inicia en 0% duty cycle
pwm_right.start(0)

def set_motors(left_speed, right_speed):
    """Controla velocidad y dirección de los motores"""
    # Motor izquierdo
    if left_speed >= 0:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    pwm_left.ChangeDutyCycle(abs(left_speed))

    # Motor derecho
    if right_speed >= 0:
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    else:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    pwm_right.ChangeDutyCycle(abs(right_speed))

def stop_motors():
    """Detiene ambos motores"""
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(0)

# Prueba de movimiento
try:
    print("Prueba: Adelante al 50%")
    set_motors(50, 50)
    time.sleep(2)
    
    print("Giro izquierda")
    set_motors(-30, 30)  # Motor izquierdo atrás, derecho adelante
    time.sleep(1.5)
    
    print("Deteniendo")
    stop_motors()

except KeyboardInterrupt:
    print("Deteniendo programa...")
finally:
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()