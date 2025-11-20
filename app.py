from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# 1. Configuración: Lista manual de tokens válidos
VALID_TOKENS = [
    "token-servicio-A",
    "token-servicio-B",
    "token-admin-secreto"
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

if __name__ == "__main__":
    # Se ejecuta la aplicación en modo debug para ver errores si aparecen
    app.run(debug=True, port=5000)
    