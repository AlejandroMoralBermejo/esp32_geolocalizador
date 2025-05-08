import machine
import network
import time
import urequests  # Necesario para hacer la petición HTTP POST

# Configuración de UART
TX_PIN = 26
RX_PIN = 27
BAUDRATE = 115200  # Baudrate actualizado
TIMEOUT = 3000

# Configuración WiFi
SSID = "alex"
PASSWORD = "atc-gaac"

# Endpoint a donde se enviarán los datos
ENDPOINT = "http://192.168.175.237:8000/api/registros/"

print("🚀 Inicializando comunicación UART...")

try:
    uart = machine.UART(2, baudrate=BAUDRATE, tx=TX_PIN, rx=RX_PIN, timeout=TIMEOUT)
    print("✅ UART inicializada correctamente.")
except Exception as e:
    print(f"❌ Error al inicializar UART: {e}")
    while True:
        pass  # Detener si hay fallo en UART

def enviar_comando(comando, espera=5):
    """Envía un comando AT y devuelve la respuesta decodificada."""
    try:
        print(f"\n📡 Enviando: {comando}")
        uart.write(comando + "\r\n")
        time.sleep(espera)
        respuesta = uart.read()
        
        if respuesta:
            resp_decodificada = respuesta.decode('utf-8', 'ignore').strip()
            print(f"📨 Respuesta: {resp_decodificada}")
            return resp_decodificada
        else:
            print("⚠️ No se recibió respuesta.")
            return ""
    except Exception as e:
        print(f"❌ Error enviando comando {comando}: {e}")
        return ""

def limpiar_datos_gnss(datos_gnss):
    """
    Extrae la línea válida de datos GNSS (la que comienza con '+CGPSINFO:')
    y elimina el prefijo innecesario.
    """
    for linea in datos_gnss.splitlines():
        if linea.startswith("+CGPSINFO:"):
            return linea.replace("+CGPSINFO: ", "").strip()
    raise Exception("No se encontró línea válida con +CGPSINFO:")


def post_registro(datos_gnss):
    """Extrae la fecha y coordenadas del mensaje GNSS y envía un POST al endpoint."""
    try:
        datos_gnss = limpiar_datos_gnss(datos_gnss)
        partes = datos_gnss.split(',')
        if len(partes) < 6:
            raise Exception("Formato de datos GNSS incorrecto.")
        
        lat = partes[0].strip()
        ns = partes[1].strip()
        lon = partes[2].strip()
        ew = partes[3].strip()
        fecha_raw = partes[4].strip()
        hora_raw = partes[5].strip()

        if not lat or not lon or not fecha_raw or not hora_raw:
            raise Exception("Datos incompletos o vacíos en la cadena GNSS.")

        lat_decimal = float(lat[:2]) + float(lat[2:])/60
        if ns == 'S': lat_decimal = -lat_decimal

        lon_decimal = float(lon[:3]) + float(lon[3:])/60
        if ew == 'W': lon_decimal = -lon_decimal

        dia = fecha_raw[0:2]
        mes = fecha_raw[2:4]
        año = "20" + fecha_raw[4:6]
        hora = hora_raw[0:2]
        minuto = hora_raw[2:4]
        segundo = hora_raw[4:6]
        fecha_formateada = f"{año}-{mes}-{dia}T{hora}:{minuto}:{segundo}"

        coordenadas = f"{lat_decimal},{lon_decimal}"

        cuerpo = {
            "fecha": fecha_formateada,
            "coordenadas": datos_gnss,
            "dispositivo_id": 1
        }

        print("📤 Enviando POST con el siguiente cuerpo:")
        print(cuerpo)

        respuesta = urequests.post(
            ENDPOINT,
            json=cuerpo,
            headers={"Content-Type": "application/json"}
        )

        print("✅ POST enviado. Código de estado:", respuesta.status_code)
        print(respuesta.text)
        respuesta.close()

    except Exception as e:
        print("❌ Error realizando POST:", e)
    finally:
        print("🔚 Finalizado envío de registro.")

def inicializar_gnss():
    """Inicializa y configura el GNSS correctamente."""
    try:
        print("Comprobar AT...")
        respuesta = enviar_comando("AT")
        
        if "OK" not in respuesta and "CPIN: SIM REMOVED" not in respuesta:
            print("❌ Error al comprobar AT.")
            return
        else:  
            print("AT comprobado correctamente.")
            
        # Reiniciar el módulo
        print("🔄 Reiniciando el módulo...")
        respuesta = enviar_comando("AT+CFUN=1,1", espera=5)
        if "OK" not in respuesta:
            print("❌ Error al reiniciar el módulo.")
            return
        
        print("🚀 Encendiendo GNSS...")
        respuesta = enviar_comando("AT+CGNSSPWR=1", espera=5)
        if "OK" not in respuesta:
            print("❌ Error al activar GNSS.")
            return

        print("⌛ Esperando hasta 5 minutos para estabilizar la señal...")
        for i in range(10):  
            time.sleep(30)  
            datos = enviar_comando("AT+CGPSINFO", espera=5)
            
            if datos and ",,,,,,,," not in datos:
                print("✅ GNSS ha obtenido FIX.")
                break
            else:
                print("⌛ GNSS aún sin FIX, esperando más...")

        print("📡 Obteniendo datos GNSS...")
        datos_gnss = enviar_comando("AT+CGPSINFO", espera=10)

        if "ERROR" in datos_gnss or ",,,,,,,," in datos_gnss:
            print("❌ No se pudo obtener datos GNSS.")
        else:
            print(f"✅ Datos GNSS obtenidos: {datos_gnss}")
            post_registro(datos_gnss)

    except Exception as e:
        print(f"❌ Error en la inicialización del GNSS: {e}")

    finally:
        print("🧹 Apagando GNSS y limpiando recursos...")
        enviar_comando("AT+CGNSSPWR=0", espera=2)  # Apagar GNSS
        print("✅ GNSS apagado correctamente.")
        uart.deinit()  # Desactivar UART
        print("✅ UART liberada. Fin del programa.")

def conectar_wifi():
    """Conecta la ESP32 a una red WiFi."""
    try:
        print("📶 Conectando a WiFi...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)

        tiempo_inicio = time.time()
        while not wlan.isconnected():
            if time.time() - tiempo_inicio > 15:  
                raise Exception("❌ No se pudo conectar a WiFi.")
            time.sleep(1)

        print(f"✅ Conectado a WiFi. IP: {wlan.ifconfig()[0]}")
        return True
    except Exception as e:
        print(f"❌ Error en WiFi: {e}")
        return False
    finally:
        if not wlan.isconnected():
            print("🛑 Apagando WiFi para evitar bloqueos.")
            wlan.active(False)

# Ejecutar inicialización con protección
try:
    if conectar_wifi():
        inicializar_gnss()
    else:
        print("⛔ GNSS no se ejecutará porque no hay conexión WiFi.")
except Exception as e:
    print(f"❌ Error fatal: {e}")
finally:
    print("🔄 Proceso terminado.")
