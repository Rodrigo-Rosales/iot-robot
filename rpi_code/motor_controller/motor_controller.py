# rpi_code/motor_controller/motor_controller.py

import RPi.GPIO as GPIO
import time

class MotorController:
    def __init__(self):
        # Configuración de pines (BCM)
        self.MOTOR_IZQUIERDO = {
            'ENA': 12,  # PWM0
            'IN1': 5,
            'IN2': 6
        }
        self.MOTOR_DERECHO = {
            'ENB': 13,  # PWM1
            'IN3': 19,
            'IN4': 26
        }

        # Parámetros del motor (ajustables)
        self.PWM_FREQ = 1000        # Frecuencia PWM en Hz
        self.PWM_INICIO = 50         # PWM mínimo para vencer la fricción estática
        self.PWM_MINIMO = 30           # PWM mínimo una vez en movimiento
        self.PWM_MAXIMO = 60          # PWM máximo
        self.PASO_ACELERACION = 5         # Paso de aceleración
        self.RETARDO_ACELERACION = 0.1      # Retardo entre pasos de aceleración

        # Estados
        self.velocidad_izquierda = 0
        self.velocidad_derecha = 0
        self.izquierda_en_movimiento = False
        self.derecha_en_movimiento = False

        # Inicialización
        self.setup_gpio()

    def setup_gpio(self):
        """Inicializa los pines GPIO y PWM."""
        GPIO.setmode(GPIO.BCM)

        # Configurar pines del motor izquierdo
        GPIO.setup(self.MOTOR_IZQUIERDO['ENA'], GPIO.OUT)
        GPIO.setup(self.MOTOR_IZQUIERDO['IN1'], GPIO.OUT)
        GPIO.setup(self.MOTOR_IZQUIERDO['IN2'], GPIO.OUT)

        # Configurar pines del motor derecho
        GPIO.setup(self.MOTOR_DERECHO['ENB'], GPIO.OUT)
        GPIO.setup(self.MOTOR_DERECHO['IN3'], GPIO.OUT)
        GPIO.setup(self.MOTOR_DERECHO['IN4'], GPIO.OUT)

        # Inicializar PWM
        self.pwm_izquierda = GPIO.PWM(self.MOTOR_IZQUIERDO['ENA'], self.PWM_FREQ)
        self.pwm_derecha = GPIO.PWM(self.MOTOR_DERECHO['ENB'], self.PWM_FREQ)
        self.pwm_izquierda.start(0)
        self.pwm_derecha.start(0)

    def _set_motor(self, motor, velocidad, direccion):
        """
        Control interno de un motor con manejo de fricción estática.
        :param motor: 'izquierda' o 'derecha'
        :param velocidad: 0-100
        :param direccion: 1 (adelante) o -1 (atrás)
        """
        if motor == 'izquierda':
            pwm = self.pwm_izquierda
            in1 = self.MOTOR_IZQUIERDO['IN1']
            in2 = self.MOTOR_IZQUIERDO['IN2']
            en_movimiento = self.izquierda_en_movimiento
        else:
            pwm = self.pwm_derecha
            in1 = self.MOTOR_DERECHO['IN3']
            in2 = self.MOTOR_DERECHO['IN4']
            en_movimiento = self.derecha_en_movimiento

        # Aplicar dirección
        GPIO.output(in1, direccion == 1)
        GPIO.output(in2, direccion != 1)

        # Manejo especial de velocidad para vencer fricción estática
        if not en_movimiento and velocidad > 0:
            # Aplicar PWM_INICIO para vencer la fricción estática
            pwm.ChangeDutyCycle(self.PWM_INICIO)
            time.sleep(0.2)  # Pequeña pausa para iniciar el movimiento
            velocidad_actual = max(velocidad, self.PWM_MINIMO)
            pwm.ChangeDutyCycle(velocidad_actual)
            if motor == 'izquierda':
                self.izquierda_en_movimiento = True
            else:
                self.derecha_en_movimiento = True
        elif en_movimiento:
            if velocidad <= 0:
                # Detener el motor
                pwm.ChangeDutyCycle(0)
                if motor == 'izquierda':
                    self.izquierda_en_movimiento = False
                else:
                    self.derecha_en_movimiento = False
            else:
                # Ajustar la velocidad manteniendo el mínimo
                velocidad_actual = max(velocidad, self.PWM_MINIMO)
                pwm.ChangeDutyCycle(velocidad_actual)

    def mover_adelante(self, velocidad=50):
        """Mueve el robot hacia adelante."""
        self._set_motor('izquierda', velocidad, 1)
        self._set_motor('derecha', velocidad, 1)
        self.velocidad_izquierda = velocidad
        self.velocidad_derecha = velocidad

    def mover_atras(self, velocidad=50):
        """Mueve el robot hacia atrás."""
        self._set_motor('izquierda', velocidad, -1)
        self._set_motor('derecha', velocidad, -1)
        self.velocidad_izquierda = velocidad
        self.velocidad_derecha = velocidad

    def girar_izquierda(self, velocidad=50):
        """Gira el robot a la izquierda (motores en direcciones opuestas)."""
        self._set_motor('izquierda', velocidad, -1)
        self._set_motor('derecha', velocidad, 1)
        self.velocidad_izquierda = velocidad
        self.velocidad_derecha = velocidad

    def girar_derecha(self, velocidad=50):
        """Gira el robot a la derecha (motores en direcciones opuestas)."""
        self._set_motor('izquierda', velocidad, 1)
        self._set_motor('derecha', velocidad, -1)
        self.velocidad_izquierda = velocidad
        self.velocidad_derecha = velocidad

    def detener(self):
        """Detiene ambos motores."""
        self._set_motor('izquierda', 0, 1)
        self._set_motor('derecha', 0, 1)
        self.velocidad_izquierda = 0
        self.velocidad_derecha = 0

    def set_speeds(self, velocidad_izquierda, velocidad_derecha):
        """
        Control independiente de los motores.
        :param velocidad_izquierda: -100 a 100 (negativo para atrás)
        :param velocidad_derecha: -100 a 100 (negativo para atrás)
        """
        direccion_izquierda = 1 if velocidad_izquierda >= 0 else -1
        direccion_derecha = 1 if velocidad_derecha >= 0 else -1
        self._set_motor('izquierda', abs(velocidad_izquierda), direccion_izquierda)
        self._set_motor('derecha', abs(velocidad_derecha), direccion_derecha)
        self.velocidad_izquierda = abs(velocidad_izquierda)
        self.velocidad_derecha = abs(velocidad_derecha)

    def detener_suave(self):
        """Detención suave con desaceleración progresiva."""
        velocidad_actual_izquierda = self.velocidad_izquierda
        velocidad_actual_derecha = self.velocidad_derecha

        pasos = max(velocidad_actual_izquierda, velocidad_actual_derecha) // self.PASO_ACELERACION
        for i in range(pasos, -1, -1):
            velocidad_izquierda = max(0, velocidad_actual_izquierda - i * self.PASO_ACELERACION)
            velocidad_derecha = max(0, velocidad_actual_derecha - i * self.PASO_ACELERACION)
            self.set_speeds(velocidad_izquierda, velocidad_derecha)
            time.sleep(self.RETARDO_ACELERACION)

        self.detener()

    def cleanup(self):
        """Limpieza de GPIO (llamar al terminar)."""
        self.detener()
        self.pwm_izquierda.stop()
        self.pwm_derecha.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    # Ejemplo de uso para pruebas
    try:
        controlador_motor = MotorController()
        print("Probando motores. Presiona Ctrl+C para detener.")
        while True:
            controlador_motor.set_speeds(50, 50)  # Mover hacia adelante
            time.sleep(3)
            # controlador_motor.set_speeds(-50, -50) # Mover hacia atrás
            # time.sleep(2)
            # controlador_motor.set_speeds(50, -50)  # Girar a la derecha
            # time.sleep(2)
            # controlador_motor.set_speeds(-50, 50)  # Girar a la izquierda
            # time.sleep(2)
            # controlador_motor.set_speeds(0, 0)    # Detener
            # time.sleep(2)
    except KeyboardInterrupt:
        print("Deteniendo motores y limpiando.")
    finally:
        if 'controlador_motor' in locals():
            controlador_motor.cleanup()