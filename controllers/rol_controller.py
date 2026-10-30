"""Controlador de roles del sistema SGI.

Proporciona funciones CRUD para la gestión de roles, incluyendo
la definición de procesos y rutas de imágenes asociadas a cada rol.
"""

from functools import lru_cache

from extension import mysql


def list_roles():
    """Obtiene todos los roles registrados en el sistema.

    Returns:
        list: Lista de tuplas (id, rol) con todos los roles.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, rol FROM rol")
    roles = cur.fetchall()
    cur.close()
    return roles


def cuenta():
    """Cuenta el número total de roles registrados.

    Returns:
        int: Cantidad de roles en la base de datos.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM rol")
    total = cur.fetchone()[0]
    cur.close()
    return total


def insertar_rol(rol):
    """Inserta un nuevo rol en la base de datos.

    Args:
        rol: Nombre del nuevo rol a crear.
    """
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO rol (rol) VALUES (%s)", (rol,))
    mysql.connection.commit()
    cur.close()
    nombre_rol.cache_clear()


def modificar_rol(id, rol):
    """Actualiza el nombre de un rol existente.

    Args:
        id: ID del rol a modificar.
        rol: Nuevo nombre para el rol.
    """
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE rol SET rol = %s WHERE id = %s", (rol, id))
        mysql.connection.commit()
        nombre_rol.cache_clear()
    except Exception as e:
        print("Error en modificacion:", e)
    finally:
        cur.close()


def elimina_rol(id):
    """Elimina un rol de la base de datos por su ID.

    Args:
        id: ID del rol a eliminar.
    """
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM rol WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    nombre_rol.cache_clear()


@lru_cache(maxsize=128)
def nombre_rol(rol_id):
    """Obtiene el nombre de un rol por su ID, con caché LRU.

    Los resultados se cachean para evitar consultas repetitivas a la
    base de datos. La caché se invalida cuando se crea, modifica o
    elimina un rol.

    Args:
        rol_id: ID del rol a consultar.

    Returns:
        str: Nombre del rol, o None si no existe.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT rol FROM rol WHERE id = %s", (rol_id,))
    nombre = cur.fetchone()
    cur.close()
    return nombre[0] if nombre else None


# Mapeo de procesos asociados a cada rol de producción/administración
# NOTA: Los nombres de proceso NO llevan sufijo del banco (ej: 'Convenios', no 'Convenios_Bancolombia')
# porque así es como se almacenan en matriz_activo.
PROCESOS_ROL = {
    2: ['Bancolombia', 'Convenios', 'Departamentales', 'Distritales', 'Nacionales'],
    4: ['Occidente'],
    5: ['Agrario', 'Nacionales'],
    6: ['Davivienda', 'Convenios', 'Departamentales', 'Distritales', 'Nacionales'],
    7: ['Itau'],
    8: ['Gestión Humana'],
    9: ['Recurso Tecnologico', 'T.I.'],
    10: ['Popular', 'Convenios', 'Departamentales', 'Nacionales'],
    11: ['AvVillas', 'Complementacion', 'Convenios', 'Departamentales', 'Distritales', 'Libranzas', 'Nacionales', 'Radicacion', 'Tarjetas'],
    12: ['Bancoomeva'],
    13: ['CajaSocial', 'Nacionales', 'Recaudos'],
    14: ['Gestion de Sistemas', 'Sistemas'],
    15: ['Recurso Financiero'],
    16: ['Sistema de Gestion Integrado', 'SGI'],
    17: ['Seguridad y Salud en el Trabajo'],
    18: ['Gestion Comercial', 'Comercial'],
    19: ['Gestion Direccion', 'Alta Dirección'],
    20: ['Sistema de Autocontrol Sagrilaft'],
    21: ['Sistema de Gestion Ambiental'],
}

# Logo/imagen asociada a cada rol para mostrar en la interfaz
ROL_IMAGES = {
    5: 'imgs/rol/agrario.png',
    2: 'imgs/rol/bancolombia.png',
    6: 'imgs/rol/davivienda.png',
    4: 'imgs/rol/occidente.png',
    7: 'imgs/rol/itau.png',
    10: 'imgs/rol/popular.png',
    11: 'imgs/rol/av villas.png',
    12: 'imgs/rol/bancoomeva.png',
    13: 'imgs/rol/caja social.png',
    14: 'imgs/rol/sistemas.png',
    8: 'imgs/rol/th.png',
    9: 'imgs/rol/ti.png',
    15: 'imgs/rol/financiero.png',
    16: 'imgs/rol/sgi.png',
    17: 'imgs/rol/sst.png',
    18: 'imgs/rol/comercial.png',
    19: 'imgs/rol/direccion.png',
    20: 'imgs/rol/sagrilaft.png',
    21: 'imgs/rol/ambiental.png',
}
