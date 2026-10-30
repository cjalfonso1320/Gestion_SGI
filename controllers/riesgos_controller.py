"""Controlador de la Matriz de Riesgos.

Gestiona el registro, consulta y actualización de riesgos en la matriz
de riesgos del sistema, incluyendo el cálculo de criticidad inherente
y residual, y la gestión de controles y tratamientos.
"""

from extension import mysql
from datetime import date, datetime


def _serializar_para_json(d):
    """Convierte objetos date y datetime a string ISO para serialización JSON.

    Args:
        d: Diccionario con posibles valores date/datetime.

    Returns:
        dict: Diccionario con valores serializables a JSON.
    """
    if d is None:
        return None
    for k, v in d.items():
        if isinstance(v, (date, datetime)):
            d[k] = v.isoformat()
    return d


def obtener_riesgo_por_id(riesgo_id):
    """Obtiene un riesgo completo por su ID.

    Args:
        riesgo_id: ID del riesgo a consultar.

    Returns:
        dict: Datos del riesgo con todas sus columnas, o None si no existe.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM matriz_riesgos WHERE id = %s", (riesgo_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        return None
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    return _serializar_para_json(dict(zip(column_names, row)))


def actualizar_riesgo_completo(riesgo_id, datos):
    """Actualiza todos los campos de un riesgo existente.

    Args:
        riesgo_id: ID del riesgo a actualizar.
        datos: Diccionario con todos los campos del riesgo.

    Returns:
        dict: Datos completos del riesgo actualizado, o None si falló.
    """
    cur = mysql.connection.cursor()
    sql = """
        UPDATE matriz_riesgos SET
            proceso = %s, nombre_activo = %s, tipo_activo = %s, criticidad_activo = %s,
            amenaza = %s, vulnerabilidad = %s, nombre_riesgo = %s, descripcion_riesgo = %s,
            tipo_riesgo = %s, responsable_riesgo = %s, norma = %s,
            probabilidad_inherente = %s, impacto_inherente = %s, total_riesgo_inherente = %s,
            criticidad_riesgo_inherente = %s, control_norma_iso = %s, control_descripcion = %s,
            control_seguimiento = %s, control_fecha_revision = %s,
            probabilidad_residual = %s, impacto_residual = %s, total_riesgo_residual = %s,
            criticidad_riesgo_residual = %s, opciones_manejo = %s,
            tratamiento_plan_accion = %s, tratamiento_fecha_implementacion = %s,
            tratamiento_responsable = %s, seguimiento_descripcion = %s, seguimiento_fecha = %s
        WHERE id = %s
    """
    valores = (
        datos.get('proceso'), datos.get('nombre_activo'), datos.get('tipoActivo'), datos.get('criticidadActivo'),
        datos.get('amenaza'), datos.get('vulnerabilidad'), datos.get('nombre_riesgo'), datos.get('descripcion_riesgo'),
        datos.get('tipoRiesgo'), datos.get('responsable_riesgo'), datos.get('norma'),
        datos.get('probabilidadInherente'), datos.get('impactoInherente'), datos.get('total_riesgoInherente'),
        datos.get('criticidadRiesgoInherente'), datos.get('NormaISO'), datos.get('descripcionControl'),
        datos.get('seguimientoControl'), datos.get('fechaRevision'),
        datos.get('probabilidadResidual'), datos.get('impactoResidual'), datos.get('total_riesgoResidual'),
        datos.get('criticidadRiesgoResidual'), datos.get('opcionesManejo'),
        datos.get('actividades_planAccion'), datos.get('fechaImplementacion'),
        datos.get('responsable_implementacion'), datos.get('descripcion_seguimiento'), datos.get('fechaSeguimiento'),
        riesgo_id
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.execute("SELECT * FROM matriz_riesgos WHERE id = %s", (riesgo_id,))
    row = cur.fetchone()
    column_names = [desc[0] for desc in cur.description]
    cur.close()
    return _serializar_para_json(dict(zip(column_names, row))) if row else None


def guardar_riesgo(datos):
    """Inserta un nuevo riesgo en la matriz de riesgos.

    Args:
        datos: Diccionario con todos los campos del riesgo.

    Returns:
        dict: Datos completos del riesgo recién creado, o None si falló.
    """
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
    return _serializar_para_json(dict(zip(column_names, nuevo_registro))) if nuevo_registro else None


def lista_riesgos(proceso):
    """Obtiene todos los riesgos asociados a un proceso específico.

    Args:
        proceso: Nombre del proceso para filtrar los riesgos.

    Returns:
        list: Lista de diccionarios con los datos de cada riesgo.
    """
    cur = mysql.connection.cursor()
    sql = "SELECT * FROM matriz_riesgos WHERE proceso = %s"
    cur.execute(sql, (proceso, ))
    column_names = [desc[0] for desc in cur.description]
    resultado = [dict(zip(column_names, row)) for row in cur.fetchall()]
    cur.close()
    return resultado


def modificar_riesgo(riesgo_id, columna, nuevo_valor):
    """Actualiza una celda específica de un riesgo en la base de datos.

    Utiliza una lista blanca de columnas permitidas para prevenir
    inyección SQL y limitar qué campos se pueden editar desde la tabla.

    Args:
        riesgo_id: ID del riesgo a modificar.
        columna: Nombre de la columna a actualizar (data-column del frontend).
        nuevo_valor: Nuevo valor a asignar.

    Raises:
        ValueError: Si la columna no está en la lista blanca.
    """
    columnas_permitidas = {
        'nombre_riesgo': 'nombre_riesgo',
        'nombre_activo': 'nombre_activo',
        'criticidad_riesgo_inherente': 'criticidad_riesgo_inherente',
        'criticidad_riesgo_residual': 'criticidad_riesgo_residual',
        'opciones_manejo': 'opciones_manejo'
    }
    if columna not in columnas_permitidas:
        raise ValueError(f"La columna '{columna}' no está permitida para actualización.")
    db_columna = columnas_permitidas[columna]
    cur = mysql.connection.cursor()
    sql = f"UPDATE matriz_riesgos SET `{db_columna}` = %s WHERE id = %s"
    cur.execute(sql, (nuevo_valor, riesgo_id))
    mysql.connection.commit()
    cur.close()
