"""Controlador de procedimientos y control de cambios.

Gestiona la edición de secciones HTML de procedimientos, el registro
de cambios pendientes, la aprobación/rechazo de cambios, la lista
maestra y la notificación por correo electrónico.
"""

import os
from bs4 import BeautifulSoup
from extension import mysql
import smtplib
from email.mime.text import MIMEText


def actualizar_seccion_procedimiento(nombre_documento, seccion_id, nuevo_contenido):
    """Actualiza el contenido de una sección específica en su archivo HTML.

    Busca el elemento .doc-content con el data-id correspondiente y
    reemplaza su contenido interno con el nuevo HTML proporcionado.

    Args:
        nombre_documento: Ruta relativa del archivo HTML desde la carpeta 'templates'.
        seccion_id: ID de la sección a actualizar (atributo data-id).
        nuevo_contenido: Nuevo contenido HTML para la sección.

    Returns:
        tuple: (True, contenido_original) si fue exitoso, (False, None) en caso contrario.
    """
    try:
        base_path = os.path.join(os.getcwd(), 'templates')
        file_path = os.path.join(base_path, nombre_documento)

        if not os.path.exists(file_path):
            print(f"Error: El archivo no existe en la ruta: {file_path}")
            return False, None

        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        target_element = soup.find('div', class_='doc-content', attrs={'data-id': str(seccion_id)})

        if not target_element:
            print(f"Error: No se encontró elemento con data-id='{seccion_id}'")
            return False, None

        contenido_original = str(target_element)
        target_element.clear()
        target_element.append(BeautifulSoup(nuevo_contenido, 'html.parser'))

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        return True, contenido_original
    except Exception as e:
        print(f"Error al actualizar el archivo HTML: {e}")
        return False, None


def registra_cambio_pendiente(nombre_usuario, descripcion_cambio, nombre_documento, rol, contenido_original):
    """Registra un cambio pendiente de aprobación en la base de datos.

    Incrementa la versión del documento y guarda el contenido original
    para posible reversión.

    Args:
        nombre_usuario: Usuario que realizó el cambio.
        descripcion_cambio: Descripción del cambio realizado.
        nombre_documento: Nombre del documento modificado.
        rol: ID del rol del usuario.
        contenido_original: HTML original de la sección modificada.

    Returns:
        bool: True si se registró correctamente.
    """
    try:
        nueva_version = incrementa_version(nombre_documento)
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO control_cambios
            (id_rol, version, elaborado, modificacion, documento, estado, contenido_original)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (rol, nueva_version, nombre_usuario, descripcion_cambio, nombre_documento, 'Pendiente', contenido_original))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error al registrar el cambio pendiente: {e}")
        return False


def registra_cambio(nombre_usuario, fecha_aprobacion, estado, id):
    """Registra la aprobación o rechazo de un cambio pendiente.

    Args:
        nombre_usuario: Usuario que aprobó/rechazó.
        fecha_aprobacion: Fecha de la aprobación/rechazo.
        estado: 'Aprobado' o 'Rechazado'.
        id: ID del cambio en control_cambios.

    Returns:
        bool: True si se registró correctamente.
    """
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE control_cambios SET revisado = %s, aprobado = %s, fecha_aprobacion = %s, estado = %s WHERE id = %s",
            (nombre_usuario, nombre_usuario, fecha_aprobacion, estado, id))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error al registrar el cambio: {e}")
        return False


