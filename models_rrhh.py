"""Modelo de usuario para el módulo de Recursos Humanos (RRHH).

Define la clase UsuariosRRHH para la autenticación de empleados
en el módulo de RRHH, utilizando Flask-Login con prefijo 'rrhh-'.
"""

from flask_login import UserMixin
from extension import mysql
from werkzeug.security import check_password_hash


# Rol SGI que tiene acceso al módulo RRHH (Talento Humano)
ROL_TALENTO_HUMANO = 8


class UsuariosRRHH(UserMixin):
    """Modelo de usuario para Recursos Humanos.

    Representa a un empleado de la organización que puede acceder
    al módulo RRHH. Se autentica contra la tabla users_rrhh.

    Attributes:
        id: ID numérico del usuario en la base de datos.
        identificacion: Número de identificación del empleado.
        nombres: Nombres del empleado.
        apellidos: Apellidos del empleado.
        correo: Correo electrónico del empleado.
        password_hash: Hash de la contraseña.
        cargo: ID del cargo del empleado.
        activo: Estado del empleado (1=activo, 2=retirado).
        primer_ingreso: Indicador de primer inicio de sesión (0/1).
    """

    def __init__(self, id, identificacion, nombres, apellidos, correo, password, activo, cargo, primer_ingreso=0, sgi_rol_id=None, fecha_confirmacion_datos=None):
        """Inicializa una instancia de UsuariosRRHH.

        Args:
            id: ID numérico del usuario.
            identificacion: Número de identificación.
            nombres: Nombres del empleado.
            apellidos: Apellidos del empleado.
            correo: Correo electrónico.
            password: Hash de la contraseña.
            cargo: ID del cargo del empleado.
            activo: Estado del empleado (1=activo, 2=retirado).
            primer_ingreso: Si es 1, debe cambiar contraseña inicial (default: 0).
            fecha_confirmacion_datos: Última fecha en que confirmó sus datos personales.
        """
        self.id = id
        self.identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.password_hash = password
        self.cargo = cargo
        self.activo = activo
        self.primer_ingreso = primer_ingreso
        self.sgi_rol_id = sgi_rol_id
        self.fecha_confirmacion_datos = fecha_confirmacion_datos

    def get_id(self):
        """Retorna el ID único con prefijo 'rrhh-' para Flask-Login.

        Returns:
            str: ID con formato 'rrhh-{id}'.
        """
        return f"rrhh-{self.id}"

    @staticmethod
    def obtener_por_id(user_id):
        """Obtiene un usuario RRHH por su ID (con prefijo 'rrhh-').

        Args:
            user_id: ID con prefijo 'rrhh-' (ej: 'rrhh-3').

        Returns:
            UsuariosRRHH: Instancia del usuario, o None si no existe.
        """
        real_id = int(str(user_id).replace("rrhh-", ""))
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT id, identificacion, nombres, apellidos, correo, password, cargo_id, activo, primer_ingreso, sgi_rol_id, fecha_confirmacion_datos
                    FROM users_rrhh
                    WHERE id = %s AND activo = 1
                    """, (real_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return UsuariosRRHH(
                id=row[0],
                identificacion=row[1],
                nombres=row[2],
                apellidos=row[3],
                correo=row[4],
                password=row[5],
                cargo=row[6],
                activo=row[7],
                primer_ingreso=row[8],
                sgi_rol_id=row[9],
                fecha_confirmacion_datos=row[10]
            )
        return None

    @staticmethod
    def obtener_por_identificacion_correo(valor):
        """Obtiene un usuario RRHH por su identificación o correo.

        Args:
            valor: Identificación o correo electrónico del usuario.

        Returns:
            UsuariosRRHH: Instancia del usuario, o None si no existe.
        """
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT id, identificacion, nombres, apellidos, correo, password, cargo_id, activo, primer_ingreso, sgi_rol_id, fecha_confirmacion_datos
                    FROM users_rrhh
                    WHERE identificacion = %s OR correo = %s
                    """, (valor, valor))
        row = cur.fetchone()
        cur.close()
        if row:
            return UsuariosRRHH(
                id=row[0],
                identificacion=row[1],
                nombres=row[2],
                apellidos=row[3],
                correo=row[4],
                password=row[5],
                cargo=row[6],
                activo=row[7],
                primer_ingreso=row[8],
                sgi_rol_id=row[9],
                fecha_confirmacion_datos=row[10]
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

    @property
    def rol(self):
        """Propiedad de compatibilidad: retorna el cargo como rol."""
        return self.cargo
