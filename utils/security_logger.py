"""Logger de eventos de seguridad con rotación de archivos.

Registra eventos importantes como intentos de login, accesos denegados,
cambios de rol, subidas rechazadas, etc., en un archivo de log rotativo.

Configuración:
    - Tamaño máximo por archivo: 5 MB.
    - Archivos rotados conservados: 3.
    - Directorio: logs/security.log en la raíz del proyecto.
"""

import os
import logging
import logging.handlers
from datetime import datetime

# ── Configuración ──────────────────────────────────────────────────────────

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'security.log')
MAX_BYTES = 5 * 1024 * 1024  # 5 MB por archivo
BACKUP_COUNT = 3              # Conservar hasta 3 archivos rotados


# ── Logger singleton ───────────────────────────────────────────────────────

_security_logger = None


def _get_logger():
    """Retorna el logger de seguridad, creándolo si es la primera vez.

    Implementa el patrón singleton para evitar duplicación de handlers
    en recargas del módulo. El logger escribe en un archivo rotativo
    con formato '[timestamp] LEVEL | message'.

    Returns:
        logging.Logger: Instancia del logger de seguridad.
    """
    global _security_logger

    if _security_logger is not None:
        return _security_logger

    os.makedirs(LOG_DIR, exist_ok=True)

    _security_logger = logging.getLogger('security')
    _security_logger.setLevel(logging.INFO)

    # Evitar duplicación de handlers si se recarga el módulo
    if not _security_logger.handlers:
        handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8',
        )
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        handler.setFormatter(formatter)
        _security_logger.addHandler(handler)

    return _security_logger


# ── Funciones públicas ─────────────────────────────────────────────────────


def log_login_failed(username, tipo_login, ip_address=None, reason=None):
    """Registra un intento de inicio de sesión fallido.

    Args:
        username: Nombre de usuario o identificación intentada.
        tipo_login: Tipo de login ('sgi', 'rrhh', 'estudiante').
        ip_address: Dirección IP desde donde se intentó (opcional).
        reason: Razón del fallo (opcional, ej: 'Credenciales inválidas').
    """
    extra = f" | IP: {ip_address}" if ip_address else ""
    extra += f" | Razón: {reason}" if reason else ""
    _get_logger().warning(
        f"LOGIN_FAILED | usuario={username} | tipo={tipo_login}{extra}"
    )


def log_login_success(username, tipo_login, ip_address=None):
    """Registra un inicio de sesión exitoso.

    Args:
        username: Nombre de usuario o identificación.
        tipo_login: Tipo de login ('sgi', 'rrhh', 'estudiante').
        ip_address: Dirección IP desde donde se conectó (opcional).
    """
    extra = f" | IP: {ip_address}" if ip_address else ""
    _get_logger().info(
        f"LOGIN_SUCCESS | usuario={username} | tipo={tipo_login}{extra}"
    )


def logout(user_id, username):
    """Registra un cierre de sesión.

    Args:
        user_id: Identificador único del usuario.
        username: Nombre de usuario visible.
    """
    _get_logger().info(f"LOGOUT | user_id={user_id} | usuario={username}")


def access_denied(user_id, username, endpoint, reason=None):
    """Registra un intento de acceso a un recurso no autorizado.

    Args:
        user_id: Identificador del usuario.
        username: Nombre de usuario.
        endpoint: Endpoint al que se intentó acceder.
        reason: Razón del bloqueo (opcional).
    """
    extra = f" | Razón: {reason}" if reason else ""
    _get_logger().warning(
        f"ACCESS_DENIED | user_id={user_id} | usuario={username} | "
        f"endpoint={endpoint}{extra}"
    )


def password_changed(user_id, username):
    """Registra un cambio de contraseña exitoso.

    Args:
        user_id: Identificador del usuario.
        username: Nombre de usuario.
    """
    _get_logger().info(
        f"PASSWORD_CHANGE | user_id={user_id} | usuario={username}"
    )


def role_change(user_id, username, new_role):
    """Registra un cambio de rol de usuario.

    Args:
        user_id: Identificador del usuario.
        username: Nombre de usuario.
        new_role: Nombre o ID del nuevo rol asignado.
    """
    _get_logger().info(
        f"ROLE_CHANGE | user_id={user_id} | usuario={username} | "
        f"nuevo_rol={new_role}"
    )


def log_employee_deleted(user_id, username, empleado_id):
    """Registra la eliminación definitiva de un empleado.

    Args:
        user_id: Identificador del usuario que ejecutó la acción.
        username: Nombre de usuario que ejecutó la acción.
        empleado_id: ID del empleado eliminado.
    """
    _get_logger().warning(
        f"EMPLOYEE_DELETE | user_id={user_id} | usuario={username} | "
        f"empleado_eliminado_id={empleado_id}"
    )


def log_employee_delete_failed(user_id, username, empleado_id, reason=None):
    """Registra un intento fallido de eliminar un empleado.

    Args:
        user_id: Identificador del usuario que intentó la acción.
        username: Nombre de usuario que intentó la acción.
        empleado_id: ID del empleado que se intentó eliminar.
        reason: Razón del fallo (ej: 'Contraseña incorrecta').
    """
    extra = f" | motivo={reason}" if reason else ""
    _get_logger().warning(
        f"EMPLOYEE_DELETE_FAILED | user_id={user_id} | usuario={username} | "
        f"empleado_id={empleado_id}{extra}"
    )


def resource_enumeration_attempt(user_id, username, endpoint, resource_id):
    """Registra un posible intento de enumeración de recursos.

    Args:
        user_id: Identificador del usuario.
        username: Nombre de usuario.
        endpoint: Endpoint al que se intentó acceder.
        resource_id: ID del recurso que se intentó enumerar.
    """
    _get_logger().warning(
        f"ENUMERATION | user_id={user_id} | usuario={username} | "
        f"endpoint={endpoint} | resource_id={resource_id}"
    )


def file_upload_rejected(user_id, username, filename, reason):
    """Registra un intento de subida de archivo rechazado por seguridad.

    Args:
        user_id: Identificador del usuario.
        username: Nombre de usuario.
        filename: Nombre del archivo rechazado.
        reason: Motivo del rechazo (magic bytes, extensión, etc.).
    """
    _get_logger().warning(
        f"UPLOAD_REJECTED | user_id={user_id} | usuario={username} | "
        f"archivo={filename} | razón={reason}"
    )


def csrf_rejection(user_id, username, endpoint):
    """Registra una petición rechazada por validación CSRF.

    Args:
        user_id: Identificador del usuario.
        username: Nombre de usuario.
        endpoint: Endpoint donde ocurrió el rechazo.
    """
    _get_logger().warning(
        f"CSRF_REJECTED | user_id={user_id} | usuario={username} | "
        f"endpoint={endpoint}"
    )


def rate_limit_hit(user_id, username, endpoint):
    """Registra cuando un usuario alcanza el límite de tasa.

    Args:
        user_id: Identificador del usuario.
        username: Nombre de usuario.
        endpoint: Endpoint donde se alcanzó el límite.
    """
    _get_logger().warning(
        f"RATE_LIMIT | user_id={user_id} | usuario={username} | "
        f"endpoint={endpoint}"
    )
