import os
from bs4 import BeautifulSoup
from extension import mysql
import smtplib
from email.mime.text import MIMEText

def actualizar_seccion_procedimiento(nombre_documento, seccion_id, nuevo_contenido):
    """
    Actualiza el contenido de una sección específica directamente en su archivo HTML.

    Args:
        nombre_documento (str): La ruta relativa del archivo HTML desde la carpeta 'templates'.
        seccion_id (int): El ID de la sección a actualizar.
        nuevo_contenido (str): El nuevo contenido HTML para la sección.

    Returns:
        tuple: (bool, str|None). (True, contenido_original) si fue exitoso, (False, None) en caso contrario.
    """
    try:
        # Construimos la ruta completa al archivo HTML
        # La base es la carpeta 'templates' en el directorio actual de tu proyecto
        base_path = os.path.join(os.getcwd(), 'templates')
        file_path = os.path.join(base_path, nombre_documento)

        if not os.path.exists(file_path):
            print(f"Error: El archivo no existe en la ruta: {file_path}")
            return False, None

        # Leemos el contenido del archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Buscamos el elemento .doc-content que corresponde al id de la sección
        # El selector de CSS [data-id="..."] es perfecto para esto
        target_element = soup.find('div', class_='doc-content', attrs={'data-id': str(seccion_id)})

        if not target_element:
            print(f"Error: No se encontró el elemento .doc-content con data-id='{seccion_id}' en {nombre_documento}")
            return False, None

        contenido_original = str(target_element) # Guardamos el div completo
        # Reemplazamos el contenido interno del elemento con el nuevo contenido
        target_element.clear()  # Limpiamos el contenido existente
        target_element.append(BeautifulSoup(nuevo_contenido, 'html.parser')) # Añadimos el nuevo contenido parseado

        # Escribimos el archivo HTML modificado de vuelta al disco
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        return True, contenido_original
    except Exception as e:
        print(f"Error al actualizar el archivo HTML: {e}")
        return False, None
    
def registra_cambio_pendiente(nombre_usuario, descripcion_cambio, nombre_documento, rol, contenido_original):
    try:
        nueva_version = incrementa_version(nombre_documento)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO control_cambios (id_rol, version, elaborado, modificacion, documento, estado, contenido_original) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (rol, nueva_version, nombre_usuario, descripcion_cambio, nombre_documento, 'Pendiente', contenido_original))
        
        mysql.connection.commit()
        cur.close()
        #notificacion_pendiente(nombre_documento)
        return True
    except Exception as e:
        print(f"Error al registrar el cambio pendiente: {e}")
        return False

def registra_cambio(nombre_usuario, fecha_aprobacion, estado, id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE control_cambios SET revisado = %s,aprobado = %s, fecha_aprobacion = %s, estado = %s WHERE id = %s", (nombre_usuario, nombre_usuario, fecha_aprobacion, estado, id))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Error al registrar el cambio aprobado/rechazado: {e}")
        return False

