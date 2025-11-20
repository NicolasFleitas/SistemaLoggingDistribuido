import requests
import time
import random
from datetime import datetime

# 1. Configuración del target
SERVER_URL = "http://127.0.0.1:5000/logs"

CONFIG_SERVICIOS = {
    "auth-service":  "token-auth-seguro-111",
    "payment-api":   "token-pagos-seguro-222",
    "email-worker":  "token-email-seguro-333",
    "database-node": "token-db-seguro-444"
}

# 2. Datos falsos para generar variedad
NIVELES = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]

MENSAJES_POR_SERVICIO = {
    "auth-service": [
        "Usuario inicio sesion exitosamente.",
        "Intento de login fallido: pass incorrecta.",
        "Token expirado, solicitando refresh.",
        "Usuario bloqueado por seguridad."
    ],
    "payment-api": [
        "Transaccion #8821 aprobada.",
        "Pago rechazado: Fondos insuficientes.",
        "Timeout conectando con el banco.",
        "Reembolso procesado."
    ],
    "email-worker": [
        "Email enviado correctamente.",
        "Error SMTP: Host inalcanzable.",
        "Generando reporte mensual en PDF.",
        "Cola de correos procesada."
    ],
    "database-node": [
        "Query ejecutada en 12ms.",
        "Error de conexion: Too many connections.",
        "Backup realizado con exito.",
        "Indice reconstruido."
    ]
}

def generar_log_falso(nombre_servicio):
  
    lista_mensajes = MENSAJES_POR_SERVICIO[nombre_servicio]
    mensaje = random.choice(lista_mensajes)

    nivel = random.choice(NIVELES)

    if "Error" in mensaje or "rechazado" in mensaje or "fallido" in mensaje:
        nivel = "ERROR"

    return {
    "service": nombre_servicio,
    "severity": nivel,
    "message": mensaje,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# Función principal del simulador de tráfico
def simular_trafico(cantidad_logs=50):
    print(f"--- Iniciando simulación de {cantidad_logs} logs --- ")

    nombres_servicios = list(CONFIG_SERVICIOS.keys())
    
    for i in range(cantidad_logs):

        # Elegimos el servicio..
        servicio_actual = random.choice(nombres_servicios)

        # Obtenemos su token especifico
        token_actual = CONFIG_SERVICIOS[servicio_actual]
        
        # Generamos el log falso coherente para el servicio
        log_data = generar_log_falso(servicio_actual) # Generamos un log falso para ese servicio
        headers = {
            "Authorization": f"Token {token_actual}",
            "Content-Type": "application/json" 
        }

        try: 
            # Enviamos el POST requests
            response = requests.post(SERVER_URL, json=log_data, headers=headers)

            # Feedback visual en la consola
            if response.status_code == 201:
                #print(f"[{i+1}/{cantidad_logs}] Enviado: {log_data['service']} -> OK")
                print(f"[{i+1}] {servicio_actual} (Token: ...{token_actual[-3:]}) -> OK")
            else:
                print(f"[{i+1}/{cantidad_logs}] Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")
            break
        
        # Esperamos un tiempo aleatorio entre 0.1 y 0.5 segundos para parecer tráfico real
        time.sleep(random.uniform(0.1,0.5))
    
    print("--- Simulación finalizada ---")

if __name__ == "__main__":
    simular_trafico(100)

