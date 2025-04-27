import RPi.GPIO as GPIO
import time

# Configuración de pines para Motor A
ENA = 13  # GPIO12/PWM0 (Control de velocidad)
IN1 = 19   # GPIO5 (Dirección)
IN2 = 26   # GPIO6 (Dirección)

# Configuración PWM
PWM_FREQ = 1000  # Frecuencia PWM en Hz

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENA, GPIO.OUT)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    
    # Inicializar PWM
    pwm = GPIO.PWM(ENA, PWM_FREQ)
    pwm.start(0)
    return pwm

def motor_test(pwm):
    try:
        print("Prueba de motor con L298N - Solo Motor A")
        
        # Test 1: Motor gira en una dirección al 50% de velocidad
        print("\nGiro hacia adelante al 50%")
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        pwm.ChangeDutyCycle(25)
        time.sleep(3)
        
        # Test 2: Motor se detiene
        print("Deteniendo motor")
        pwm.ChangeDutyCycle(0)
        time.sleep(3)
        
        # Test 3: Motor gira en dirección contraria al 75%
        print("\nGiro hacia atrás al 75%")
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        pwm.ChangeDutyCycle(75)
        time.sleep(3)
        
        # Test 4: Barrido de velocidad
        print("\nBarrido de velocidad 0-100%")
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        for speed in range(0, 101, 10):
            pwm.ChangeDutyCycle(speed)
            print(f"Velocidad: {speed}%")
            time.sleep(0.5)
        
        # Detener motor
        print("\nPrueba completada - Motor detenido")
        pwm.ChangeDutyCycle(0)
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        
    except KeyboardInterrupt:
        print("\nPrueba interrumpida por el usuario")

def cleanup(pwm):
    pwm.stop()
    GPIO.cleanup()
    print("GPIO limpiado")

if __name__ == "__main__":
    pwm = setup()
    motor_test(pwm)
    cleanup(pwm)