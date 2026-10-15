import os
import time
from urllib.parse import quote_plus
 
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine, text
 
load_dotenv()
 
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "taller_python")
 
# Cambia "esteban" por tu primer nombre (minusculas, sin tildes)
TABLA = "personas_esteban"
TOTAL = 100_000
LOTE = 20_000
 
fake = Faker("es_CO")
 
 
def generar_persona():
    return {
        "nombre": fake.name(),
        "correo": fake.email(),
        "fecha_nacimiento": fake.date_of_birth(minimum_age=18, maximum_age=75),
        "ciudad": fake.city(),
        "telefono": fake.phone_number(),
        "direccion": fake.address().replace("\n", ", "),
        "profesion": fake.job(),
    }
 
 
def main():
    inicio = time.time()

    servidor = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
 
    # 1. Crear la base de datos si no existe
    engine_base = create_engine(servidor)
    with engine_base.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
 
    # 2. Conectar a la base y crear la tabla si no existe
    engine = create_engine(f"{servidor}/{DB_NAME}?charset=utf8mb4")
    with engine.begin() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS `{TABLA}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL,
                correo VARCHAR(150) NOT NULL,
                fecha_nacimiento DATE NOT NULL,
                ciudad VARCHAR(80) NOT NULL,
                telefono VARCHAR(40) NOT NULL,
                direccion VARCHAR(255) NOT NULL,
                profesion VARCHAR(120) NOT NULL
            )
        """))
        # Vacia la tabla para que, al ejecutar varias veces, siempre queden 100.000
        conn.execute(text(f"TRUNCATE TABLE `{TABLA}`"))
 
    # 3. Insertar los registros por lotes
    insert = text(f"""
        INSERT INTO `{TABLA}`
        (nombre, correo, fecha_nacimiento, ciudad, telefono, direccion, profesion)
        VALUES
        (:nombre, :correo, :fecha_nacimiento, :ciudad, :telefono, :direccion, :profesion)
    """)
    with engine.begin() as conn:
        for insertados in range(LOTE, TOTAL + 1, LOTE):
            conn.execute(insert, [generar_persona() for _ in range(LOTE)])
            print(f"Insertados {insertados:,} / {TOTAL:,}")
 
    # 4. Verificar
    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) FROM `{TABLA}`")).scalar()
    print(f"Registros en {TABLA}: {total:,}")

    tiempo_total = time.time() - inicio  
    print(f"Tiempo total de ejecucion: {tiempo_total:.2f} segundos")  
 
 
if __name__ == "__main__":
    main()