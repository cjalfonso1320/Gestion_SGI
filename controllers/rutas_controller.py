"""Controlador de rutas compartidas del sistema.

Gestiona las rutas de red o directorios compartidos asociados a cada rol,
permitiendo listar, modificar y eliminar las rutas de almacenamiento
de documentos.
"""

from extension import mysql


def listar_rutas():
    """Obtiene todas las rutas compartidas con su rol y carpeta asociados.

    Realiza un JOIN con la tabla 'rol' y reemplaza 'Occidente' por
    'Gestion de Produccion' para mejor legibilidad.

    Returns:
        list: Lista de tuplas (id, rol_id, rol_nombre, ruta_compartida, carpeta).
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT ru.id, ru.rol_id, CASE WHEN ro.rol = 'Occidente' THEN 'Gestion de Produccion' ELSE ro.rol END AS rol, ru.ruta_compartida, ru.carpeta FROM rutas ru INNER JOIN rol ro ON ru.rol_id = ro.id ORDER BY ro.rol ASC")
    rutas = cur.fetchall()
    cur.close()
    return rutas


def modificar_ruta(id, ruta):
    """Actualiza la ruta compartida de un registro existente.

    Args:
        id: ID del registro de ruta a modificar.
        ruta: Nueva ruta de directorio compartido.
    """
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE rutas SET ruta_compartida = %s WHERE id = %s", (ruta, id))
        mysql.connection.commit()
    except Exception as e:
        print("Error en modificación:", e)
    finally:
        cur.close()


def elimina_ruta(id):
    """Elimina un registro de ruta compartida de la base de datos.

    Args:
        id: ID del registro de ruta a eliminar.
    """
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM rutas WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
