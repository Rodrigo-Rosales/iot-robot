# rpi_code/config.py

# Configuración del envío de video
SERVER_IP = '192.168.0.10'  # IP de la PC que recibe
SERVER_PORT = 9999          # Puerto de conexión

# Configuración de la cámara
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
JPEG_QUALITY = 80  # Calidad de la compresión JPEG

# --- Configuración para recibir comandos de control ---
RASPBERRY_PI_IP_CONTROL_RECEIVER = '0.0.0.0'
RASPBERRY_PI_PORT_CONTROL = 12346