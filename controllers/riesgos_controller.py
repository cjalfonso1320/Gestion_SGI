from extension import mysql

def guardar_riesgo(datos):
    cur = mysql.connection.cursor()
    sql = """
            INSERT INTO matriz_riesgos (
            proceso, nombre_activo, tipo_activo, criticidad_activo, amenaza, vulnerabilidad, 
            nombre_riesgo, descripcion_riesgo, tipo_riesgo, responsable_riesgo, norma,
            probabilidad_inherente, impacto_inherente, total_riesgo_inherente,
            criticidad_riesgo_inherente, control_norma_iso, control_descripcion,
            control_seguimiento, control_fecha_revision, probabilidad_residual, impacto_residual,
            total_riesgo_residual, criticidad_riesgo_residual, opciones_manejo, tratamiento_plan_accion,
            tratamiento_fecha_implementacion, tratamiento_responsable, seguimiento_descripcion, seguimiento_fecha
            ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
    valores = (
        datos.get('proceso'), datos.get('nombre_activo'), datos.get('tipoActivo'), datos.get('criticidadActivo'), datos.get('amenaza'),
        datos.get('vulnerabilidad'), datos.get('nombre_riesgo'), datos.get('descripcion_riesgo'), datos.get('tipoRiesgo'), datos.get('responsable_riesgo'),
        datos.get('norma'), datos.get('probabilidadInherente'), datos.get('impactoInherente'), datos.get('total_riesgoInherente'), datos.get('criticidadRiesgoInherente'),
        datos.get('NormaISO'), datos.get('descripcionControl'), datos.get('seguimientoControl'), datos.get('fechaRevision'), datos.get('probabilidadResidual'),
        datos.get('impactoResidual'), datos.get('total_riesgoResidual'), datos.get('criticidadRiesgoResidual'), datos.get('opcionesManejo'), datos.get('actividades_planAccion'),
        datos.get('fechaImplementacion'), datos.get('descripcion_seguimiento'), datos.get('responsable_implementacion'), datos.get('fechaSeguimiento')
    )
    cur.execute(sql, valores)
    nuevo_id = cur.lastrowid
    mysql.connection.commit()

    sql_select = "SELECT * from matriz_riesgos WHERE id = %s"
    cur.execute(sql_select, (nuevo_id, ))
    nuevo_registro = cur.fetchone()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    return dict(zip(column_names, nuevo_registro)) if nuevo_registro else None

def lista_riesgos(proceso):
    cur = mysql.connection.cursor()
    sql = "SELECT * FROM matriz_riesgos WHERE proceso = %s"
    cur.execute(sql, (proceso, ))
    column_names = [desc[0] for desc in cur.description]
    resultado = [dict(zip(column_names, row)) for row in cur.fetchall()]
    cur.close
    return resultado

def modificar_riesgo(riesgo_id, columna, nuevo_valor):
    """
    Actualiza una celda específica de un riesgo en la base de datos.
    """
    # Lista blanca de columnas para evitar inyección SQL y limitar qué se puede editar.
    columnas_permitidas = {
        'nombre_riesgo': 'nombre_riesgo',
        'nombre_activo': 'nombre_activo',
        'criticidad_riesgo_inherente': 'criticidad_riesgo_inherente',
        'criticidad_riesgo_residual': 'criticidad_riesgo_residual',
        'opciones_manejo': 'opciones_manejo'
        # Añade aquí otras columnas que quieras que sean editables desde la tabla.
    }

    if columna not in columnas_permitidas:
        # Si la columna no está en nuestra lista, lanzamos un error para prevenir cambios no deseados.
        raise ValueError(f"La columna '{columna}' no está permitida para actualización.")

    db_columna = columnas_permitidas[columna]
    
    cur = mysql.connection.cursor()
    # Usamos f-string de forma segura para el nombre de la columna (validado antes)
    # y parámetros de consulta para los valores, previniendo inyección SQL.
    sql = f"UPDATE matriz_riesgos SET `{db_columna}` = %s WHERE id = %s"
    
    cur.execute(sql, (nuevo_valor, riesgo_id))
    mysql.connection.commit()
    cur.close()