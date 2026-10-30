from extension import mysql
from utils.password_utils import hash_password
from utils.cache import cache_result
from utils.email_utils import enviar_correo
import MySQLdb.cursors
import re
import os
import time
from datetime import datetime


#------------------------------------------------------
#--- BUZÓN: crear tabla si no existe (auto-creación) ---
#------------------------------------------------------
def asegurar_tabla_buzon():
    """Crea la tabla buzon_mensajes si no existe.
    Se ejecuta al enviar el primer mensaje."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SHOW TABLES LIKE 'buzon_mensajes'")
        if not cur.fetchone():
            cur.execute("""
                CREATE TABLE buzon_mensajes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    empleado_id INT NOT NULL,
                    asunto VARCHAR(200) NOT NULL,
                    mensaje_html TEXT,
                    leido TINYINT(1) DEFAULT 0,
                    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
                    enviado_por_id INT DEFAULT NULL,
                    enviado_por_nombre VARCHAR(200) DEFAULT NULL,
                    INDEX idx_empleado (empleado_id),
                    INDEX idx_leido (empleado_id, leido),
                    FOREIGN KEY (empleado_id) REFERENCES users_rrhh(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            mysql.connection.commit()
        cur.close()
    except Exception:
        pass  # Si falla, el administrador crea la tabla manualmente


#------------------------------------------------------
#----- BUZÓN: guardar mensajes en la BD ---------------
#------------------------------------------------------
def guardar_mensajes_buzon(destinatarios_ids, asunto, mensaje_html, enviado_por_id=None, enviado_por_nombre=None):
    """Guarda un mensaje en el buzón de cada destinatario."""
    if not destinatarios_ids:
        return
    asegurar_tabla_buzon()
    cur = mysql.connection.cursor()
    try:
        for emp_id in destinatarios_ids:
            cur.execute(
                """INSERT INTO buzon_mensajes (empleado_id, asunto, mensaje_html, enviado_por_id, enviado_por_nombre)
                   VALUES (%s, %s, %s, %s, %s)""",
                (emp_id, asunto, mensaje_html, enviado_por_id, enviado_por_nombre)
            )
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al guardar en buzón: {e}")
    finally:
        cur.close()


#------------------------------------------------------
#----- BUZÓN: obtener mensajes de un empleado ---------
#------------------------------------------------------
def obtener_mensajes_buzon(empleado_id, solo_no_leidos=False):
    """Retorna los mensajes del buzón para un empleado."""
    asegurar_tabla_buzon()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        if solo_no_leidos:
            cur.execute(
                """SELECT id, asunto, mensaje_html, leido, fecha_envio, enviado_por_nombre
                   FROM buzon_mensajes
                   WHERE empleado_id = %s AND leido = 0
                   ORDER BY fecha_envio DESC""",
                (empleado_id,)
            )
        else:
            cur.execute(
                """SELECT id, asunto, mensaje_html, leido, fecha_envio, enviado_por_nombre
                   FROM buzon_mensajes
                   WHERE empleado_id = %s
                   ORDER BY fecha_envio DESC""",
                (empleado_id,)
            )
        mensajes = cur.fetchall()
        for m in mensajes:
            if m.get('fecha_envio'):
                m['fecha_envio'] = m['fecha_envio'].strftime('%Y-%m-%d %H:%M') if hasattr(m['fecha_envio'], 'strftime') else str(m['fecha_envio'])
        return mensajes
    except Exception:
        return []
    finally:
        cur.close()


#------------------------------------------------------
#----- BUZÓN: obtener mensajes ENVIADOS por un usuario ---
#------------------------------------------------------
def obtener_mensajes_enviados_buzon(empleado_id):
    """Retorna los mensajes enviados por un usuario (buzón de salida).

    Busca en buzon_mensajes los registros donde enviado_por_id coincide
    con el id del usuario y une con users_rrhh para mostrar el nombre
    de cada destinatario.
    """
    asegurar_tabla_buzon()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute(
            """SELECT b.id, b.asunto, b.mensaje_html, b.fecha_envio, b.enviado_por_nombre,
                       u.nombres AS dest_nombres, u.apellidos AS dest_apellidos
               FROM buzon_mensajes b
               LEFT JOIN users_rrhh u ON b.empleado_id = u.id
               WHERE b.enviado_por_id = %s
               ORDER BY b.fecha_envio DESC""",
            (empleado_id,)
        )
        mensajes = cur.fetchall()
        for m in mensajes:
            if m.get('fecha_envio'):
                m['fecha_envio'] = m['fecha_envio'].strftime('%Y-%m-%d %H:%M') if hasattr(m['fecha_envio'], 'strftime') else str(m['fecha_envio'])
            dest = ' '.join(filter(None, [m.get('dest_nombres'), m.get('dest_apellidos')]))
            m['destinatario_nombre'] = dest or 'Empleado'
        return mensajes
    except Exception:
        return []
    finally:
        cur.close()


#------------------------------------------------------
#----- BUZÓN: marcar mensaje como leído ---------------
#------------------------------------------------------
def marcar_mensaje_leido(mensaje_id, empleado_id):
    """Marca un mensaje como leído."""
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "UPDATE buzon_mensajes SET leido = 1 WHERE id = %s AND empleado_id = %s",
            (mensaje_id, empleado_id)
        )
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()
    finally:
        cur.close()


#------------------------------------------------------
#----- BUZÓN: contar no leídos ------------------------
#------------------------------------------------------
def contar_mensajes_no_leidos(empleado_id):
    """Retorna la cantidad de mensajes no leídos."""
    asegurar_tabla_buzon()
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "SELECT COUNT(*) FROM buzon_mensajes WHERE empleado_id = %s AND leido = 0",
            (empleado_id,)
        )
        return cur.fetchone()[0]
    except Exception:
        return 0
    finally:
        cur.close()


#------------------------------------------------------
#------------ MENSAJERÍA: filtrar destinatarios --------
#------------------------------------------------------
def empleados_para_mensajeria(cargo_id=None, sede_id=None, busqueda=None):
    """Retorna empleados activos con correo, filtrados opcionalmente
    por cargo, sede y/o búsqueda por nombre/identificación."""
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    where = ["u.activo = 1", "u.correo IS NOT NULL", "u.correo != ''"]
    params = []
    if cargo_id:
        where.append("u.cargo_id = %s")
        params.append(cargo_id)
    if sede_id:
        where.append("u.sede = %s")
        params.append(sede_id)
    if busqueda:
        where.append("(u.identificacion LIKE %s OR u.nombres LIKE %s OR u.apellidos LIKE %s OR CONCAT(u.nombres, ' ', u.apellidos) LIKE %s)")
        like = f"%{busqueda}%"
        params.extend([like, like, like, like])
    sql = f"""
        SELECT u.id, u.identificacion, u.nombres, u.apellidos, u.correo,
               cg.nombre AS cargo, sd.nombre AS sede
        FROM users_rrhh u
        LEFT JOIN cargos cg ON u.cargo_id = cg.id
        LEFT JOIN sedes sd ON u.sede = sd.id
        WHERE {' AND '.join(where)}
        ORDER BY u.apellidos, u.nombres
    """
    cur.execute(sql, tuple(params))
    empleados = cur.fetchall()
    cur.close()
    return empleados


def enviar_mensaje_masivo(asunto, mensaje_html, destinatarios_ids, enviado_por_id=None, enviado_por_nombre=None):
    """Envía un correo a los empleados cuyos IDs están en destinatarios_ids.
    Retorna (enviados: int, total: int, errores: list).
    """
    if not destinatarios_ids:
        return 0, 0, ["No hay destinatarios seleccionados"]

    # Obtener correos de los empleados seleccionados
    placeholders = ', '.join(['%s'] * len(destinatarios_ids))
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(
        f"SELECT correo FROM users_rrhh WHERE id IN ({placeholders}) AND correo IS NOT NULL AND correo != ''",
        tuple(destinatarios_ids)
    )
    correos = [row['correo'] for row in cur.fetchall()]
    cur.close()

    if not correos:
        return 0, len(destinatarios_ids), ["Ningún destinatario tiene correo electrónico registrado"]

    # Envolver el mensaje en plantilla HTML profesional con logo
    base_url = os.getenv('BASE_URL', '').rstrip('/')
    logo_url = f"{base_url}/static/imgs/logo.png" if base_url else ""
    logo_img = f'<img src="{logo_url}" alt="Digicom" style="max-height:50px;margin-bottom:6px;">' if logo_url else ''
    plantilla_html = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{asunto}</title>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8;padding:30px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.10);">
          <tr>
            <td style="background-color:#1e3a8a;background:linear-gradient(135deg,#1e3a8a,#2563eb);padding:28px 36px 24px;text-align:center;">
              {logo_img}
              <h1 style="margin:0;color:#ffffff;font-size:20px;font-weight:700;">
                {asunto}
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 36px 28px;color:#1e293b;font-size:15px;line-height:1.7;">
              {mensaje_html}
            </td>
          </tr>
          <tr>
            <td style="background-color:#f8fafc;padding:22px 36px;text-align:center;border-top:1px solid #e2e8f0;">
              <img src="{logo_url}" alt="Digicom" style="max-height:28px;margin-bottom:6px;" onerror="this.style.display='none'">
              <p style="margin:0 0 4px;color:#64748b;font-size:12px;">
                <strong>Sistema de Gestión Integral (SGI)</strong><br>
                Digicom Colombia
              </p>
              <p style="margin:0;color:#94a3b8;font-size:11px;">
                Este es un mensaje automático, por favor no responder.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    # Enviar UN correo individual por destinatario para proteger la privacidad:
    # así cada empleado solo ve su propio correo en el campo Para, sin exponer
    # las direcciones de los demás destinatarios.
    total = len(correos)
    enviados = 0
    errores = []
    for i, correo in enumerate(correos):
        try:
            enviado_ok = enviar_correo([correo], asunto, plantilla_html)
        except Exception as e:
            print(f"Error inesperado enviando a {correo}: {e}")
            enviado_ok = False
        if enviado_ok:
            enviados += 1
        else:
            errores.append(f"No se pudo enviar a {correo}")
        # Pequeña pausa entre envíos para no saturar el servidor SMTP
        if i < total - 1:
            time.sleep(0.3)

    # Guardar en buzón (persistir en BD para que el empleado lo vea)
    try:
        guardar_mensajes_buzon(
            destinatarios_ids,
            asunto,
            plantilla_html,
            enviado_por_id=enviado_por_id,
            enviado_por_nombre=enviado_por_nombre or 'Sistema de Mensajería'
        )
    except Exception as e:
        print(f"Error al guardar en buzón (no crítico): {e}")

    if enviados:
        return enviados, total, errores
    else:
        return 0, total, errores or ["Error al enviar los correos. Verifica la configuración SMTP."]


