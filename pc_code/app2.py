# pc_code/app_pruebas.py

from receiver.image_receiver import receive_frames
from detection.detector import Detector
import cv2
from config import SHOW_RESULTS, WHEEL_BASE, KP_ANGULAR, KP_LINEAR, AREA_TARGUET, MAX_PWM, MIN_PWM

def main():
    detector = Detector()
    frame_generator = receive_frames()

    for frame in frame_generator:
        detection_output = detector.detect(frame)
        for annotated, error_x, error_y, area, bbox_info in detection_output:
            linear_speed = 0.0
            angular_speed = 0.0

            if error_x is not None and area is not None:
                print(f"[DETECCIÓN] Error X: {error_x:.2f}, Error Y: {error_y:.2f}, Area: {area:.2f}, BBox Info: {bbox_info}")

                # --- Lógica de Control ---
                angular_speed = KP_ANGULAR * error_x
                error_area = AREA_TARGUET - area
                linear_speed = KP_LINEAR * error_area

                # --- Modelo Cinemático Inverso (Velocidades de las ruedas - lineal) ---
                v_right = linear_speed + (WHEEL_BASE / 2) * angular_speed
                v_left = linear_speed - (WHEEL_BASE / 2) * angular_speed

                # --- Escalar a PWM (Esto es una aproximación y necesita calibración) ---
                # Asumimos que las velocidades están en un rango que se puede escalar a PWM
                # Necesitarás experimentar con estos factores de escala
                pwm_right = v_right * 50  # Factor de escala inicial
                pwm_left = v_left * 50   # Factor de escala inicial

                # Limitar PWM
                pwm_right = max(MIN_PWM, min(MAX_PWM, pwm_right))
                pwm_left = max(MIN_PWM, min(MAX_PWM, pwm_left))

                print(f"[PRUEBA CONTROL] PWM Izquierda: {pwm_left:.2f}, PWM Derecha: {pwm_right:.2f}")

            else:
                print("[PRUEBA CONTROL] No se detecta el balón, PWM Izquierda: 0, PWM Derecha: 0")

            if SHOW_RESULTS:
                cv2.imshow("Deteccion + Seguimiento (PRUEBA)", annotated)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()