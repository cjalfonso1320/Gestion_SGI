from extension import mysql

def list_roles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, rol FROM rol")
    roles = cur.fetchall()
    cur.close()
    return roles

def cuenta():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM rol")
    cuenta = cur.fetchone()[0]
    cur.close()
    return cuenta

def insertar_rol(rol):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO rol (rol) VALUES (%s)", (rol,))
    mysql.connection.commit()
    cur.close()

def modificar_rol(id, rol):
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE rol SET rol = %s WHERE id = %s", (rol, id))
        mysql.connection.commit()
    except Exception as e:
        print("Error en modificación:", e)
    finally:
        cur.close()

def elimina_rol(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM rol WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

def nombre_rol(rol_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT rol FROM rol WHERE id = %s", (rol_id,))
    nombre = cur.fetchone()
    cur.close()
    return nombre[0] if nombre else None