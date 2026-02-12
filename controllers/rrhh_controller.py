from extension import mysql
from utils.password_utils import hash_password
import MySQLdb.cursors
import re
from datetime import datetime


#------------------------------------------------------
#-------------- TOTAL DE EMPLEADOS CONTEO -------------
#------------------------------------------------------
def total_empleados():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users_rrhh WHERE activo = 1")
    empleados = cur.fetchone()[0]
    cur.close()
    return empleados

#------------------------------------------------------
#------------ TOTAL DE EMPLEADOS RETIRADOS ------------
#------------------------------------------------------
def total_empleados_retirados():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users_rrhh WHERE activo = 2")
    empleados_retirados = cur.fetchone()[0]
    cur.close()
    return empleados_retirados

#------------------------------------------------------
#----------------- LISTA DE EMPLEADOS -----------------
#------------------------------------------------------
def empleados_lista():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT u.id, u.identificacion, u.nombres, u.apellidos, u.cedula_expedida_en, u.sexo, u.fecha_nacimiento,
        u.lugar_nacimiento, u.edad, ec.nombre AS estado_civil, gs.tipo AS grupo_sanguineo, u.numero_hijos, u.direccion, ci.nombre AS barrio, u.localidad,
        u.estrato, u.telefono_fijo, u.celular, u.correo, u.contacto_emergencia, u.telefono_emergencia,
        u.parentesco, eps.nombre AS eps, afp.nombre AS afp, ces.nombre AS cesantias, ccf.nombre AS ccf, arl.nombre AS arl,
        tp.nombre AS tipo_contrato, cg.nombre AS cargos, u.jornada,
        sd.nombre AS sedes, 
        u.antiguedad, ne.nombre AS nivel_escolaridad, u.estudia_actualmente, u.nombre_programa_actual, u.programa_academico,
        u.numero_cuenta, b.nombre AS bancos, gn.nombre AS grupo_nomina, cedula_path, foto_path, u.activo
        FROM users_rrhh u
        LEFT JOIN estado_civil ec ON u.estado_civil_id = ec.id
        LEFT JOIN grupo_sanguineo gs ON u.grupo_sanguineo_id = gs.id
        LEFT JOIN eps ON u.eps_id = eps.id
        LEFT JOIN afp ON u.afp_id = afp.id
        LEFT JOIN cesantias ces ON u.cesantias_id = ces.id
        LEFT JOIN ccf ON u.ccf_id = ccf.id
        LEFT JOIN arl ON u.arl_id = arl.id
        LEFT JOIN tipo_contrato tp ON u.tipo_contrato_id = tp.id
        LEFT JOIN cargos cg ON u.cargo_id = cg.id
        LEFT JOIN sedes sd ON u.sede = sd.id
        LEFT JOIN nivel_escolaridad ne ON u.nivel_escolaridad_id = ne.id
        LEFT JOIN banco b ON u.banco = b.id
        LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id 
        LEFT JOIN ciudades ci ON u.barrio = ci.id
    """
    cur.execute(sql)
    empleados = cur.fetchall()
    cantidad_contratos_sql = """
        SELECT empleado_id, COUNT(*) AS cantidad_contratos
        FROM contratos
        GROUP BY empleado_id
    """
    cur.execute(cantidad_contratos_sql)
    cantidad_contratos = cur.fetchall()
    cantidad_contratos_dict = {row['empleado_id']: row['cantidad_contratos'] for row in cantidad_contratos}
    for empleado in empleados:
        empleado['cantidad_contratos'] = cantidad_contratos_dict.get(empleado['id'], 0)
        
    salarios_sql = """
        SELECT empleado_id, salario_basico, factor_no_salarial, fecha_ingreso, fecha_finalizacion
        FROM contratos
        WHERE (empleado_id, id) IN (
            SELECT empleado_id, MAX(id)
            FROM contratos
            GROUP BY empleado_id
        )
    """
    cur.execute(salarios_sql)
    salarios = cur.fetchall()
    salarios_dict = {row['empleado_id']: row for row in salarios}
    for empleado in empleados:
        salario_info = salarios_dict.get(empleado['id'])
        if salario_info:
            empleado['fecha_ingreso'] = salario_info['fecha_ingreso']
            empleado['fecha_finalizacion'] = salario_info['fecha_finalizacion']
            empleado['salario_basico'] = salario_info['salario_basico']
            empleado['factor_no_salarial'] = salario_info['factor_no_salarial']
        else:
            empleado['fecha_ingreso'] = None
            empleado['fecha_finalizacion'] = None
            empleado['salario_basico'] = 0
            empleado['factor_no_salarial'] = 0
    cur.close()
    return empleados

#------------------------------------------------------
#------------- LISTA DE EMPLEADO POR ID ---------------
#------------------------------------------------------
def empleado_lista_completo(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT 
            u.id,
            u.identificacion,
            u.nombres,
            u.apellidos,
            u.cedula_expedida_en,
            u.sexo,
            u.fecha_nacimiento,
            u.lugar_nacimiento,
            u.edad,
            ec.nombre AS estado_civil,
            gs.tipo AS grupo_sanguineo,
            u.numero_hijos,
            u.direccion,
            ci.nombre AS barrio,
            u.localidad,
            u.estrato,
            u.telefono_fijo,
            u.celular,
            u.correo,
            u.contacto_emergencia,
            u.telefono_emergencia,
            u.parentesco, 
            eps.nombre AS eps,
            afp.nombre AS afp,
            ces.nombre AS cesantias,
            ccf.nombre AS ccf,
            arl.nombre AS arl,
            tp.nombre AS tipo_contrato,
            cg.nombre AS cargos, 
            u.jornada,
            sd.nombre AS sedes,
            u.antiguedad,
            ne.nombre AS nivel_escolaridad,
            u.estudia_actualmente,
            u.nombre_programa_actual,
            u.programa_academico,
            u.numero_cuenta,
            b.nombre AS bancos,
            gn.nombre AS grupo_nomina,
            cedula_path,
            foto_path,
            
            -- ids
            u.estado_civil_id,
            u.grupo_sanguineo_id,
            u.eps_id,
            u.afp_id,
            u.cesantias_id,
            u.ccf_id,
            u.arl_id,
            u.tipo_contrato_id,
            u.cargo_id,
            u.banco,
            u.grupo_nomina_id,
            u.barrio AS barrio_id,
            u.sede,
            u.nivel_escolaridad_id
            
        FROM users_rrhh u
            LEFT JOIN estado_civil ec ON u.estado_civil_id = ec.id
            LEFT JOIN grupo_sanguineo gs ON u.grupo_sanguineo_id = gs.id
            LEFT JOIN eps ON u.eps_id = eps.id
            LEFT JOIN afp ON u.afp_id = afp.id
            LEFT JOIN cesantias ces ON u.cesantias_id = ces.id
            LEFT JOIN ccf ON u.ccf_id = ccf.id
            LEFT JOIN arl ON u.arl_id = arl.id
            LEFT JOIN tipo_contrato tp ON u.tipo_contrato_id = tp.id
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
            LEFT JOIN sedes sd ON u.sede = sd.id
            LEFT JOIN nivel_escolaridad ne ON u.nivel_escolaridad_id = ne.id
            LEFT JOIN banco b ON u.banco = b.id
            LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id
            LEFT JOIN ciudades ci ON u.barrio = ci.id
        WHERE u.id = %s
    """
    cur.execute(sql, (id,))
    empleado = cur.fetchone()
    camtidad_contratos = """
        SELECT COUNT(*) AS cantidad_contratos
        FROM contratos
        WHERE empleado_id = %s
    """
    cur.execute(camtidad_contratos, (id,))
    cantidad_contratos = cur.fetchone()['cantidad_contratos']
    empleado['cantidad_contratos'] = cantidad_contratos
    salarios = """
        SELECT salario_basico, factor_no_salarial, fecha_ingreso, motivo, n_consecutivo
        FROM contratos
        WHERE empleado_id = %s
        ORDER BY id DESC
        LIMIT 1
    """
    cur.execute(salarios, (id,))
    salario = cur.fetchone()
    if salario:
        empleado['fecha_ingreso'] = salario['fecha_ingreso']
        empleado['salario_basico'] = salario['salario_basico']
        empleado['factor_no_salarial'] = salario['factor_no_salarial']
        empleado['motivo'] = salario['motivo']
        empleado['n_consecutivo'] = salario['n_consecutivo']
    else:
        empleado['salario_basico'] = 0
        empleado['factor_no_salarial'] = 0
        
    otrosi = """SELECT COUNT(*) AS total_otrosi FROM otrosi_contratos o
                LEFT JOIN contratos c ON o.id_contrato = c.id
                LEFT JOIN users_rrhh u ON c.empleado_id = u.id
                WHERE u.id = %s
            """
    cur.execute(otrosi, (id,))
    resul = cur.fetchone()
    
    if resul:
        empleado['cuenta_otrosi'] = resul['total_otrosi']
    if empleado:
        empleado["fecha_nacimiento"] = format_fecha(empleado.get("fecha_nacimiento"))
        empleado["fecha_ingreso"] = format_fecha(empleado.get("fecha_ingreso"))
    cur.close()
    return empleado