def registra_lista_maestra(fecha_aprobacion, nombre_usuario, nombre_documento, version):
    """Registra o actualiza un documento aprobado en la lista maestra.

    Si el documento ya existe, actualiza sus datos. Si no, lo inserta.

    Args:
        fecha_aprobacion: Fecha de aprobación del documento.
        nombre_usuario: Usuario que aprobó.
        nombre_documento: Nombre del documento.
        version: Nueva versión del documento.
    """
    try:
        cur = mysql.connection.cursor()
        sql_update = """UPDATE lista_maestra
            SET fecha_aprobacion = %s, responsable_aprobacion = %s, version = %s, fecha_ultima_revision = %s
            WHERE nombre_documento = %s"""
        cur.execute(sql_update, (fecha_aprobacion, nombre_usuario, version, fecha_aprobacion, nombre_documento))

        if cur.rowcount == 0:
            sql_insert = """INSERT INTO lista_maestra
                (nombre_documento, version, fecha_aprobacion, responsable_aprobacion, fecha_ultima_revision, estado)
                VALUES (%s, %s, %s, %s, %s, 'Aprobado')"""
            cur.execute(sql_insert, (nombre_documento, version, fecha_aprobacion, nombre_usuario, fecha_aprobacion))

        mysql.connection.commit()
    except Exception as e:
        print(f"Error en registra_lista_maestra: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()


def revertir_cambio_html(id_cambio):
    """Revierte un cambio en un archivo HTML usando el contenido original guardado.

    Args:
        id_cambio: ID del cambio en control_cambios a revertir.

    Returns:
        bool: True si la reversión fue exitosa.
    """
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT documento, contenido_original FROM control_cambios WHERE id = %s", (id_cambio,))
        resultado = cur.fetchone()
        cur.close()

        if not resultado or not resultado[1]:
            print(f"No se encontró contenido original para revertir el cambio ID: {id_cambio}")
            return False

        nombre_documento_legible, contenido_original_html = resultado

        if nombre_documento_legible == "TEC-PR-001 REGISTRO, MONITOREO Y MANEJO DE LOGS":
            ruta_archivo_relativa = "procedimientos/TI/Tec_pr_001.html"
        else:
            print(f"No se encontró la ruta para el documento: {nombre_documento_legible}")
            return False

        soup_original = BeautifulSoup(contenido_original_html, 'html.parser')
        seccion_id = soup_original.div['data-id']
        contenido_interno_original = ''.join(str(c) for c in soup_original.div.contents)
        exito, _ = actualizar_seccion_procedimiento(ruta_archivo_relativa, seccion_id, contenido_interno_original)
        return exito
    except Exception as e:
        print(f"Error al revertir el cambio HTML: {e}")
        return False


def lista_cambios(nombre_documento):
    """Obtiene todos los cambios registrados para un documento.

    Args:
        nombre_documento: Nombre del documento a consultar.

    Returns:
        list: Lista de tuplas con los cambios del documento.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM control_cambios WHERE documento = %s", (nombre_documento,))
    cambios = cur.fetchall()
    cur.close()
    return cambios


def incrementa_version(documento):
    """Incrementa la versión de un documento en la lista maestra.

    Args:
        documento: Nombre del documento.

    Returns:
        int: Nueva versión, o None si el documento no existe en lista maestra.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT version FROM lista_maestra WHERE nombre_documento = %s", (documento,))
    version_actual = cur.fetchone()
    cur.close()
    if version_actual:
        nueva_version = int(version_actual[0]) + 1
    else:
        nueva_version = version_actual
    return nueva_version


def notificacion_pendiente(nombre_documento):
    """Envía una notificación por correo sobre cambios pendientes.

    Args:
        nombre_documento: Nombre del documento con cambios pendientes.
    """
    message = MIMEText(f"Hay cambios pendientes de aprobación en el procedimiento {nombre_documento}. Por favor, revise el sistema para aprobar o rechazar los cambios.")
    message['Subject'] = f'Notificación de Cambios Pendientes en {nombre_documento}'
    message['From'] = 'calfonso@digicomsys.com.co'
    message['To'] = 'auxiliar.t-i@digicomsys.com.co'

    with smtplib.SMTP('webmail.digicomsys.com.co', 25) as server:
        server.starttls()
        server.login('calfonso@digicomsys.com.co', '**Combosken1953/*$')
        server.send_message(message)


def cuenta_pendientes(rol):
    """Cuenta los cambios pendientes de aprobación para un rol.

    Args:
        rol: ID del rol. Si es 16 (SGI), cuenta todos los pendientes.

    Returns:
        int: Cantidad de cambios pendientes.
    """
    cur = mysql.connection.cursor()
    if rol == 16:
        cur.execute("SELECT COUNT(*) FROM control_cambios WHERE estado = 'Pendiente'")
    else:
        cur.execute("SELECT COUNT(*) FROM control_cambios WHERE estado = 'Pendiente' and id_rol = %s", (rol,))
    count = cur.fetchone()[0]
    cur.close()
    return count


def cuenta_rechazados():
    """Cuenta los cambios rechazados en el sistema.

    Returns:
        int: Cantidad de cambios rechazados.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM control_cambios WHERE estado = 'Rechazado'")
    count = cur.fetchone()[0]
    cur.close()
    return count


def lista_cambios_pendientes(rol):
    """Obtiene la lista de cambios pendientes para un rol.

    Args:
        rol: ID del rol. Si es 16 (SGI), obtiene todos los pendientes.

    Returns:
        list: Lista de tuplas con los cambios pendientes.
    """
    cur = mysql.connection.cursor()
    if rol == 16:
        cur.execute("SELECT * FROM control_cambios WHERE estado = 'Pendiente'")
    else:
        cur.execute("SELECT * FROM control_cambios WHERE estado = 'Pendiente' and id_rol = %s", (rol,))
    cambios = cur.fetchall()
    cur.close()
    return cambios


def lista_cambios_rechazados():
    """Obtiene la lista de todos los cambios rechazados.

    Returns:
        list: Lista de tuplas con los cambios rechazados.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM control_cambios WHERE estado = 'Rechazado'")
    cambios = cur.fetchall()
    cur.close()
    return cambios