#------------------------------------------------------
#-------------- TOTAL DE EMPLEADOS CONTEO -------------
#------------------------------------------------------
# NOTA: estos conteos NO se cachean porque deben reflejar
# al instante los cambios de retiro/activación/creación.
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
        u.lugar_nacimiento, u.edad, ec.nombre AS estado_civil, gs.tipo AS grupo_sanguineo, u.numero_hijos, u.direccion, ci.nombre AS barrio, u.barrio2, u.barrio AS barrio_id, u.localidad,
        u.estrato, u.telefono_fijo, u.celular, u.correo, u.contacto_emergencia, u.telefono_emergencia,
        u.parentesco, eps.nombre AS eps, afp.nombre AS afp, ces.nombre AS cesantias, ccf.nombre AS ccf, arl.nombre AS arl,
        tp.nombre AS tipo_contrato, cg.nombre AS cargos, u.jornada,
        sd.nombre AS sedes, 
        u.antiguedad, ne.nombre AS nivel_escolaridad, u.estudia_actualmente, u.nombre_programa_actual, u.programa_academico,
        u.numero_cuenta, b.nombre AS bancos, gn.nombre AS grupo_nomina,
        u.sgi_rol_id, rsgi.rol AS sgi_rol,
        cedula_path, foto_path, u.activo,
        td.nombre AS tipo_doc_nombre, u.tipo_identificacion
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
        LEFT JOIN rol rsgi ON u.sgi_rol_id = rsgi.id
        LEFT JOIN tipo_doc td ON u.tipo_identificacion = td.id
        ORDER BY u.apellidos, u.nombres
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
        # Normalizar rutas de Windows a forward slashes para compatibilidad web
        if empleado.get('cedula_path'):
            empleado['cedula_path'] = empleado['cedula_path'].replace('\\', '/')
        if empleado.get('foto_path'):
            empleado['foto_path'] = empleado['foto_path'].replace('\\', '/')
        
    salarios_sql = """
        SELECT empleado_id, salario_basico, factor_no_salarial, fecha_ingreso, fecha_finalizacion, motivo
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
            empleado['motivo'] = salario_info['motivo']
        else:
            empleado['fecha_ingreso'] = None
            empleado['fecha_finalizacion'] = None
            empleado['salario_basico'] = 0
            empleado['factor_no_salarial'] = 0
            empleado['motivo'] = None
        # Formato moneda ($2.000.000) para mostrar en el detalle
        empleado['salario_basico_moneda'] = formatear_moneda(empleado.get('salario_basico'))
        empleado['factor_no_salarial_moneda'] = formatear_moneda(empleado.get('factor_no_salarial'))
        # Texto legible de antigüedad (años y meses) para mostrar en el detalle.
        # Para empleados retirados (activo == 2) se calcula hasta la fecha de
        # finalización del contrato, no hasta hoy.
        fecha_final = empleado.get('fecha_finalizacion') if empleado.get('activo') == 2 else None
        empleado['antiguedad_texto'] = formatear_antiguedad(empleado.get('fecha_ingreso'), fecha_final)
    cur.close()
    return empleados

#------------------------------------------------------
#-------------- LISTA RESUMIDA DE EMPLEADOS -----------
#------------ (solo id, nombres, activo) --------------
#------------------------------------------------------
@cache_result(ttl_seconds=30)
def empleados_lista_resumida():
    """
    Versión ligera de empleados_lista(). Solo trae id, identificacion,
    nombres y apellidos para llenar dropdowns. Evita el JOIN masivo
    con 15 tablas que hace empleados_lista().
    """
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT id, identificacion, nombres, apellidos, activo
        FROM users_rrhh
        ORDER BY apellidos, nombres
    """)
    empleados = cur.fetchall()
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
            u.barrio2,
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
            u.sgi_rol_id,
            rsgi.rol AS sgi_rol,
            cedula_path,
            foto_path,
            u.activo,
            
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
            u.nivel_escolaridad_id,
            u.tipo_identificacion,
            td.nombre AS tipo_doc_nombre
            
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
            LEFT JOIN rol rsgi ON u.sgi_rol_id = rsgi.id
            LEFT JOIN tipo_doc td ON u.tipo_identificacion = td.id
        WHERE u.id = %s ORDER BY u.apellidos, u.nombres DESC
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
        SELECT salario_basico, factor_no_salarial, fecha_ingreso, fecha_finalizacion, motivo, n_consecutivo
        FROM contratos
        WHERE empleado_id = %s
        ORDER BY id DESC
        LIMIT 1
    """
    cur.execute(salarios, (id,))
    salario = cur.fetchone()
    if salario:
        empleado['fecha_ingreso'] = salario['fecha_ingreso']
        empleado['fecha_finalizacion'] = salario['fecha_finalizacion']
        empleado['salario_basico'] = salario['salario_basico']
        empleado['factor_no_salarial'] = salario['factor_no_salarial']
        empleado['motivo'] = salario['motivo']
        empleado['n_consecutivo'] = salario['n_consecutivo']
    else:
        empleado['fecha_ingreso'] = None
        empleado['fecha_finalizacion'] = None
        empleado['salario_basico'] = 0
        empleado['factor_no_salarial'] = 0

    # Formato moneda ($2.000.000) para mostrar en el detalle y en el JSON de edición
    empleado['salario_basico_moneda'] = formatear_moneda(empleado.get('salario_basico'))
    empleado['factor_no_salarial_moneda'] = formatear_moneda(empleado.get('factor_no_salarial'))

    # Solo contar los Otrosí del ÚLTIMO contrato (el de mayor id), no de todos
    # los contratos históricos (incluidos los ya finalizados).
    otrosi = """SELECT COUNT(*) AS total_otrosi
                FROM otrosi_contratos o
                INNER JOIN contratos c ON o.id_contrato = c.id
                WHERE c.empleado_id = %s
                  AND c.id = (SELECT MAX(c2.id) FROM contratos c2 WHERE c2.empleado_id = %s)
            """
    cur.execute(otrosi, (id, id))
    resul = cur.fetchone()
    
    if resul:
        empleado['cuenta_otrosi'] = resul['total_otrosi']
    if empleado:
        empleado["fecha_nacimiento"] = format_fecha(empleado.get("fecha_nacimiento"))
        empleado["fecha_ingreso"] = format_fecha(empleado.get("fecha_ingreso"))
        # Texto legible de antigüedad (años y meses) para mostrar en el detalle.
        # Para empleados retirados (activo == 2) se calcula hasta la fecha de
        # finalización del contrato, no hasta hoy.
        fecha_final = empleado.get('fecha_finalizacion') if empleado.get('activo') == 2 else None
        empleado['antiguedad_texto'] = formatear_antiguedad(empleado.get('fecha_ingreso'), fecha_final)
        # Normalizar rutas de Windows a forward slashes para compatibilidad web
        if empleado.get('cedula_path'):
            empleado['cedula_path'] = empleado['cedula_path'].replace('\\', '/')
        if empleado.get('foto_path'):
            empleado['foto_path'] = empleado['foto_path'].replace('\\', '/')
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

    # Obtener el contrato activo (sin fecha de finalización) antes de cerrarlo,
    # para poder actualizar también el último Otrosí con la fecha de retiro.
    cur.execute(
        "SELECT id FROM contratos WHERE empleado_id = %s AND fecha_finalizacion IS NULL ORDER BY id DESC LIMIT 1",
        (id,))
    res = cur.fetchone()

    update_contrato = """
                UPDATE contratos SET
                    fecha_finalizacion = %s,
                    motivo = %s
                WHERE empleado_id = %s AND fecha_finalizacion IS NULL
                """
    cur.execute(update_contrato, (fecha_retiro, motivo_retiro, id))

    # La fecha de retiro (igual a la fecha fin del contrato) también debe ser
    # la fecha fin del último Otrosí de ese contrato (los Otrosí se ordenan por id).
    if res and fecha_retiro:
        id_contrato = res[0]
        update_otrosi = """
                    UPDATE otrosi_contratos
                    SET fecha_fin = %s
                    WHERE id_contrato = %s
                    ORDER BY id DESC
                    LIMIT 1
                    """
        cur.execute(update_otrosi, (fecha_retiro, id_contrato))

    mysql.connection.commit()
    cur.close()


#------------------------------------------------------
#------------- ELIMINAR EMPLEADO (DEFINITIVO) ---------
#------------------------------------------------------
def eliminar_empleado_db(id):
    """Elimina definitivamente un empleado de la base de datos.

    Borra en cascada todos los registros relacionados:
        - Historial del aula virtual (cursos asignados e intentos de
          evaluación; estos últimos guardan la identificación en estudiante_id)
        - Documentos, mensajes del buzón
        - Contratos y sus Otrosí
        - Evaluaciones de desempeño (como evaluado y como evaluador)
        - El usuario en users_rrhh

    Args:
        id: ID numérico del empleado en users_rrhh.

    Returns:
        tuple: (success: bool, error: str or None)
    """
    cur = mysql.connection.cursor()
    try:
        # El aula virtual guarda la identificación (string) como estudiante_id
        cur.execute("SELECT identificacion FROM users_rrhh WHERE id = %s", (id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            return False, "Empleado no encontrado"
        identificacion = str(row[0] or '')

        # --- Historial aula virtual ---
        cur.execute(
            "DELETE FROM respuestas_estudiante WHERE intento_id IN "
            "(SELECT id FROM intentos_evaluacion WHERE estudiante_id = %s)",
            (identificacion,))
        cur.execute("DELETE FROM intentos_evaluacion WHERE estudiante_id = %s", (identificacion,))
        cur.execute("DELETE FROM curso_empleados WHERE empleado_id = %s", (id,))

        # --- RRHH: documentos y buzón ---
        cur.execute("DELETE FROM empleados_documentos WHERE empleado_id = %s", (id,))
        cur.execute("DELETE FROM buzon_mensajes WHERE empleado_id = %s", (id,))

        # --- Contratos y sus Otrosí ---
        cur.execute(
            "DELETE FROM otrosi_contratos WHERE id_contrato IN "
            "(SELECT id FROM contratos WHERE empleado_id = %s)", (id,))
        cur.execute("DELETE FROM contratos WHERE empleado_id = %s", (id,))

        # --- Evaluaciones de desempeño (como evaluado y como evaluador) ---
        # Cada tabla se intenta eliminar de forma independiente: si alguna
        # no existe en la BD, se ignora sin abortar la eliminación del empleado.
        # IMPORTANTE: NUNCA hacer rollback() aquí, ya que desharía las
        # eliminaciones anteriores (contratos, documentos, etc.).
        _tablas_desempeno = [
            'evaluacion_desempeno_resultado_competencias',
            'evaluacion_desempeno_resultado_tipos',
            'evaluacion_desempeno_resultado',
            'evaluacion_desempeno_resultados',
        ]
        for tabla in _tablas_desempeno:
            try:
                cur.execute(
                    f"DELETE FROM {tabla} WHERE id_asignacion IN "
                    "(SELECT id FROM evaluacion_desempeno_asignaciones WHERE id_evaluado = %s OR id_evaluador = %s)",
                    (id, id))
            except Exception:
                pass  # Tabla puede no existir; se ignora silenciosamente
        # Asignaciones se eliminan al final
        cur.execute(
            "DELETE FROM evaluacion_desempeno_asignaciones WHERE id_evaluado = %s OR id_evaluador = %s",
            (id, id))

        # --- Usuario ---
        cur.execute("DELETE FROM users_rrhh WHERE id = %s", (id,))

        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        print(f"Error al eliminar empleado {id}: {e}")
        return False, str(e)


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
                INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo, tipo_contrato_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
    salario_basico = limpiar_decumal(salario_basico)
    factor_no_salarial = limpiar_decumal(factor_no_salarial)
    n_consecutivo = genera_consecutivo(tipoContrato)
    update_contrato = "UPDATE users_rrhh SET tipo_contrato_id = %s WHERE id = %s"
    cur.execute(update_contrato, (tipoContrato, id))
    cur.execute(create_contrato, (id, fecha_reingreso, salario_basico, factor_no_salarial, n_consecutivo, tipoContrato))
    mysql.connection.commit()
    cur.close()

#------------------------------------------------------
#-------------------- ESTADO CIVIL --------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def estado_civil():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM estado_civil")
    estados = cur.fetchall()
    cur.close()
    return estados

#------------------------------------------------------
#------------------ GRUPO SANGUINEO -------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def grupo_sanguineo():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM grupo_sanguineo")
    g_sanguineo = cur.fetchall()
    cur.close()
    return g_sanguineo

#------------------------------------------------------
#------------------------- EPS ------------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def eps():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM eps")
    eps = cur.fetchall()
    cur.close()
    return eps

#------------------------------------------------------
#------------------------- AFP ------------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def afp():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM afp")
    afp = cur.fetchall()
    cur.close()
    return afp

#------------------------------------------------------
#--------------------- CESANTIAS ----------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def cesantias():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM cesantias")
    cesantias = cur.fetchall()
    cur.close()
    return cesantias

#------------------------------------------------------
#------------------------- CCF ------------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def ccf():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM ccf")
    ccf = cur.fetchall()
    cur.close()
    return ccf

#------------------------------------------------------
#------------------------- ARL ------------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def arl():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM arl")
    arl = cur.fetchall()
    cur.close()
    return arl

#------------------------------------------------------
#---------------------- CONTRATOS ---------------------
#------------------------------------------------------
@cache_result(ttl_seconds=60)
def tipo_contrato():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tipo_contrato ORDER BY nombre ASC")
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
def guardar_fecha_contrato(empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, consecutivo, tipo_contrato_id=None):
    cur = mysql.connection.cursor()
    salario_basico = limpiar_decumal(salario_basico)
    factor_no_salarial = limpiar_decumal(factor_no_salarial)
    cur.execute("""
                INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo, tipo_contrato_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, consecutivo, tipo_contrato_id))
    mysql.connection.commit()
    cur.close()
