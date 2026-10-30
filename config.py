"""Configuración central de la aplicación Flask.

Carga variables de entorno desde un archivo .env (sin sobrescribir
variables del sistema) y expone la clase Config con los parámetros
necesarios para la conexión a la base de datos MySQL y el secreto
de la aplicación.

Variables de entorno requeridas:
    SECRET_KEY: Clave secreta de Flask.
    MYSQL_HOST: Host del servidor MySQL.
    MYSQL_USER: Usuario de base de datos.
    MYSQL_PASSWORD: Contraseña del usuario.
    MYSQL_DB: Nombre de la base de datos.
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def load_local_env():
    """Carga un archivo .env simple sin sobrescribir variables ya definidas.

    Lee cada línea del archivo .env, ignora comentarios (#) y líneas vacías,
    y establece la variable de entorno solo si no existe previamente en os.environ.

    El archivo .env debe estar en el mismo directorio que este archivo.
    """
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        # Elimina comentarios inline (# ...) que estén después del valor
        value = value.split("#")[0] if "#" in value else value
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


def required_env(name):
    """Obtiene una variable de entorno o lanza un error si falta.

    Args:
        name: Nombre de la variable de entorno requerida.

    Returns:
        str: Valor de la variable de entorno.

    Raises:
        RuntimeError: Si la variable no está definida en el entorno.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno obligatoria: {name}. "
            "Definela en el sistema o en un archivo .env local."
        )
    return value


load_local_env()


class Config:
    """Configuración principal de la aplicación Flask.

    Attributes:
        SECRET_KEY: Clave secreta para firmar cookies de sesión.
        MYSQL_HOST: Host del servidor MySQL.
        MYSQL_USER: Usuario de conexión a la base de datos.
        MYSQL_PASSWORD: Contraseña del usuario MySQL.
        MYSQL_DB: Nombre de la base de datos.
        BASE_URL: URL base del sitio (ej: https://midominio.com/gestion).
                  Si no se define, se genera automáticamente con _external=True.
    """
    SECRET_KEY = required_env("SECRET_KEY")
    MYSQL_HOST = required_env("MYSQL_HOST")
    MYSQL_USER = required_env("MYSQL_USER")
    MYSQL_PASSWORD = required_env("MYSQL_PASSWORD")
    MYSQL_DB = required_env("MYSQL_DB")
    BASE_URL = os.getenv("BASE_URL", "").rstrip("/")

    # --- SMTP (correo electrónico) ---
    # Se cargan desde variables de entorno o archivo .env
    # En producción (IIS), configúralas como variables de entorno del sistema Windows
    SMTP_SERVER = os.getenv('SMTP_SERVER', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

    # Límite de tamaño de subida de archivos (5GB para videos largos)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024  # 5 GB en bytes

    # Tiempo de espera largo para subidas grandes
    # (Se puede sobrescribir desde IIS/nginx si es necesario)
