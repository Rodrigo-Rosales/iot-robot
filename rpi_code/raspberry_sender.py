import cv2
import socket
import pickle
import struct
import time
import logging
from datetime import datetime

# Configuración de logging (registro de eventos)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Muestra logs en consola
        logging.FileHandler('rpi_stream.log')  # Guarda logs en archivo
    ]
)
logger = logging.getLogger("RPi_Streamer")

# --- Configuración ---
HOST = '192.168.18.2'  # Reemplaza con la IP de tu laptop
PORT = 5000
RESOLUTION = (640, 480)
FPS_TARGET = 25
JPEG_QUALITY = 80
TIMEOUT = 5  # segundos para timeout de conexión

def setup_camera():
    """Configura la cámara con parámetros optimizados"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("No se pudo abrir la cámara")
        exit(1)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION[1])
    cap.set(cv2.CAP_PROP_FPS, FPS_TARGET)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Reduce latency
    logger.info(f"Cámara configurada a {RESOLUTION[0]}x{RESOLUTION[1]} @ {FPS_TARGET}FPS")
    return cap

def connect_to_server():
    """Establece conexión con el servidor en la laptop"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    
    try:
        logger.info(f"Conectando a {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        logger.info("Conexión exitosa con el servidor")
        return sock
    except Exception as e:
        logger.error(f"Error de conexión: {str(e)}")
        sock.close()
        exit(1)

def send_frame(sock, frame):
    """Envía un frame comprimido al servidor"""
    try:
        # Compresión JPEG
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        data = pickle.dumps(buffer)
        
        # Cabecera (tamaño del frame)
        message = struct.pack("Q", len(data)) + data
        
        # Envío
        start_time = time.time()
        sock.sendall(message)
        transfer_time = time.time() - start_time
        
        # Log de rendimiento
        logger.debug(f"Frame enviado | Tamaño: {len(data)/1024:.1f} KB | "
                    f"Tiempo: {transfer_time*1000:.1f} ms")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar frame: {str(e)}")
        return False

def main():
    # Inicialización
    cap = setup_camera()
    sock = connect_to_server()
    
    # Estadísticas
    frame_count = 0
    start_time = time.time()
    
    try:
        logger.info("Iniciando transmisión... (Presiona 'q' para detener)")
        while True:
            # Captura de frame
            ret, frame = cap.read()
            if not ret:
                logger.warning("Frame vacío recibido de la cámara")
                continue
            
            # Envío y monitoreo
            if send_frame(sock, frame):
                frame_count += 1
                
                # Mostrar estadísticas cada 5 segundos
                elapsed_time = time.time() - start_time
                if elapsed_time >= 5:
                    current_fps = frame_count / elapsed_time
                    logger.info(
                        f"ESTADO: Transmitiendo | "
                        f"FPS: {current_fps:.1f}/{FPS_TARGET} | "
                        f"Resolución: {RESOLUTION[0]}x{RESOLUTION[1]} | "
                        f"Calidad JPEG: {JPEG_QUALITY}%"
                    )
                    frame_count = 0
                    start_time = time.time()
            
            # Preview local (opcional)
            cv2.imshow("RPi Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Transmisión detenida por el usuario")
                break
                
    except KeyboardInterrupt:
        logger.info("Interrupción por teclado recibida")
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)
    finally:
        # Liberación de recursos
        cap.release()
        sock.close()
        cv2.destroyAllWindows()
        logger.info("Recursos liberados. Programa terminado.")

if __name__ == "__main__":
    main()