def contratos_empleado(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
                SELECT 
                    c.id, c.empleado_id, c.fecha_ingreso, 
                    c.fecha_finalizacion, c.salario_basico, 
                    c.factor_no_salarial, tc.nombre AS tipo_contrato,
                    c.tipo_contrato_id,
                    c.motivo, c.n_consecutivo
                FROM contratos c
                LEFT JOIN users_rrhh u ON c.empleado_id = u.id
                LEFT JOIN tipo_contrato tc ON tc.id = COALESCE(c.tipo_contrato_id, u.tipo_contrato_id)
                WHERE empleado_id = %s
                ORDER BY c.id DESC
                """, (id,))
    contratos = cur.fetchall()
    
    #PARA CADA CONTRATO BUSCAMOS SUU OTROSI
    for contrato in contratos:
        cur.execute("""
                    SELECT
                        tipo_otrosi, fecha_inicio, fecha_fin, descripcion
                        FROM otrosi_contratos
                        WHERE id_contrato = %s
                        ORDER BY id ASC
                    """, (contrato['id'],))
        lista_otrosi = cur.fetchall()
        for o in lista_otrosi:
            o['fecha_inicio'] = format_fecha(o['fecha_inicio'])
            o['fecha_fin'] = format_fecha(o['fecha_fin']) if o.get('fecha_fin') else None
        contrato['otrosi'] = lista_otrosi
    cur.close()
    return contratos


#------------------------------------------------------
#------------------------- SEDE -----------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def sede():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM sedes")
    sede = cur.fetchall()
    cur.close()
    return sede

#------------------------------------------------------
#-------------------- ESCOLARIDAD ---------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
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
@cache_result(ttl_seconds=300)
def bancos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM banco")
    banco = cur.fetchall()
    cur.close()
    return banco

#------------------------------------------------------
#--------------------- GRUPO NOMINA -------------------
#------------------------------------------------------
@cache_result(ttl_seconds=60)
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
#-------------------- TIPO DOC ------------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def tipo_doc():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM tipo_doc")
    tipos = cur.fetchall()
    cur.close()
    return tipos

#------------------------------------------------------
#----------------------- CARGOS -----------------------
#------------------------------------------------------
@cache_result(ttl_seconds=300)
def cargos():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM cargos ORDER BY nombre")
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
@cache_result(ttl_seconds=300)
def ciudades():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT * FROM ciudades
        ORDER BY
            CASE
                WHEN UPPER(nombre) LIKE '%%BOGOT%%' THEN 0
                ELSE 1
            END,
            nombre ASC
    """)
    ciudad = cur.fetchall()
    cur.close()
    # Parsear departamento y municipio para agrupar por departamento
    for c in ciudad:
        parts = (c['nombre'] or '').split(' - ', 1)
        if len(parts) == 2:
            c['departamento'] = parts[0].strip()
            c['municipio'] = parts[1].strip()
        else:
            c['departamento'] = ''
            c['municipio'] = c['nombre'] or ''
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
            barrio2,
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
            sgi_rol_id,
            cedula_path,
            foto_path,
            tipo_identificacion
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
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
        data.get('barrio2') or None,
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
        data.get('sgi_rol_id') or None,
        ruta_cedula,
        ruta_foto,
        data.get('tipo_identificacion') or None
    )
    cur.execute(sql, valores)
    mysql.connection.commit()
    empleado_id = cur.lastrowid
    
    # El contrato se crea SOLO si se indicó una fecha de ingreso. La fecha de
    # ingreso ya no se pide en el formulario del empleado (se gestiona desde el
    # modal de contratos), por lo que un empleado puede crearse sin contrato
    # y este se le asigna después desde el modal de contratos.
    fehca_ingreso = data.get('fecha_ingreso_antigua')
    if fehca_ingreso:
        #GENERA CONSECUTIVO
        tipo_id = data.get('tipo_contrato_id') or None
        consecutivo_final = genera_consecutivo(tipo_id)

        #guarda en la tabla de contratos
        salario_basico = data.get('salario_basico')
        factor_no_salarial = data.get('factor_no_salarial')
        guardar_fecha_contrato(empleado_id, fehca_ingreso, salario_basico, factor_no_salarial, consecutivo_final, tipo_id)
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
                barrio2=%s,
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
                sgi_rol_id=%s,
                nivel_escolaridad_id=%s,
                programa_academico=%s,
                estudia_actualmente=%s,
                nombre_programa_actual=%s,
                tipo_identificacion=%s
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
        data.get("barrio2") or None,
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
        data.get("sgi_rol_id") or None,
        data["nivel_escolaridad_id"],
        data["programa_academico"],
        data["estudia_actualmente"],
        data["nombre_programa_actual"],
        data.get("tipo_identificacion") or None,
        id
    ))
    
    #actualizacion salario
    salario_basico = limpiar_decumal(data['salario_basico'])
    factor_no_salarial = limpiar_decumal(data['factor_no_salarial'])
    # Cap values to fit DECIMAL(10,2) max 99999999.99
    salario_basico = min(salario_basico, 99999999.99)
    factor_no_salarial = min(factor_no_salarial, 99999999.99)
    cur.execute("""
                UPDATE contratos SET
                    salario_basico = %s,
                    factor_no_salarial = %s,
                    tipo_contrato_id = %s
                WHERE empleado_id = %s AND fecha_finalizacion IS NULL
                """, (salario_basico, factor_no_salarial, data.get('tipo_contrato_id') or None, id))
    mysql.connection.commit()
    cur.close()
    

