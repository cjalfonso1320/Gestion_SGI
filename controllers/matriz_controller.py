"""Controlador de la Matriz de Activos de Información.

Gestiona el registro, consulta y actualización de activos de información
en la matriz de activos, incluyendo la clasificación de seguridad
(confidencialidad, integridad, disponibilidad) y el cálculo del total.
"""

from extension import mysql


def obtener_activo_por_id(activo_id):
    """Obtiene un activo de información por su ID.

    Args:
        activo_id: ID del activo a consultar.

    Returns:
        dict: Datos del activo con claves descriptivas, o None si no existe.
    """
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, tipo_activo, nombre, cantidad, responsable, clasificacion, "
        "confidencialidad, integridad, disponibilidad, total "
        "FROM matriz_activo WHERE id = %s", (activo_id,)
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        return None
    return {
        'id': row[0],
        'tipoActivo': row[1],
        'nombre_activo': row[2],
        'cant_activo': row[3],
        'responsable_activo': row[4],
        'clasificacionActivo': row[5],
        'ConfidencialidadActivo': row[6],
        'IntegridadActivo': row[7],
        'DisponibilidadActivo': row[8],
        'TotalActivo': row[9],
    }


def actualizar_activo_completo(activo_id, datos):
    """Actualiza todos los campos de un activo de información.

    Args:
        activo_id: ID del activo a actualizar.
        datos: Diccionario con todos los campos del activo.

    Returns:
        dict: Datos del activo actualizado.
    """
    cur = mysql.connection.cursor()
    sql = """
        UPDATE matriz_activo SET
            tipo_activo = %s, nombre = %s, cantidad = %s, responsable = %s,
            clasificacion = %s, confidencialidad = %s, integridad = %s,
            disponibilidad = %s, total = %s
        WHERE id = %s
    """
    valores = (
        datos.get('tipoActivo'), datos.get('nombre_activo'), datos.get('cant_activo'),
        datos.get('responsable_activo'), datos.get('clasificacionActivo'),
        datos.get('ConfidencialidadActivo'), datos.get('IntegridadActivo'),
        datos.get('DisponibilidadActivo'), datos.get('TotalActivo'),
        activo_id
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
    return obtener_activo_por_id(activo_id)


def guardar_matriz(rol, proceso, datos):
    """Inserta un nuevo activo en la matriz de activos.

    Args:
        rol: ID del rol al que pertenece el activo.
        proceso: Nombre del proceso asociado.
        datos: Diccionario con los datos del activo.

    Returns:
        tuple: Registro completo del activo recién creado.
    """
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
    """Obtiene todos los activos de un rol y proceso específicos.

    Args:
        rol: ID del rol para filtrar activos.
        proceso: Nombre del proceso para filtrar.

    Returns:
        list: Lista de tuplas con los datos de cada activo.
    """
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, tipo_activo, nombre, cantidad, responsable, clasificacion, "
        "confidencialidad, integridad, disponibilidad, total "
        "FROM matriz_activo WHERE id_rol = %s AND proceso = %s",
        (rol, proceso)
    )
    resultado = cur.fetchall()
    cur.close()
    return resultado


def modificar_matriz(activo_id, columna, nuevo_valor):
    """Actualiza una celda específica de un activo y recalcula el total.

    Si la columna modificada es de criticidad (confidencialidad, integridad,
    disponibilidad), se recalcula automáticamente el total como la suma
    de los tres valores.

    Args:
        activo_id: ID del activo a modificar.
        columna: Nombre de la columna (data-column del frontend).
        nuevo_valor: Nuevo valor a asignar.

    Returns:
        int: Nuevo valor total del activo.

    Raises:
        ValueError: Si la columna no está permitida.
    """
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

    try:
        valor_numerico = int(nuevo_valor)
    except (ValueError, TypeError):
        valor_numerico = 0

    if db_columna in columnas_criticas:
        sql = f"""
            UPDATE matriz_activo
            SET
                `{db_columna}` = %s,
                total = (
                    (CASE WHEN '{db_columna}' = 'confidencialidad' THEN %s ELSE CAST(confidencialidad AS SIGNED) END) +
                    (CASE WHEN '{db_columna}' = 'integridad' THEN %s ELSE CAST(integridad AS SIGNED) END) +
                    (CASE WHEN '{db_columna}' = 'disponibilidad' THEN %s ELSE CAST(disponibilidad AS SIGNED) END)
                )
            WHERE id = %s
        """
        cur.execute(sql, (nuevo_valor, valor_numerico, valor_numerico, valor_numerico, activo_id))
    else:
        sql = f"UPDATE matriz_activo SET `{db_columna}` = %s WHERE id = %s"
        cur.execute(sql, (nuevo_valor, activo_id))

    mysql.connection.commit()

    cur.execute("SELECT total FROM matriz_activo WHERE id = %s", (activo_id,))
    resultado_total = cur.fetchone()
    cur.close()

    return resultado_total[0] if resultado_total else 0


