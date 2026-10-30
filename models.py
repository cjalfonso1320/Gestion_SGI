"""Modelos de usuario para el sistema SGI (administración).

Define la clase Usuarios para autenticación de usuarios administrativos
con Flask-Login, y la función obtener_roles para listar roles disponibles.
"""

from flask_login import UserMixin
from extension import mysql
from werkzeug.security import check_password_hash
import MySQLdb.cursors
from flask_sqlalchemy import SQLAlchemy


class Usuarios(UserMixin):
    """Modelo de usuario SGI para autenticación administrativa.

    Representa un usuario con acceso al panel de administración SGI.
    Se autentica contra la tabla users_rrhh filtrando por sgi_rol_id no nulo.

    Attributes:
        id: ID numérico del usuario en la base de datos.
        name: Nombre completo (nombres + apellidos).
        username: Identificación o correo usado para login.
        password_hash: Hash de la contraseña (pbkdf2:sha256).
        rol: ID del rol SGI asignado.
        identificacion: Número de identificación.
        correo: Correo electrónico del usuario.
        primer_ingreso: Indicador de primer inicio de sesión (0/1).
    """

    def __init__(self, id, name, username, password_hash, rol, identificacion=None, correo=None, primer_ingreso=0):
        """Inicializa una instancia de Usuarios SGI.

        Args:
            id: ID numérico del usuario.
            name: Nombre completo del usuario.
            username: Identificación o correo para login.
            password_hash: Hash de la contraseña.
            rol: ID del rol SGI.
            identificacion: Número de identificación (opcional).
            correo: Correo electrónico (opcional).
            primer_ingreso: Si es 1, debe cambiar contraseña (default: 0).
        """
        self.id = id
        self.name = name
        self.username = username
        self.password_hash = password_hash
        self.rol = rol
        self.identificacion = identificacion or username
        self.correo = correo
        self.primer_ingreso = primer_ingreso

    @staticmethod
    def obtener_por_id(user_id):
        """Obtiene un usuario SGI por su ID (con prefijo 'sgi-').

        Args:
            user_id: ID con prefijo 'sgi-' (ej: 'sgi-5').

        Returns:
            Usuarios: Instancia del usuario, o None si no existe.
        """
        real_id = int(str(user_id).replace("sgi-", ""))
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, nombres, apellidos, identificacion, correo, password, sgi_rol_id, primer_ingreso
            FROM users_rrhh
            WHERE id = %s AND activo = 1 AND sgi_rol_id IS NOT NULL
        """, (real_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Usuarios(
                id=row[0],
                name=f"{row[1]} {row[2]}",
                username=row[3],
                password_hash=row[5],
                rol=row[6],
                identificacion=row[3],
                correo=row[4],
                primer_ingreso=row[7],
            )
        return None

    @staticmethod
    def obtener_por_username(username):
        """Obtiene un usuario SGI por su identificación o correo.

        Args:
            username: Identificación o correo electrónico del usuario.

        Returns:
            Usuarios: Instancia del usuario, o None si no existe o no tiene rol SGI.
        """
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, nombres, apellidos, identificacion, correo, password, sgi_rol_id, primer_ingreso
            FROM users_rrhh
            WHERE activo = 1
              AND sgi_rol_id IS NOT NULL
              AND (identificacion = %s OR correo = %s)
        """, (username, username))
        row = cur.fetchone()
        cur.close()
        if row:
            return Usuarios(
                id=row[0],
                name=f"{row[1]} {row[2]}",
                username=row[3],
                password_hash=row[5],
                rol=row[6],
                identificacion=row[3],
                correo=row[4],
                primer_ingreso=row[7],
            )
        return None

    def verifica_contrasena(self, contrasena):
        """Verifica la contraseña contra el hash almacenado.

        Args:
            contrasena: Contraseña en texto plano.

        Returns:
            bool: True si coincide, False en caso contrario.
        """
        return check_password_hash(self.password_hash, contrasena)

    def get_id(self):
        """Retorna el ID único con prefijo 'sgi-' para Flask-Login.

        Returns:
            str: ID con formato 'sgi-{id}'.
        """
        return f"sgi-{self.id}"


def obtener_roles():
    """Obtiene todos los roles disponibles en el sistema.

    Returns:
        list: Lista de diccionarios con 'id' y 'rol'.
    """
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, rol FROM rol")
    roles = cur.fetchall()
    cur.close()
    return roles
