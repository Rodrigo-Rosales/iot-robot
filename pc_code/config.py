# pc_code/config.py

# Configuración del servidor de recepción
HOST = '0.0.0.0'   # Recibe de cualquier IP
PORT = 9999        # Puerto a escuchar

# Configuración de procesamiento
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_SKIP_ENABLED = True  # Activar frame skipping para reducir latencia

CONFIDENCE_THRESHOLD = 0.4
SHOW_RESULTS = True
MODEL_PATH = 'C:/Users/Rodri/Desktop/School/proyecto-modular/iot-robot/pc_code/models/best.pt'

# --- Configuración para enviar comandos a la Raspberry Pi ---
RASPBERRY_PI_IP = '192.168.0.11'  # Reemplaza con la IP de tu Raspberry Pi
RASPBERRY_PI_PORT_CONTROL = 12346        # Puerto para el control (debe coincidir en la RPi)

# --- Parámetros del Robot ---
WHEEL_BASE = 0.18  # Distancia entre ruedas en metros

# --- Ganancias del Controlador ---
KP_ANGULAR = 0.005
KP_LINEAR = 0.0005
KP_VERTICAL = 0.0005
AREA_TARGUET = 5000

# --- Rango de PWM (ajusta según tu MotorController) ---
MAX_PWM = 100
MIN_PWM = 0