def importar_matriz_masiva_db(data):
    """Inserta o actualiza un activo desde una carga masiva (Excel).

    Si existe un activo con el mismo nombre, rol y proceso, actualiza
    sus datos. Si no existe, inserta uno nuevo.

    Args:
        data: dict con claves:
            - tipo_activo, nombre, cantidad, responsable, clasificacion
            - confidencialidad, integridad, disponibilidad, total
            - id_rol, proceso

    Returns:
        tuple: (success: bool, error: str or None)
    """
    try:
        cur = mysql.connection.cursor()

        # Verificar si ya existe un activo con el mismo nombre, rol y proceso
        cur.execute(
            "SELECT id FROM matriz_activo WHERE nombre = %s AND id_rol = %s AND proceso = %s",
            (data.get('nombre'), data.get('id_rol'), data.get('proceso'))
        )
        existente = cur.fetchone()

        if existente:
            # Actualizar registro existente
            sql = """
                UPDATE matriz_activo SET
                    tipo_activo = %s,
                    cantidad = %s,
                    responsable = %s,
                    clasificacion = %s,
                    confidencialidad = %s,
                    integridad = %s,
                    disponibilidad = %s,
                    total = %s
                WHERE id = %s
            """
            cur.execute(sql, (
                data.get('tipo_activo'),
                data.get('cantidad'),
                data.get('responsable'),
                data.get('clasificacion'),
                data.get('confidencialidad'),
                data.get('integridad'),
                data.get('disponibilidad'),
                data.get('total'),
                existente[0]
            ))
        else:
            # Insertar nuevo registro
            sql = """
                INSERT INTO matriz_activo
                    (tipo_activo, nombre, cantidad, responsable, clasificacion,
                     confidencialidad, integridad, disponibilidad, total, id_rol, proceso)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                data.get('tipo_activo'),
                data.get('nombre'),
                data.get('cantidad'),
                data.get('responsable'),
                data.get('clasificacion'),
                data.get('confidencialidad'),
                data.get('integridad'),
                data.get('disponibilidad'),
                data.get('total'),
                data.get('id_rol'),
                data.get('proceso')
            ))

        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al importar activo masivo: {e}")
        return False, str(e)


def lista_para_riesgos(riesgo):
    """Obtiene activos con criticidad alta (total >= 9) para la matriz de riesgos.

    Filtra los activos según el tipo de riesgo: operacional, administrativo o T-I.

    Args:
        riesgo: Tipo de riesgo ('operacional', 'administrativo', 'T-I').

    Returns:
        list: Lista de diccionarios con nombre, tipo_activo y total del activo.
    """
    cur = mysql.connection.cursor()
    if riesgo == 'operacional':
        sql = """SELECT nombre, tipo_activo, total FROM matriz_activo
                 WHERE id_rol IN (2, 4, 5, 6, 7, 10, 11, 12, 13) AND total >= 9"""
    elif riesgo == 'administrativo':
        sql = """SELECT nombre, tipo_activo, total FROM matriz_activo
                 WHERE id_rol IN (8, 14, 15, 16, 17, 18, 19, 20, 21) AND total >= 9"""
    elif riesgo == 'T-I':
        sql = """SELECT nombre, tipo_activo, total FROM matriz_activo
                 WHERE id_rol = 9 AND total >= 9"""
    else:
        return []

    cur.execute(sql)
    nombre_columnas = [desc[0] for desc in cur.description]
    activos_lista = [dict(zip(nombre_columnas, row)) for row in cur.fetchall()]
    cur.close()
    return activos_lista
