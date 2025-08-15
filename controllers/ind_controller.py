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
    
    # Validar y convertir valores numéricos
    form_digitados = int(datos['form_digitados']) if datos['form_digitados'] and datos['form_digitados'].strip() else 0
    err_digitacion = int(datos['err_digitacion']) if datos['err_digitacion'] and datos['err_digitacion'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        form_digitados,
        err_digitacion,
        resultado,
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
    
    # Validar y convertir valores numéricos
    t_registros = int(datos['T_registros']) if datos['T_registros'] and datos['T_registros'].strip() else 0
    r_extemporaneos = int(datos['R_extemporaneos']) if datos['R_extemporaneos'] and datos['R_extemporaneos'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        t_registros,
        r_extemporaneos,
        resultado,
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
    
    # Validar y convertir valores numéricos
    r_extemporaneos = int(datos['R_extemporaneos2']) if datos['R_extemporaneos2'] and datos['R_extemporaneos2'].strip() else 0
    r_digicom = int(datos['r_digicom']) if datos['r_digicom'] and datos['r_digicom'].strip() else 0
    p_aceptacion = float(datos['P_aceptacion']) if datos['P_aceptacion'] and datos['P_aceptacion'].strip() else 0.0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    uvt = float(datos['uvt']) if datos['uvt'] and datos['uvt'].strip() else 0.0
    multa = float(datos['multa']) if datos['multa'] and datos['multa'].strip() else 0.0
    
    valores = (
        datos['mes'],
        r_extemporaneos,
        r_digicom,
        p_aceptacion,
        resultado,
        datos['meta'],
        uvt,
        multa,
        datos['analisis'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_sancionesMagneticas(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT mes, multa FROM ind_sancionesMagneticas WHERE rol = %s ", (rol,))
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
    
    # Validar y convertir valores numéricos
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
        
    """
    cur.execute(sql, (rol, proceso))
    registros_fisicos = cur.fetchall()
    cur.close()
    return registros_fisicos
def grafica_registrosFisicos(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_EntregasFisicas WHERE id_rol = %s AND proceso = %s
        
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
    
    # Validar y convertir valores numéricos
    d_extemporaneos = int(datos['D_extemporaneos2']) if datos['D_extemporaneos2'] and datos['D_extemporaneos2'].strip() else 0
    dr_digicom = int(datos['dr_digicom']) if datos['dr_digicom'] and datos['dr_digicom'].strip() else 0
    p_aceptacion = float(datos['P_aceptacion_fisicos']) if datos['P_aceptacion_fisicos'] and datos['P_aceptacion_fisicos'].strip() else 0.0
    resultado = float(datos['resultado_sancionesFisicos']) if datos['resultado_sancionesFisicos'] and datos['resultado_sancionesFisicos'].strip() else 0.0
    uvt = float(datos['uvt_sancionesFisicos']) if datos['uvt_sancionesFisicos'] and datos['uvt_sancionesFisicos'].strip() else 0.0
    multa = float(datos['multa_sancionesFisicos']) if datos['multa_sancionesFisicos'] and datos['multa_sancionesFisicos'].strip() else 0.0
    
    valores = (
        datos['mes'],
        d_extemporaneos,
        dr_digicom,
        p_aceptacion,
        resultado,
        datos['meta_sancionesFisicos'],
        uvt,
        multa,
        datos['analisis_sancionesFisicos'], 
        rol
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    cur.close()
def grafica_sancionesFisicos(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT mes, multa FROM ind_sancionesFisicos WHERE rol = %s ", (rol,))
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
    
    # Validar y convertir valores numéricos
    cin_enviadas = int(datos['cintas_enviadas']) if datos['cintas_enviadas'] and datos['cintas_enviadas'].strip() else 0
    cin_rechazadas = int(datos['cintas_rechazadas']) if datos['cintas_rechazadas'] and datos['cintas_rechazadas'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        cin_enviadas,
        cin_rechazadas,
        resultado,
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
    
    # Validar y convertir valores numéricos
    inf_enviados = int(datos['informes_entregados']) if datos['informes_entregados'] and datos['informes_entregados'].strip() else 0
    inf_fuera_tiempo = int(datos['informes_extemporaneos']) if datos['informes_extemporaneos'] and datos['informes_extemporaneos'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        inf_enviados,
        inf_fuera_tiempo,
        resultado,
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
    
    # Validar y convertir valores numéricos
    img_enviados = int(datos['img_enviados']) if datos['img_enviados'] and datos['img_enviados'].strip() else 0
    img_fuera_tiempo = int(datos['img_fueraTiempo']) if datos['img_fueraTiempo'] and datos['img_fueraTiempo'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        img_enviados,
        img_fuera_tiempo,
        resultado,
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
    
    # Validar y convertir valores numéricos
    inf_entregados = int(datos['inf_entregados']) if datos['inf_entregados'] and datos['inf_entregados'].strip() else 0
    inf_errados = int(datos['inf_errados']) if datos['inf_errados'] and datos['inf_errados'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        inf_entregados,
        inf_errados,
        resultado,
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
    
    # Validar y convertir valores numéricos
    img_entregadas = int(datos['img_entregadas']) if datos['img_entregadas'] and datos['img_entregadas'].strip() else 0
    img_extemporaneas = int(datos['img_extemporaneas']) if datos['img_extemporaneas'] and datos['img_extemporaneas'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        img_entregadas,
        img_extemporaneas,
        resultado,
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
    
    # Validar y convertir valores numéricos
    inc_repotadas = int(datos['inc_repotadas']) if datos['inc_repotadas'] and datos['inc_repotadas'].strip() else 0
    inc_solucionadas = int(datos['inc_solucionadas']) if datos['inc_solucionadas'] and datos['inc_solucionadas'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        inc_repotadas,
        inc_solucionadas,
        resultado,
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
    
    # Validar y convertir valores numéricos
    traslados = int(datos['traslados']) if datos['traslados'] and datos['traslados'].strip() else 0
    traslados_extemporaneos = int(datos['traslados_extemporaneos']) if datos['traslados_extemporaneos'] and datos['traslados_extemporaneos'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        traslados,
        traslados_extemporaneos,
        resultado,
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
    
    # Validar y convertir valores numéricos
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
    
    # Validar y convertir valores numéricos
    t_creditos = int(datos['t_creditos']) if datos['t_creditos'] and datos['t_creditos'].strip() else 0
    
    valores = (
        datos['mes'],
        t_creditos,
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
    
    # Validar y convertir valores numéricos
    t_aduanas = int(datos['t_aduanas']) if datos['t_aduanas'] and datos['t_aduanas'].strip() else 0
    t_aduanas_fuera_tiempo = int(datos['t_aduanasFueraTiempo']) if datos['t_aduanasFueraTiempo'] and datos['t_aduanasFueraTiempo'].strip() else 0
    resultado = float(datos['resultado']) if datos['resultado'] and datos['resultado'].strip() else 0.0
    
    valores = (
        datos['mes'],
        t_aduanas,
        t_aduanas_fuera_tiempo,
        resultado,
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
        
    """
    cur.execute(sql, (rol, proceso))
    transmisioin_aduanas = cur.fetchall()
    cur.close()
    return transmisioin_aduanas
def grafica_TransAduanas(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_TransAduanas WHERE id_rol = %s AND proceso = %s
        
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
    
    # Validar y convertir valores numéricos
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
        
    """
    cur.execute(sql, (rol, proceso))
    resultado_administrativo = cur.fetchall()
    cur.close()
    return resultado_administrativo
def grafica_Administrativo(rol, proceso):
    cur = mysql.connection.cursor()
    sql = """
        SELECT mes, resultado FROM ind_Administrativo WHERE id_rol = %s AND proceso = %s
        
        """
    cur.execute(sql, (rol, proceso))
    resultados = cur.fetchall()
    meses = [fila[0] for fila in resultados]
    porcentajes = [float(fila[1]) for fila in resultados]
    cur.close()
    return meses, porcentajes