#------------------------------------------------------
#----------------- DESCATIVAR EMPLEADO ----------------
#------------------------------------------------------
def desactivar_empleado(id, fecha_retiro, motivo_retiro):
    cur = mysql.connection.cursor()
    update_estado = """
                UPDATE users_rrhh SET
                    activo = 2
                WHERE id = %s
                """
    cur.execute(update_estado, (id,))
    update_contrato = """
                UPDATE contratos SET
                    fecha_finalizacion = %s,
                    motivo = %s
                WHERE empleado_id = %s AND fecha_finalizacion IS NULL
                """
    cur.execute(update_contrato, (fecha_retiro, motivo_retiro, id))
    mysql.connection.commit()
    cur.close()


#------------------------------------------------------
#----------------- ACTIVAR EMPLEADO -------------------
#------------------------------------------------------
def activar_empleado(id, fecha_reingreso, salario_basico, factor_no_salarial, tipoContrato):
    cur = mysql.connection.cursor()
    update_estado = """
                UPDATE users_rrhh SET
                    activo = 1
                WHERE id = %s
                """
    cur.execute(update_estado, (id,))
    create_contrato = """
                INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo)
                VALUES (%s, %s, %s, %s, %s)
                """
    salario_basico = limpiar_decumal(salario_basico)
    factor_no_salarial = limpiar_decumal(factor_no_salarial)
    n_consecutivo = genera_consecutivo(tipoContrato)
    update_contrato = "UPDATE users_rrhh SET tipo_contrato_id = %s WHERE id = %s"
    cur.execute(update_contrato, (tipoContrato, id))
    cur.execute(create_contrato, (id, fecha_reingreso, salario_basico, factor_no_salarial, n_consecutivo))
    mysql.connection.commit()
    cur.close()

