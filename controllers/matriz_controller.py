from extension import mysql

def guardar_matriz(rol, proceso, datos):
    cur = mysql.connection.cursor()
    sql_insert = """
        INSERT INTO matriz_activo (tipo_activo, nombre, cantidad, responsable, clasificacion, 
                                   confidencialidad, integridad, disponibilidad, total, id_rol, proceso) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    valores = (
        datos.get('tipoActivo'), datos.get('nombre_activo'), datos.get('cant_activo'),
        datos.get('responsable_activo'), datos.get('clasificacionActivo'),
        datos.get('ConfidencialidadActivo'), datos.get('IntegridadActivo'),
        datos.get('DisponibilidadActivo'), datos.get('TotalActivo'), rol, proceso
    )
    
    cur.execute(sql_insert, valores)
    nuevo_id = cur.lastrowid
    mysql.connection.commit()

    # --- CONSULTA CORREGIDA ---
    # Asegúrate de que los nombres de las columnas aquí son EXACTAMENTE los de tu tabla en la BD
    sql_select = """
        SELECT id, tipo_activo, nombre, cantidad, responsable, clasificacion, 
               confidencialidad, integridad, disponibilidad, total 
        FROM matriz_activo WHERE id = %s
    """
    cur.execute(sql_select, (nuevo_id,))
    nuevo_registro = cur.fetchone()
    cur.close()
    return nuevo_registro
def lista_matriz(rol, proceso):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, tipo_activo, nombre, cantidad, responsable, clasificacion, confidencialidad, integridad, disponibilidad, total FROM matriz_activo WHERE id_rol = %s AND proceso = %s", (rol, proceso))
    print("SELECT id, tipo_activo, nombre, cantidad, responsable, clasificacion, confidencialidad, integridad, disponibilidad, total FROM matriz_activo WHERE id_rol = %s AND proceso = %s", (rol, proceso))
    resultado = cur.fetchall()
    cur.close()
    return resultado
def modificar_matriz(activo_id, columna, nuevo_valor):
    columnas = {
        'tipoActivo': 'tipo_activo',
        'nombre_activo': 'nombre',
        'cant_activo': 'cantidad',
        'responsable_activo': 'responsable',
        'clasificacionActivo': 'clasificacion',
        'ConfidencialidadActivo': 'confidencialidad',
        'IntegridadActivo': 'integridad',
        'DisponibilidadActivo': 'disponibilidad'
    }

    if columna not in columnas:
        raise ValueError("Columna no permitida para actualizacion")

    db_columna = columnas[columna]
    cur = mysql.connection.cursor()
    
    columnas_criticas = ['confidencialidad', 'integridad', 'disponibilidad']
    
    # Intenta convertir el nuevo valor a un entero para la suma. Si falla, usa 0.
    try:
        valor_numerico = int(nuevo_valor)
    except (ValueError, TypeError):
        valor_numerico = 0

    if db_columna in columnas_criticas:
        # --- LÓGICA SQL CORREGIDA Y ROBUSTA ---
        sql = f"""
            UPDATE matriz_activo
            SET
                `{db_columna}` = %s,
                total = (
                    -- Si la columna que estamos actualizando es 'confidencialidad', usa el nuevo valor. Si no, usa el valor que ya está en la BD.
                    (CASE WHEN '{db_columna}' = 'confidencialidad' THEN %s ELSE CAST(confidencialidad AS SIGNED) END) +
                    (CASE WHEN '{db_columna}' = 'integridad' THEN %s ELSE CAST(integridad AS SIGNED) END) +
                    (CASE WHEN '{db_columna}' = 'disponibilidad' THEN %s ELSE CAST(disponibilidad AS SIGNED) END)
                )
            WHERE id = %s
        """
        # Pasamos el valor de texto para el SET y el valor numérico para la suma
        cur.execute(sql, (nuevo_valor, valor_numerico, valor_numerico, valor_numerico, activo_id))
    else:
        sql = f"UPDATE matriz_activo SET `{db_columna}` = %s WHERE id = %s"
        cur.execute(sql, (nuevo_valor, activo_id))

    mysql.connection.commit()

    # Obtenemos el nuevo total para devolverlo
    cur.execute("SELECT total FROM matriz_activo WHERE id = %s", (activo_id,))
    resultado_total = cur.fetchone()
    cur.close()

    return resultado_total[0] if resultado_total else 0

def lista_para_riesgos(riesgo): 
    cur = mysql.connection.cursor()
    if riesgo == 'operacional':
        sql = """
        SELECT nombre, tipo_activo, total FROM matriz_activo WHERE id_rol IN (2, 4, 5, 6, 7, 10, 11, 12, 13) AND total >= 9
        """
    elif riesgo == 'administrativo':
        sql = """
        SELECT nombre, tipo_activo, total FROM matriz_activo WHERE id_rol IN (8, 14, 15, 16, 17, 18, 19, 20, 21) AND total >= 9
        """
    elif riesgo == 'T-I':
        sql = """
        SELECT nombre, tipo_activo, total FROM matriz_activo WHERE id_rol = 9 AND total >= 9
        """

    if not sql:
        return []
    cur.execute(sql)
    nombre_columnas = [desc[0] for desc in cur.description]
    activos_lista = [dict(zip(nombre_columnas, row)) for row in cur.fetchall()]
    cur.close()
    return activos_lista



