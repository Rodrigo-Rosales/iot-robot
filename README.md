# Robot Móvil de Seguimiento Autónomo con IA e IoT

Este proyecto presenta un robot móvil diseñado para realizar tareas de seguimiento autónomo de objetos, integrando Inteligencia Artificial (IA) e Internet de las Cosas (IoT). Utiliza una Raspberry Pi para la captura de video, procesamiento de visión por computadora en una PC remota y comunicación inalámbrica para el control del movimiento del robot.

## Arquitectura del Proyecto

El proyecto se divide en los siguientes módulos principales:

### `rpi_code/` (Código para Raspberry Pi)

Este directorio contiene el código que se ejecuta en la Raspberry Pi 4.

* **`sender/image_sender.py`**: Responsable de capturar video de la cámara conectada a la Raspberry Pi y transmitir los frames comprimidos (JPEG) en tiempo real a través de una red TCP/IP a la PC remota.
* **`receiver/control_receiver.py`**: Establece un servidor TCP/IP en la Raspberry Pi para recibir comandos de control (valores PWM para los motores) enviados desde la PC remota. Estos comandos se deserializan de formato JSON.
* **`motor_controller/motor_controller.py`**: Contiene la clase `MotorController` que gestiona el control de los motores del robot utilizando los pines GPIO de la Raspberry Pi y modulación por ancho de pulsos (PWM). Permite controlar la velocidad y dirección de cada motor de forma independiente.
* **`app.py`**: Script principal que inicia los hilos para la transmisión de video (`image_sender`) y la recepción de comandos de control (`control_receiver`), coordinando la operación del robot.

### `pc_code/` (Código para PC Remota)

Este directorio contiene el código que se ejecuta en la PC remota (con GPU NVIDIA para el procesamiento de IA).

* **`receiver/image_receiver.py`**: Actúa como un servidor TCP/IP, esperando la conexión de la Raspberry Pi y recibiendo los frames de video transmitidos. Los frames recibidos se decodifican y se ponen a disposición para el módulo de detección.
* **`detection/detector.py`**: Implementa la clase `Detector`, que carga un modelo de detección de objetos pre-entrenado (YOLOv8 nano) y lo utiliza para identificar el objeto objetivo (balón de baloncesto) en los frames de video. Calcula la posición central y el tamaño del bounding box del objeto detectado.
* **`sender/control_sender.py`**: Establece una conexión TCP/IP con la Raspberry Pi para enviar comandos de control (valores PWM para los motores) basados en el análisis de la detección. Los comandos se serializan en formato JSON antes de ser enviados.
* **`control/controller.py`**: Contiene la clase `Controller`, que toma la información de la detección (error en x, error en y, área del bounding box) y calcula los valores PWM necesarios para los motores del robot utilizando un modelo cinemático diferencial y ganancias definidas.
* **`app.py`**: Script principal que inicia el receptor de video (`image_receiver`), el detector de objetos (`detector`), el controlador (`controller`) y el emisor de comandos de control (`control_sender`) para orquestar el seguimiento autónomo.

### `config.py`

Este archivo contiene variables de configuración como direcciones IP, puertos de red, rutas de modelos, umbrales de confianza, dimensiones de los frames, parámetros del controlador, etc.

## ¡Explora y Colabora!

Te invitamos a explorar el código, entender su funcionamiento y contribuir a mejorar este proyecto. Si tienes ideas para nuevas funcionalidades, optimizaciones o corrección de errores, ¡no dudes en abrir un issue o enviar un pull request!

## Planes a Futuro

Este proyecto tiene un gran potencial de crecimiento. Algunos de los planes a futuro incluyen:

* **Motores más robustos:** Integrar motores con mayor torque y encoders para un control de movimiento más preciso y retroalimentado.
* **Detección de obstáculos:** Incorporar sensores ultrasónicos u otros sensores de proximidad para permitir al robot evitar obstáculos de forma autónoma.
* **Algoritmo de búsqueda:** Implementar un algoritmo de búsqueda inteligente para que el robot pueda volver a localizar el objetivo si lo pierde de vista temporalmente.
* **Control vertical de la cámara:** Añadir la capacidad de controlar la orientación vertical de la cámara para corregir errores de seguimiento en el eje Y de manera activa.
* **Mapeo y localización:** Extender las capacidades del robot para construir un mapa simple de su entorno y localizarse dentro de él.
* **Optimización del modelo de IA:** Explorar técnicas de cuantización o poda del modelo de IA para reducir los requisitos de cómputo y potencialmente ejecutarlo en la Raspberry Pi.
* **Interfaz de usuario:** Desarrollar una interfaz gráfica de usuario (GUI) para facilitar la configuración, el control y la visualización del estado del robot.
* **Simulación:** Crear un entorno de simulación para probar algoritmos y funcionalidades antes de desplegarlos en el hardware real.

¡Tu contribución puede hacer que este proyecto avance aún más!