def registra_lista_maestra(fecha_aprobacion, nombre_usuario, nombre_documento, version):
    try:
        cur = mysql.connection.cursor()
        
        # 1. Intentar actualizar el registro existente
        sql_update = """
            UPDATE lista_maestra 
            SET fecha_aprobacion = %s, responsable_aprobacion = %s, version = %s, fecha_ultima_revision = %s
            WHERE nombre_documento = %s
        """
        cur.execute(sql_update, (fecha_aprobacion, nombre_usuario, version, fecha_aprobacion, nombre_documento))

        # 2. Verificar si se actualizó alguna fila. Si no, es un registro nuevo.
        if cur.rowcount == 0:
            # 3. Insertar un nuevo registro si no existía
            sql_insert = """
                INSERT INTO lista_maestra (nombre_documento, version, fecha_aprobacion, responsable_aprobacion, fecha_ultima_revision, estado) 
                VALUES (%s, %s, %s, %s, %s, 'Aprobado')
            """
            cur.execute(sql_insert, (nombre_documento, version, fecha_aprobacion, nombre_usuario, fecha_aprobacion))

        mysql.connection.commit()
    except Exception as e:
        print(f"Error en registra_lista_maestra: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()

def revertir_cambio_html(id_cambio):
    """
    Revierte un cambio en un archivo HTML usando el contenido original guardado en la BD.
    """
    try:
        cur = mysql.connection.cursor()
        # Obtenemos la información del cambio, incluyendo el contenido original y el nombre del documento
        cur.execute("SELECT documento, contenido_original FROM control_cambios WHERE id = %s", (id_cambio,))
        resultado = cur.fetchone()
        cur.close()

        if not resultado or not resultado[1]:
            print(f"No se encontró contenido original para revertir el cambio ID: {id_cambio}")
            return False

        nombre_documento_legible, contenido_original_html = resultado
        
        # Necesitamos la ruta del archivo, que no está en control_cambios.
        # Asumimos una convención o buscamos en otra tabla. Por ahora, lo hardcodeamos para el ejemplo.
        # TODO: Mejorar esto para obtener la ruta del archivo dinámicamente.
        if nombre_documento_legible == "TEC-PR-001 REGISTRO, MONITOREO Y MANEJO DE LOGS":
            ruta_archivo_relativa = "procedimientos/TI/Tec_pr_001.html"
        else:
            # Aquí iría la lógica para otros documentos
            print(f"No se encontró la ruta para el documento: {nombre_documento_legible}")
            return False

        soup_original = BeautifulSoup(contenido_original_html, 'html.parser')
        seccion_id = soup_original.div['data-id']

        # Reutilizamos la lógica de `actualizar_seccion_procedimiento` para restaurar
        # Extraemos solo el contenido interno del div original para pasarlo
        contenido_interno_original = ''.join(str(c) for c in soup_original.div.contents)
        
        exito, _ = actualizar_seccion_procedimiento(ruta_archivo_relativa, seccion_id, contenido_interno_original)

        return exito

    except Exception as e:
        print(f"Error al revertir el cambio HTML: {e}")
        return False

def lista_cambios(nombre_documento):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM control_cambios WHERE documento = %s", (nombre_documento,))
    cambios = cur.fetchall()
    print(cambios)
    cur.close()
    return cambios

def incrementa_version(documento):
    cur = mysql.connection.cursor()
    
    #obtener version actual
    cur.execute("SELECT version FROM lista_maestra WHERE nombre_documento = %s", (documento,))
    version_actual = cur.fetchone()
    cur.close()
    if version_actual:
        nueva_version = int(version_actual[0]) + 1
    else:
        nueva_version = version_actual
    
    return nueva_version

def notificacion_pendiente(nombre_documento):
    message = MIMEText(f"Hay cambios pendientes de aprobación en el procedimiento {nombre_documento}. Por favor, revise el sistema para aprobar o rechazar los cambios.")
    message['Subject'] = f'Notificación de Cambios Pendientes en {nombre_documento}'
    message['From'] = 'calfonso@digicomsys.com.co'
    message['To'] = 'auxiliar.t-i@digicomsys.com.co'

    with smtplib.SMTP('webmail.digicomsys.com.co', 25) as server:
        server.starttls()
        server.login('calfonso@digicomsys.com.co', '**Combosken1953/*$')
        server.send_message(message)

def cuenta_pendientes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM control_cambios WHERE estado = 'Pendiente'")
    count = cur.fetchone()[0]
    cur.close()
    return count

def cuenta_rechazados():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM control_cambios WHERE estado = 'Rechazado'")
    count = cur.fetchone()[0]
    cur.close()
    return count

def lista_cambios_pendientes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM control_cambios WHERE estado = 'Pendiente'")
    cambios = cur.fetchall()
    cur.close()
    return cambios

def lista_cambios_rechazados():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM control_cambios WHERE estado = 'Rechazado'")
    cambios = cur.fetchall()
    cur.close()
    return cambios
