from datetime import datetime
import pytz
import time

from extension import mysql


zona_actual = pytz.timezone('America/Bogota')
fecha_registro = datetime.now(zona_actual)
IND_CACHE_TTL = 30
_IND_CACHE = {}


def _cache_get(key):
    cached = _IND_CACHE.get(key)
    if not cached:
        return None

    expires_at, value = cached
    if expires_at < time.time():
        _IND_CACHE.pop(key, None)
        return None

    return value


def _cache_set(key, value, ttl=IND_CACHE_TTL):
    _IND_CACHE[key] = (time.time() + ttl, value)
    return value


def clear_indicadores_cache():
    _IND_CACHE.clear()


'''GESTION DE PRODUCCION'''
def uvt_rol(rol):
    valores_uvt = {
        5: 36308,
        2: 49799,
        4: 47065,
        7: 47065,
        13: 49799,
    }
    return valores_uvt.get(rol, 0)


def obtener_r_extemporeaneo_mes(mes, rol, proceso):
    cache_key = ("obtener_r_extemporaneo", mes, rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT documentos_extemporaneos, documentos_entregados FROM ind_EntregasFisicas WHERE mes = %s AND id_rol = %s AND proceso = %s",
        (mes, rol, proceso),
    )
    resultado = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, resultado[0] if resultado else None)


def obtener_r_extemporeaneoFisico_mes(mes, rol, proceso):
    cache_key = ("obtener_r_extemporaneo_fisico", mes, rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT documentos_extemporaneos, documentos_entregados FROM ind_EntregasFisicas WHERE mes = %s AND id_rol = %s AND proceso = %s",
        (mes, rol, proceso),
    )
    resultado = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, resultado[0] if resultado else None)


