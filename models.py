from flask_login import UserMixin
from extension import mysql
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy

class Usuarios(UserMixin):
    def __init__(self, id, name, username, password_hash, rol ):
        self.id = id
        self.name = name
        self.username = username
        self.password_hash = password_hash
        self.rol = rol

    @staticmethod
    def obtener_por_id(user_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, username, password, rol FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Usuarios(id=row[0], name=row[1], username=row[2], password_hash=row[3], rol=row[4])
        return None
    
    @staticmethod
    def obtener_por_username(username):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, username, password, rol FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Usuarios(id=row[0], name=row[1], username=row[2], password_hash=row[3], rol=row[4])
        return None
    
    def verifica_contrasena(self, contrasena):
        return check_password_hash(self.password_hash, contrasena)
    
def obtener_roles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, rol FROM rol")
    roles = cur.fetchall()
    return roles

# class Rutas:
#     def __init__(self, id, nombre, descripcion):
#         self.id = id
#         self.nombre = nombre
#         self.descripcion = descripcion

#     @staticmethod
#     def obtener_todas():
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT id, nombre, descripcion FROM rutas")
#         rutas = cur.fetchall()
#         cur.close()
#         return [Rutas(id=row[0], nombre=row[1], descripcion=row[2]) for row in rutas]