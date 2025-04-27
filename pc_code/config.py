# pc_code/config.py

# Configuración del servidor de recepción
HOST = '0.0.0.0'   # Recibe de cualquier IP
PORT = 9999        # Puerto a escuchar

# Configuración de procesamiento
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FRAME_SKIP_ENABLED = True  # Activar frame skipping para reducir latencia

CONFIDENCE_THRESHOLD = 0.4
SHOW_RESULTS = True
MODEL_PATH = 'C:/Users/Rodri/Desktop/School/proyecto-modular/iot-robot/pc_code/models/best.pt'