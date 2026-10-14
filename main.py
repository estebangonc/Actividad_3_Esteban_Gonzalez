import os
import time
 
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
 
# Cargar las credenciales desde el archivo .env
load_dotenv()
 
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "taller_python")
 
# Reemplaza "esteban" por tu primer nombre real, en minusculas y sin tildes.
NOMBRE_ESTUDIANTE = "esteban"
TABLA_NOMBRE = f"personas_{NOMBRE_ESTUDIANTE}"
 
TOTAL_REGISTROS = 100_000
TAMANO_LOTE = 10_000
 
# Faker con datos de Colombia
fake = Faker("es_CO")
 
 
def construir_url(base_datos=None):
    """Construye la URL de conexion. URL.create escapa caracteres especiales
    en la contrasena (@, :, /, etc.) que romperian un string armado a mano."""
    return URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=base_datos,
        query={"charset": "utf8mb4"},
    )
 
 
def crear_base_datos_si_no_existe():
    """Se conecta al servidor MySQL y crea la base de datos si no existe."""
    engine_base = create_engine(construir_url())
    try:
        with engine_base.begin() as conn:
            conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
    finally:
        engine_base.dispose()
    print(f"Base de datos '{DB_NAME}' verificada o creada.")
 
 
def crear_tabla(engine):
    """Crea la tabla personas_<nombre> con clave primaria y 7 atributos Faker."""
    sql_crear_tabla = f"""
    CREATE TABLE IF NOT EXISTS `{TABLA_NOMBRE}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(120) NOT NULL,
        correo VARCHAR(150) NOT NULL,
        fecha_nacimiento DATE NOT NULL,
        ciudad VARCHAR(80) NOT NULL,
        telefono VARCHAR(40) NOT NULL,
        direccion VARCHAR(255) NOT NULL,
        profesion VARCHAR(120) NOT NULL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    with engine.begin() as conn:
        conn.execute(text(sql_crear_tabla))
    print(f"Tabla '{TABLA_NOMBRE}' verificada o creada.")
 
 
def generar_registro():
    """Genera un registro sintetico (un diccionario) con datos de Faker."""
    return {
        "nombre": fake.name(),
        "correo": fake.email(),
        "fecha_nacimiento": fake.date_of_birth(minimum_age=18, maximum_age=75),
        "ciudad": fake.city(),
        "telefono": fake.phone_number(),
        "direccion": fake.address().replace("\n", ", "),
        "profesion": fake.job(),
    }
 
 
def contar_registros(engine):
    """Devuelve la cantidad de filas actuales de la tabla."""
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM `{TABLA_NOMBRE}`")).scalar()
 
 
def generar_e_insertar_datos(engine, total_registros=TOTAL_REGISTROS, tamano_lote=TAMANO_LOTE):
    """Inserta registros por lotes hasta que la tabla tenga `total_registros`.
 
    Si la tabla ya tiene filas (por una ejecucion anterior), solo inserta las
    que faltan, de modo que el resultado final sea exactamente 100.000.
    """
    existentes = contar_registros(engine)
    faltantes = total_registros - existentes
 
    if faltantes <= 0:
        print(f"La tabla ya tiene {existentes:,} registros. No se insertan datos nuevos.")
        return
 
    print(f"Registros existentes: {existentes:,}. Se insertaran {faltantes:,}.")
 
    sql_insert = text(
        f"""
        INSERT INTO `{TABLA_NOMBRE}`
        (nombre, correo, fecha_nacimiento, ciudad, telefono, direccion, profesion)
        VALUES
        (:nombre, :correo, :fecha_nacimiento, :ciudad, :telefono, :direccion, :profesion)
        """
    )
 
    tiempo_inicio = time.time()
    insertados = 0
 
    while insertados < faltantes:
        cantidad = min(tamano_lote, faltantes - insertados)
        lote = [generar_registro() for _ in range(cantidad)]
 
        # Una lista de diccionarios se ejecuta como insercion por lotes
        with engine.begin() as conn:
            conn.execute(sql_insert, lote)
 
        insertados += cantidad
        print(f"  Insertados {insertados:,} / {faltantes:,} registros")
 
    tiempo_total = time.time() - tiempo_inicio
    print(f"Insercion completada en {tiempo_total:.2f} segundos.")
 
 
def main():
    try:
        crear_base_datos_si_no_existe()
        engine = create_engine(construir_url(DB_NAME), pool_pre_ping=True)
        try:
            crear_tabla(engine)
            generar_e_insertar_datos(engine)
            print(f"Total de registros en '{TABLA_NOMBRE}': {contar_registros(engine):,}")
        finally:
            engine.dispose()
    except Exception as error:
        print(f"Error durante la ejecucion del script: {error}")
        raise SystemExit(1)
 
 
if __name__ == "__main__":
    main()