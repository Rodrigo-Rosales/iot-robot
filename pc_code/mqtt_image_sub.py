import paho.mqtt.client as mqtt
import base64
import numpy as np
import cv2

MQTT_BROKER = "localhost"
MQTT_TOPIC = "robot/camera"

def on_message(client, userdata, msg):
    try:
        img_base64 = msg.payload.decode('utf-8')
        img_bytes = base64.b64decode(img_base64)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        cv2.imshow("Imagen recibida", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            client.disconnect()
    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER)
client.subscribe(MQTT_TOPIC)
print("Esperando imágenes...")
client.loop_forever()