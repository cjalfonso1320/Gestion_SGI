"""Utilidades para el manejo seguro de contraseñas.

Proporciona funciones para generar hashes y verificar contraseñas
usando Werkzeug, que implementa pbkdf2:sha256 de forma segura.
"""

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña proporcionada.

    Usa el algoritmo pbkdf2:sha256 de Werkzeug con un salt aleatorio.

    Args:
        password: Contraseña en texto plano a hashear.

    Returns:
        str: Hash de la contraseña en formato Werkzeug.
    """
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash almacenado.

    Compara la contraseña en texto plano con el hash previamente generado.

    Args:
        password: Contraseña en texto plano a verificar.
        password_hash: Hash almacenado previamente generado.

    Returns:
        bool: True si la contraseña coincide, False en caso contrario.
    """
    return check_password_hash(password_hash, password)
