import os
import psycopg2
from psycopg2 import OperationalError


def get_db_connection():
    # Asegurarse de que la base de datos existe antes de conectarse
    # Conectar a la base de datos existente
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="oliver"
    )
    return conn

# Obtener la URL de la base de datos de las variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL')
def get_db_connection2():
    try:
        # Conexión usando la URL de la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        print("Conexión a PostgreSQL exitosa")
        return conn
    except OperationalError as e:
        print(f"La conexión a PostgreSQL falló: {e}")
        return None