# pc_code/app.py

from receiver.image_receiver import receive_frames
# from detection.detector import Detector
# from sender.control_sender import ControlSender
# from control.controller import Controller
import cv2
from config import SHOW_RESULTS

def main():
    # detector = Detector()
    frame_generator = receive_frames()
    # controller = Controller()
    # control_sender = ControlSender()

    # if not control_sender.connect():
    #     print("[APP PC] No se pudo conectar al robot para comandos de control. Saliendo.")
    #     return

    try:
        for frame in frame_generator:
            # results_generator = detector.detect(frame)
            # for annotated_frame, error_x, error_y, area, bbox_info in results_generator:
            #     if error_x is not None and error_y is not None and area is not None:
            #         left_pwm, right_pwm = controller.calculate_pwm(error_x, error_y, area)
            #         control_sender.send_control_command(left_pwm, right_pwm)
            #     else:
            #         control_sender.send_control_command(0, 0)

            if SHOW_RESULTS:
                cv2.imshow("Frame con Deteccion", frame)  # Mostrar el frame original sin detección
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except KeyboardInterrupt:
        print("[APP PC] Deteniendo...")
    finally:
        # if control_sender:
        #     control_sender.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()