#------------------------------------------------------
#------------------ UTILIDADES ------------------------
#------------------------------------------------------ 
def limpiar_decumal(valor):
    if valor is None or valor == '':
        return 0
    # Si ya es un número (int o float), retornar directamente
    if isinstance(valor, (int, float)):
        return float(valor)
    # Si es string, limpiar formato
    return float(valor.replace(".", "").replace(",", "."))


def formatear_moneda(valor):
    """Formatea un valor numérico como moneda colombiana: $2.000.000

    Args:
        valor: Número, Decimal o string con el valor (ej. 2000000.00).

    Returns:
        str: "$2.000.000" (sin decimales si es entero, con coma si aplica).
        Cadena vacía si el valor es None/vacío.
    """
    if valor is None or valor == '':
        return ''
    try:
        num = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if num == int(num):
        texto = f"{int(num):,}".replace(',', '.')
    else:
        # "1,500,000.50" -> miles con punto y decimales con coma (formato es-CO)
        texto = f"{num:,.2f}".replace(',', '.')
        if '.' in texto:
            entero, decimal = texto.rsplit('.', 1)
            texto = entero + ',' + decimal
        texto = texto.rstrip('0').rstrip(',')
    return f"${texto}"


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


def formatear_antiguedad(fecha_ingreso, fecha_final=None):
    """Calcula la antigüedad desde la fecha de ingreso hasta una fecha final.

    - Si fecha_final es None (empleado activo), calcula hasta hoy.
    - Si fecha_final se indica (empleado retirado), calcula hasta la fecha
      de finalización del contrato.

    Devuelve texto legible: '3 años 5 meses', '8 meses', '1 año',
    'Menos de 1 mes' o '' si no hay fecha. NO se usa para guardar en BD
    (la columna antiguedad sigue almacenando solo los años).
    """
    if not fecha_ingreso:
        return ''
    try:
        if isinstance(fecha_ingreso, str):
            fecha_ing = datetime.strptime(fecha_ingreso[:10], "%Y-%m-%d")
        else:
            fecha_ing = fecha_ingreso

        if fecha_final:
            if isinstance(fecha_final, str):
                fecha_fin = datetime.strptime(fecha_final[:10], "%Y-%m-%d")
            else:
                fecha_fin = fecha_final
        else:
            fecha_fin = datetime.now()

        anios = fecha_fin.year - fecha_ing.year
        meses = fecha_fin.month - fecha_ing.month
        if fecha_fin.day < fecha_ing.day:
            meses -= 1
        if meses < 0:
            anios -= 1
            meses += 12

        # Protección contra fechas inválidas (final antes que inicio)
        if anios < 0 or (anios == 0 and meses < 0):
            return ''

        partes = []
        if anios > 0:
            partes.append(f"{anios} {'año' if anios == 1 else 'años'}")
        if meses > 0:
            partes.append(f"{meses} {'mes' if meses == 1 else 'meses'}")
        return ' '.join(partes) if partes else 'Menos de 1 mes'
    except Exception:
        return ''


