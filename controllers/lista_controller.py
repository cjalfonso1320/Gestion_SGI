from extension import mysql


from extension import mysql

def lista_maestra():
    """
    Obtiene los documentos de la lista maestra para un rol y proceso específicos.
    """
    cur = mysql.connection.cursor()
    # Asegúrate de que los nombres de las columnas sean los correctos de tu nueva tabla
    sql = """
        SELECT 
            id, area, tipo_documento, consecutivo, int_ext, medio,
            nombre_documento, procedimiento, fecha_aprobacion, version,
            responsable_aprobacion, fecha_ultima_revision, almacenamiento_como,
            almacenamiento_donde, clasificacion, disponible_para, proteccion,
            tiempo_activo, tiempo_inactivo, disposicion, estado
        FROM lista_maestra
    """
    cur.execute(sql)
    resultado = cur.fetchall()
    cur.close()
    return resultado

def guardar_lista_maestra(datos):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO lista_maestra
(    area, tipo_documento, consecutivo, int_ext, medio, nombre_documento, 
    procedimiento, fecha_aprobacion, version, responsable_aprobacion, fecha_ultima_revision, 
    almacenamiento_como, almacenamiento_donde, clasificacion, disponible_para, 
    proteccion, tiempo_activo, tiempo_inactivo, disposicion, estado
) 
VALUES 
(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    valores = (
        datos.get('area'),
        datos.get('tipo_documento'),
        datos.get('consecutivo'),
        datos.get('int_ext'),
        datos.get('medio'),
        datos.get('nombre_documento'),
        datos.get('procedimiento'),
        datos.get('fecha_aprobacion'),
        datos.get('version'),
        datos.get('responsable_aprobacion'),
        datos.get('fecha_ultima_revision'),
        datos.get('almacenamiento_como'),
        datos.get('almacenamiento_donde'),
        datos.get('clasificacion'),
        datos.get('disponible_para'),
        datos.get('proteccion'),
        datos.get('tiempo_activo'),
        datos.get('tiempo_inactivo'),
        datos.get('disposicion'),
        datos.get('estado')
    )
    cur.execute(sql, valores)
    nuevo_id = cur.lastrowid
    mysql.connection.commit()
    sql_select = "SELECT * FROM lista_maestra WHERE id = %s"
    cur.execute(sql_select, (nuevo_id,))
    nuevo_registro = cur.fetchone()
    cur.close()
    return nuevo_registro


def actualizar_documento_maestro(doc_id, columna, nuevo_valor):
    """
    Actualiza una celda específica de un documento en la lista maestra.
    """
    # IMPORTANTE: Lista blanca de columnas para evitar inyección SQL.
    # Mapea el nombre del 'data-column' del frontend al nombre real de la columna en la BD.
    columnas_permitidas = {
        'area': 'area',
        'tipo_documento': 'tipo_documento',
        'consecutivo': 'consecutivo',
        'int_ext': 'int_ext',
        'medio': 'medio',
        'nombre_documento': 'nombre_documento',
        'procedimiento': 'procedimiento',
        'fecha_aprobacion': 'fecha_aprobacion',
        'version': 'version',
        'responsable_aprobacion': 'responsable_aprobacion',
        'fecha_ultima_revision': 'fecha_ultima_revision',
        'almacenamiento_como': 'almacenamiento_como',
        'almacenamiento_donde': 'almacenamiento_donde',
        'clasificacion': 'clasificacion',
        'disponible_para': 'disponible_para',
        'proteccion': 'proteccion',
        'tiempo_activo': 'tiempo_activo',
        'tiempo_inactivo': 'tiempo_inactivo',
        'disposicion': 'disposicion',
        'estado': 'estado'
    }

    if columna not in columnas_permitidas:
        raise ValueError(f"La columna '{columna}' no está permitida para actualización.")

    db_columna = columnas_permitidas[columna]
    
    cur = mysql.connection.cursor()
    # Usamos f-string de forma segura para el nombre de la columna y parámetros para los valores
    sql = f"UPDATE lista_maestra SET `{db_columna}` = %s WHERE id = %s"
    
    cur.execute(sql, (nuevo_valor, doc_id))
    mysql.connection.commit()
    cur.close()
