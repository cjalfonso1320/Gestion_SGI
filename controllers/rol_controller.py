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
    5: ['Agrario'],
    2: ['Bancolombia', 'Distritales_Bancolombia', 'Departamentales_Bancolombia', 'Convenios_Bancolombia'],
    6: ['Davivienda', 'Distritales_Davivienda', 'Departamentales_Davivienda', 'Convenios_Davivienda'],
    4: ['Occidente'],
    7: ['Itau', 'Departamentales_Itau'],
    10: ['Popular', 'Departamentales_Popular', 'Convenios_Popular'],
    11: ['AvVillas', 'Distritales_AvVillas', 'Convenios_AvVillas', 'Complementacion_AvVillas', 'Tarjetas_AvVillas', 'Libranzas_AvVillas', 'Radicacion_AvVillas'],
    12: ['Bancoomeva'],
    13: ['CajaSocial', 'Recaudos_CajaSocial'],
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

ROL_IMAGES = {
    5: 'imgs/rol/agrario.png',
    2: 'imgs/rol/bancolombia.png',
    6: 'imgs/rol/davivienda.png',
    4: 'imgs/rol/occidente.png',
    7: 'imgs/rol/itau.png',
    10: 'imgs/rol/popular.png',
    11: 'imgs/rol/av villas.png',
    12: 'imgs/rol/bancoomeva.png',
    13: 'imgs/rol/caja social.png',
    14: 'imgs/rol/sistemas.png',
    8: 'imgs/rol/th.png',
    9: 'imgs/rol/ti.png',
    15: 'imgs/rol/financiero.png',
    16: 'imgs/rol/sgi.png',
    17: 'imgs/rol/sst.png',
    18: 'imgs/rol/comercial.png',
    19: 'imgs/rol/direccion.png',
    20: 'imgs/rol/sagrilaft.png',
    21: 'imgs/rol/ambiental.png',
}