#------------------------------------------------------
#------------ IMPORTAR CONTRATOS MASIVOS --------------
#------------------------------------------------------
def importar_contratos_plantilla(data):
    """Actualiza o inserta contratos desde una carga masiva.

    Busca al empleado por identificacion, actualiza el contrato
    cuyo n_consecutivo coincida con codigo_contrato (o el activo
    si no se proporciona), y opcionalmente actualiza el tipo de
    contrato del empleado.
    Si se proporciona fecha_ingreso y no hay codigo_contrato,
    crea un nuevo contrato.

    Args:
        data: dict con claves:
            - identificacion: str
            - salario_basico: float
            - factor_no_salarial: float
            - codigo_contrato: str (opcional)
            - tipo_contrato_id: int (opcional)
            - fecha_ingreso: str (opcional, formato YYYY-MM-DD)
            - fecha_finalizacion: str (opcional, formato YYYY-MM-DD)
            - motivo: str (opcional, motivo del retiro/terminación)

    Returns:
        tuple: (success: bool, error: str or None)
    """
    try:
        cur = mysql.connection.cursor()

        # 1. Buscar empleado por identificacion
        cur.execute("SELECT id, tipo_contrato_id FROM users_rrhh WHERE identificacion = %s", (data['identificacion'],))
        emp = cur.fetchone()
        if not emp:
            cur.close()
            return False, f"Empleado con identificacion {data['identificacion']} no encontrado"

        empleado_id = emp[0]
        empleado_tipo_contrato_id = emp[1]
        salario = limpiar_decumal(data['salario_basico'])
        factor = limpiar_decumal(data.get('factor_no_salarial'))
        fecha_ingreso = data.get('fecha_ingreso')
        fecha_finalizacion = data.get('fecha_finalizacion')
        motivo = data.get('motivo')

        # 2. Determinar accion segun los datos proporcionados
        codigo = data.get('codigo_contrato')

        # Si hay codigo_contrato, primero verificar si el contrato ya existe en BD
        contrato_existente_id = None
        if codigo:
            # Buscar por código exacto
            cur.execute(
                "SELECT id FROM contratos WHERE empleado_id = %s AND n_consecutivo = %s",
                (empleado_id, codigo)
            )
            row = cur.fetchone()
            if row:
                contrato_existente_id = row[0]
            # Si no encontró y es numérico, puede que Excel haya quitado ceros a la izquierda
            if not contrato_existente_id and codigo.isdigit():
                cur.execute(
                    "SELECT id FROM contratos WHERE empleado_id = %s AND CAST(n_consecutivo AS UNSIGNED) = %s LIMIT 1",
                    (empleado_id, int(codigo))
                )
                row = cur.fetchone()
                if row:
                    contrato_existente_id = row[0]

        if contrato_existente_id:
            # Actualizar contrato existente
            set_parts = ["salario_basico = %s", "factor_no_salarial = %s"]
            vals = [salario, factor]
            if fecha_ingreso:
                set_parts.append("fecha_ingreso = %s")
                vals.append(fecha_ingreso)
            if fecha_finalizacion:
                set_parts.append("fecha_finalizacion = %s")
                vals.append(fecha_finalizacion)
            if data.get('tipo_contrato_id'):
                set_parts.append("tipo_contrato_id = %s")
                vals.append(data['tipo_contrato_id'])
            if motivo:
                set_parts.append("motivo = %s")
                vals.append(motivo)
            vals.append(contrato_existente_id)
            cur.execute(
                f"UPDATE contratos SET {', '.join(set_parts)} WHERE id = %s",
                tuple(vals)
            )

        elif fecha_ingreso:
            # Crear un nuevo contrato
            # Si se proporciono codigo_contrato, usarlo; si no, generar uno nuevo
            if codigo:
                n_consecutivo = codigo
            else:
                n_consecutivo = genera_consecutivo(
                    data.get('tipo_contrato_id') or empleado_tipo_contrato_id
                )
            tipo_contrato_nuevo = data.get('tipo_contrato_id') or empleado_tipo_contrato_id
            cur.execute(
                """INSERT INTO contratos (empleado_id, fecha_ingreso, fecha_finalizacion, salario_basico, factor_no_salarial, n_consecutivo, tipo_contrato_id, motivo)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (empleado_id, fecha_ingreso, fecha_finalizacion, salario, factor, n_consecutivo, tipo_contrato_nuevo, motivo)
            )

        else:
            # Si se indicó un codigo_contrato que no existe y no hay fecha para
            # crear uno nuevo, es un error: NO debe caer a actualizar el contrato
            # activo con datos de una fila que apunta a otro contrato.
            if codigo:
                cur.close()
                return False, f"Contrato con codigo {codigo} no encontrado para empleado {data['identificacion']}"

            # Actualizar el contrato activo mas reciente (solo aplica si hay)
            update_fields = "salario_basico = %s, factor_no_salarial = %s"
            update_vals = [salario, factor]

            if fecha_finalizacion:
                update_fields += ", fecha_finalizacion = %s"
                update_vals.append(fecha_finalizacion)
            if motivo:
                update_fields += ", motivo = %s"
                update_vals.append(motivo)

            update_vals.append(empleado_id)
            cur.execute(
                f"""UPDATE contratos SET {update_fields}
                   WHERE empleado_id = %s AND fecha_finalizacion IS NULL
                   ORDER BY id DESC LIMIT 1""",
                tuple(update_vals)
            )
            if cur.rowcount == 0:
                cur.close()
                return False, f"No se encontro contrato activo para empleado {data['identificacion']}"

        # 3. Actualizar tipo de contrato del empleado si se proporciono
        if data.get('tipo_contrato_id'):
            cur.execute("UPDATE users_rrhh SET tipo_contrato_id = %s WHERE id = %s", (data['tipo_contrato_id'], empleado_id))

        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al importar contratos: {e}")
        return False, str(e)


#------------------------------------------------------
#-------------- ASIGNAR ROL SGI MASIVO ----------------
#------------------------------------------------------
def asignar_rol_sgi_db(data):
    """Asigna un Rol SGI a un empleado por su identificación.

    Args:
        data: dict con claves:
            - identificacion: str
            - sgi_rol_id: int (puede ser None para quitar el rol)

    Returns:
        tuple: (success: bool, error: str or None)
    """
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users_rrhh WHERE identificacion = %s", (data['identificacion'],))
        emp = cur.fetchone()
        if not emp:
            cur.close()
            return False, f"Empleado con identificacion {data['identificacion']} no encontrado"

        cur.execute("UPDATE users_rrhh SET sgi_rol_id = %s WHERE id = %s", (data['sgi_rol_id'], emp[0]))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al asignar rol SGI: {e}")
        return False, str(e)


def restablecer_password_db(empleado_id):
    """Restablece la contraseña de un empleado a su número de identificación
    y marca primer_ingreso = 1 para forzar cambio en el próximo inicio de sesión.

    Args:
        empleado_id: ID del empleado en users_rrhh.

    Returns:
        tuple: (success: bool, identificacion: str or None, error: str or None)
    """
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Obtener la identificación del empleado
        cur.execute("SELECT identificacion FROM users_rrhh WHERE id = %s", (empleado_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            return False, None, "Empleado no encontrado"

        identificacion = str(row['identificacion'])
        nueva_password = hash_password(identificacion)

        cur.execute(
            "UPDATE users_rrhh SET password = %s, primer_ingreso = 1 WHERE id = %s",
            (nueva_password, empleado_id)
        )
        mysql.connection.commit()
        cur.close()
        return True, identificacion, None
    except Exception as e:
        print(f"Error al restablecer password: {e}")
        return False, None, str(e)
    
    
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
                grupo_sanguineo_id,                numero_hijos, direccion, barrio, barrio2, localidad, 
                estrato, telefono_fijo, celular, correo, contacto_emergencia, 
                telefono_emergencia, parentesco, eps_id, afp_id, cesantias_id, 
                ccf_id, arl_id, tipo_contrato_id, cargo_id, jornada, sede, 
                antiguedad, nivel_escolaridad_id, programa_academico, 
                estudia_actualmente, nombre_programa_actual, numero_cuenta, 
                banco, password, activo, grupo_nomina_id,
                tipo_identificacion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, 1, %s,
                %s
            )
        """
        cur.execute(sql_user, (
            data['identificacion'], data['nombres'], data['apellidos'], data['cedula_expedida_en'],
            data['sexo'], data['fecha_nacimiento'], data['lugar_nacimiento'], data['edad'],
            data['estado_civil_id'], data['grupo_sanguineo_id'], data['numero_hijos'],
            data['direccion'], data['barrio_id'], data.get('barrio2') or None, data['localidad'], data['estrato'],
            data['telefono_fijo'], data['celular'], data['correo'], data['contacto_emergencia'],
            data['telefono_emergencia'], data['parentesco'], data['eps_id'], data['afp_id'],
            data['cesantias_id'], data['ccf_id'], data['arl_id'], data['tipo_contrato_id'],
            data['cargo_id'], data['jornada'], data['sede_id'], data['antiguedad'],
            data['nivel_escolaridad_id'], data['programa_academico'], data['estudia_actualmente'],
            data['nombre_programa_actual'], data['numero_cuenta'], data['banco_id'],
            data['password'], data['grupo_nomina_id'],
            data.get('tipo_identificacion_id') or None
        ))
        empleado_id = cur.lastrowid
        
        consecutivo_final = genera_consecutivo(data['tipo_contrato_id'])
        
        # sql_contrato = """
        #     INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo)
        #     VALUES (%s, %s, %s, %s, %s)
        # """
        # cur.execute(sql_contrato, (empleado_id, data['fecha_ingreso'], data['salario_basico'], data['factor_no_salarial'], consecutivo_final))
        
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
                numero_hijos=%s, direccion=%s, barrio=%s, barrio2=%s, 
                localidad=%s, estrato=%s, telefono_fijo=%s, celular=%s, correo=%s, 
                contacto_emergencia=%s, telefono_emergencia=%s, parentesco=%s, 
                eps_id=%s, afp_id=%s, cesantias_id=%s, ccf_id=%s, arl_id=%s, 
                tipo_contrato_id=%s, cargo_id=%s, jornada=%s, sede=%s, 
                nivel_escolaridad_id=%s, programa_academico=%s, 
                estudia_actualmente=%s, nombre_programa_actual=%s, 
                numero_cuenta=%s, banco=%s, grupo_nomina_id=%s,
                tipo_identificacion=%s
            WHERE identificacion = %s
        """
        valores = (
            data['sexo'],data['edad'], data['estado_civil_id'],
            data['numero_hijos'], data['direccion'], data['barrio_id'],
            data.get('barrio2') or None,
            data['localidad'], data['estrato'], data['telefono_fijo'], data['celular'], data['correo'],
            data['contacto_emergencia'], data['telefono_emergencia'], data['parentesco'],
            data['eps_id'], data['afp_id'], data['cesantias_id'], data['ccf_id'], data['arl_id'],
            data['tipo_contrato_id'], data['cargo_id'], data['jornada'], data['sede_id'],
            data['nivel_escolaridad_id'], data['programa_academico'], data['estudia_actualmente'],
            data['nombre_programa_actual'], data['numero_cuenta'], data['banco_id'],
            data['grupo_nomina_id'],
            data.get('tipo_identificacion_id') or None,
            data['identificacion'] # El WHERE
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
            LEFT JOIN contratos c ON u.id = c.empleado_id
            LEFT JOIN tipo_contrato tp ON tp.id = COALESCE(c.tipo_contrato_id, u.tipo_contrato_id)
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
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
    try:
        id_contrato = None

        # La creación de contrato inicial NO requiere un contrato previo;
        # el resto de acciones sí operan sobre un contrato existente.
        if accion != 'crear_contrato':
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
        
        elif accion == 'cambio_contrato':
            cur.execute("UPDATE users_rrhh SET tipo_contrato_id = %s WHERE id = %s", (data['tipo_contrato_id'], id_empleado))
            tipo_texto = "Cambio de Tipo de Contrato"


        if accion == 'crear_contrato':
            # Crear contrato inicial para empleado sin contrato
            if not data.get('tipo_contrato_id') or not data.get('fecha_inicio'):
                cur.close()
                raise Exception("Debe seleccionar el tipo de contrato y la fecha de inicio")
            consecutivo_final = genera_consecutivo(data['tipo_contrato_id'])
            salario = limpiar_decumal(data.get('salario'))
            factor_salarial = limpiar_decumal(data.get('factor_salarial'))
            cur.execute(
                """INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo, tipo_contrato_id)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (id_empleado, data['fecha_inicio'], salario, factor_salarial, consecutivo_final, data['tipo_contrato_id'])
            )
            cur.execute("UPDATE users_rrhh SET tipo_contrato_id = %s WHERE id = %s", (data['tipo_contrato_id'], id_empleado))

        elif accion == 'cambio_contrato':
            # Cerrar el contrato anterior (solo si aun no tiene fecha de finalizacion)
            cur.execute(
                "UPDATE contratos SET fecha_finalizacion = %s WHERE id = %s AND fecha_finalizacion IS NULL",
                (data['fecha_inicio'], id_contrato)
            )
            # Generar nuevo consecutivo SOLO para cambio_contrato (evita desperdiciar numeros)
            consecutivo_final = genera_consecutivo(data['tipo_contrato_id'])
            salario = limpiar_decumal(data['salario'])
            factor_salarial = limpiar_decumal(data['factor_salarial'])
            sql_contrato = """
            INSERT INTO contratos (empleado_id, fecha_ingreso, salario_basico, factor_no_salarial, n_consecutivo, tipo_contrato_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
            cur.execute(sql_contrato, (id_empleado, data['fecha_inicio'], salario, factor_salarial, consecutivo_final, data.get('tipo_contrato_id') or None))
        elif accion == 'eliminar_contrato':
            # Eliminar primero los Otrosí asociados al contrato (evita conflictos de FK)
            cur.execute("DELETE FROM otrosi_contratos WHERE id_contrato = %s", (id_contrato,))
            cur.execute("DELETE FROM contratos WHERE id = %s", (id_contrato,))
        elif accion == 'editar_otrosi':
            # Editar SOLO la fecha de finalización del último Otrosí del contrato
            if not fecha_fin_otrosi:
                cur.close()
                raise Exception("Debe ingresar la fecha de finalización")
            cur.execute(
                """UPDATE otrosi_contratos
                   SET fecha_fin = %s
                   WHERE id = (
                       SELECT id FROM (
                           SELECT id FROM otrosi_contratos
                           WHERE id_contrato = %s
                           ORDER BY id DESC LIMIT 1
                       ) AS ultimo
                   )""",
                (fecha_fin_otrosi, id_contrato)
            )
        else:
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
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al procesar otrosi: {e}")
        raise e


#------------------------------------------------------
#--------------- EVALUACION DESEMPEÑO -----------------
#------------------------------------------------------
def habilita_evaluacion(anio, inicio, fin, evaluador, evaluados):
    try:
        estado = 1 # 1: habilitado, 0: desabilitado
        cur = mysql.connection.cursor() 
        sql = "INSERT INTO evaluaciones_desempeno (anio_evaluacion, fecha_inicio, fecha_fin, estado) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (anio, inicio, fin, estado))

        id_evaluacion = cur.lastrowid

        sql_asignacion = """
            INSERT INTO evaluacion_desempeno_asignaciones (id_evaluacion, id_evaluador, id_evaluado, id_plantilla)
            VALUES (%s, %s, %s, %s)
        """
        for evaluado in evaluados:
            sql_cargo = "SELECT c.id as cargo FROM cargos c INNER JOIN users_rrhh u ON c.id = u.cargo_id WHERE u.id = %s"
            cur.execute(sql_cargo, (evaluado,))
            cargo = cur.fetchone()
            id_plantilla = cargo[0] if cargo else None
            cur.execute(sql_asignacion, (id_evaluacion, evaluador, evaluado, id_plantilla))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al habilitar evaluacion: {e}")
        return False, str(e)

def guarda_resultado_evaluacion(id_asignacion, resultado):
    try:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO evaluacion_desempeno_resultados (id_asignacion, resultado) VALUES (%s, %s)"
        cur.execute(sql, (id_asignacion, resultado))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al guardar resultado de evaluacion: {e}")
        return False, str(e)

def guardaEvaluacion(id_asignacion, resultado_competencias, resultado_tipos, resultado_general, observaciones_evaluador, aspectos_sobresalientes, aspectos_mejorar):
    cur = mysql.connection.cursor()
    #evaluacion desempeño asignaciones
    try:
        fecha_evaluacion = datetime.now()
        estado = 1

        sql_asignacion= """
            UPDATE evaluacion_desempeno_asignaciones
            SET fecha = %s,
                estado = %s
            WHERE id = %s
        """
        cur.execute(sql_asignacion, (fecha_evaluacion, estado, id_asignacion))
        
        #competencias resultado POR ASIGNACION (nueva tabla)
        sql_competencias = """
            INSERT INTO evaluacion_desempeno_resultado_competencias (id_asignacion, id_competencia, resultado)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE resultado = VALUES(resultado)
        """
        for comp in resultado_competencias:
            cur.execute(sql_competencias, (
                id_asignacion,
                comp['id_competencia'],
                comp['resultado_ponderado']
            ))

        #tipo competencias resultado POR ASIGNACION (nueva tabla)
        sql_tipo_competencia = """
            INSERT INTO evaluacion_desempeno_resultado_tipos (id_asignacion, id_tipo, resultado)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE resultado = VALUES(resultado)
        """
        for tipo in resultado_tipos:
            cur.execute(sql_tipo_competencia, (
                id_asignacion,
                tipo['id_tipo'],
                tipo['total']
            ))

        #resultado general
        sql_resultado_general = """
            INSERT INTO evaluacion_desempeno_resultado (id_asignacion, resultado, observaciones_evaluador, aspectos_sobresalientes, aspectos_mejorar)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE resultado = VALUES(resultado), observaciones_evaluador = VALUES(observaciones_evaluador)
        """
        total_final = resultado_general.get('total', 0)
        cur.execute(sql_resultado_general, (id_asignacion, total_final, observaciones_evaluador, aspectos_sobresalientes, aspectos_mejorar))
        mysql.connection.commit()
        cur.close()
        return True, "La evaluacion de ha guardado y actualizado correctamente."
    except Exception as e:
        print(f'Error en el controller: {e}')
        return False, f"Error al guardar en la base de datos: {str(e)}"


def consulta_evaluacion_habilitada(id_usuario):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = """SELECT eda.id_evaluador, u.nombres, u.apellidos, c.nombre AS plantilla, ed.id, eda.id AS id_asignacion, eda.id_plantilla FROM evaluacion_desempeno_asignaciones AS eda 
                INNER JOIN users_rrhh u ON eda.id_evaluado = u.id 
                INNER JOIN evaluaciones_desempeno ed ON eda.id_evaluacion = ed.id 
                INNER JOIN cargos c ON eda.id_plantilla = c.id 
                WHERE eda.id_evaluador = %s AND eda.estado = 0"""
        cur.execute(sql, (id_usuario,))
        evaluacion = cur.fetchall() # lista de diccionarios (id_evaluador, nombres, apellidos, id_evaluacion)
        cur.close()
        return evaluacion
    except Exception as e:
        print(f"Error al consultar evaluacion habilitada: {e}")
        return None

def busca_asignacion_evaluacion(id_usuario):
    ahora = datetime.now()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT COUNT(*) AS cuenta FROM evaluacion_desempeno_asignaciones eda 
        INNER JOIN evaluaciones_desempeno ed ON eda.id_evaluacion = ed.id
        WHERE id_evaluador = %s AND ed.fecha_fin >= %s
    """
    cur.execute(sql, (id_usuario, ahora))
    asignacion = cur.fetchone()
    return asignacion

