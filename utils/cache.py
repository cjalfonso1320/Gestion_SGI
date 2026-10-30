"""Caché simple con TTL (time-to-live) para resultados de funciones.

Almacena en memoria los resultados de funciones por un tiempo limitado,
evitando consultas repetitivas a la base de datos. Es thread-safe.

Uso:
    from utils.cache import cache_result

    @cache_result(ttl_seconds=30)
    def total_empleados():
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM users_rrhh WHERE activo = 1")
        return cur.fetchone()[0]

El decorador cachea automáticamente el resultado y lo invalida
después de ttl_seconds segundos.
"""

import time
import functools
import threading


class TTLCache:
    """Caché thread-safe con TTL (time-to-live).

    Almacena resultados de funciones en memoria con tiempo de expiración.
    Utiliza un lock para garantizar seguridad en entornos multi-thread.

    Attributes:
        _data: Diccionario interno con los valores cacheados.
        _lock: Lock de threading para operaciones atómicas.
    """

    def __init__(self):
        """Inicializa la caché vacía con su lock correspondiente."""
        self._data = {}
        self._lock = threading.Lock()

    def get(self, key):
        """Obtiene un valor de la caché por su clave.

        Args:
            key: Clave del valor a recuperar.

        Returns:
            El valor almacenado o None si la clave no existe.
        """
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            result, timestamp = entry
            return result

    def set(self, key, result, timestamp):
        """Almacena un valor en la caché asociado a una clave.

        Args:
            key: Clave bajo la cual almacenar el valor.
            result: Valor a almacenar.
            timestamp: Marca de tiempo de la inserción (time.time()).
        """
        with self._lock:
            self._data[key] = (result, timestamp)

    def has_valid(self, key, ttl, now):
        """Verifica si una clave tiene un valor vigente en la caché.

        Args:
            key: Clave a verificar.
            ttl: Tiempo de vida en segundos desde la inserción.
            now: Timestamp actual para comparar.

        Returns:
            bool: True si la clave existe y no ha expirado.
        """
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return False
            _, timestamp = entry
            return (now - timestamp) < ttl

    def clear(self):
        """Limpia completamente la caché eliminando todas las entradas."""
        with self._lock:
            self._data.clear()


# Instancia global compartida por todos los decoradores
global_cache = TTLCache()


def cache_result(ttl_seconds=30):
    """Decorador que cachea el resultado de una función durante un tiempo.

    Thread-safe: usa un lock para evitar race conditions en producción
    con múltiples workers/threads.

    Si la función tiene argumentos, se genera una clave compuesta para
    diferenciar distintas invocaciones.

    Args:
        ttl_seconds: Tiempo de vida de la caché en segundos (default: 30).

    Returns:
        callable: Decorador que envuelve la función con caché.

    Ejemplo:
        @cache_result(ttl_seconds=60)
        def obtener_datos():
            return consulta_pesada_bd()

        # Invalidación manual tras un write:
        obtener_datos.invalidate()
    """
    def decorator(func):
        cache_key = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Si tiene argumentos dinámicos, genera clave compuesta
            if args or kwargs:
                key = (cache_key, args, tuple(sorted(kwargs.items())))
            else:
                key = cache_key

            now = time.time()

            # Verifica si hay un valor válido en caché
            if global_cache.has_valid(key, ttl_seconds, now):
                return global_cache.get(key)

            # Ejecuta la función y cachea el resultado
            result = func(*args, **kwargs)
            global_cache.set(key, result, now)
            return result

        def invalidate():
            """Invalida manualmente la caché de esta función.

            Limpia toda la caché global por simplicidad.
            """
            global_cache.clear()

        wrapper.invalidate = invalidate
        return wrapper
    return decorator
