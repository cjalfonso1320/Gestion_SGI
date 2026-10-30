"""Controlador de usuarios administrativos del sistema SGI.

Proporciona funciones CRUD para la gestión de usuarios SGI
(tabla 'users'), incluyendo creación, modificación, listado y eliminación.
"""

from werkzeug.security import generate_password_hash
from extension import mysql


def insertar_usuario(name, username, password, rol):
    """Crea un nuevo usuario SGI en la base de datos.

    La contraseña se almacena como hash seguro generado por Werkzeug.

    Args:
        name: Nombre completo del usuario.
        username: Nombre de usuario para inicio de sesión.
        password: Contraseña en texto plano (se hashea automáticamente).
        rol: ID del rol SGI asignado al usuario.
    """
    password_hash = generate_password_hash(password)
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (name, username, password, rol) VALUES (%s, %s, %s, %s)",
                (name, username, password_hash, rol))
    mysql.connection.commit()
    cur.close()


def modificar_usuario(id, nombre, username, password, rol):
    """Actualiza los datos de un usuario SGI existente.

    Si se proporciona una nueva contraseña, se hashea antes de almacenar.

    Args:
        id: ID del usuario a modificar.
        nombre: Nuevo nombre completo.
        username: Nuevo nombre de usuario.
        password: Nueva contraseña (se hashea automáticamente).
        rol: Nuevo ID de rol.
    """
    password_hash = generate_password_hash(password)
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE users SET name = %s, username = %s, password = %s, rol = %s WHERE id = %s",
                    (nombre, username, password_hash, int(rol), int(id)))
        mysql.connection.commit()
    except Exception as e:
        print("Error en modificación:", e)
    finally:
        cur.close()


def list_usuarios():
    """Obtiene todos los usuarios SGI con su nombre de rol.

    Realiza un JOIN con la tabla 'rol' para incluir el nombre del rol.

    Returns:
        list: Lista de tuplas (id, name, username, rol_nombre).
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.id, u.name, u.username, r.rol FROM users AS u INNER JOIN rol AS r ON u.rol = r.id")
    usuarios = cur.fetchall()
    cur.close()
    return usuarios


def eliminar(id):
    """Elimina un usuario SGI de la base de datos.

    Args:
        id: ID del usuario a eliminar.
    """
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()


def cuenta():
    """Cuenta el número total de usuarios SGI registrados.

    Returns:
        int: Cantidad de usuarios en la tabla 'users'.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    cuenta = cur.fetchone()[0]
    cur.close()
    return cuenta
