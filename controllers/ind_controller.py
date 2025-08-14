from extension import mysql
from controllers.rol_controller import nombre_rol as nombre
import os

'''GESTION DE PRODUCCION'''
def uvt_rol(rol):
    valores_uvt = {
        5:36308,
        2:49799,
        4:47065,
        7:47065,
        13:49799,
    }
    return valores_uvt.get(rol, 0)

def lista__calidadInformacion(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, form_digitados, err_digitacion, resultado, meta, analisis
        FROM ind_calidadinformacion
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    calidad_info = cur.fetchall()
    cur.close()
    return calidad_info
def guardar_calidadInformacion(datos, rol):

    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_calidadinformacion (mes, form_digitados, err_digitacion, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['form_digitados'],
        datos['err_digitacion'],
        datos['resultado'],
        datos['meta'],
        datos['analisis'], 
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_calidadInformacion(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_calidadinformacion WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_registrosExtemporaneos(rol):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, T_registros, R_extemporaneos, resultado, meta, analisis
        FROM ind_registrosExtemporaneos
        WHERE id_rol = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol,))
    registros_extemporaneos = cur.fetchall()
    cur.close()
    return registros_extemporaneos
def guardar_registrosExtemporaneos(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_registrosExtemporaneos (mes, T_registros, R_extemporaneos, resultado, meta, analisis, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['T_registros'],
        datos['R_extemporaneos'],
        datos['resultado'],
        datos['meta'],
        datos['analisis'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_registrosExtemporaneos(rol):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_registrosExtemporaneos WHERE id_rol = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol,))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def obtener_r_extemporeaneo_mes(mes, rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT R_extemporaneos, T_registros FROM ind_registrosExtemporaneos WHERE mes = %s AND id_rol = %s", (mes, rol))
    resultado = cur.fetchall()
    cur.close()
    return resultado[0] if resultado else None
def obtener_r_extemporeaneoFisico_mes(mes, rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT documentos_extemporaneos, documentos_entregados FROM ind_EntregasFisicas WHERE mes = %s AND id_rol = %s", (mes, rol))
    resultado = cur.fetchall()
    cur.close()
    return resultado[0] if resultado else None

def lista_sancionesMagenticas(rol):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, R_extemporaneos, r_digicom, meta, multa, analisis
        FROM ind_sancionesMagneticas
        WHERE rol = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol,))
    sanciones_magneticas = cur.fetchall()
    cur.close()
    return sanciones_magneticas
def guardar_sancionesMagneticas(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_sancionesMagneticas (mes, R_extemporaneos, r_digicom, p_aceptacion, resultado, meta, uvt, multa, analisis, rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['R_extemporaneos2'],
        datos['r_digicom'],
        datos['P_aceptacion'],
        float(datos['resultado']),
        datos['meta'],
        float(datos['uvt']),
        datos['multa'],
        datos['analisis'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_sancionesMagneticas(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT mes, multa FROM ind_sancionesMagneticas WHERE rol = %s ORDER BY mes ASC", (rol,))
    resultados = cur.fetchall()
    cur.close()

    meses = []
    multas = []
    for fila in resultados:
        meses.append(fila[0])
        try:
            # Convertir "$ 18154" a 18154
            multa = float(str(fila[1]).replace('$', '').strip()) if fila[1] else 0
        except ValueError:
            multa = 0
        multas.append(multa)

    return meses, multas


def guardar_registrosFisicos(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_EntregasFisicas (mes, documentos_entregados, documentos_extemporaneos, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['documentos_entregados'],
        datos['documentos_extemporaneos'],
        datos['resultado'],
        datos['meta'],
        datos['analisis'],
        datos['proceso'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def lista_registrosFisicos(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, documentos_entregados, documentos_extemporaneos, resultado, meta, analisis
        FROM ind_EntregasFisicas
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    registros_fisicos = cur.fetchall()
    cur.close()
    return registros_fisicos
def grafica_registrosFisicos(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_EntregasFisicas WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_sancionesFisicos(rol):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, D_extemporaneos, D_digicom, meta, multa, analisis
        FROM ind_sancionesFisicos
        WHERE rol = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol,))
    sanciones_fisicos = cur.fetchall()
    cur.close()
    return sanciones_fisicos
def guardar_sancionesFisicos(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_sancionesFisicos (mes, D_extemporaneos, D_digicom, p_aceptacion, resultado, meta, uvt, multa, analisis, rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['D_extemporaneos2'],
        datos['dr_digicom'],
        datos['P_aceptacion_fisicos'],
        float(datos['resultado_sancionesFisicos']),
        datos['meta_sancionesFisicos'],
        float(datos['uvt_sancionesFisicos']),
        datos['multa_sancionesFisicos'],
        datos['analisis_sancionesFisicos'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_sancionesFisicos(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT mes, multa FROM ind_sancionesFisicos WHERE rol = %s ORDER BY mes ASC", (rol,))
    resultados = cur.fetchall()
    cur.close()

    meses = []
    multas = []
    for fila in resultados:
        meses.append(fila[0])
        try:
            # Convertir "$ 18154" a 18154
            multa = float(str(fila[1]).replace('$', '').strip()) if fila[1] else 0
        except ValueError:
            multa = 0
        multas.append(multa)

    return meses, multas

def lista_cintasMagneticas(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, cin_enviadas, cin_rechazadas, resultado, meta, analisis
        FROM ind_cintasMagneticas
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    cintas_magneticas = cur.fetchall()
    cur.close()
    return cintas_magneticas
def guardar_cintasMagneticas(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_cintasMagneticas (mes, cin_enviadas, cin_rechazadas, resultado, meta, analisis, id_rol, proceso)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['cintas_enviadas'],
        datos['cintas_rechazadas'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'], 
        rol,
        datos['proceso']
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_cintasMagneticas(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_cintasMagneticas WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    multas = []
    for fila in resultados:
        try:
            # Convertir "$ 18154" a 18154
            multa = float(str(fila[1]).replace('$', '').strip()) if fila[1] else 0
        except ValueError:
            multa = 0
        multas.append(multa)
    cur.close()
    return meses, multas

def lista_informesEntregados(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, inf_enviados, inf_fueraTiempo, resultado, meta, analisis
        FROM ind_entregaInformes
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    informes_entregados = cur.fetchall()
    cur.close()
    return informes_entregados
def guardar_informesEntregados(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_entregaInformes (mes, inf_enviados, inf_fueraTiempo, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['informes_entregados'],
        datos['informes_extemporaneos'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_informesEntregados(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_entregaInformes WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_sitio_web(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, img_enviados, img_fueraTiempo, resultado, meta, analisis
        FROM ind_sitioWeb
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    informes_entregados = cur.fetchall()
    cur.close()
    return informes_entregados
def guardar_sitio_web(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_sitioWeb (mes, img_enviados, img_fueraTiempo, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['img_enviados'],
        datos['img_fueraTiempo'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_sitio_web(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_sitioWeb WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_calidad_informes(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, inf_entregados, inf_errados, resultado, meta, analisis
        FROM ind_calidadInformes
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    informes_entregados = cur.fetchall()
    cur.close()
    return informes_entregados    
def guardar_calidadInformes(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_calidadInformes (mes, inf_entregados, inf_errados, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['inf_entregados'],
        datos['inf_errados'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_calidadInformes(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_calidadInformes WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_entregaImagenes(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, img_entregadas, img_extemporaneas, resultado, meta, analisis
        FROM ind_entregaImagenes
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    informes_entregados = cur.fetchall()
    cur.close()
    return informes_entregados    
def guardar_entregaImagenes(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_entregaImagenes (mes, img_entregadas, img_extemporaneas, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['img_entregadas'],
        datos['img_extemporaneas'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_entregaImagenes(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_entregaImagenes WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_inconsistenciasSolucionadas(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, inc_repotadas, inc_solucionadas, resultado, meta, analisis
        FROM ind_inconsistenciasSolucionadas
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    incosistencias = cur.fetchall()
    cur.close()
    return incosistencias    
def guardar_inconsistenciasSolucionadas(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_inconsistenciasSolucionadas (mes, inc_repotadas, inc_solucionadas, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['inc_repotadas'],
        datos['inc_solucionadas'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_inconsistenciasSolucionadas(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_inconsistenciasSolucionadas WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_traslado(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, traslados, traslados_extemporaneos, resultado, meta, analisis
        FROM ind_traslados
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    traslados = cur.fetchall()
    cur.close()
    return traslados    
def guardar_traslado(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_traslados (mes, traslados, traslados_extemporaneos, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['traslados'],
        datos['traslados_extemporaneos'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_traslado(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_traslados WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes

def lista_inconsitenciasPasivo(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, t_casos, e_grabacion_analisis, resultado, meta, analisis
        FROM ind_incPasivo
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    inconsistencias_pasivo = cur.fetchall()
    cur.close()
    return inconsistencias_pasivo    
def guardar_inconsitenciasPasivo(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_incPasivo (mes, t_casos, e_grabacion_analisis, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['t_casos'],
        datos['e_grabacion_analisis'],
        float(datos['resultado']),
        datos['meta'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_inconsitenciasPasivo(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_incPasivo WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes


def lista_TRespuesta_credito(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, t_creditos, t_respuesta, resultado, analisis 
        FROM ind_Trespuesta_credito
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    t_respuestaCredito = cur.fetchall()
    cur.close()
    return t_respuestaCredito    
def guardar_TRespuesta_credito(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_Trespuesta_credito (mes, t_creditos, t_respuesta, resultado, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['t_creditos'],
        datos['t_respuesta'],
        datos['resultado'],
        datos['analisis'],
        datos['proceso'],
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def datos_mes_anterior(mes, proceso, rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT t_respuesta FROM ind_Trespuesta_credito WHERE proceso = %s AND id_rol = %s AND mes = %s", (proceso, rol, mes))
    mes_anterior = cur.fetchone()
    cur.close()
    return mes_anterior
def grafica_TRespuesta_credito(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, t_respuesta FROM ind_Trespuesta_credito WHERE id_rol = %s AND proceso = %s
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    t_respuesta = [fila[1].total_seconds() for fila in resultados]
    cur.close()
    return meses, t_respuesta

def guardar_TransAduanas(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_TransAduanas (mes, t_aduanas, t_aduanasFueraTiempo, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['t_aduanas'],
        datos['t_aduanasFueraTiempo'],
        datos['resultado'],
        datos['meta'],
        datos['analisis'],
        datos['proceso'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def lista_TransAduanas(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, t_aduanas, t_aduanasFueraTiempo, resultado, meta, analisis
        FROM ind_TransAduanas
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    transmisioin_aduanas = cur.fetchall()
    cur.close()
    return transmisioin_aduanas
def grafica_TransAduanas(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_TransAduanas WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes


'''ADMINISTRATIVO'''
def guardar_Administrativo(datos, rol):
    cur = mysql.connection.cursor()
    sql = """
        INSERT INTO ind_Administrativo (mes, Sol_atendidas, Sol_realizadas, resultado, meta, analisis, proceso, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    valores = (
        datos['mes'],
        datos['Sol_atendidas'],
        datos['Sol_realizadas'],
        datos['resultado'],
        datos['meta'],
        datos['analisis'],
        datos['proceso'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def lista_Administrativo(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, Sol_atendidas, Sol_realizadas, resultado, meta, analisis
        FROM ind_Administrativo
        WHERE id_rol = %s AND proceso = %s
        ORDER BY mes DESC
    """
    cur.execute(sql, (rol, proceso))
    resultado_administrativo = cur.fetchall()
    cur.close()
    return resultado_administrativo
def grafica_Administrativo(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_Administrativo WHERE id_rol = %s AND proceso = %s
        ORDER BY mes ASC
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes






