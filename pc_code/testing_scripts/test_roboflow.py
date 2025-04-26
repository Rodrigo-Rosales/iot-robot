from inference_sdk import InferenceHTTPClient
import base64

# Configuración de la API
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="jjVaPG6AhMyJS4GocOpG"
)

# Ruta de la imagen que deseas probar
IMAGE_PATH = "capturas_roboflow/captura_20250330_183733.jpg"  # Reemplaza con la imagen real

# Leer la imagen correctamente y codificarla en base64
try:
    with open(IMAGE_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Realizar la inferencia
    result = CLIENT.infer(encoded_image, model_id="basketball-1zhpe/1")

    print("Resultado de la detección:", result)

except Exception as e:
    print(f"Error en la inferencia: {e}")
