import os
import psycopg2
from psycopg2 import OperationalError

def get_db_connection2():
    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        database="Actividad8",
        user="postgres",
        password="oliver"
    )
    return conn

# URL de la base de datos de las variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL')
def get_db_connection():
    try:
        # Conexión usando la URL de la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        print("Conexión a PostgreSQL exitosa")
        return conn
    except OperationalError as e:
        print(f"La conexión a PostgreSQL falló: {e}")
        return None