def lista_sancionesMagenticas(rol):
    cache_key = ("lista_sanciones_magneticas", rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, R_extemporaneos, r_digicom, meta, multa, analisis
        FROM ind_sancionesMagneticas
        WHERE rol = %s
    """
    cur.execute(sql, (rol,))
    sanciones_magneticas = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, sanciones_magneticas)


def guardar_sancionesMagneticas(datos, rol):
    cur = mysql.connection.cursor()
    check_sql = "SELECT COUNT(*) FROM ind_sancionesMagneticas WHERE mes = %s AND rol = %s"
    cur.execute(check_sql, (datos['mes'], rol))
    if cur.fetchone()[0] > 0:
        cur.close()
        raise ValueError(f"Ya existe un registro para el mes de '{datos['mes']}' en este indicador.")

    sql = """
        INSERT INTO ind_sancionesMagneticas (mes, R_extemporaneos, r_digicom, p_aceptacion, resultado, meta, uvt, multa, analisis, fecha_registro, rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    r_extemporaneos = int(datos.get('R_extemporaneos', '0').strip() or 0)
    r_digicom = int(datos.get('r_digicom', '0').strip() or 0)
    p_aceptacion = float(datos.get('P_aceptacion', '0.0').strip() or 0.0)
    resultado = float(datos.get('resultado', '0.0').strip() or 0.0)
    uvt = float(datos.get('uvt', '0.0').strip() or 0.0)
    multa = float(datos.get('multa', '0.0').strip() or 0.0)

    valores = (
        datos.get('mes', ''),
        r_extemporaneos,
        r_digicom,
        p_aceptacion,
        resultado,
        datos.get('meta', ''),
        uvt,
        multa,
        datos.get('analisis', ''),
        fecha_registro,
        rol,
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
    clear_indicadores_cache()


def grafica_sancionesMagneticas(rol):
    cache_key = ("grafica_sanciones_magneticas", rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    cur.execute("SELECT mes, multa FROM ind_sancionesMagneticas WHERE rol = %s ", (rol,))
    resultados = cur.fetchall()
    cur.close()

    meses = []
    multas = []
    for fila in resultados:
        meses.append(fila[0])
        try:
            multa = float(str(fila[1]).replace('$', '').strip()) if fila[1] else 0
        except ValueError:
            multa = 0
        multas.append(multa)

    return _cache_set(cache_key, (meses, multas))


def guardar_registrosFisicos(datos, rol):
    cur = mysql.connection.cursor()
    check_sql = "SELECT COUNT(*) FROM ind_EntregasFisicas WHERE mes = %s AND id_rol = %s AND proceso = %s"
    cur.execute(check_sql, (datos['mes'], rol, datos['proceso']))
    if cur.fetchone()[0] > 0:
        cur.close()
        raise ValueError(f"Ya existe un registro para el mes de '{datos['mes']}' en este indicador.")

    sql = """
        INSERT INTO ind_EntregasFisicas (mes, documentos_entregados, documentos_extemporaneos, resultado, meta, analisis, fecha_registro, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    documentos_entregados = int(datos['documentos_entregados']) if datos['documentos_entregados'] and datos['documentos_entregados'].strip() else 0
    documentos_extemporaneos = int(datos['documentos_extemporaneos']) if datos['documentos_extemporaneos'] and datos['documentos_extemporaneos'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0

    valores = (
        datos['mes'],
        documentos_entregados,
        documentos_extemporaneos,
        resultado,
        datos['meta'],
        datos['analisis'],
        fecha_registro,
        datos['proceso'],
        rol,
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
    clear_indicadores_cache()


def lista_registrosFisicos(rol, proceso):
    cache_key = ("lista_registros_fisicos", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, documentos_entregados, documentos_extemporaneos, resultado, meta, analisis
        FROM ind_EntregasFisicas
        WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    registros_fisicos = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, registros_fisicos)


def grafica_registrosFisicos(rol, proceso):
    cache_key = ("grafica_registros_fisicos", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_EntregasFisicas WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    cur.close()

    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    return _cache_set(cache_key, (meses, porcentajes))


def lista_sancionesFisicos(rol):
    cache_key = ("lista_sanciones_fisicos", rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, D_extemporaneos, D_digicom, meta, multa, analisis
        FROM ind_sancionesFisicos
        WHERE rol = %s
    """
    cur.execute(sql, (rol,))
    sanciones_fisicos = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, sanciones_fisicos)


def guardar_sancionesFisicos(datos, rol):
    cur = mysql.connection.cursor()
    check_sql = "SELECT COUNT(*) FROM ind_sancionesFisicos WHERE mes = %s AND rol = %s"
    cur.execute(check_sql, (datos['mes'], rol))
    if cur.fetchone()[0] > 0:
        cur.close()
        raise ValueError(f"Ya existe un registro para el mes de '{datos['mes']}' en este indicador.")

    sql = """
        INSERT INTO ind_sancionesFisicos (mes, D_extemporaneos, D_digicom, p_aceptacion, resultado, meta, uvt, multa, analisis, fecha_registro, rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    d_extemporaneos = int(datos.get('D_extemporaneos2', '0').strip() or 0)
    dr_digicom = int(datos.get('dr_digicom', '0').strip() or 0)
    p_aceptacion = float(datos.get('P_aceptacion_fisicos', '0.0').strip() or 0.0)
    resultado = float(datos.get('resultado_sancionesFisicos', '0.0').strip() or 0.0)
    uvt = float(datos.get('uvt_sancionesFisicos', '0.0').strip() or 0.0)
    multa = float(datos.get('multa_sancionesFisicos', '0.0').strip() or 0.0)

    valores = (
        datos.get('mes', ''),
        d_extemporaneos,
        dr_digicom,
        p_aceptacion,
        resultado,
        datos.get('meta_sancionesFisicos', ''),
        uvt,
        multa,
        datos.get('analisis_sancionesFisicos', ''),
        fecha_registro,
        rol,
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
    clear_indicadores_cache()


def grafica_sancionesFisicos(rol):
    cache_key = ("grafica_sanciones_fisicos", rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    cur.execute("SELECT mes, multa FROM ind_sancionesFisicos WHERE rol = %s ", (rol,))
    resultados = cur.fetchall()
    cur.close()

    meses = []
    multas = []
    for fila in resultados:
        meses.append(fila[0])
        try:
            multa = float(str(fila[1]).replace('$', '').strip()) if fila[1] else 0
        except ValueError:
            multa = 0
        multas.append(multa)

    return _cache_set(cache_key, (meses, multas))


def lista_inconsitenciasPasivo(rol, proceso):
    cache_key = ("lista_inconsistencias_pasivo", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, t_casos, e_grabacion_analisis, resultado, meta, analisis
        FROM ind_incPasivo
        WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    inconsistencias_pasivo = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, inconsistencias_pasivo)


def guardar_inconsitenciasPasivo(datos, rol):
    cur = mysql.connection.cursor()
    check_sql = "SELECT COUNT(*) FROM ind_incPasivo WHERE mes = %s AND id_rol = %s AND proceso = %s"
    cur.execute(check_sql, (datos['mes'], rol, datos['proceso']))
    if cur.fetchone()[0] > 0:
        cur.close()
        raise ValueError(f"Ya existe un registro para el mes de '{datos['mes']}' en este indicador.")

    sql = """
        INSERT INTO ind_incPasivo (mes, t_casos, e_grabacion_analisis, resultado, meta, analisis, fecha_registro, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    t_casos = int(datos['t_casos']) if datos['t_casos'] and datos['t_casos'].strip() else 0
    e_grabacion_analisis = int(datos['e_grabacion_analisis']) if datos['e_grabacion_analisis'] and datos['e_grabacion_analisis'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0

    valores = (
        datos['mes'],
        t_casos,
        e_grabacion_analisis,
        resultado,
        datos['meta'],
        datos['analisis'],
        fecha_registro,
        datos['proceso'],
        rol,
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
    clear_indicadores_cache()


def grafica_inconsitenciasPasivo(rol, proceso):
    cache_key = ("grafica_inconsistencias_pasivo", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_incPasivo WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    cur.close()

    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    return _cache_set(cache_key, (meses, porcentajes))


def lista_TRespuesta_credito(rol, proceso):
    cache_key = ("lista_trespuesta_credito", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, t_creditos, t_respuesta, resultado, analisis
        FROM ind_Trespuesta_credito
        WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    t_respuestaCredito = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, t_respuestaCredito)


def guardar_TRespuesta_credito(datos, rol):
    cur = mysql.connection.cursor()
    check_sql = "SELECT COUNT(*) FROM ind_Trespuesta_credito WHERE mes = %s AND id_rol = %s AND proceso = %s"
    cur.execute(check_sql, (datos['mes'], rol, datos['proceso']))
    if cur.fetchone()[0] > 0:
        cur.close()
        raise ValueError(f"Ya existe un registro para el mes de '{datos['mes']}' en este indicador.")

    sql = """
        INSERT INTO ind_Trespuesta_credito (mes, t_creditos, t_respuesta, resultado, analisis, fecha_registro, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    t_creditos = int(datos['t_creditos']) if datos['t_creditos'] and datos['t_creditos'].strip() else 0

    valores = (
        datos['mes'],
        t_creditos,
        datos['t_respuesta'],
        datos['resultado'],
        datos['analisis'],
        fecha_registro,
        datos['proceso'],
        rol,
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
    clear_indicadores_cache()


def datos_mes_anterior(mes, proceso, rol):
    cache_key = ("datos_mes_anterior", mes, proceso, rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT t_respuesta FROM ind_Trespuesta_credito WHERE proceso = %s AND id_rol = %s AND mes = %s",
        (proceso, rol, mes),
    )
    mes_anterior = cur.fetchone()
    cur.close()
    return _cache_set(cache_key, mes_anterior)


def grafica_TRespuesta_credito(rol, proceso):
    cache_key = ("grafica_trespuesta_credito", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, t_respuesta FROM ind_Trespuesta_credito WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    cur.close()

    meses = [fila[0] for fila in resultados]
    t_respuesta = [fila[1].total_seconds() for fila in resultados]
    return _cache_set(cache_key, (meses, t_respuesta))


'''ADMINISTRATIVO'''
def guardar_Administrativo(datos, rol):
    cur = mysql.connection.cursor()
    check_sql = "SELECT COUNT(*) FROM ind_Administrativo WHERE mes = %s AND id_rol = %s AND proceso = %s"
    cur.execute(check_sql, (datos['mes'], rol, datos['proceso']))
    if cur.fetchone()[0] > 0:
        cur.close()
        raise ValueError(f"Ya existe un registro para el mes de '{datos['mes']}' en este indicador.")

    sql = """
        INSERT INTO ind_Administrativo (mes, Sol_atendidas, Sol_realizadas, resultado, meta, analisis, fecha_registro, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    sol_atendidas = int(datos['Sol_atendidas']) if datos['Sol_atendidas'] and datos['Sol_atendidas'].strip() else 0
    sol_realizadas = int(datos['Sol_realizadas']) if datos['Sol_realizadas'] and datos['Sol_realizadas'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0

    valores = (
        datos['mes'],
        sol_atendidas,
        sol_realizadas,
        resultado,
        datos['meta'],
        datos['analisis'],
        fecha_registro,
        datos['proceso'],
        rol,
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
    clear_indicadores_cache()


def lista_Administrativo(rol, proceso):
    cache_key = ("lista_administrativo", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, Sol_atendidas, Sol_realizadas, resultado, meta, analisis
        FROM ind_Administrativo
        WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    resultado_administrativo = cur.fetchall()
    cur.close()
    return _cache_set(cache_key, resultado_administrativo)


def grafica_Administrativo(rol, proceso):
    cache_key = ("grafica_administrativo", rol, proceso)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_Administrativo WHERE id_rol = %s AND proceso = %s
    """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    cur.close()

    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    return _cache_set(cache_key, (meses, porcentajes))