def obtener_plantilla(id_asignacion):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Usamos el cargo ACTUAL del empleado (u.cargo_id) en lugar del guardado
    # en la asignacion (eda.id_plantilla). Esto permite que si el empleado
    # cambia de cargo despues de habilitada la evaluacion, se usen las
    # preguntas del cargo correcto.
    sql_evaluado = """
        SELECT u.id, eda.id AS id_asignacion, u.nombres, u.apellidos,
               COALESCE(u.cargo_id, eda.id_plantilla) AS id_plantilla
        FROM evaluacion_desempeno_asignaciones eda
        INNER JOIN users_rrhh u ON u.id = eda.id_evaluado
        WHERE eda.id = %s
    """
    cur.execute(sql_evaluado, (id_asignacion,))
    evaluado = cur.fetchone()

    if not evaluado:
        cur.close()
        return None, [], [], []

    id_plantilla = evaluado['id_plantilla']

    if id_plantilla is None:
        cur.close()
        return evaluado, [], [], []

    sql_preguntas = """
        SELECT edp.id, edp.tipo AS id_tipo, edp.competencia AS id_competencia,
               tc.nombre AS tipo_competencia, com.nombre AS competencia, edp.pregunta,
               COALESCE(cr.porcentaje, 0) AS porcentaje_competencia
        FROM evaluacion_desempeno_preguntas edp
        INNER JOIN tipo_competencias tc ON tc.id = edp.tipo
        INNER JOIN competencia com ON com.id = edp.competencia
        LEFT JOIN competencias_resultado cr
            ON cr.id_competencia = edp.competencia AND cr.id_plantilla = edp.id_plantilla
        WHERE edp.id_plantilla = %s
    """
    cur.execute(sql_preguntas, (id_plantilla,))
    preguntas = cur.fetchall()
    cur.close()
    tipo_competencias = consulta_tipo_competencias_resultado_plantilla(id_plantilla)
    competencias = consulta_competencias_resultado_plantilla(id_plantilla)
    return evaluado, preguntas, tipo_competencias, competencias

def consulta_tipo_competencias():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT id, nombre FROM tipo_competencias"
    cur.execute(sql)
    competencias = cur.fetchall()
    cur.close()
    return competencias

def consulta_tipo_competencias_resultado_plantilla(id_plantilla):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT tcr.id_tipo, tc.nombre AS nombre, tcr.porcentaje AS porcentaje FROM tipo_competencias_resultado tcr
        INNER JOIN tipo_competencias tc ON tc.id = tcr.id_tipo
        WHERE tcr.id_plantilla = %s
    """
    cur.execute(sql, (id_plantilla,))
    tipo_competencias = cur.fetchall()
    cur.close()
    return tipo_competencias

def consulta_competencias_resultado_plantilla(id_plantilla):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT cr.id_competencia, comp.nombre AS nombre, cr.porcentaje AS porcentaje FROM competencias_resultado cr
        INNER JOIN competencia comp ON comp.id = cr.id_competencia
        WHERE cr.id_plantilla = %s
    """
    cur.execute(sql, (id_plantilla,))
    competencias = cur.fetchall()
    cur.close()
    return competencias


def consulta_criterios():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT crit.id AS id_criterio, crit.id_tipo, tc.nombre AS competencia, crit.nombre
        FROM competencia crit
        INNER JOIN tipo_competencias tc ON crit.id_tipo = tc.id
    """
    cur.execute(sql)
    criterios = cur.fetchall()
    cur.close()
    return criterios

def consulta_preguntas():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT preg.id, preg.pregunta, c.nombre AS asignado,
               preg.id_plantilla, preg.tipo, preg.competencia, 
                tc.nombre AS tipo_competencia, comp.nombre AS criterio,
                tcr.porcentaje AS tipo_porcentaje, cr.porcentaje AS competencia_porcentaje              
        FROM evaluacion_desempeno_preguntas preg
        INNER JOIN cargos c ON preg.id_plantilla = c.id
        INNER JOIN tipo_competencias tc ON preg.tipo = tc.id
        INNER JOIN competencia comp ON preg.competencia = comp.id
        LEFT JOIN tipo_competencias_resultado tcr
            ON tcr.id_tipo = preg.tipo AND tcr.id_plantilla = preg.id_plantilla
        LEFT JOIN competencias_resultado cr
            ON cr.id_competencia = preg.competencia AND cr.id_plantilla = preg.id_plantilla
    """
    cur.execute(sql)
    preguntas = cur.fetchall()
    cur.close()
    return preguntas


def consulta_plantillas_evaluacion_desde_asignaciones():
    """
    Cargos disponibles para construir preguntas de evaluacion.
    """
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT id, nombre
        FROM cargos
        ORDER BY nombre
    """
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    return rows


def id_plantilla_existe_en_asignaciones_evaluacion(id_plantilla):
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT 1 FROM cargos
        WHERE id = %s LIMIT 1
        """,
        (id_plantilla,),
    )
    ok = cur.fetchone() is not None
    cur.close()
    return ok


def id_plantilla_aceptada_al_editar_pregunta(pregunta_id, id_plantilla):
    """Nuevo valor debe estar en asignaciones, o ser el mismo id que ya tiene la fila (legado)."""
    if id_plantilla_existe_en_asignaciones_evaluacion(id_plantilla):
        return True
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id_plantilla FROM evaluacion_desempeno_preguntas WHERE id = %s",
        (pregunta_id,),
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        return False
    return int(row[0]) == int(id_plantilla)


def editar_tipo_competencia(tipo_id, nombre):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tipo_competencias SET nombre = %s WHERE id = %s", (nombre, tipo_id))
    mysql.connection.commit()
    cur.close()


def eliminar_tipo_competencia(tipo_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tipo_competencias WHERE id = %s", (tipo_id,))
    mysql.connection.commit()
    cur.close()


def editar_criterio_competencia(criterio_id, nombre, id_tipo):
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE competencia SET nombre = %s, id_tipo = %s WHERE id = %s",
        (nombre, id_tipo, criterio_id),
    )
    mysql.connection.commit()
    cur.close()


