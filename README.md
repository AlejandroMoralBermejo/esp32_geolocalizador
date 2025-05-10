# esp32_geolocalizador

Proyecto de geolocalización con ESP32 y módulo GPS utilizando MicroPython.

## 📌 Descripción

Este proyecto permite obtener y mostrar las coordenadas geográficas (latitud y longitud) utilizando una placa ESP32 conectada a un módulo GPS (como el NEO-6M). El sistema se programa utilizando MicroPython, lo que permite ejecutar scripts ligeros directamente en el microcontrolador.

Nota: Las credenciales Wifi que están son de ejemplo, debes cambiarlas por las tuyas en caso de que utilizes wifi

## 🔧 Hardware requerido

- Placa ESP32
- Módulo GPS (ej. NEO-6M o similar)
- Fuente de alimentación o conexión USB

## 🔌 Conexiones

Módulo GPS | ESP32
-----------|--------
VCC        | 3.3V o 5V
GND        | GND
TX         | GPIO 26
RX         | GPIO 27


## 💻 Software utilizado

- Visual Studio Code o cualquier otro editor compatible con MicroPython
- Firmware MicroPython para ESP32
- Driver USB para la placa ESP32

## 📂 Estructura del proyecto

esp32_geolocalizador/
├── boot.py              -> Script de arranque
├── main.py              -> Lógica principal para leer datos del GPS
├── pymark.conf          -> Configuración de Pymark
└── README.txt           -> Documentación del proyecto

## 🚀 Cómo empezar

1. Flashea el firmware de MicroPython en tu ESP32.
   Usa herramientas como esptool (https://github.com/espressif/esptool).

2. Carga los scripts (boot.py, main.py) en tu placa ESP32 usando pymark u otro software.

3. Conecta el GPS como se indica arriba.

4. Reinicia el ESP32 y abre el monitor serie para ver las coordenadas GPS. *Importante aclarar que hay módulos GPS que requieren de estar en el aire libre* 

## 🧠 Funcionamiento

El ESP32 lee los datos NMEA del GPS a través de UART, los decodifica para obtener la latitud y longitud y los imprime por consola y los envia a una API. Puedes adaptar el código para almacenar estos datos, enviarlos por WiFi o mostrarlos en una pantalla.

## 🛠 Posibles mejoras

- Mostrar posición en una pantalla OLED o TFT
- Registrar datos en una tarjeta SD
- Crear una interfaz web de seguimiento en tiempo real

## 📃 Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

## 🙋‍♂️ Autor

Alejandro Moral Bermejo  
Contacto: alejandromoralbermejo@gmail.com  
GitHub: https://github.com/AlejandroMoralBermejo
