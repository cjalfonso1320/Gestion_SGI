from werkzeug.security import generate_password_hash
from extension import mysql

def insertar_usuario(name, username, password, rol):
    password_hash = generate_password_hash(password)
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (name, username, password, rol) VALUES (%s, %s, %s, %s)",
                (name, username, password_hash, rol))
    mysql.connection.commit()
    cur.close()

def modificar_usuario(id, nombre, username, password, rol):
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.id, u.name, u.username, r.rol FROM users AS u INNER JOIN rol AS r ON u.rol = r.id")
    usuarios = cur.fetchall()
    cur.close()
    return usuarios

def eliminar(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

def cuenta():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    cuenta = cur.fetchone()[0]
    cur.close()
    return cuenta

