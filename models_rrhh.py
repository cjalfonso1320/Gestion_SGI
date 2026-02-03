from flask_login import UserMixin
from extension import mysql
from werkzeug.security import check_password_hash

class UsuariosRRHH(UserMixin):
    def __init__(self, id, identificacion, nombres, apellidos, correo, password, activo, cargo):
        self.id = id
        self.identificacion = identificacion
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.password_hash = password
        self.cargo = cargo
        self.activo = activo
        
    def get_id(self):
        return f"rrhh-{self.id}"
    
    @staticmethod
    def obtener_por_id(user_id):       
        real_id = int(str(user_id).replace("rrhh-", ""))
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT id, identificacion, nombres, apellidos, correo, password, cargo_id, activo
                    FROM users_rrhh
                    WHERE id = %s
                    """, (real_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return UsuariosRRHH(
                id = row[0],
                identificacion= row[1],
                nombres= row[2],
                apellidos=row[3],
                correo=row[4],
                password=row[5],
                cargo=row[6],
                activo=row[7]
            )
        return None
    
    @staticmethod
    def obtener_por_identificacion_correo(valor):
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT id, identificacion, nombres, apellidos, correo, password, cargo_id, activo
                    FROM users_rrhh
                    WHERE identificacion = %s OR correo = %s
                    """, (valor, valor))
        row = cur.fetchone()
        cur.close()
        if row:
            return UsuariosRRHH(
                id = row[0],
                identificacion= row[1],
                nombres= row[2],
                apellidos=row[3],
                correo=row[4],
                password=row[5],
                cargo=row[6],
                activo=row[7]
            )
        return None
    
    def verifica_contrasena(self, contrasena):
        return check_password_hash(self.password_hash, contrasena)
    
    @property
    def rol(self):
        return self.cargo
        