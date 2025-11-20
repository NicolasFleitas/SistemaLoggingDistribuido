from flask import Flask, request, jsonify
from functools import wraps
import sqlite3

app = Flask(__name__)

# 1. Configuración: Lista manual de tokens válidos
VALID_TOKENS = [
    "token-auth-seguro-111",
    "token-pagos-seguro-222",
    "token-email-seguro-333",
    "token-db-seguro-444",
    "token-admin-secreto" # Para pruebas 
]
# 2. El Decorador de Autenticación (EL GRAN GUARDIÁN)

def require_api_token(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Obtenemos el header de autorización
        auth_header = request.headers.get('Authorization')

        # Verificamos que el header existe y tenga formato correcto: "Token XXXXX"
        if auth_header and auth_header.startswith("Token "):
            token = auth_header.split(" ")[1] # Separamos la palabra "Token" de la clave

            if token in VALID_TOKENS:
                return func(*args, **kwargs) # ¡Pasa nomás, adelante!
            
        # Si falla cualquier validación, devolvemos el error específico
        return jsonify({"error": "Lo siento, no estás autorizado"}), 401
    
    return decorated_function

# 3. Ruta de prueba (Health Check)
# Esta ruta solo sirve para ver si la seguridad funciona.
@app.route('/status', methods=['GET'])
@require_api_token # Uso del decorador para proteger esta ruta
def server_status():
    return jsonify({"mensaje": "El sistema esta online y seguro"}), 200

# 4. Ruta para recibir logs
@app.route('/logs', methods=['POST'])
@require_api_token # 1. Primero se verifica la seguridad
def create_log():
    # 2. Obtenemos los datos JSON enviados por el cliente
    data = request.get_json()     

    if not data:
        return jsonify({"error:" "Payload invalido, se esperaba JSON"}), 400
    
    # 3. Validación básica: ¿Están los campos obligatorios?
    required_fields = ['service', 'severity', 'message', 'timestamp']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo obligatorio: {field}"}), 400
    
    # 4.Guardado en Base de Datos
    try:
        conn = sqlite3.connect('logs.db')
        cursor = conn.cursor()
        
        # Insertamos los datos
        # NOTA: No insertamos 'received_at', la DB lo pone sola por defecto
        query = '''
            INSERT INTO logs (service_name, severity, message, timestamp)
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(query,(
            data['service'],
            data['severity'],
            data['message'],
            data['timestamp']
        ))

        conn.commit() # Guardamos los cambios
        conn.close() # Cerramos conexión para liberar el archivo

        return jsonify({"message": "Log guardado exitosamente"}), 201
    except Exception as e:
        # Si algo explota en la base de datos, avisamos sin romper el servidor
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

# ENDPOINT DE CONSULTA DE LOGS 
@app.route('/logs', methods=['GET'])
@require_api_token
def get_logs():
    # 1. Capturamos los parámetros de la URL (Query Parameters)
    # Ejemplo: /logs?timestamp_start=2023-01-01
    ts_start = request.args.get('timestamp_start')
    ts_end = request.args.get('timestamp_end')
    rc_start = request.args.get('received_at_start')
    rc_end = request.args.get('received_at_end')

    # 2. Construcción de la Query dinámica
    # "WHERE 1=1" es un truco común: es un condición siempre verdadera
    # que nos permite agregar más condiciones con "AND" sin preocuparnos si es la primera
    query = "SELECT * FROM logs WHERE 1=1"
    params = [] 

    # Agregamos filtros solos si el usuario los envió
    if ts_start:
        query += " AND timestamp >= ?"
        params.append(ts_start)
    
    if ts_end:
        query += " AND timestamp <= ?"
        params.append(ts_end)
    
    if rc_start:
        query += " AND received_at >= ?"
        params.append(rc_start)
    
    if rc_end:
        query += " AND received_at <= ?"
        params.append(rc_end)
    
    # Ordenamos para ver lo más reciente primero
    query += " ORDER BY timestamp DESC"

    # 3. Ejecución y Formateo
    try:
        conn = sqlite3.connect('logs.db')
        # Hace que SQLite devuelva objetos parecidos a diccionarios en lugar de tuplas numéricas
        conn.row_factory = sqlite3.Row # Esto permite acceder a las columnas por nombbre
        cursor = conn.cursor()

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convertimos las filas de la DB a una lista de diccionarios (JSON)
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "service": row["service_name"],
                "severity": row["severity"],
                "message": row["message"],
                "timestamp": row["timestamp"],
                "received_at": row["received_at"]
            })        

        conn.close() # Cerramos conexión para liberar el archivo

        # 4. Respuesta clara y ordenada
        return jsonify({
            "count": len(results),
            "logs": results
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar: {str(e)}"}), 500

if __name__ == "__main__":
    # Se ejecuta la aplicación en modo debug para ver errores si aparecen
    app.run(debug=True, port=5000)
    