#------------------------------------------------------
#-------------------- ESTADO CIVIL --------------------
#------------------------------------------------------
def estado_civil():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM estado_civil")
    estados = cur.fetchall()
    cur.close()
    return estados

#------------------------------------------------------
#------------------ GRUPO SANGUINEO -------------------
#------------------------------------------------------
def grupo_sanguineo():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM grupo_sanguineo")
    g_sanguineo = cur.fetchall()
    cur.close()
    return g_sanguineo

#------------------------------------------------------
#------------------------- EPS ------------------------
#------------------------------------------------------
def eps():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM eps")
    eps = cur.fetchall()
    cur.close()
    return eps

#------------------------------------------------------
#------------------------- AFP ------------------------
#------------------------------------------------------
def afp():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM afp")
    afp = cur.fetchall()
    cur.close()
    return afp

#------------------------------------------------------
#--------------------- CESANTIAS ----------------------
#------------------------------------------------------
def cesantias():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM cesantias")
    cesantias = cur.fetchall()
    cur.close()
    return cesantias

#------------------------------------------------------
#------------------------- CCF ------------------------
#------------------------------------------------------
def ccf():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM ccf")
    ccf = cur.fetchall()
    cur.close()
    return ccf

#------------------------------------------------------
#------------------------- ARL ------------------------
#------------------------------------------------------
def arl():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM arl")
    arl = cur.fetchall()
    cur.close()
    return arl

#------------------------------------------------------
#---------------------- CONTRATOS ---------------------
#------------------------------------------------------
def tipo_contrato():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tipo_contrato")
    tipo_contrato = cur.fetchall()
    cur.close()
    return tipo_contrato
