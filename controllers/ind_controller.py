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


def obtener_r_extemporeaneo_mes(mes, rol, proceso):
    cur = mysql.connection.cursor()
    #cur.execute("SELECT R_extemporaneos, T_registros FROM ind_registrosExtemporaneos WHERE mes = %s AND id_rol = %s", (mes, rol))
    cur.execute("SELECT documentos_extemporaneos, documentos_entregados FROM ind_EntregasFisicas WHERE mes = %s AND id_rol = %s AND proceso = %s", (mes, rol, proceso))
    print("Magneticos", mes, rol, proceso)
    resultado = cur.fetchall()
    
    cur.close()
    return resultado[0] if resultado else None
def obtener_r_extemporeaneoFisico_mes(mes, rol, proceso):
    cur = mysql.connection.cursor()
    cur.execute("SELECT documentos_extemporaneos, documentos_entregados FROM ind_EntregasFisicas WHERE mes = %s AND id_rol = %s AND proceso = %s", (mes, rol, proceso))
    resultado = cur.fetchall()
    print(resultado)
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
    
    # Leemos las claves específicas que la ruta nos envía
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






