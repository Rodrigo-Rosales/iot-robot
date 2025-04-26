from ultralytics import YOLO
import cv2
import time

# Ruta al modelo entrenado
model = YOLO('C:/Users/Rodri/Desktop/School/proyecto_modular/iot-robot/pc_code/models/bestBIG.pt')

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

CONFIDENCE_THRESHOLD = 0.40
SHOW_RESULTS = True

frame_center_x = 640 // 2
area_near_threshold = 30000
area_far_threshold = 5000
margin_x = 50

# Guardar el último "mejor" bbox (simplificado)
last_target_box = None

def get_instruction(x_center, area):
    if area > area_near_threshold:
        return "RETROCEDER"
    elif area < area_far_threshold:
        return "AVANZAR"
    elif x_center < frame_center_x - margin_x:
        return "GIRAR IZQUIERDA"
    elif x_center > frame_center_x + margin_x:
        return "GIRAR DERECHA"
    else:
        return "ADELANTE RECTO"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    start_time = time.time()
    results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, save=False, verbose=False)
    annotated = results[0].plot()

    boxes = results[0].boxes
    if boxes:
        # Elegir el objeto con mayor confianza
        best_box = max(boxes, key=lambda b: b.conf[0].item())
        x1, y1, x2, y2 = map(int, best_box.xyxy[0])
        x_center = (x1 + x2) // 2
        y_center = (y1 + y2) // 2
        area = (x2 - x1) * (y2 - y1)

        instruction = get_instruction(x_center, area)
        print(f"[INSTRUCCIÓN] {instruction}")

        # Dibujar la instrucción
        cv2.putText(annotated, instruction, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

        # Solo dibujar el objetivo principal
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # FPS
    fps = 1.0 / (time.time() - start_time)
    cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    if SHOW_RESULTS:
        cv2.imshow("Detección + Seguimiento", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()