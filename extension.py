"""Extensiones globales de Flask inicializadas para la aplicación.

Proporciona instancias compartidas de:
    - MySQL: Conexión a la base de datos MySQL mediante Flask-MySQLdb.
    - Limiter: Limitador de tasa de peticiones (rate limiting) con Flask-Limiter.

Parchea pymysql como reemplazo de MySQLdb para compatibilidad.
"""

import pymysql


pymysql.install_as_MySQLdb()


from flask_mysqldb import MySQL
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


mysql = MySQL()
"""Conexión a la base de datos MySQL.

Se inicializa en app.py con mysql.init_app(app).
Usa las credenciales definidas en config.Config.
"""

def _get_client_key():
    """Retorna la IP del cliente, o None si el usuario está autenticado.

    Si el usuario tiene sesión activa (autenticado), retorna None para
    eximirlo del rate limiting. Esto evita que usuarios internos que
    trabajan activamente en la aplicación se queden sin requests.
    Solo se limita a usuarios no autenticados (IP anónima).
    """
    try:
        from flask_login import current_user
        if current_user.is_authenticated:
            return None
    except RuntimeError:
        pass
    return get_remote_address()


limiter = Limiter(
    _get_client_key,
    default_limits=["500 per day", "200 per hour"],
)
"""Limitador de tasa de peticiones.

Los usuarios autenticados (con sesión activa) quedan exentos del
rate limiting. Solo se aplica a peticiones anónimas.
Límites para anónimos:
    - 500 peticiones por día.
    - 200 peticiones por hora.
Se pueden aplicar límites más estrictos por endpoint con @limiter.limit().
"""
