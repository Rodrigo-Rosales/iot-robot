# pc_code/app.py

from receiver.image_receiver import receive_frames
from detection.detector import Detector
from sender.control_sender import send_control_command
from control.controller import Controller
import cv2
from config import SHOW_RESULTS

def main():
    detector = Detector()
    frame_generator = receive_frames()
    controller = Controller()

    for frame in frame_generator:
        detection_output = detector.detect(frame)
        for annotated, error_x, error_y, area, bbox_info in detection_output:
            if error_x is not None and error_y is not None and area is not None:
                print(f"[DETECCIÓN] Error X: {error_x:.2f}, Error Y: {error_y:.2f}, Area: {area:.2f}, BBox Info: {bbox_info}")

                # --- Lógica de Control (usando el Controller) ---
                left_pwm, right_pwm = controller.calculate_pwm(error_x, error_y, area)
                print(f"[CONTROL] PWM Izquierdo: {left_pwm}, PWM Derecho: {right_pwm}")

                # --- Enviar comandos de control ---
                send_control_command(left_pwm, right_pwm)

            else:
                # Si no se detecta el balón, detener el robot
                send_control_command(0, 0)

            if SHOW_RESULTS:
                cv2.imshow("Deteccion + Seguimiento", annotated)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()