# rpi_code/motor_controllerd/motor_controller.py

import RPi.GPIO as GPIO
import time

class MotorController:
    def __init__(self):
        # Configuración de pines (BCM)
        self.MOTOR_LEFT = {
            'ENA': 12,  # PWM0
            'IN1': 5,
            'IN2': 6
        }
        self.MOTOR_RIGHT = {
            'ENB': 13,  # PWM1
            'IN3': 19,
            'IN4': 26
        }
        
        # Parámetros del motor (ajustables)
        self.PWM_FREQ = 1000          # Frecuencia PWM en Hz
        self.START_PWM = 50           # PWM mínimo para vencer fricción estática
        self.MIN_PWM = 30             # PWM mínimo una vez en movimiento
        self.MAX_PWM = 100            # PWM máximo
        self.ACCEL_STEP = 5           # Paso de aceleración
        self.ACCEL_DELAY = 0.1        # Retardo entre pasos de aceleración
        
        # Estados
        self.left_speed = 0
        self.right_speed = 0
        self.left_moving = False
        self.right_moving = False
        
        # Inicialización
        self.setup_gpio()
    
    def setup_gpio(self):
        """Inicializa los pines GPIO y PWM"""
        GPIO.setmode(GPIO.BCM)
        
        # Configurar pines del motor izquierdo
        GPIO.setup(self.MOTOR_LEFT['ENA'], GPIO.OUT)
        GPIO.setup(self.MOTOR_LEFT['IN1'], GPIO.OUT)
        GPIO.setup(self.MOTOR_LEFT['IN2'], GPIO.OUT)
        
        # Configurar pines del motor derecho
        GPIO.setup(self.MOTOR_RIGHT['ENB'], GPIO.OUT)
        GPIO.setup(self.MOTOR_RIGHT['IN3'], GPIO.OUT)
        GPIO.setup(self.MOTOR_RIGHT['IN4'], GPIO.OUT)
        
        # Inicializar PWM
        self.pwm_left = GPIO.PWM(self.MOTOR_LEFT['ENA'], self.PWM_FREQ)
        self.pwm_right = GPIO.PWM(self.MOTOR_RIGHT['ENB'], self.PWM_FREQ)
        self.pwm_left.start(0)
        self.pwm_right.start(0)
    
    def _set_motor(self, motor, speed, direction):
        """
        Control interno de un motor con manejo de fricción estática
        :param motor: 'left' o 'right'
        :param speed: 0-100
        :param direction: 1 (adelante) o -1 (atrás)
        """
        if motor == 'left':
            pwm = self.pwm_left
            in1 = self.MOTOR_LEFT['IN1']
            in2 = self.MOTOR_LEFT['IN2']
            current_moving = self.left_moving
        else:
            pwm = self.pwm_right
            in1 = self.MOTOR_RIGHT['IN3']
            in2 = self.MOTOR_RIGHT['IN4']
            current_moving = self.right_moving
        
        # Aplicar dirección
        GPIO.output(in1, direction == 1)
        GPIO.output(in2, direction != 1)
        
        # Manejo especial de velocidad
        if not current_moving and speed > 0:
            # Aplicar START_PWM para vencer fricción estática
            pwm.ChangeDutyCycle(self.START_PWM)
            time.sleep(0.2)  # Pequeña pausa para iniciar movimiento
            actual_speed = max(speed, self.MIN_PWM)
            pwm.ChangeDutyCycle(actual_speed)
            if motor == 'left':
                self.left_moving = True
            else:
                self.right_moving = True
        elif current_moving:
            if speed <= 0:
                # Detener motor
                pwm.ChangeDutyCycle(0)
                if motor == 'left':
                    self.left_moving = False
                else:
                    self.right_moving = False
            else:
                # Ajustar velocidad manteniendo mínimo
                actual_speed = max(speed, self.MIN_PWM)
                pwm.ChangeDutyCycle(actual_speed)
    
    def move_forward(self, speed=50):
        """Mueve el robot hacia adelante"""
        self._set_motor('left', speed, 1)
        self._set_motor('right', speed, 1)
        self.left_speed = speed
        self.right_speed = speed
    
    def move_backward(self, speed=50):
        """Mueve el robot hacia atrás"""
        self._set_motor('left', speed, -1)
        self._set_motor('right', speed, -1)
        self.left_speed = speed
        self.right_speed = speed
    
    def turn_left(self, speed=50):
        """Gira el robot a la izquierda (motores en direcciones opuestas)"""
        self._set_motor('left', speed, -1)
        self._set_motor('right', speed, 1)
        self.left_speed = speed
        self.right_speed = speed
    
    def turn_right(self, speed=50):
        """Gira el robot a la derecha (motores en direcciones opuestas)"""
        self._set_motor('left', speed, 1)
        self._set_motor('right', speed, -1)
        self.left_speed = speed
        self.right_speed = speed
    
    def stop(self):
        """Detiene ambos motores"""
        self._set_motor('left', 0, 1)
        self._set_motor('right', 0, 1)
        self.left_speed = 0
        self.right_speed = 0
    
    def set_speeds(self, left_speed, right_speed):
        """
        Control independiente de motores
        :param left_speed: -100 a 100 (negativo para atrás)
        :param right_speed: -100 a 100 (negativo para atrás)
        """
        left_dir = 1 if left_speed >= 0 else -1
        right_dir = 1 if right_speed >= 0 else -1
        self._set_motor('left', abs(left_speed), left_dir)
        self._set_motor('right', abs(right_speed), right_dir)
        self.left_speed = abs(left_speed)
        self.right_speed = abs(right_speed)
    
    def smooth_stop(self):
        """Detención suave con desaceleración progresiva"""
        current_left = self.left_speed
        current_right = self.right_speed
        
        steps = max(current_left, current_right) // self.ACCEL_STEP
        for i in range(steps, -1, -1):
            left_speed = max(0, current_left - i*self.ACCEL_STEP)
            right_speed = max(0, current_right - i*self.ACCEL_STEP)
            self.set_speeds(left_speed, right_speed)
            time.sleep(self.ACCEL_DELAY)
        
        self.stop()
    
    def cleanup(self):
        """Limpieza de GPIO (llamar al terminar)"""
        self.stop()
        self.pwm_left.stop()
        self.pwm_right.stop()
        GPIO.cleanup()