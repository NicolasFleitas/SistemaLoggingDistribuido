import requests
import time
import random
from datetime import datetime

# 1. Configuración del target
SERVER_URL = "http://127.0.0.1:5000/logs"



# Lista de tokens válidos
TOKENS = [
    "token-servicio-A",
    "token-servicio-B"
]

# 2. Datos falsos para generar variedad
SERVICIOS = ["auth-service", "payment-api", "email-worker", "database-node"]
NIVELES = ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]
MENSAJES = [
    "Conexión establecida correctamente.",
    "Tiempo de espera agotado (Timeout).",
    "Usuario 'admin' intentó ingresar.",
    "Error de sintaxis en consulta SQL.",
    "Pago rechazado por fondos insuficientes.",
    "El servidor se está reiniciando."
]

def generar_log_falso():
    # Crea un diccionario con datos aleatorios pero con sentido
    return {
        "service": random.choice(SERVICIOS),
        "severity": random.choice(NIVELES),
        "message": random.choice(MENSAJES),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def simiular_trafico(cantidad_logs=50):
    print(f"--- Iniciando simulación de {cantidad_logs} logs --- ")

    for i in range(cantidad_logs):
        # Preparamos los datos
        log_data = generar_log_falso()

        # Elegimos un token al azar para simular distintos clientes autenticados
        token_actual = random.choice(TOKENS)
        headers = {"Authorization": f"Token {token_actual}"}

        try: 
            # Enviamos el POST requests
            response = requests.post(SERVER_URL, json=log_data, headers=headers)

            # Feedback visual en la consola
            if response.status_code == 201:
                print(f"[{i+1}/{cantidad_logs}] Enviado: {log_data['service']} -> OK")
            else:
                print(f"[{i+1}/{cantidad_logs}] Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")
            break
        
        # Esperamos un tiempo aleatorio entre 0.1 y 0.5 segundos para parecer tráfico real
        time.sleep(random.uniform(0.1,0.5))
    
    print("--- Simulación finalizada ---")

if __name__ == "__main__":
    simiular_trafico(1000)

