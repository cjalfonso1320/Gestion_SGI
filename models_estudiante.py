"""Modelo de usuario para estudiantes (aula virtual).

Define la clase Estudiante para la autenticación de estudiantes
en el módulo de aula virtual, utilizando Flask-Login con prefijo 'estu-'.
"""

from flask_login import UserMixin
from extension import mysql
from werkzeug.security import check_password_hash


class Estudiante(UserMixin):
    """Modelo de estudiante para el aula virtual.

    Representa a un empleado en rol de estudiante. Se autentica contra
    la tabla users_rrhh sin filtro de rol SGI.

    Attributes:
        id: ID numérico en la base de datos.
        identificacion: Número de identificación del estudiante.
        nombres: Nombres del estudiante.
        apellidos: Apellidos del estudiante.
        password_hash: Hash de la contraseña.
        primer_ingreso: Indicador de primer inicio de sesión (0/1).
    """

    def __init__(self, id, identificacion, nombres, apellidos, password, primer_ingreso, activo=1):
        """Inicializa una instancia de Estudiante.

        Args:
            id: ID numérico del usuario.
            identificacion: Número de identificación.
            nombres: Nombres del estudiante.
            apellidos: Apellidos del estudiante.
            password: Hash de la contraseña.
            primer_ingreso: Si es 1, debe cambiar contraseña inicial.
            activo: Estado del empleado (1=activo, 2=retirado).
        """
        self.id = id
        self.identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.password_hash = password
        self.primer_ingreso = primer_ingreso
        self.activo = activo

    def get_id(self):
        """Retorna el ID único con prefijo 'estu-' para Flask-Login.

        Returns:
            str: ID con formato 'estu-{id}'.
        """
        return f"estu-{self.id}"

    @staticmethod
    def obtener_por_id(user_id):
        """Obtiene un estudiante por su ID (con prefijo 'estu-').

        Args:
            user_id: ID con prefijo 'estu-' (ej: 'estu-5').

        Returns:
            Estudiante: Instancia del estudiante, o None si no existe.
        """
        real_id = int(str(user_id).replace("estu-", ""))
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, identificacion, nombres, apellidos, password, primer_ingreso, activo
            FROM users_rrhh WHERE id = %s AND activo = 1
        """, (real_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Estudiante(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        return None

    @staticmethod
    def obtener_por_identificacion(identificacion):
        """Obtiene un estudiante por su número de identificación.

        Args:
            identificacion: Número de identificación del estudiante.

        Returns:
            Estudiante: Instancia del estudiante, o None si no existe.
        """
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, identificacion, nombres, apellidos, password, primer_ingreso, activo
            FROM users_rrhh WHERE identificacion = %s
        """, (identificacion,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Estudiante(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        return None

    def verifica_contrasena(self, contrasena):
        """Verifica la contraseña contra el hash almacenado.

        Args:
            contrasena: Contraseña en texto plano.

        Returns:
            bool: True si coincide, False en caso contrario.
        """
        return check_password_hash(self.password_hash, contrasena)
