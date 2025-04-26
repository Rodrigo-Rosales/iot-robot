# pc_code/app.py

from receiver.image_receiver import receive_frames
from detection.detector import Detector
import cv2
from config import PORT

def main():
    detector = Detector()
    frame_generator = receive_frames(PORT)

    for frame in frame_generator:
        annotated, _ = detector.detect(frame)

        cv2.imshow('Detección', annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()