def eliminar_criterio_competencia(criterio_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM competencia WHERE id = %s", (criterio_id,))
    mysql.connection.commit()
    cur.close()


def editar_pregunta_evaluacion(pregunta_id, pregunta, id_plantilla, tipo, competencia, porc_tipo, porc_competencia):
    # Validar porcentajes al editar también
    validar_suma_porcentajes(id_plantilla, tipo, competencia, porc_tipo, porc_competencia)

    cur = mysql.connection.cursor()
    try:
        cur.execute(
        """
        UPDATE evaluacion_desempeno_preguntas
        SET pregunta = %s, id_plantilla = %s, tipo = %s, competencia = %s
        WHERE id = %s
        """,
        (pregunta, id_plantilla, tipo, competencia, pregunta_id),
    )
        cur.execute("""
            UPDATE tipo_competencias_resultado
            SET porcentaje = %s
            WHERE id_tipo = %s AND id_plantilla = %s
        """,
        (porc_tipo, tipo, id_plantilla)
        )
        cur.execute("""
            UPDATE competencias_resultado
            SET porcentaje = %s
            WHERE id_competencia = %s AND id_plantilla = %s
        """,
        (porc_competencia, competencia, id_plantilla)
        )
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()


def eliminar_pregunta_evaluacion(pregunta_id, id_plantilla=None):
    cur = mysql.connection.cursor()
    try:
        if id_plantilla is None:
            cur.execute(
                "SELECT id_plantilla, competencia FROM evaluacion_desempeno_preguntas WHERE id = %s",
                (pregunta_id,),
            )
        else:
            cur.execute(
                """
                SELECT id_plantilla, competencia
                FROM evaluacion_desempeno_preguntas
                WHERE id = %s AND id_plantilla = %s
                """,
                (pregunta_id, id_plantilla),
            )
        pregunta = cur.fetchone()
        if not pregunta:
            return 0

        pregunta_plantilla = pregunta[0]
        pregunta_competencia = pregunta[1]
        cur.execute(
            "DELETE FROM evaluacion_desempeno_preguntas WHERE id = %s AND id_plantilla = %s",
            (pregunta_id, pregunta_plantilla),
        )
        eliminadas = cur.rowcount

        cur.execute(
            """
            SELECT 1 FROM evaluacion_desempeno_preguntas
            WHERE id_plantilla = %s AND competencia = %s
            LIMIT 1
            """,
            (pregunta_plantilla, pregunta_competencia),
        )
        if not cur.fetchone():
            cur.execute(
                "DELETE FROM competencias_resultado WHERE id_competencia = %s AND id_plantilla = %s",
                (pregunta_competencia, pregunta_plantilla),
            )

        mysql.connection.commit()
        return eliminadas
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cur.close()


def crear_tipo_competencia(nombre):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tipo_competencias (nombre) VALUES (%s)", (nombre,))
    mysql.connection.commit()
    new_id = cur.lastrowid
    cur.close()
    return new_id


def crear_criterio_competencia(nombre, id_tipo):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO competencia (nombre, id_tipo) VALUES (%s, %s)",
        (nombre, id_tipo),
    )
    mysql.connection.commit()
    new_id = cur.lastrowid
    cur.close()
    return new_id


def validar_suma_porcentajes(plantilla, tipo, competencia, porc_tipo, porc_competencia):
    """
    Valida que la suma de porcentajes no exceda 100%.
    Funciona tanto para creación como edición: si el registro ya existe,
    resta su valor actual de la suma para no contarlo doble.
    Levanta Exception si la validación falla.
    """
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    porc_tipo = float(porc_tipo) if porc_tipo else 0
    porc_competencia = float(porc_competencia) if porc_competencia else 0

    # ---- Validar suma de % tipo ----
    cur.execute(
        "SELECT id, porcentaje FROM tipo_competencias_resultado WHERE id_tipo = %s AND id_plantilla = %s",
        (tipo, plantilla)
    )
    tipo_row = cur.fetchone()

    cur.execute(
        "SELECT COALESCE(SUM(porcentaje), 0) AS suma FROM tipo_competencias_resultado WHERE id_plantilla = %s",
        (plantilla,)
    )
    suma_tipo = float(cur.fetchone()['suma'])

    # Si ya existe, restamos su valor actual para no contarlo doble
    if tipo_row:
        suma_tipo -= float(tipo_row['porcentaje'])

    if porc_tipo > 0 and suma_tipo + porc_tipo > 100:
        cur.close()
        raise Exception(
            f"La suma de % de tipos de competencia excede 100%. "
            f"Actual: {suma_tipo}%, nuevo: {porc_tipo}%"
        )

    # ---- Validar suma de % criterios para este tipo ----
    cur.execute(
        "SELECT id, porcentaje FROM competencias_resultado WHERE id_competencia = %s AND id_plantilla = %s",
        (competencia, plantilla)
    )
    comp_row = cur.fetchone()

    cur.execute(
        """
        SELECT COALESCE(SUM(cr.porcentaje), 0) AS suma
        FROM competencias_resultado cr
        INNER JOIN competencia c ON c.id = cr.id_competencia
        WHERE cr.id_plantilla = %s AND c.id_tipo = %s
        """,
        (plantilla, tipo),
    )
    suma_comp = float(cur.fetchone()['suma'])

    # Si ya existe, restamos su valor actual
    if comp_row:
        suma_comp -= float(comp_row['porcentaje'])

    if porc_competencia > 0 and suma_comp + porc_competencia > 100:
        cur.close()
        raise Exception(
            f"La suma de % de criterios para este tipo excede 100%. "
            f"Actual: {suma_comp}%, nuevo: {porc_competencia}%"
        )

    cur.close()


def crear_pregunta_evaluacion(pregunta, id_plantilla, tipo, competencia, porcentaje_tipo, porcentaje_criterio):
    # Validar porcentajes antes de insertar
    validar_suma_porcentajes(id_plantilla, tipo, competencia, porcentaje_tipo, porcentaje_criterio)

    cur = mysql.connection.cursor()
    cur.execute(
        """
        INSERT INTO evaluacion_desempeno_preguntas (pregunta, id_plantilla, tipo, competencia)
        VALUES (%s, %s, %s, %s)
        """,
        (pregunta, id_plantilla, tipo, competencia),
    )
    new_id = cur.lastrowid

    #inserta porcentaje de tipo solo si no existe para esa plantilla
    cur.execute("SELECT id FROM tipo_competencias_resultado WHERE id_tipo = %s AND id_plantilla = %s", (tipo, id_plantilla))
    if not cur.fetchone():
        sql_porcentaje_tipo = """
            INSERT INTO tipo_competencias_resultado (id_tipo, id_plantilla, porcentaje)
            VALUES (%s, %s, %s)
        """
        cur.execute(sql_porcentaje_tipo, (tipo, id_plantilla, porcentaje_tipo))

    #inserta porcentaje de competencia solo si no existe para esa plantilla
    cur.execute("SELECT id FROM competencias_resultado WHERE id_competencia = %s AND id_plantilla = %s", (competencia, id_plantilla))
    if not cur.fetchone():
        sql_porcentaje_competencia = """
            INSERT INTO competencias_resultado (id_competencia, id_plantilla, porcentaje)
            VALUES (%s, %s, %s)
        """
        cur.execute(sql_porcentaje_competencia, (competencia, id_plantilla, porcentaje_criterio))
    mysql.connection.commit()
    cur.close()
    return new_id

def consulta_porcentajes_tipo():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id_tipo, id_plantilla, porcentaje FROM tipo_competencias_resultado")
    porcentajes = cur.fetchall()
    return porcentajes

def consulta_porcentajes_competencia():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id_competencia, id_plantilla, porcentaje FROM competencias_resultado")
    porcentajes_competencia = cur.fetchall()
    return porcentajes_competencia


def consulta_evaluaciones_pendientes_evaluado(id_usuario):
    """
    Obtiene las evaluaciones completadas donde el usuario es evaluado
    y aún no han sido aprobadas por él (aprobado_evaluado IS NULL o 0).
    """
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = """
            SELECT
                eda.id AS id_asignacion,
                ed.anio_evaluacion,
                eda.fecha AS fecha_evaluacion,
                eda.id_plantilla,
                ev.id AS evaluador_id,
                ev.nombres AS evaluador_nombres,
                ev.apellidos AS evaluador_apellidos,
                c.nombre AS plantilla_nombre,
                edr.resultado AS resultado_general,
                edr.observaciones_evaluador,
                edr.aprobado_evaluado,
                edr.aprobado_rrhh,
                eda.fecha_aprobacion
            FROM evaluacion_desempeno_asignaciones eda
            INNER JOIN evaluaciones_desempeno ed ON eda.id_evaluacion = ed.id
            INNER JOIN users_rrhh ev ON eda.id_evaluador = ev.id
            LEFT JOIN cargos c ON eda.id_plantilla = c.id
            LEFT JOIN evaluacion_desempeno_resultado edr ON eda.id = edr.id_asignacion
            WHERE eda.id_evaluado = %s
              AND eda.estado = 1
              AND (edr.aprobado_evaluado IS NULL OR edr.aprobado_evaluado = 0)
            ORDER BY ed.anio_evaluacion DESC, eda.fecha DESC
        """
        cur.execute(sql, (id_usuario,))
        evaluaciones = cur.fetchall()
        
        # Obtener también los resultados de competencias y tipos para mostrar en el modal
        for ev in evaluaciones:
            id_asignacion = ev['id_asignacion']
            id_plantilla = ev.get('id_plantilla')
            
            # Resultados de tipo
            sql_tipo = """
                SELECT edrt.id_tipo, tc.nombre AS nombre_tipo, edrt.resultado
                FROM evaluacion_desempeno_resultado_tipos edrt
                INNER JOIN tipo_competencias tc ON tc.id = edrt.id_tipo
                WHERE edrt.id_asignacion = %s
            """
            cur.execute(sql_tipo, (id_asignacion,))
            ev['resultados_tipo'] = cur.fetchall()
            
            # Resultados de competencias
            sql_comp = """
                SELECT edrc.id_competencia, comp.nombre AS nombre_competencia, comp.id_tipo, edrc.resultado
                FROM evaluacion_desempeno_resultado_competencias edrc
                INNER JOIN competencia comp ON comp.id = edrc.id_competencia
                WHERE edrc.id_asignacion = %s
            """
            cur.execute(sql_comp, (id_asignacion,))
            resultados_competencias = cur.fetchall()
            
            # Agrupar competencias dentro de cada tipo
            for tipo in ev['resultados_tipo']:
                tipo_id = tipo['id_tipo']
                tipo['competencias'] = [
                    c for c in resultados_competencias
                    if c['id_tipo'] == tipo_id
                ]
            ev['resultados_competencias'] = resultados_competencias
        
        cur.close()
        return evaluaciones
    except Exception as e:
        print(f"Error al consultar evaluaciones pendientes del evaluado: {e}")
        return []


