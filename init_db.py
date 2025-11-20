import sqlite3

def init_db():
    # Conectamos a la base de datos (se crea si no existe)
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()

    # Creamos la tabla si no existe
    # Nota: Agrego 'received_at' para registrar la hora de recepción del log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        severity TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')

    conn.commit()
    conn.close()
    print("Base de datos 'logs.db' inicializada correctamente")

if __name__ == '__main__':
    init_db()


