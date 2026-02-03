from extension import mysql
from utils.password_utils import hash_password
import MySQLdb.cursors

def total_empleados():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users_rrhh")
    empleados = cur.fetchone()[0]
    cur.close()
    return empleados

def empleados_lista():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #cur.execute("SELECT * FROM users_rrhh")
    sql = """
        SELECT u.id, u.identificacion, u.nombres, u.apellidos, u.cedula_expedida_en, u.sexo, u.fecha_nacimiento,
        u.lugar_nacimiento, u.edad, ec.nombre AS estado_civil, gs.tipo AS grupo_sanguineo, u.numero_hijos, u.direccion, u.barrio, u.localidad,
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
    cur.close()
    return empleados

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
        SELECT salario_basico, factor_no_salarial
        FROM contratos
        WHERE empleado_id = %s
        ORDER BY id DESC
        LIMIT 1
    """
    cur.execute(salarios, (id,))
    salario = cur.fetchone()
    if salario:
        empleado['salario_basico'] = salario['salario_basico']
        empleado['factor_no_salarial'] = salario['factor_no_salarial']
    else:
        empleado['salario_basico'] = 0
        empleado['factor_no_salarial'] = 0
    cur.close()
    return empleado

def desactivar_empleado(id, fecha_retiro):
    cur = mysql.connection.cursor()
    update_estado = """
                UPDATE users_rrhh SET
                    activo = 2
                WHERE id = %s
                """
    cur.execute(update_estado, (id,))
    update_contrato = """
                UPDATE contratos SET
                    fecha_finalizacion = %s
                WHERE empleado_id = %s AND fecha_finalizacion IS NULL
                """
    cur.execute(update_contrato, (fecha_retiro, id))
    mysql.connection.commit()
    cur.close()

def activar_empleado(id, fecha_reingreso):
    cur = mysql.connection.cursor()
    update_estado = """
                UPDATE users_rrhh SET
                    activo = 1
                WHERE id = %s
                """
    cur.execute(update_estado, (id,))
    create_contrato = """
                INSERT INTO contratos (empleado_id, fecha_ingreso)
                VALUES (%s, %s)
                """
    cur.execute(create_contrato, (id, fecha_reingreso))
    mysql.connection.commit()
    cur.close()

def estado_civil():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM estado_civil")
    estados = cur.fetchall()
    cur.close()
    return estados

def grupo_sanguineo():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM grupo_sanguineo")
    g_sanguineo = cur.fetchall()
    cur.close()
    return g_sanguineo

def eps():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM eps")
    eps = cur.fetchall()
    cur.close()
    return eps

def afp():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM afp")
    afp = cur.fetchall()
    cur.close()
    return afp

def cesantias():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM cesantias")
    cesantias = cur.fetchall()
    cur.close()
    return cesantias

def ccf():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM ccf")
    ccf = cur.fetchall()
    cur.close()
    return ccf

def arl():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM arl")
    arl = cur.fetchall()
    cur.close()
    return arl

def tipo_contrato():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tipo_contrato")
    tipo_contrato = cur.fetchall()
    cur.close()
    return tipo_contrato

def sede():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM sedes")
    sede = cur.fetchall()
    cur.close()
    return sede

def escolaridad():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM nivel_escolaridad")
    nivel_escolaridad = cur.fetchall()
    cur.close()
    return nivel_escolaridad

def bancos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM banco")
    banco = cur.fetchall()
    cur.close()
    return banco

def grupo_nomina():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM grupo_nomina")
    nomina = cur.fetchall()
    cur.close()
    return nomina

def cargos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM cargos")
    cargo = cur.fetchall()
    cur.close()
    return cargo

def ciudades():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM ciudades")
    ciudad = cur.fetchall()
    cur.close
    return ciudad


#####EMPLEADOS######
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
    fehca_ingreso = data['fecha_ingreso_antigua']
    salario_basico = data['salario_basico']
    factor_no_salarial = data['factor_no_salarial']
    guardar_fecha_contrato(empleado_id, fehca_ingreso, salario_basico, factor_no_salarial)
    cur.close()
    return empleado_id
    
def guardar_fecha_contrato(empleado_id, fecha_ingreso, salario_basico, factor_no_salarial):
    cur = mysql.connection.cursor()
    salario_basico = limpiar_decumal(salario_basico)
    factor_no_salarial = limpiar_decumal(factor_no_salarial)
    cur.execute("""
                INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial)
                VALUES (%s, %s, %s, %s)
                """, (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial))
    mysql.connection.commit()
    cur.close()
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
                salario_basico=%s,
                factor_no_salarial=%s,
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
        data["salario_basico"],
        data["factor_no_salarial"],
        data["numero_cuenta"],
        data["banco"],
        data["grupo_nomina_id"],
        data["nivel_escolaridad_id"],
        data["programa_academico"],
        data["estudia_actualmente"],
        data["nombre_programa_actual"],
        id
    ))
    mysql.connection.commit()
    cur.close()
    
    
####ver contratos empleado####
def contratos_empleado(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
                SELECT c.id, c.empleado_id, c.fecha_ingreso, c.fecha_finalizacion, tc.nombre AS tipo_contrato
                FROM contratos c
                LEFT JOIN users_rrhh u ON c.empleado_id = u.id
                LEFT JOIN tipo_contrato tc ON u.tipo_contrato_id = tc.id
                WHERE empleado_id = %s
                """, (id,))
    contratos = cur.fetchall()
    cur.close()
    return contratos

    #####GRUPO DE NOMINA###
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
    

#########CARGOS#######
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
    
def limpiar_decumal(valor):
    if valor is None or valor == '':
        return 0
    
    return float(valor.replace(".", "").replace(",", "."))