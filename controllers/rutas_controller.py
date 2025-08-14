from extension import mysql

def listar_rutas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT ru.id, ru.rol_id, CASE WHEN ro.rol = 'Occidente' THEN 'Gestion de Produccion' ELSE ro.rol END AS rol, ru.ruta_compartida, ru.carpeta FROM rutas ru INNER JOIN rol ro ON ru.rol_id = ro.id ORDER BY ro.rol ASC")
    rutas = cur.fetchall()
    cur.close()
    return rutas

def modificar_ruta(id, ruta):
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE rutas SET ruta_compartida = %s WHERE id = %s", (ruta, id))
        mysql.connection.commit()
    except Exception as e:
        print("Error en modificación:", e)
    finally:
        cur.close()

def elimina_ruta(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM rutas WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()