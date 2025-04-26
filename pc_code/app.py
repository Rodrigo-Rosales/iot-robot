# pc_code/app.py

from receiver.image_receiver import receive_frames
from detection.detector import Detector
import cv2
from config import SHOW_RESULTS

def main():
    detector = Detector()
    frame_generator = receive_frames()

    for frame in frame_generator:
        annotated, instruction = detector.detect(frame)

        if instruction:
            print(f"[INSTRUCCIÓN] {instruction}")

        if SHOW_RESULTS:
            cv2.imshow("Detección + Seguimiento", annotated)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()