def tipoContrato_id(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT nombre, ult_consecutivo FROM tipo_contrato WHERE id = %s ", (id,))
    contrato = cur.fetchone()
    cur.close()
    return contrato
def actualiza_consecutivo(id, valor):
    cur = mysql.connection.cursor()
    sql = "UPDATE tipo_contrato SET ult_consecutivo = %s WHERE id = %s"
    cur.execute(sql, (valor, id))
    mysql.connection.commit()
    cur.close()
def genera_consecutivo(tipo_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cur.execute("SELECT ult_consecutivo FROM tipo_contrato WHERE id = %s", (tipo_id,))
    res = cur.fetchone()
    
    if not res or not res['ult_consecutivo']:
        cur.close()
        return "CONTRATO-001"
    
    ultimo_texto = res['ult_consecutivo']
    
    #separa prefijo y codigo
    match = re.search(r'(.*?)(\d+)$', ultimo_texto)
    
    if match:
        prefijo = match.group(1)
        numero_str = match.group(2)
        logintud_ceros = len(numero_str)
        
        #incrementa consecutivo
        nuevo_numero = int(numero_str) + 1
        
        #rellena ceros
        nuevo_consecutivo_texto = f"{prefijo}{str(nuevo_numero).zfill(logintud_ceros)}"
        
        #actualiza tabla para el siguiente empleado
        cur.execute("UPDATE tipo_contrato SET ult_consecutivo = %s WHERE id = %s", (nuevo_consecutivo_texto, tipo_id))
        mysql.connection.commit()
        cur.close()
        return nuevo_consecutivo_texto
    cur.close()
    return ultimo_texto #si no hay numeros, devuelve lo mismo por seguridad
def guardar_fecha_contrato(empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, consecutivo):
    cur = mysql.connection.cursor()
    salario_basico = limpiar_decumal(salario_basico)
    factor_no_salarial = limpiar_decumal(factor_no_salarial)
    cur.execute("""
                INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo)
                VALUES (%s, %s, %s, %s, %s)
                """, (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, consecutivo))
    mysql.connection.commit()
    cur.close()
def contratos_empleado(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
                SELECT 
                    c.id, c.empleado_id, c.fecha_ingreso, 
                    c.fecha_finalizacion, c.salario_basico, 
                    c.factor_no_salarial, tc.nombre AS tipo_contrato, 
                    c.motivo, c.n_consecutivo
                FROM contratos c
                LEFT JOIN users_rrhh u ON c.empleado_id = u.id
                LEFT JOIN tipo_contrato tc ON u.tipo_contrato_id = tc.id
                WHERE empleado_id = %s
                ORDER BY c.id DESC
                """, (id,))
    contratos = cur.fetchall()
    
    #PARA CADA CONTRATO BUSCAMOS SUU OTROSI
    for contrato in contratos:
        cur.execute("""
                    SELECT
                        tipo_otrosi, fecha_inicio, descripcion
                        FROM otrosi_contratos
                        WHERE id_contrato = %s
                        ORDER BY id ASC
                    """, (contrato['id'],))
        lista_otrosi = cur.fetchall()
        for o in lista_otrosi:
            o['fecha_inicio'] = format_fecha(o['fecha_inicio'])
        contrato['otrosi'] = lista_otrosi
    cur.close()
    return contratos


#------------------------------------------------------
#------------------------- SEDE -----------------------
#------------------------------------------------------
def sede():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM sedes")
    sede = cur.fetchall()
    cur.close()
    return sede

#------------------------------------------------------
#-------------------- ESCOLARIDAD ---------------------
#------------------------------------------------------
def escolaridad():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM nivel_escolaridad")
    nivel_escolaridad = cur.fetchall()
    cur.close()
    return nivel_escolaridad
def guardar_documentos_estudio(empleado_id, rutas):
    if not rutas:
        return
    cur = mysql.connection.cursor()
    for ruta in rutas:
        cur.execute("""
                    INSERT INTO empleados_documentos (empleado_id, tipo, ruta)
                    VALUES (%s, %s, %s)
                    """, (empleado_id, 'estudio', ruta))
    mysql.connection.commit()
    cur.close()
def lista_documentos_estudio_empleado(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT ruta FROM empleados_documentos WHERE empleado_id = %s", (id,))
    documentos = cur.fetchall()
    cur.close()
    return documentos
def guardar_documento_estudio(empleado_id, ruta_documento):
    cur = mysql.connection.cursor()
    cur.execute("""
                INSERT INTO empleados_documentos (empleado_id, tipo, ruta)
                VALUES (%s, %s, %s)
                """, (empleado_id, 'estudio', ruta_documento))
    mysql.connection.commit()
    cur.close()

#------------------------------------------------------
#------------------------ BANCOS ----------------------
#------------------------------------------------------
def bancos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM banco")
    banco = cur.fetchall()
    cur.close()
    return banco

#------------------------------------------------------
#--------------------- GRUPO NOMINA -------------------
#------------------------------------------------------
def grupo_nomina():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM grupo_nomina")
    nomina = cur.fetchall()
    cur.close()
    return nomina
def crear_grupoNomina(data):
    cur = mysql.connection.cursor()

    sql = """
        INSERT INTO grupo_nomina (nombre)
        VALUES (%s)
    """
    cur.execute(sql, (data['nombre'],))
    mysql.connection.commit()

    grupo_nomina_id = cur.lastrowid

    cur.execute(
        "SELECT id, nombre FROM grupo_nomina WHERE id = %s",
        (grupo_nomina_id,)
    )
    row = cur.fetchone()
    cur.close()

    return type('GrupoNomina', (), {
        'id': row[0],
        'nombre': row[1]
    })
def editar_grupoNomina(grupo_id, nombre):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE grupo_nomina SET nombre = %s WHERE id = %s", (nombre, grupo_id))
    mysql.connection.commit()
    cur.close()   
def eliminar_grupoNomina(grupo_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM grupo_nomina WHERE id = %s", (grupo_id,))
    mysql.connection.commit()    
    cur.close()
    
#------------------------------------------------------
#----------------------- CARGOS -----------------------
#------------------------------------------------------
def cargos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM cargos")
    cargo = cur.fetchall()
    cur.close()
    return cargo
def crear_cargo(data):
    cur = mysql.connection.cursor()

    sql = """
        INSERT INTO cargos (nombre)
        VALUES (%s)
    """
    cur.execute(sql, (data['nombre'],))
    mysql.connection.commit()

    cargo_id = cur.lastrowid

    cur.execute(
        "SELECT id, nombre FROM cargos WHERE id = %s",
        (cargo_id,)
    )
    row = cur.fetchone()
    cur.close()

    return type('Cargo', (), {
        'id': row[0],
        'nombre': row[1]
    })
def editar_cargo(cargo_id, nombre):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE cargos SET nombre = %s WHERE id = %s", (nombre, cargo_id))
    mysql.connection.commit()
    cur.close()  
def eliminar_cargo(cargo_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cargos WHERE id = %s", (cargo_id,))
    mysql.connection.commit()    
    cur.close()

#------------------------------------------------------
#-------------------- CIUDADES ------------------------
#------------------------------------------------------
def ciudades():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM ciudades")
    ciudad = cur.fetchall()
    cur.close()
    return ciudad

#------------------------------------------------------
#------------------ CREA EMPLEADO ---------------------
#------------------------------------------------------
def crear_empleado(data, ruta_cedula, ruta_foto):
    cur = mysql.connection.cursor()
    activo = 1
    password_hash = hash_password(data['identificacion'])
    sql = """
        INSERT INTO users_rrhh (
            identificacion,
            nombres,
            apellidos,
            cedula_expedida_en,
            sexo,
            fecha_nacimiento,
            lugar_nacimiento,
            edad,
            estado_civil_id,
            grupo_sanguineo_id,
            numero_hijos,
            direccion,
            barrio,
            localidad,
            estrato,
            telefono_fijo,
            celular,
            correo,
            contacto_emergencia,
            telefono_emergencia,
            parentesco,
            eps_id,
            afp_id,
            cesantias_id,
            ccf_id,
            arl_id,
            tipo_contrato_id,
            cargo_id,
            jornada,
            sede,
            antiguedad,
            nivel_escolaridad_id,
            programa_academico,
            estudia_actualmente,
            nombre_programa_actual,
            numero_cuenta,
            banco,
            password,
            activo,
            grupo_nomina_id,
            cedula_path,
            foto_path
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
    """
    valores = (
        data['identificacion'],
        data['nombres'],
        data['apellidos'],
        data['cedula_expedida_en'],
        data['sexo'],
        data['fecha_nacimiento'],
        data['lugar_nacimiento'],
        data['edad'],
        data['estado_civil_id'],
        data['grupo_sanguineo_id'],
        data['numero_hijos'],
        data['direccion'],
        data['barrio'],
        data['localidad'],
        data['estrato'],
        data['telefono_fijo'],
        data['celular'],
        data['correo'],
        data['contacto_emergencia'],
        data['telefono_emergencia'],
        data['parentesco'],
        data['eps_id'],
        data['afp_id'],
        data['cesantias_id'],
        data['ccf_id'],
        data['arl_id'],
        data['tipo_contrato_id'],
        data['cargo_id'],
        data['jornada'],
        data['sede'],
        data['antiguedad'],
        data['nivel_escolaridad_id'],
        data['programa_academico'],
        data['estudia_actualmente'],
        data['nombre_programa_actual'],
        data['numero_cuenta'],
        data['banco'],
        password_hash, #password
        activo,
        data['grupo_nomina_id'],
        ruta_cedula,
        ruta_foto
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    empleado_id = cur.lastrowid
    
    #GENERA CONSECUTIVO
    tipo_id = data['tipo_contrato_id']
    consecutivo_final = genera_consecutivo(tipo_id)
       
        #guarda en la tabla de contratos    
    fehca_ingreso = data['fecha_ingreso_antigua']
    salario_basico = data['salario_basico']
    factor_no_salarial = data['factor_no_salarial']
    guardar_fecha_contrato(empleado_id, fehca_ingreso, salario_basico, factor_no_salarial, consecutivo_final)
    cur.close()
    return empleado_id
    
#------------------------------------------------------
#------------- ACTUALIZA EMPLEADO ---------------------
#------------------------------------------------------
def actualizar_empleado(id, data):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
            UPDATE users_rrhh SET
                identificacion=%s,
                nombres=%s,
                apellidos=%s,
                cedula_expedida_en=%s,
                sexo=%s,
                fecha_nacimiento=%s,
                lugar_nacimiento=%s,
                edad=%s,
                estado_civil_id=%s,
                grupo_sanguineo_id=%s,
                numero_hijos=%s,
                direccion=%s,
                barrio=%s,
                localidad=%s,
                estrato=%s,
                telefono_fijo=%s,
                celular=%s,
                correo=%s,
                contacto_emergencia=%s,
                telefono_emergencia=%s,
                parentesco=%s,
                eps_id=%s,
                afp_id=%s,
                cesantias_id=%s,
                ccf_id=%s,
                arl_id=%s,
                tipo_contrato_id=%s,
                cargo_id=%s,
                jornada=%s,
                sede=%s,
                antiguedad=%s,
                numero_cuenta=%s,
                banco=%s,
                grupo_nomina_id=%s,
                nivel_escolaridad_id=%s,
                programa_academico=%s,
                estudia_actualmente=%s,
                nombre_programa_actual=%s
            WHERE id = %s                
        """
    cur.execute(sql, (
        data["identificacion"],
        data["nombres"],
        data["apellidos"],
        data["cedula_expedida_en"],
        data["sexo"],
        data["fecha_nacimiento"],
        data["lugar_nacimiento"],
        data["edad"],
        data["estado_civil_id"],
        data["grupo_sanguineo_id"],
        data["numero_hijos"],
        data["direccion"],
        data["barrio"],
        data["localidad"],
        data["estrato"],
        data["telefono_fijo"],
        data["celular"],
        data["correo"],
        data["contacto_emergencia"],
        data["telefono_emergencia"],
        data["parentesco"],
        data["eps_id"],
        data["afp_id"],
        data["cesantias_id"],
        data["ccf_id"],
        data["arl_id"],
        data["tipo_contrato_id"],
        data["cargo_id"],
        data["jornada"],
        data["sede"],
        data["antiguedad"],
        data["numero_cuenta"],
        data["banco"],
        data["grupo_nomina_id"],
        data["nivel_escolaridad_id"],
        data["programa_academico"],
        data["estudia_actualmente"],
        data["nombre_programa_actual"],
        id
    ))
    
    #actualizacion salario
    salario_basico = limpiar_decumal(data['salario_basico'])
    factor_no_salarial = limpiar_decumal(data['factor_no_salarial'])
    cur.execute("""
                UPDATE contratos SET
                    salario_basico = %s,
                    factor_no_salarial = %s
                WHERE empleado_id = %s AND fecha_finalizacion IS NULL
                """, (salario_basico, factor_no_salarial, id))
    mysql.connection.commit()
    cur.close()
    

#------------------------------------------------------
#------------------ UTILIDADES ------------------------
#------------------------------------------------------ 
def limpiar_decumal(valor):
    if valor is None or valor == '':
        return 0
    
    return float(valor.replace(".", "").replace(",", "."))
def empleado_existe(identificacion):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users_rrhh WHERE identificacion = %s", (identificacion,))
    existe = cur.fetchone()
    cur.close()
    return existe is not None
def empleado_lista_completo_por_identificacion(identificacion):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id FROM users_rrhh WHERE identificacion = %s", (identificacion,))
    empleado = cur.fetchone()
    cur.close()
    return empleado # Devuelve el dict {'id': 123} o
def format_fecha(fecha):
    if fecha:
        try:
            return fecha.strftime("%Y-%m-%d")
        except AttributeError:
            try:
                return datetime.strptime(str(fecha).split(' ')[0], "%Y-%m-%d").strftime("%Y-%m-%d")
            except:
                return str(fecha)
    return ""
    
    
#------------------------------------------------------
#--------------- ACCIONES MASIVAS ---------------------
#------------------------------------------------------
def importar_empleados_plantilla(data):
    try:
        cur = mysql.connection.cursor()
        sql_user = """
            INSERT INTO users_rrhh (
                identificacion, nombres, apellidos, cedula_expedida_en, sexo, 
                fecha_nacimiento, lugar_nacimiento, edad, estado_civil_id, 
                grupo_sanguineo_id, numero_hijos, direccion, barrio, localidad, 
                estrato, telefono_fijo, celular, correo, contacto_emergencia, 
                telefono_emergencia, parentesco, eps_id, afp_id, cesantias_id, 
                ccf_id, arl_id, tipo_contrato_id, cargo_id, jornada, sede, 
                antiguedad, nivel_escolaridad_id, programa_academico, 
                estudia_actualmente, nombre_programa_actual, numero_cuenta, 
                banco, password, activo, grupo_nomina_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, 1, %s
            )
        """
        cur.execute(sql_user, (
            data['identificacion'], data['nombres'], data['apellidos'], data['cedula_expedida_en'],
            data['sexo'], data['fecha_nacimiento'], data['lugar_nacimiento'], data['edad'],
            data['estado_civil_id'], data['grupo_sanguineo_id'], data['numero_hijos'],
            data['direccion'], data['barrio_id'], data['localidad'], data['estrato'],
            data['telefono_fijo'], data['celular'], data['correo'], data['contacto_emergencia'],
            data['telefono_emergencia'], data['parentesco'], data['eps_id'], data['afp_id'],
            data['cesantias_id'], data['ccf_id'], data['arl_id'], data['tipo_contrato_id'],
            data['cargo_id'], data['jornada'], data['sede_id'], data['antiguedad'],
            data['nivel_escolaridad_id'], data['programa_academico'], data['estudia_actualmente'],
            data['nombre_programa_actual'], data['numero_cuenta'], data['banco_id'],
            data['password'], data['grupo_nomina_id']
        ))
        empleado_id = cur.lastrowid
        
        consecutivo_final = genera_consecutivo(data['tipo_contrato_id'])
        
        sql_contrato = """
            INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(sql_contrato, (empleado_id, data['fecha_ingreso'], data['salario_basico'], data['factor_no_salarial'], consecutivo_final))
        
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al importar empleados desde plantilla: {e}")
        raise e    
def actualizar_empleados_plantilla(data):
    try:
        cur = mysql.connection.cursor()
        sql_user = """
            UPDATE users_rrhh SET
                sexo=%s, edad=%s, estado_civil_id=%s, 
                numero_hijos=%s, direccion=%s, barrio=%s, 
                localidad=%s, estrato=%s, telefono_fijo=%s, celular=%s, correo=%s, 
                contacto_emergencia=%s, telefono_emergencia=%s, parentesco=%s, 
                eps_id=%s, afp_id=%s, cesantias_id=%s, ccf_id=%s, arl_id=%s, 
                tipo_contrato_id=%s, cargo_id=%s, jornada=%s, sede=%s, 
                nivel_escolaridad_id=%s, programa_academico=%s, 
                estudia_actualmente=%s, nombre_programa_actual=%s, 
                numero_cuenta=%s, banco=%s, grupo_nomina_id=%s
            WHERE identificacion = %s
        """
        valores = (
            data['sexo'],data['edad'], data['estado_civil_id'],
            data['numero_hijos'], data['direccion'], data['barrio_id'],
            data['localidad'], data['estrato'], data['telefono_fijo'], data['celular'], data['correo'],
            data['contacto_emergencia'], data['telefono_emergencia'], data['parentesco'],
            data['eps_id'], data['afp_id'], data['cesantias_id'], data['ccf_id'], data['arl_id'],
            data['tipo_contrato_id'], data['cargo_id'], data['jornada'], data['sede_id'],
            data['nivel_escolaridad_id'], data['programa_academico'], data['estudia_actualmente'],
            data['nombre_programa_actual'], data['numero_cuenta'], data['banco_id'],
            data['grupo_nomina_id'], data['identificacion'] # El WHERE
        )
        cur.execute(sql_user, valores)
        
        sql_contrato = """
            UPDATE contratos 
            SET salario_basico = %s, factor_no_salarial = %s, fecha_ingreso = %s
            WHERE empleado_id = (SELECT id FROM users_rrhh WHERE identificacion = %s)
            ORDER BY id DESC LIMIT 1
        """
        cur.execute(sql_contrato, (
            data['salario_basico'], 
            data['factor_no_salarial'], 
            data['fecha_ingreso'],
            data['identificacion']
        ))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al actualizar empleados desde plantilla: {e}")
        raise e   

#------------------------------------------------------
#------------------ FOTO Y CEDULA ---------------------
#------------------------------------------------------
def actualiza_foto(empleado_id, ruta_foto):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users_rrhh SET foto_path = %s WHERE id = %s", (ruta_foto, empleado_id))
    mysql.connection.commit()
    cur.close()  
def actualiza_cedula(empleado_id, ruta_cedula):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users_rrhh SET cedula_path = %s WHERE id = %s", (ruta_cedula, empleado_id))
    mysql.connection.commit()
    cur.close()

#------------------------------------------------------
#------------------- CERTIFICADOS ---------------------
#------------------------------------------------------
def obtener_datos_certificado(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT 
            u.nombres, u.apellidos, u.identificacion,
            tp.nombre AS tipo_contrato, cg.nombre AS cargo,
            c.fecha_ingreso, c.salario_basico, c.factor_no_salarial, gn.nombre AS grupo_nomina
        FROM users_rrhh u
            LEFT JOIN tipo_contrato tp ON u.tipo_contrato_id = tp.id
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
            LEFT JOIN contratos c ON u.id = c.empleado_id
            LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id
        WHERE u.id = %s
        ORDER BY c.id DESC LIMIT 1
    """
    cur.execute(sql, (id,))
    datos = cur.fetchone()
    cur.close()
    return datos

#------------------------------------------------------
#---------------------- OTRO SI -----------------------
#------------------------------------------------------
def procesar_otrosi_db(id_empleado, data):
    cur = mysql.connection.cursor()
    accion = data.get('accion')
    contrato_consecutivo = data.get('codigoContrato')
    
    #busca el id del contrato actual
    cur.execute("SELECT id FROM contratos WHERE n_consecutivo = %s", (contrato_consecutivo,))
    res = cur.fetchone()
    if not res:
        cur.close()
        raise Exception("No se encontro el contrato original")
    id_contrato = res[0]
    
    tipo_texto = ""
    fecha_fin_otrosi = data.get('fecha_fin') if data.get('fecha_fin') != "" else None
    
    #logica segun tipo de accion
    if accion == 'cambio_cargo':
        cur.execute("UPDATE users_rrhh SET cargo_id = %s WHERE id = %s", (data['cargo_id'], id_empleado))
        cur.execute("UPDATE contratos SET salario_basico = %s, factor_no_salarial = %s WHERE id = %s",
                    (limpiar_decumal(data['salario']), limpiar_decumal(data['factor_salarial']), id_contrato))
        tipo_texto = "Cambio de Cargo"
        
    elif accion == 'cambio_salario':
        cur.execute("UPDATE contratos SET salario_basico = %s, factor_no_salarial = %s WHERE id = %s",
                    (limpiar_decumal(data['salario']), limpiar_decumal(data['factor_salarial']), id_contrato))
        tipo_texto = "Cambio de Salario"
        
    elif accion == 'prorroga':
        tipo_texto = "Prorroga de Contrato"
        
    sql_otrosi = """
                    INSERT INTO otrosi_contratos
                    (id_contrato, tipo_otrosi, fecha_inicio, fecha_fin, descripcion)
                    VALUES
                    (%s, %s, %s, %s, %s)
                """
    cur.execute(sql_otrosi, (
        id_contrato,
        tipo_texto,
        data['fecha_inicio'],
        fecha_fin_otrosi,
        data['descripcion']
    ))
    mysql.connection.commit()
    cur.close()