def guardar_aprobacion_evaluado(id_asignacion, observaciones):
    """
    Guarda las observaciones del evaluado, marca aprobado_evaluado = 1
    y registra la fecha de aprobacion.
    """
    try:
        cur = mysql.connection.cursor()
        # Actualizar resultado
        sql = """
            UPDATE evaluacion_desempeno_resultado
            SET observaciones_evaluado = %s,
                aprobado_evaluado = 1
            WHERE id_asignacion = %s
        """
        cur.execute(sql, (observaciones, id_asignacion))
        # Actualizar fecha de aprobacion en asignacion
        sql_fecha = """
            UPDATE evaluacion_desempeno_asignaciones
            SET fecha_aprobacion = NOW()
            WHERE id = %s
        """
        cur.execute(sql_fecha, (id_asignacion,))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al guardar aprobación del evaluado: {e}")
        return False, str(e)


def guardar_aprobacion_rrhh(id_asignacion):
    """
    Marca aprobado_rrhh = 1 y registra la fecha de aprobacion.
    """
    try:
        cur = mysql.connection.cursor()
        sql = """
            UPDATE evaluacion_desempeno_resultado
            SET aprobado_rrhh = 1
            WHERE id_asignacion = %s
        """
        cur.execute(sql, (id_asignacion,))
        # Actualizar fecha de aprobacion en asignacion
        sql_fecha = """
            UPDATE evaluacion_desempeno_asignaciones
            SET fecha_aprobacion = NOW()
            WHERE id = %s
        """
        cur.execute(sql_fecha, (id_asignacion,))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        print(f"Error al guardar aprobación RRHH: {e}")
        return False, str(e)


def consulta_resultados_evaluacion():
    """
    Obtiene todos los resultados de evaluaciones de desempeño,
    incluyendo evaluador, evaluado, resultado general,
    resultados por tipo de competencia y por competencia.
    """
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
        SELECT
            eda.id AS id_asignacion,
            ed.anio_evaluacion,
            eda.fecha AS fecha_evaluacion,
            eda.estado AS estado_asignacion,
            eda.id_plantilla,
            ev.id AS evaluador_id,
            ev.nombres AS evaluador_nombres,
            ev.apellidos AS evaluador_apellidos,
            ev.identificacion AS evaluador_identificacion,
            ed_u.id AS evaluado_id,
            ed_u.nombres AS evaluado_nombres,
            ed_u.apellidos AS evaluado_apellidos,
            ed_u.identificacion AS evaluado_identificacion,
            c.nombre AS plantilla_nombre,
            edr.resultado AS resultado_general,
            edr.aprobado_evaluado,
            edr.aprobado_rrhh,
            edr.observaciones_evaluador,
            edr.observaciones_evaluado,
            eda.fecha_aprobacion
        FROM evaluacion_desempeno_asignaciones eda
        INNER JOIN evaluaciones_desempeno ed ON eda.id_evaluacion = ed.id
        INNER JOIN users_rrhh ev ON eda.id_evaluador = ev.id
        INNER JOIN users_rrhh ed_u ON eda.id_evaluado = ed_u.id
        LEFT JOIN cargos c ON eda.id_plantilla = c.id
        LEFT JOIN evaluacion_desempeno_resultado edr ON eda.id = edr.id_asignacion
        ORDER BY eda.fecha DESC, ed.anio_evaluacion DESC
    """
    cur.execute(sql)
    asignaciones = cur.fetchall()
    
    for asig in asignaciones:
        id_asignacion = asig['id_asignacion']
        id_plantilla = asig.get('id_plantilla')
        
        if id_asignacion:
            # Leer resultados de tipo POR ASIGNACION (nueva tabla)
            sql_tipo = """
                SELECT edrt.id_tipo, tc.nombre AS nombre_tipo, tcr.porcentaje AS porcentaje, edrt.resultado
                FROM evaluacion_desempeno_resultado_tipos edrt
                INNER JOIN tipo_competencias tc ON tc.id = edrt.id_tipo
                LEFT JOIN tipo_competencias_resultado tcr
                    ON tcr.id_tipo = edrt.id_tipo AND tcr.id_plantilla = %s
                WHERE edrt.id_asignacion = %s
            """
            cur.execute(sql_tipo, (id_plantilla, id_asignacion))
            asig['resultados_tipo'] = cur.fetchall()
            
            # Si no hay resultados en la nueva tabla, intentar con la tabla de configuración (legado)
            if not asig['resultados_tipo'] and id_plantilla:
                sql_tipo_legacy = """
                    SELECT tcr.id_tipo, tc.nombre AS nombre_tipo, tcr.porcentaje, tcr.resultado
                    FROM tipo_competencias_resultado tcr
                    INNER JOIN tipo_competencias tc ON tc.id = tcr.id_tipo
                    WHERE tcr.id_plantilla = %s
                """
                cur.execute(sql_tipo_legacy, (id_plantilla,))
                asig['resultados_tipo'] = cur.fetchall()
            
            # Leer resultados de competencias POR ASIGNACION (nueva tabla)
            sql_comp = """
                SELECT edrc.id_competencia, comp.nombre AS nombre_competencia, comp.id_tipo, 
                       cr.porcentaje AS porcentaje, edrc.resultado
                FROM evaluacion_desempeno_resultado_competencias edrc
                INNER JOIN competencia comp ON comp.id = edrc.id_competencia
                LEFT JOIN competencias_resultado cr
                    ON cr.id_competencia = edrc.id_competencia AND cr.id_plantilla = %s
                WHERE edrc.id_asignacion = %s
            """
            cur.execute(sql_comp, (id_plantilla, id_asignacion))
            resultados_competencias = cur.fetchall()
            
            # Si no hay resultados en la nueva tabla, intentar con la tabla de configuración (legado)
            if not resultados_competencias and id_plantilla:
                sql_comp_legacy = """
                    SELECT cr.id_competencia, comp.nombre AS nombre_competencia, comp.id_tipo, 
                           cr.porcentaje, cr.resultado
                    FROM competencias_resultado cr
                    INNER JOIN competencia comp ON comp.id = cr.id_competencia
                    WHERE cr.id_plantilla = %s
                """
                cur.execute(sql_comp_legacy, (id_plantilla,))
                resultados_competencias = cur.fetchall()
            
            # Agrupar competencias dentro de cada tipo
            for tipo in asig['resultados_tipo']:
                tipo_id = tipo['id_tipo']
                tipo['competencias'] = [
                    c for c in resultados_competencias
                    if c['id_tipo'] == tipo_id
                ]
            asig['resultados_competencias'] = resultados_competencias
        else:
            asig['resultados_tipo'] = []
            asig['resultados_competencias'] = []
    
    cur.close()
    return asignaciones


#------------------------------------------------------
#--- CONFIRMACIÓN DE DATOS PERSONALES ---
#------------------------------------------------------
def obtener_datos_confirmacion(empleado_id):
    """Obtiene los datos personales de un empleado para el modal de confirmación.

    Retorna solo los campos que el empleado debe verificar: correo y celular.

    Args:
        empleado_id: ID interno del empleado en users_rrhh.

    Returns:
        dict con nombres, apellidos, identificacion, correo, celular,
        fecha_confirmacion_datos, o None si no existe.
    """
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT nombres, apellidos, identificacion, correo, celular,
               fecha_confirmacion_datos
        FROM users_rrhh
        WHERE id = %s
    """, (empleado_id,))
    empleado = cur.fetchone()
    cur.close()
    return empleado


def guardar_confirmacion_datos(empleado_id, correo, celular):
    """Actualiza el correo, celular y la fecha de confirmación del empleado.

    Args:
        empleado_id: ID interno del empleado en users_rrhh.
        correo: Nuevo correo electrónico.
        celular: Nuevo número de celular.

    Returns:
        bool: True si se actualizó correctamente.
    """
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE users_rrhh
        SET correo = %s, celular = %s, fecha_confirmacion_datos = NOW()
        WHERE id = %s
    """, (correo, celular, empleado_id))
    mysql.connection.commit()
    cur.close()
    return True


def necesita_confirmacion_datos(fecha_confirmacion):
    """Verifica si han pasado 3 meses desde la última confirmación.

    Args:
        fecha_confirmacion: Fecha de la última confirmación (datetime o None).

    Returns:
        bool: True si necesita confirmar (3+ meses o nunca confirmó).
    """
    if not fecha_confirmacion:
        return True  # Nunca confirmó
    from datetime import timedelta
    if isinstance(fecha_confirmacion, str):
        try:
            fecha_confirmacion = datetime.strptime(str(fecha_confirmacion).split('.')[0], '%Y-%m-%d %H:%M:%S')
        except:
            return True
    return (datetime.now() - fecha_confirmacion).days >= 90

