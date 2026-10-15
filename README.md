# Taller U3 - Automatizacion de BD con Python, Faker y Git

Bases de Datos para Ciencia de Datos - Universidad de Antioquia

## Descripcion

Script en Python que automatiza la creacion y el poblado de una base de datos
MySQL local. Usa SQLAlchemy para la conexion y Faker para generar datos
sinteticos en espanol de Colombia.

Al ejecutarlo, el script:

1. Lee las credenciales de MySQL desde un archivo `.env` (no se sube al repositorio).
2. Crea la base de datos si no existe.
3. Crea la tabla `personas_esteban` si no existe.
4. Genera 100.000 registros con Faker y los inserta por lotes de 20.000.
5. Muestra el total de registros de la tabla al terminar.

El proceso es idempotente: si se ejecuta varias veces, la tabla queda con
100.000 registros y no se acumulan duplicados.

## Estructura de la tabla

Tabla `personas_esteban`:

| Columna          | Tipo         | Descripcion                      |
|------------------|--------------|----------------------------------|
| id               | INT (PK)     | Clave primaria autoincremental   |
| nombre           | VARCHAR      | Nombre completo (Faker)          |
| correo           | VARCHAR      | Correo electronico (Faker)       |
| fecha_nacimiento | DATE         | Fecha de nacimiento (Faker)      |
| ciudad           | VARCHAR      | Ciudad (Faker)                   |
| telefono         | VARCHAR      | Numero de telefono (Faker)       |
| direccion        | VARCHAR      | Direccion (Faker)                |
| profesion        | VARCHAR      | Profesion (Faker)                |

## Requisitos

- Python 3.10 o superior
- MySQL en ejecucion en local
- DBeaver (para validar los datos)
- Git

## Instalacion

1. Clonar el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd <carpeta_del_repositorio>
```

2. Crear y activar un entorno virtual:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Configuracion

Copiar la plantilla `.env.example` a `.env` y completar los datos reales:

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Variables del archivo `.env`:

```
DB_USER=root
DB_PASSWORD=tu_contrasena_aqui
DB_HOST=localhost
DB_PORT=3306
DB_NAME=taller_python
```

El archivo `.env` esta en `.gitignore`, por lo que las credenciales reales
nunca se suben al repositorio.

## Ejecucion

```bash
python main.py
```

## Validacion

Desde DBeaver, ejecutar:

```sql
SELECT COUNT(*) FROM personas_esteban;
```

El resultado esperado es `100000`.

## Tecnologias

- Python
- SQLAlchemy
- PyMySQL
- Faker
- python-dotenv
- MySQL