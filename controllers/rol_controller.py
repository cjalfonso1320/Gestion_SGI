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

PROCESOS_ROL = {
    5: ['Nacionales_Agrario'],
    2: ['Nacionales_Bancolombia', 'Distritales_Bancolombia', 'Departamentales_Bancolombia', 'Convenios_Bancolombia'],
    6: ['Nacionales_Davivienda', 'Distritales_Davivienda', 'Departamentales_Davivienda', 'Convenios_Davivienda'],
    4: ['Nacionales_Occidente'],
    7: ['Nacionales_Itau', 'Departamentales_Itau'],
    10: ['Nacionales_Popular', 'Departamentales_Popular', 'Convenios_Popular'],
    11: ['Nacionales_AvVillas', 'Distritales_AvVillas', 'Convenios_AvVillas', 'Complementacion_AvVillas', 'Tarjetas_AvVillas', 'Libranzas_AvVillas', 'Radicacion_AvVillas'],
    12: ['Nacionales_Bancoomeva'],
    13: ['Nacionales_CajaSocial', 'Recaudos_CajaSocial'],
    14: ['Gestion de Sistemas'],
    8: ['Gestion Humana'],
    9: ['Recurso Tecnologico'],
    15: ['Recurso Financiero'],
    16: ['Sistema de Gestion Integrado'],
    17: ['Seguridad y Salud en el Trabajo'],
    18: ['Gestion Comercial'],
    19: ['Gestion Direccion'],
    20: ['Sistema de Autocontrol Sagrilaft'],
    21: ['Sistema de Gestión Ambiental'],
}
