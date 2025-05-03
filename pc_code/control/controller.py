# pc_code/control/controller.py

from config import WHEEL_BASE, KP_ANGULAR, KP_LINEAR, AREA_TARGUET, MAX_PWM, MIN_PWM, KP_VERTICAL

class Controller:
    def __init__(self):
        self.wheel_base = WHEEL_BASE
        self.kp_angular = KP_ANGULAR
        self.kp_linear = KP_LINEAR
        self.area_target = AREA_TARGUET
        self.max_pwm = MAX_PWM
        self.min_pwm = MIN_PWM
        self.kp_vertical = KP_VERTICAL  # Nueva ganancia para el error vertical

    def calculate_pwm(self, error_x, error_y, area):
        """Calcula los valores PWM para los motores basados en los errores de detección."""
        if error_x is None or error_y is None or area is None:
            return 0, 0  # Detener si no hay detección

        angular_speed = self.kp_angular * error_x
        error_area = self.area_target - area

        # Modificamos la velocidad lineal para que dependa del error en y (ejemplo simple)
        linear_speed = self.kp_linear * error_area # - self.kp_vertical * error_y

        # Modelo Cinemático Inverso (Velocidades de las ruedas - lineal)
        v_right = linear_speed + (self.wheel_base / 2) * angular_speed
        v_left = linear_speed - (self.wheel_base / 2) * angular_speed

        print(f"[CONTROLLER] Error X: {error_x:.2f}, Error Y: {error_y:.2f}, Area: {area:.2f}, Angular Speed: {angular_speed:.4f}, Linear Speed: {linear_speed:.4f}, V_right: {v_right:.4f}, V_left: {v_left:.4f}") # <--- IMPRESIÓN DE DIAGNÓSTICO

        pwm_right = v_right * 5
        pwm_left = v_left * 15

        # Limitar PWM
        pwm_right = max(self.min_pwm, min(self.max_pwm, pwm_right))
        pwm_left = max(self.min_pwm, min(self.max_pwm, pwm_left))

        return int(pwm_left), int(pwm_right)

if __name__ == "__main__":
    # Ejemplo de prueba
    controller = Controller()
    pwm_izquierdo, pwm_derecho = controller.calculate_pwm(0.1, 0.05, 5000)
    print(f"[CONTROLLER TEST] PWM Izquierdo: {pwm_izquierdo}, PWM Derecho: {pwm_derecho}")