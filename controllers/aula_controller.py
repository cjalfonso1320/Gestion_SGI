from extension import mysql
import MySQLdb.cursors
import os
from datetime import datetime, timedelta
from utils.password_utils import hash_password
from utils.email_utils import enviar_notificacion_curso
from utils.whatsapp_utils import enviar_notificacion_curso_whatsapp

UPDLOAD_FOLDER = 'static/uploads/cursos'

def get_cursos_db():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # CURDATE() y no NOW(): fecha_limite es DATE, con NOW() un curso cuyo
    # límite es HOY se cerraba desde las 00:00 de ese día (el portal solo
    # muestra cursos 'Abierto' y el usuario no veía su curso asignado).
    cursor.execute("""
                UPDATE cursos 
                SET estado = 'Cerrado'
                WHERE fecha_limite < CURDATE() AND estado = 'Abierto'
                """)
    cursor.connection.commit()
    query = "SELECT * FROM cursos ORDER BY fecha_limite DESC"
    cursor.execute(query)
    cursos = cursor.fetchall()
    cursor.close()
    return cursos


def get_cursos_estudiante_db(identificacion):
    """Retorna solo los cursos asignados a un estudiante específico.

    Filtra los cursos según las asignaciones:
        - Asignación directa (curso_empleados)
        - Asignación por rol (curso_roles)
        - Cursos legacy que no tienen ninguna asignación (compatibilidad)

    Args:
        identificacion: Número de identificación del estudiante.

    Returns:
        list[dict]: Lista de cursos asignados al estudiante.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 1. Cerrar cursos vencidos (misma lógica que get_cursos_db)
    cursor.execute("""
        UPDATE cursos 
        SET estado = 'Cerrado'
        WHERE fecha_limite < CURDATE() AND estado = 'Abierto'
    """)
    cursor.connection.commit()

    # 2. Obtener id interno y rol del estudiante desde users_rrhh
    cursor.execute(
        "SELECT id, sgi_rol_id FROM users_rrhh WHERE identificacion = %s AND activo = 1",
        (identificacion,))
    estudiante_data = cursor.fetchone()

    if not estudiante_data:
        cursor.close()
        return []

    estudiante_id = estudiante_data['id']
    rol_id = estudiante_data['sgi_rol_id']

    # 3. Buscar cursos asignados: directa, por rol, o legacy sin asignaciones
    sql = """
        SELECT DISTINCT c.*
        FROM cursos c
        LEFT JOIN curso_empleados ce 
            ON c.id = ce.curso_id AND ce.empleado_id = %s
        LEFT JOIN curso_roles cr 
            ON c.id = cr.curso_id AND cr.rol_id = %s
        WHERE ce.empleado_id IS NOT NULL 
           OR cr.rol_id IS NOT NULL
           OR (
               -- Cursos legacy sin ninguna asignación (compatibilidad)
               NOT EXISTS (SELECT 1 FROM curso_empleados WHERE curso_id = c.id)
               AND NOT EXISTS (SELECT 1 FROM curso_roles WHERE curso_id = c.id)
           )
        ORDER BY c.fecha_limite DESC
    """
    cursor.execute(sql, (estudiante_id, rol_id if rol_id else 0))
    cursos = cursor.fetchall()

    # 4. Verificar prórrogas individuales activas para cada curso
    for c in cursos:
        cursor.execute("""
            SELECT id, nueva_fecha_limite, motivo, fecha_limite_anterior
            FROM curso_prorrogas
            WHERE curso_id = %s 
              AND identificacion = %s 
              AND activo = 1 
              AND nueva_fecha_limite >= CURDATE()
            ORDER BY nueva_fecha_limite DESC 
            LIMIT 1
        """, (c['id'], identificacion))
        prorroga = cursor.fetchone()
        if prorroga:
            c['tiene_prorroga'] = True
            c['fecha_prorroga'] = prorroga['nueva_fecha_limite'].strftime('%Y-%m-%d') if hasattr(prorroga['nueva_fecha_limite'], 'strftime') else str(prorroga['nueva_fecha_limite'])
            c['fecha_limite_original'] = c['fecha_limite']
            c['fecha_limite'] = prorroga['nueva_fecha_limite']
            c['motivo_prorroga'] = prorroga.get('motivo')
            # Si el curso estaba cerrado globalmente pero tiene prórroga vigente, para este estudiante está ABIERTO
            c['estado'] = 'Abierto'
        else:
            c['tiene_prorroga'] = False

    cursor.close()
    return cursos


def get_curso_db(curso_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM cursos WHERE id = %s", (curso_id,))
    curso = cursor.fetchone()
    cursor.close()
    return curso


def get_curso_asignaciones(curso_id):
    """Retorna los roles y personas ya asignados a un curso."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT rol_id FROM curso_roles WHERE curso_id = %s", (curso_id,))
    roles = [row['rol_id'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT empleado_id FROM curso_empleados WHERE curso_id = %s", (curso_id,))
    personas = [row['empleado_id'] for row in cursor.fetchall()]
    
    cursor.close()
    return {'roles': roles, 'personas': personas}


def crear_curso_db(nombre, descripcion, archivo, fecha_limite, creado_por, estado, enlace_video, dirigido_a=None, personas=None, roles=None):
    cursor = mysql.connection.cursor()

    try:
        cursor.execute(
            """INSERT INTO cursos (nombre, descripcion, archivo, enlace_video, fecha_limite, creado_por, estado, dirigido_a)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (nombre, descripcion, archivo, enlace_video, fecha_limite, creado_por, estado, dirigido_a))
        cursor.connection.commit()
        curso_id = cursor.lastrowid

        # Guardar asignaciones y recopilar correos y celulares para notificación
        destinatarios_correo = []
        destinatarios_whatsapp = []

        if dirigido_a == 'todos':
            # Asignar a TODOS los empleados activos
            print("📋 Asignando curso a TODOS los empleados activos")
            cursor.execute("SELECT id, correo, celular FROM users_rrhh WHERE activo = 1")
            todos_empleados = cursor.fetchall()
            for fila in todos_empleados:
                empleado_id = fila[0]
                cursor.execute("INSERT INTO curso_empleados (curso_id, empleado_id) VALUES (%s, %s)", (curso_id, empleado_id))
                if fila[1]:
                    destinatarios_correo.append(fila[1])
                if fila[2]:
                    destinatarios_whatsapp.append(fila[2])
            print(f"✅ Asignados {len(todos_empleados)} empleados a 'Todos'")

        elif dirigido_a == 'personas' and personas:
            print(f"📋 Asignando curso a {len(personas)} personas específicas")
            for empleado_id in personas:
                cursor.execute("INSERT INTO curso_empleados (curso_id, empleado_id) VALUES (%s, %s)", (curso_id, empleado_id))
                # Obtener correo y celular del empleado
                cursor.execute("SELECT correo, celular FROM users_rrhh WHERE id = %s", (empleado_id,))
                empleado = cursor.fetchone()
                if empleado:
                    if empleado[0]:
                        destinatarios_correo.append(empleado[0])
                        print(f"✅ Correo ID {empleado_id}: {empleado[0]}")
                    if empleado[1]:
                        destinatarios_whatsapp.append(empleado[1])
                        print(f"📱 WhatsApp ID {empleado_id}: {empleado[1]}")

        elif dirigido_a == 'roles' and roles:
            print(f"📋 Asignando curso a {len(roles)} roles")
            for rol_id in roles:
                cursor.execute("INSERT INTO curso_roles (curso_id, rol_id) VALUES (%s, %s)", (curso_id, rol_id))
                # Obtener correos y celulares de todos los empleados activos con este rol
                cursor.execute("SELECT correo, celular FROM users_rrhh WHERE sgi_rol_id = %s AND activo = 1", (rol_id,))
                empleados_rol = cursor.fetchall()
                print(f"👥 Rol ID {rol_id}: encontrados {len(empleados_rol)} empleados")
                for empleado in empleados_rol:
                    if empleado[0]:
                        destinatarios_correo.append(empleado[0])
                    if empleado[1]:
                        destinatarios_whatsapp.append(empleado[1])

        cursor.connection.commit()

        # ── Notificaciones (FUERA del try para no afectar el curso) ──
        email_enviado = False
        whatsapp_enviado = False
        cant_correos = 0
        cant_whatsapp = 0
        
        try:
            if destinatarios_correo:
                # Evita direcciones vacías, espacios accidentales y duplicados
                # por diferencias de mayúsculas/minúsculas.
                correos_normalizados = {}
                for correo in destinatarios_correo:
                    if correo and correo.strip():
                        limpio = correo.strip()
                        correos_normalizados.setdefault(limpio.casefold(), limpio)
                unicos_correo = list(correos_normalizados.values())
                cant_correos = len(unicos_correo)
                print(f"📧 Enviando notificación por correo a {cant_correos} destinatarios")
                email_enviado = enviar_notificacion_curso(nombre, descripcion, fecha_limite, unicos_correo)
            else:
                print("⚠️ No se encontraron correos válidos para notificar")

            if destinatarios_whatsapp:
                unicos_whatsapp = list(set(destinatarios_whatsapp))
                cant_whatsapp = len(unicos_whatsapp)
                print(f"💬 Enviando notificación por WhatsApp a {cant_whatsapp} números")
                whatsapp_enviado = enviar_notificacion_curso_whatsapp(nombre, fecha_limite, unicos_whatsapp)
            else:
                print("ℹ️ No se encontraron celulares válidos para WhatsApp")
        except Exception as e:
            print(f"⚠️ Error en notificaciones (el curso se creó igual): {e}")
            import traceback
            traceback.print_exc()

        return curso_id, email_enviado, whatsapp_enviado, cant_correos, cant_whatsapp
    except Exception as e:
        try:
            cursor.connection.rollback()
        except Exception:
            pass
        raise e
    finally:
        try:
            cursor.close()
        except Exception:
            pass


def editar_curso_db(curso_id, nombre, descripcion, archivo, fecha_limite, enlace_video, dirigido_a=None, personas=None, roles=None):
    cursor = mysql.connection.cursor()

    try:
        # Actualizar datos del curso
        # Al editar se recalcula el estado: si la nueva fecha límite aún no
        # venció, el curso vuelve a 'Abierto' (antes quedaba 'Cerrado' para
        # siempre y los estudiantes no lo veían en el portal aunque se les
        # hubiera notificado por correo).
        nuevo_estado = (
            "CASE WHEN fecha_limite IS NULL OR fecha_limite >= CURDATE() "
            "THEN 'Abierto' ELSE 'Cerrado' END"
        )
        if archivo:
            cursor.execute(
                f"""UPDATE cursos SET nombre=%s, descripcion=%s, archivo=%s, enlace_video=%s,
                    fecha_limite=%s, dirigido_a=%s, estado={nuevo_estado} WHERE id=%s""",
                (nombre, descripcion, archivo, enlace_video, fecha_limite, dirigido_a, curso_id))
        else:
            cursor.execute(
                f"""UPDATE cursos SET nombre=%s, descripcion=%s, enlace_video=%s,
                    fecha_limite=%s, dirigido_a=%s, estado={nuevo_estado} WHERE id=%s""",
                (nombre, descripcion, enlace_video, fecha_limite, dirigido_a, curso_id))

        # Reemplazar asignaciones: eliminar viejas e insertar nuevas
        cursor.execute("DELETE FROM curso_empleados WHERE curso_id = %s", (curso_id,))
        cursor.execute("DELETE FROM curso_roles WHERE curso_id = %s", (curso_id,))

        destinatarios_correo = []
        destinatarios_whatsapp = []

        if dirigido_a == 'todos':
            # Asignar a TODOS los empleados activos
            print("📋 (Editar) Asignando curso a TODOS los empleados activos")
            cursor.execute("SELECT id, correo, celular FROM users_rrhh WHERE activo = 1")
            todos_empleados = cursor.fetchall()
            for fila in todos_empleados:
                empleado_id = fila[0]
                cursor.execute("INSERT INTO curso_empleados (curso_id, empleado_id) VALUES (%s, %s)", (curso_id, empleado_id))
                if fila[1]:
                    destinatarios_correo.append(fila[1])
                if fila[2]:
                    destinatarios_whatsapp.append(fila[2])
            print(f"✅ (Editar) Asignados {len(todos_empleados)} empleados a 'Todos'")

        elif dirigido_a == 'personas' and personas:
            for empleado_id in personas:
                cursor.execute("INSERT INTO curso_empleados (curso_id, empleado_id) VALUES (%s, %s)", (curso_id, empleado_id))
                cursor.execute("SELECT correo, celular FROM users_rrhh WHERE id = %s", (empleado_id,))
                empleado = cursor.fetchone()
                if empleado:
                    if empleado[0]:
                        destinatarios_correo.append(empleado[0])
                    if empleado[1]:
                        destinatarios_whatsapp.append(empleado[1])

        elif dirigido_a == 'roles' and roles:
            for rol_id in roles:
                cursor.execute("INSERT INTO curso_roles (curso_id, rol_id) VALUES (%s, %s)", (curso_id, rol_id))
                cursor.execute("SELECT correo, celular FROM users_rrhh WHERE sgi_rol_id = %s AND activo = 1", (rol_id,))
                for empleado in cursor.fetchall():
                    if empleado[0]:
                        destinatarios_correo.append(empleado[0])
                    if empleado[1]:
                        destinatarios_whatsapp.append(empleado[1])

        cursor.connection.commit()

        # ── Notificaciones (FUERA del try para no afectar la edición) ──
        try:
            if destinatarios_correo:
                enviar_notificacion_curso(nombre, descripcion, fecha_limite, list(set(destinatarios_correo)))

            if destinatarios_whatsapp:
                enviar_notificacion_curso_whatsapp(nombre, fecha_limite, list(set(destinatarios_whatsapp)))
        except Exception as e:
            print(f"⚠️ Error en notificaciones (el curso se editó igual): {e}")
            import traceback
            traceback.print_exc()

        return True
    except Exception as e:
        try:
            cursor.connection.rollback()
        except Exception:
            pass
        raise e
    finally:
        try:
            cursor.close()
        except Exception:
            pass

def crear_evaluacion_db(curso_id, nombre, preguntas):
    cur = mysql.connection.cursor()
    total_preguntas = len(preguntas)
    titulo = f'Evaluacion de {nombre}'
    try:
        cur.execute(
            "INSERT INTO evaluaciones (curso_id, titulo, total_preguntas) VALUES (%s, %s, %s)", (curso_id, titulo, total_preguntas))
        evaluacion_id = cur.lastrowid
        
        for p in preguntas:
            cur.execute(
                """INSERT INTO preguntas (evaluacion_id, pregunta, tipo)
                VALUES (%s, %s, %s)""",
                (evaluacion_id, p['pregunta'], p['tipo']))
            pregunta_id = cur.lastrowid
            
            #opciones (solo multiple)
            if p['tipo'] == 'opcion_multiple':
                for opcion in p['opciones']:
                    es_correcta = 1 if opcion == p['respuesta'] else 0
                    cur.execute(
                        """INSERT INTO opciones (pregunta_id, texto, es_correcta)
                        VALUES (%s, %s, %s)""",
                        (pregunta_id, opcion, es_correcta))
            #respuesta
            cur.execute(
                """INSERT INTO respuestas (pregunta_id, respuesta)
                VALUES (%s, %s)""",
                (pregunta_id, p['respuesta']))
        cur.connection.commit()
    except Exception as e:
        cur.connection.rollback()
        raise e
    finally:
        cur.close()
        
def get_evaluacion_curso_db(curso_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    #evaluacion
    cursor.execute("SELECT id, titulo FROM evaluaciones WHERE curso_id = %s LIMIT 1", (curso_id,))
    evaluacion = cursor.fetchone()
    
    if not evaluacion:
        cursor.close()
        return None
    
    #preguntas
    cursor.execute("SELECT id, pregunta, tipo FROM preguntas WHERE evaluacion_id = %s", (evaluacion['id'],))
    preguntas = cursor.fetchall()
    
    for p in preguntas:
        #opciones
        cursor.execute("SELECT texto, es_correcta FROM opciones WHERE pregunta_id = %s", (p['id'],))
        p['opciones'] = cursor.fetchall()
        
        #respuesta
        cursor.execute("SELECT respuesta FROM respuestas WHERE pregunta_id = %s LIMIT 1", (p['id'],))
        r = cursor.fetchone()
        p['respuesta'] = r['respuesta'] if r else None
        
    evaluacion['preguntas'] = preguntas
    cursor.close()
    return evaluacion

#------------------------------------------------------
#----- VIDEOS DE CURSO: guardar ------------------------
#------------------------------------------------------
def guardar_video_curso(curso_id, nombre_original, ruta):
    """Guarda la referencia de un video subido para un curso."""
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO curso_videos (curso_id, nombre_original, ruta) VALUES (%s, %s, %s)",
            (curso_id, nombre_original, ruta)
        )
        cur.connection.commit()
        return cur.lastrowid
    except Exception as e:
        cur.connection.rollback()
        raise e
    finally:
        cur.close()


#------------------------------------------------------
#----- VIDEOS DE CURSO: obtener lista -----------------
#------------------------------------------------------
def get_videos_curso(curso_id):
    """Retorna todos los videos subidos para un curso."""
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute(
            "SELECT id, nombre_original, ruta, created_at FROM curso_videos WHERE curso_id = %s ORDER BY created_at ASC",
            (curso_id,)
        )
        videos = cur.fetchall()
        for v in videos:
            v['ruta'] = v['ruta'].replace('\\', '/')
        return videos
    finally:
        cur.close()


#------------------------------------------------------
#----- VIDEOS DE CURSO: eliminar por curso ------------
#------------------------------------------------------
def eliminar_videos_curso(curso_id):
    """Elimina las referencias de videos de un curso (no los archivos)."""
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM curso_videos WHERE curso_id = %s", (curso_id,))
        cur.connection.commit()
    except Exception as e:
        cur.connection.rollback()
        raise e
    finally:
        cur.close()


def eliminar_curso_db(curso_id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT archivo FROM cursos WHERE id = %s", (curso_id,))
        curso = cursor.fetchone()
        ruta_archivo = None
        if curso and curso[0]:
            ruta_archivo = os.path.join(os.getcwd(), 'static', curso[0])

        # Eliminar asignaciones relacionadas
        cursor.execute("DELETE FROM curso_videos WHERE curso_id = %s", (curso_id,))
        cursor.execute("DELETE FROM curso_empleados WHERE curso_id = %s", (curso_id,))
        cursor.execute("DELETE FROM curso_roles WHERE curso_id = %s", (curso_id,))

        # Eliminar evaluación asociada y sus dependencias
        cursor.execute("SELECT id FROM evaluaciones WHERE curso_id = %s", (curso_id,))
        evaluaciones = cursor.fetchall()
        evaluacion_ids = [row[0] for row in evaluaciones] if evaluaciones else []
        if evaluacion_ids:
            cursor.execute(
                "DELETE FROM intentos_evaluacion WHERE evaluacion_id IN (%s)" % \
                ",".join(["%s"] * len(evaluacion_ids)), evaluacion_ids)
            cursor.execute(
                "DELETE FROM respuestas WHERE pregunta_id IN (SELECT id FROM preguntas WHERE evaluacion_id IN (%s))" % \
                ",".join(["%s"] * len(evaluacion_ids)), evaluacion_ids)
            cursor.execute(
                "DELETE FROM opciones WHERE pregunta_id IN (SELECT id FROM preguntas WHERE evaluacion_id IN (%s))" % \
                ",".join(["%s"] * len(evaluacion_ids)), evaluacion_ids)
            cursor.execute(
                "DELETE FROM preguntas WHERE evaluacion_id IN (%s)" % \
                ",".join(["%s"] * len(evaluacion_ids)), evaluacion_ids)
            cursor.execute("DELETE FROM evaluaciones WHERE id IN (%s)" % \
                ",".join(["%s"] * len(evaluacion_ids)), evaluacion_ids)

        cursor.execute("DELETE FROM cursos WHERE id = %s", (curso_id,))
        cursor.connection.commit()

        if ruta_archivo and os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except OSError:
                pass
    except Exception as e:
        cursor.connection.rollback()
        raise e
    finally:
        cursor.close()
        
def verificar_intentos_evaluacion(evaluacion_id, estudiante_id):
    """Verifica si el estudiante puede presentar la evaluación y cuántos intentos le quedan.

    Reglas:
        - Si ya aprobó (nota >= 70) → no puede volver a presentar
        - Máximo 3 intentos en total
        - Si ha fallado y tiene intentos restantes → puede volver a presentar

    Returns:
        dict: {
            'puede_presentar': bool,
            'mensaje': str or None,
            'intentos_realizados': int,
            'intentos_restantes': int,
            'max_intentos': int
        }
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 1. Verificar si ya aprobó (nota >= 70)
    cursor.execute(
        """SELECT id FROM intentos_evaluacion
           WHERE evaluacion_id = %s AND estudiante_id = %s AND nota >= 70""",
        (evaluacion_id, estudiante_id))
    aprobado = cursor.fetchone()

    if aprobado:
        cursor.close()
        return {
            'puede_presentar': False,
            'mensaje': 'Ya has aprobado esta evaluación. No puedes presentarla nuevamente.',
            'intentos_realizados': 0,
            'intentos_restantes': 0,
            'max_intentos': 3
        }

    # 2. Contar intentos totales
    cursor.execute(
        """SELECT COUNT(*) AS total FROM intentos_evaluacion
           WHERE evaluacion_id = %s AND estudiante_id = %s""",
        (evaluacion_id, estudiante_id))
    count = cursor.fetchone()['total']
    cursor.close()

    max_intentos = 3
    intentos_restantes = max_intentos - count

    if count >= max_intentos:
        return {
            'puede_presentar': False,
            'mensaje': f'Has agotado tus {max_intentos} intentos para esta evaluación.',
            'intentos_realizados': count,
            'intentos_restantes': 0,
            'max_intentos': max_intentos
        }

    return {
        'puede_presentar': True,
        'mensaje': None,
        'intentos_realizados': count,
        'intentos_restantes': intentos_restantes,
        'max_intentos': max_intentos
    }


def ya_presento_evaluacion(evaluacion_id, estudiaten_id):
    """(Deprecated) Usar verificar_intentos_evaluacion() en su lugar."""
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT id FROM intentos_evaluacion WHERE evaluacion_id = %s AND estudiante_id = %s", (evaluacion_id, estudiaten_id))
    existe = cursor.fetchone()
    cursor.close()
    return existe is not None

def guardar_intento_respuestas(evaluacion, form, estudiante):
    cursor = mysql.connection.cursor()
    try:
        # Hora local de Colombia (UTC-5)
        ahora_colombia = datetime.utcnow() - timedelta(hours=5)

        #crea intento
        cursor.execute("""
                       INSERT INTO intentos_evaluacion (
                           evaluacion_id, estudiante_id, nombre_estudiante, ciudad, cargo, proceso, estado, fecha_presentacion
                       ) VALUES (
                           %s, %s, %s, %s, %s, %s, %s, %s
                       )
                       """, (
                           evaluacion['id'],
                           estudiante['identificacion'],
                           estudiante['nombre'],
                           estudiante['ciudad'],
                           estudiante['cargo'],
                           estudiante['proceso'],
                           'Pendiente',
                           ahora_colombia
                       ))
        intento_id = cursor.lastrowid
        
        total_auto = 0
        correctas = 0
        tiene_texto = False
        
        #recorre preguntas
        for p in evaluacion['preguntas']:
            pid = p['id']
            
            respuesta_usuario = form.get(f'pregunta_{pid}')
            es_correcta = None
            
            #opcion multiple
            if p['tipo'] == 'opcion_multiple':
                total_auto += 1
                es_correcta = 1 if respuesta_usuario == p['respuesta'] else 0
                if es_correcta:
                    correctas += 1
                    
            #verdadero/falso
            elif p['tipo'] == 'vf':
                total_auto += 1
                es_correcta = 1 if respuesta_usuario == p['respuesta'] else 0
                if es_correcta:
                    correctas += 1
                    
            #texto (se guarda, no se califica automatico )
            elif p['tipo'] == 'texto':
                tiene_texto = True
                es_correcta = None
                              
            #guarda respuestas
            cursor.execute("""
                           INSERT INTO respuestas_estudiante (
                               intento_id, pregunta_id, respuesta_texto, es_correcta
                           ) VALUES (
                               %s, %s, %s, %s
                           )
                           """, (
                               intento_id,
                               pid, 
                               respuesta_usuario,
                               es_correcta
                           ))
        #calcula nota
        nota = round((correctas / total_auto) * 100, 2) if total_auto > 0 else 0
        estado = 'Pendiente' if tiene_texto else 'Calificado'
        
        #actualiza nota
        cursor.execute("""
                       UPDATE intentos_evaluacion
                       SET nota = %s, estado = %s
                       WHERE id = %s
                       """, (nota, estado, intento_id))
        cursor.connection.commit()
        
        return {
            'nota': nota,
            'estado': estado,
            'intento_id': intento_id,
            'aprobado': nota >= 70 and estado == 'Calificado',
            'tiene_texto': tiene_texto
        }
    except Exception as e:
        cursor.connection.rollback()
        # Verificar si es error de llave duplicada (UNIQUE constraint)
        if hasattr(e, 'args') and len(e.args) > 0 and '1062' in str(e.args[0]):
            raise Exception(
                'Error de base de datos: La tabla intentos_evaluacion tiene una restricción UNIQUE '
                'que impide múltiples intentos. Ejecuta el script sql/eliminar_unique_intentos.sql '
                'en tu base de datos para solucionarlo.'
            )
        raise e
    finally:
        cursor.close()
        
        
def obtener_asignados_curso(cursor, curso_id, dirigido_a):
    """Retorna la lista de empleados activos asignados a un curso (población objetivo)."""
    if dirigido_a == 'todos':
        sql = """
            SELECT u.id, u.identificacion, CONCAT(u.nombres, ' ', u.apellidos) AS nombre_completo,
                   cg.nombre AS cargo, ci.nombre AS ciudad, gn.nombre AS proceso,
                   u.correo, u.celular, u.foto_path
            FROM users_rrhh u
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
            LEFT JOIN ciudades ci ON u.barrio = ci.id
            LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id
            WHERE u.activo = 1
            ORDER BY u.nombres
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
    elif dirigido_a == 'roles':
        sql = """
            SELECT u.id, u.identificacion, CONCAT(u.nombres, ' ', u.apellidos) AS nombre_completo,
                   cg.nombre AS cargo, ci.nombre AS ciudad, gn.nombre AS proceso,
                   u.correo, u.celular, u.foto_path
            FROM users_rrhh u
            INNER JOIN curso_roles cr ON u.sgi_rol_id = cr.rol_id
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
            LEFT JOIN ciudades ci ON u.barrio = ci.id
            LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id
            WHERE cr.curso_id = %s AND u.activo = 1
            ORDER BY u.nombres
        """
        cursor.execute(sql, (curso_id,))
        rows = cursor.fetchall()
    elif dirigido_a == 'personas':
        sql = """
            SELECT DISTINCT u.id, u.identificacion, CONCAT(u.nombres, ' ', u.apellidos) AS nombre_completo,
                   cg.nombre AS cargo, ci.nombre AS ciudad, gn.nombre AS proceso,
                   u.correo, u.celular, u.foto_path
            FROM users_rrhh u
            LEFT JOIN curso_empleados ce ON u.id = ce.empleado_id AND ce.curso_id = %s
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
            LEFT JOIN ciudades ci ON u.barrio = ci.id
            LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id
            WHERE (ce.id IS NOT NULL OR u.identificacion IN (
                SELECT DISTINCT ie.estudiante_id FROM intentos_evaluacion ie
                INNER JOIN evaluaciones e ON ie.evaluacion_id = e.id
                WHERE e.curso_id = %s
            )) AND u.activo = 1
            ORDER BY u.nombres
        """
        cursor.execute(sql, (curso_id, curso_id))
        rows = cursor.fetchall()
    else:
        sql = """
            SELECT u.id, u.identificacion, CONCAT(u.nombres, ' ', u.apellidos) AS nombre_completo,
                   cg.nombre AS cargo, ci.nombre AS ciudad, gn.nombre AS proceso,
                   u.correo, u.celular, u.foto_path
            FROM users_rrhh u
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
            LEFT JOIN ciudades ci ON u.barrio = ci.id
            LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id
            WHERE u.activo = 1
            ORDER BY u.nombres
        """
        cursor.execute(sql)
        rows = cursor.fetchall()

    for r in rows:
        if r.get('foto_path'):
            r['foto_path'] = r['foto_path'].replace('\\', '/')
    return rows


def get_resultados_cursos_db():
    """Retorna los resultados de las evaluaciones estructurados por curso con estadísticas de asignación."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT DISTINCT
            c.id AS curso_id,
            c.nombre AS curso_nombre,
            c.fecha_limite,
            c.dirigido_a
        FROM cursos c
        INNER JOIN evaluaciones e ON e.curso_id = c.id
        INNER JOIN intentos_evaluacion ie ON ie.evaluacion_id = e.id
        ORDER BY c.nombre
    """)
    cursos = cursor.fetchall()

    resultados = []
    for c in cursos:
        curso_id = c['curso_id']
        dirigido_a = c.get('dirigido_a')

        asignados = obtener_asignados_curso(cursor, curso_id, dirigido_a)
        total_asignados = len(asignados)

        cursor.execute("""
            SELECT
                c.nombre AS curso,
                ie.id AS intento_id,
                ie.estudiante_id,
                ie.nombre_estudiante,
                ie.cargo,
                ie.ciudad,
                ie.proceso,
                ie.nota,
                ie.fecha_presentacion,
                ie.estado,
                u.foto_path
            FROM intentos_evaluacion ie
            INNER JOIN evaluaciones e ON ie.evaluacion_id = e.id
            INNER JOIN cursos c ON e.curso_id = c.id
            LEFT JOIN users_rrhh u ON ie.estudiante_id = u.identificacion
            WHERE e.curso_id = %s
            ORDER BY ie.fecha_presentacion DESC
        """, (curso_id,))
        intentos = cursor.fetchall()
        for d in intentos:
            if d.get('foto_path'):
                d['foto_path'] = d['foto_path'].replace('\\', '/')
            if d.get('fecha_presentacion'):
                d['fecha_presentacion'] = d['fecha_presentacion'].strftime('%Y-%m-%d %H:%M') if hasattr(d['fecha_presentacion'], 'strftime') else str(d['fecha_presentacion'])

        evaluados_ids = {str(d['estudiante_id']) for d in intentos}
        total_evaluados = len(evaluados_ids)
        total_asignados_real = total_asignados if total_asignados >= total_evaluados else total_evaluados

        no_presentaron = [a for a in asignados if str(a['identificacion']) not in evaluados_ids]
        total_no_presentaron = len(no_presentaron)

        # Consultar prórrogas activas para empleados sin presentar
        cursor.execute("""
            SELECT identificacion, nueva_fecha_limite, motivo
            FROM curso_prorrogas
            WHERE curso_id = %s AND activo = 1 AND nueva_fecha_limite >= CURDATE()
            ORDER BY nueva_fecha_limite DESC
        """, (curso_id,))
        prorrogas_map = {str(p['identificacion']): p for p in cursor.fetchall()}

        for a in no_presentaron:
            ident_str = str(a['identificacion'])
            if ident_str in prorrogas_map:
                pr = prorrogas_map[ident_str]
                a['prorroga'] = {
                    'nueva_fecha_limite': pr['nueva_fecha_limite'].strftime('%Y-%m-%d') if hasattr(pr['nueva_fecha_limite'], 'strftime') else str(pr['nueva_fecha_limite']),
                    'motivo': pr.get('motivo')
                }
            else:
                a['prorroga'] = None

        cursor.execute("""
            SELECT ie.estudiante_id, ie.nota, ie.estado
            FROM intentos_evaluacion ie
            INNER JOIN evaluaciones e ON ie.evaluacion_id = e.id
            INNER JOIN (
                SELECT MAX(ie2.id) AS max_id
                FROM intentos_evaluacion ie2
                INNER JOIN evaluaciones e2 ON ie2.evaluacion_id = e2.id
                WHERE e2.curso_id = %s
                GROUP BY ie2.estudiante_id
            ) latest ON ie.id = latest.max_id
            WHERE e.curso_id = %s
        """, (curso_id, curso_id))
        ultimos = cursor.fetchall()

        aprobados = sum(1 for u in ultimos if u['nota'] is not None and u['nota'] >= 70)
        reprobados = sum(1 for u in ultimos if u['nota'] is not None and u['nota'] < 70)
        pendientes = sum(1 for u in ultimos if u['nota'] is None or u['estado'] == 'Pendiente')

        pct_cumplimiento = round((aprobados / total_evaluados * 100), 1) if total_evaluados > 0 else 0
        pct_aprobados_eval = round((aprobados / total_evaluados * 100), 1) if total_evaluados > 0 else 0

        fecha_lim_str = c.get('fecha_limite').strftime('%Y-%m-%d') if hasattr(c.get('fecha_limite'), 'strftime') else str(c.get('fecha_limite') or '')
        resultados.append({
            'curso_id': curso_id,
            'curso_nombre': c['curso_nombre'],
            'fecha_limite': fecha_lim_str,
            'dirigido_a': dirigido_a,
            'total_asignados': total_asignados_real,
            'total_evaluados': total_evaluados,
            'total_no_presentaron': total_no_presentaron,
            'total_aprobados': aprobados,
            'total_reprobados': reprobados,
            'total_pendientes': pendientes,
            'porcentaje_cumplimiento': pct_cumplimiento,
            'porcentaje_aprobados': pct_aprobados_eval,
            'intentos': intentos,
            'no_presentaron': no_presentaron
        })

    cursor.close()
    return resultados

def get_intento_validar(intento_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
                   SELECT ie.id, ie.nombre_estudiante, ie.nota, u.foto_path
                   FROM intentos_evaluacion ie
                   LEFT JOIN users_rrhh u ON ie.estudiante_id = u.identificacion
                   WHERE ie.id = %s
                   """, (intento_id,))
    intento = cursor.fetchone()
    if not intento:
        cursor.close()
        return None
    if intento.get('foto_path'):
        intento['foto_path'] = intento['foto_path'].replace('\\', '/')
    cursor.execute("""
                   SELECT
                        re.id AS respuesta_id,
                        p.id AS pregunta_id,
                        p.pregunta,
                        p.tipo,
                        re.respuesta_texto,
                        re.es_correcta,
                        re.puntaje
                    FROM respuestas_estudiante re
                    INNER JOIN preguntas p ON re.pregunta_id = p.id
                    WHERE re.intento_id = %s
                   """, (intento_id,))
    intento['respuestas'] = cursor.fetchall()

    # Determinar la letra (A, B, C, D) para preguntas de opción múltiple
    letras = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    for r in intento['respuestas']:
        r['letra_opcion'] = None
        if r['tipo'] == 'opcion_multiple':
            cursor.execute(
                "SELECT texto FROM opciones WHERE pregunta_id = %s ORDER BY id",
                (r['pregunta_id'],))
            opciones = [row['texto'] for row in cursor.fetchall()]
            for idx, opcion in enumerate(opciones):
                if opcion == r['respuesta_texto']:
                    if idx < len(letras):
                        r['letra_opcion'] = letras[idx]
                    break

    cursor.close()
    return intento

def validar_respuestas_texto(intento_id, form):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        for key in form:
            #busca solo respuestas de texto
            if key.startswith('correcta_'):
                respuesta_id = key.replace('correcta_', '')
                es_correcta = int(form.get(key))
                
                cursor.execute("""
                               UPDATE respuestas_estudiante
                               SET es_correcta = %s
                                WHERE id = %s
                                    AND intento_id = %s
                               """, (
                                   es_correcta,
                                   respuesta_id,
                                   intento_id))
        cursor.connection.commit()
    except Exception as e:
        cursor.connection.rollback()
        raise e
    finally:
        cursor.close()
    
def recalcular_nota_final(intento_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        #preguntas auto
        cursor.execute("""
                       SELECT COUNT(*) AS total
                       FROM respuestas_estudiante
                       WHERE intento_id = %s
                       """, (intento_id,))
        total = cursor.fetchone()['total']
        
        cursor.execute("""
                       SELECT COUNT(*) AS correctas
                       FROM respuestas_estudiante
                       WHERE intento_id = %s AND es_correcta = 1
                       """, (intento_id,))
        correctas = cursor.fetchone()['correctas']
        
        #calculo final
        nota = round((correctas / total) * 100, 2) if total > 0 else 0
        #actualiza intento
        cursor.execute("""
                       UPDATE intentos_evaluacion
                       SET nota = %s,
                            estado = 'Calificado'
                        WHERE id = %s
                       """, (nota, intento_id))
        cursor.connection.commit()
    except Exception as e:
        cursor.connection.rollback()
        raise e
    finally:
        cursor.close()

def busca_estudiante(identificacion):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
            SELECT u.identificacion,
                u.nombres,
                u.apellidos,
                cg.nombre AS cargo,
                ci.nombre AS ciudad,
                gn.nombre AS proceso,
                u.primer_ingreso,
                u.password,
                u.foto_path
            FROM users_rrhh u
            LEFT JOIN cargos cg ON u.cargo_id = cg.id
            LEFT JOIN ciudades ci ON u.barrio = ci.id
            LEFT JOIN grupo_nomina gn ON u.grupo_nomina_id = gn.id
            WHERE u.identificacion = %s AND u.activo = 1
        """
    cur.execute(sql, (identificacion,))
    estudiante = cur.fetchone()
    cur.close()
    return estudiante

def resultados_estudiante(identificacion):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
            SELECT
                c.id,
                c.nombre AS curso,
                ie.nota,
                ie.fecha_presentacion,
                ie.estado,
                ie.id as intento_id
            FROM intentos_evaluacion ie
            INNER JOIN evaluaciones e ON ie.evaluacion_id = e.id
            INNER JOIN cursos c ON e.curso_id = c.id
            WHERE ie.estudiante_id = %s
            ORDER BY e.curso_id, ie.fecha_presentacion ASC
        """
    cur.execute(sql, (identificacion,))
    resultados = list(cur.fetchall())
    cur.close()

    # Calcular número de intento por curso (usando c.id que viene como 'id')
    conteos = {}
    for r in resultados:
        curso_id = r['id']
        conteos[curso_id] = conteos.get(curso_id, 0) + 1
        r['intento_num'] = conteos[curso_id]

    # Reordenar por fecha descendente (más reciente primero)
    resultados.sort(key=lambda x: (x.get('fecha_presentacion') or ''), reverse=True)

    return resultados

def curso_aprobado(identificacion, curso_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
            SELECT ie.id
            FROM intentos_evaluacion ie
            INNER JOIN evaluaciones e ON ie.evaluacion_id = e.id
            WHERE ie.estudiante_id = %s AND e.curso_id = %s AND ie.nota >= 70
        """
    cur.execute(sql, (identificacion, curso_id))
    resultado = cur.fetchone()
    cur.close()
    return resultado is not None


#------------------------------------------------------
#----- TABULACIÓN: datos agrupados por curso -----------
#------------------------------------------------------
def get_tabulacion_db():
    """Retorna datos de tabulación: cursos con sus estudiantes, respuestas y estadísticas detalladas de asignación y cumplimiento."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Obtener todos los cursos que tienen evaluaciones con intentos
    sql_cursos = """
        SELECT DISTINCT
            c.id AS curso_id,
            c.nombre AS curso_nombre,
            c.fecha_limite,
            c.dirigido_a
        FROM cursos c
        INNER JOIN evaluaciones e ON e.curso_id = c.id
        INNER JOIN intentos_evaluacion ie ON ie.evaluacion_id = e.id
        ORDER BY c.nombre
    """
    cursor.execute(sql_cursos)
    cursos = cursor.fetchall()

    for curso in cursos:
        curso_id = curso['curso_id']
        dirigido_a = curso.get('dirigido_a')

        # 1. Obtener empleados asignados (población objetivo)
        asignados = obtener_asignados_curso(cursor, curso_id, dirigido_a)
        total_asignados = len(asignados)

        # 2. Obtener preguntas del curso para mostrar encabezados
        sql_preguntas = """
            SELECT p.id, p.pregunta, p.tipo
            FROM preguntas p
            INNER JOIN evaluaciones e ON p.evaluacion_id = e.id
            WHERE e.curso_id = %s
            ORDER BY p.id
        """
        cursor.execute(sql_preguntas, (curso_id,))
        curso['preguntas'] = cursor.fetchall()

        # 3. Obtener SOLO el último intento por estudiante
        sql_estudiantes = """
            SELECT
                ie.id AS intento_id,
                ie.estudiante_id,
                ie.nombre_estudiante,
                ie.cargo,
                ie.ciudad,
                ie.proceso,
                ie.nota,
                ie.fecha_presentacion,
                ie.estado,
                (
                    SELECT COUNT(*) > 0
                    FROM intentos_evaluacion ie3
                    INNER JOIN evaluaciones e3 ON ie3.evaluacion_id = e3.id
                    WHERE e3.curso_id = %s
                      AND ie3.estudiante_id = ie.estudiante_id
                      AND ie3.id < ie.id
                      AND ie3.nota >= 70
                ) AS aprobo_en_anterior
            FROM intentos_evaluacion ie
            INNER JOIN evaluaciones e ON ie.evaluacion_id = e.id
            INNER JOIN (
                SELECT MAX(ie2.id) AS max_id
                FROM intentos_evaluacion ie2
                INNER JOIN evaluaciones e2 ON ie2.evaluacion_id = e2.id
                WHERE e2.curso_id = %s
                GROUP BY ie2.estudiante_id
            ) latest ON ie.id = latest.max_id
            ORDER BY ie.nombre_estudiante
        """
        cursor.execute(sql_estudiantes, (curso_id, curso_id))
        estudiantes = cursor.fetchall()

        evaluados_ids = set()
        for est in estudiantes:
            evaluados_ids.add(str(est['estudiante_id']))
            # Para cada estudiante, obtener sus respuestas
            sql_respuestas = """
                SELECT
                    re.pregunta_id,
                    p.pregunta,
                    p.tipo,
                    re.respuesta_texto,
                    re.es_correcta,
                    rp.respuesta AS respuesta_correcta
                FROM respuestas_estudiante re
                INNER JOIN preguntas p ON re.pregunta_id = p.id
                LEFT JOIN respuestas rp ON rp.pregunta_id = p.id
                WHERE re.intento_id = %s
                ORDER BY re.pregunta_id
            """
            cursor.execute(sql_respuestas, (est['intento_id'],))
            est['respuestas'] = cursor.fetchall()

            # Formatear fecha
            if est.get('fecha_presentacion'):
                est['fecha_presentacion'] = est['fecha_presentacion'].strftime('%Y-%m-%d %H:%M') if hasattr(est['fecha_presentacion'], 'strftime') else str(est['fecha_presentacion'])

        curso['estudiantes'] = estudiantes

        # 4. Empleados asignados que NO presentaron la evaluación
        no_presentaron = [a for a in asignados if str(a['identificacion']) not in evaluados_ids]

        # Consultar prórrogas activas para empleados sin presentar
        cursor.execute("""
            SELECT identificacion, nueva_fecha_limite, motivo
            FROM curso_prorrogas
            WHERE curso_id = %s AND activo = 1 AND nueva_fecha_limite >= CURDATE()
            ORDER BY nueva_fecha_limite DESC
        """, (curso_id,))
        prorrogas_map = {str(p['identificacion']): p for p in cursor.fetchall()}

        for a in no_presentaron:
            ident_str = str(a['identificacion'])
            if ident_str in prorrogas_map:
                pr = prorrogas_map[ident_str]
                a['prorroga'] = {
                    'nueva_fecha_limite': pr['nueva_fecha_limite'].strftime('%Y-%m-%d') if hasattr(pr['nueva_fecha_limite'], 'strftime') else str(pr['nueva_fecha_limite']),
                    'motivo': pr.get('motivo')
                }
            else:
                a['prorroga'] = None

        curso['estudiantes_no_presentaron'] = no_presentaron
        curso['total_no_presentaron'] = len(no_presentaron)
        curso['fecha_limite'] = curso.get('fecha_limite').strftime('%Y-%m-%d') if hasattr(curso.get('fecha_limite'), 'strftime') else str(curso.get('fecha_limite') or '')

               #5. calcula estadisticas precisas (modificado -solo muestra los aprobados)
        total_intentos = len(estudiantes)

        aprobados = sum(1 for e in estudiantes if e['nota'] is not None and e['nota'] >= 70)
        reprobados = sum(1 for e in estudiantes if e['nota'] is not None and e['nota'] < 70)
        pendientes = sum(1 for e in estudiantes if e['nota'] is None or e['estado'] == 'Pendiente')

        #evaluados = intentos con nota; los pendientes no entran en este porcentaje
        total_evaluados  = aprobados + reprobados

        total_asignados_real = max(total_asignados, total_intentos)
        curso['total_asignados'] = total_asignados_real
        curso['total_estudiantes'] = total_intentos
        curso['total_evaluados'] = total_evaluados

        curso['total_aprobados'] = aprobados
        curso['total_reprobados'] = reprobados
        curso['total_pendientes'] = pendientes

        #aprobacion y reprobacion sobre quines ya tiene resultado
        curso['porcentaje_aprobados'] = (round((aprobados / total_evaluados * 100), 1) if total_evaluados else 0)
        curso['porcentaje_reprobados'] = (round((reprobados / total_evaluados * 100), 1) if total_evaluados else 0)

        #cumplimiento global sobre la poblacion asignada
        curso['porcentaje_cumplimiento'] = (round((aprobados / total_asignados_real * 100), 1) if total_asignados_real else 0)
        curso['porcentaje_no_presentaron'] = (round(curso['total_no_presentaron'] / total_asignados_real * 100, 1) if total_asignados_real else 0)

    cursor.close()
    return cursos


def actualiza_password(identificacion, nueva_pass):
    """Actualiza la contraseña en la BD y marca primer_ingreso = 0."""
    try:
        password_hash = hash_password(nueva_pass)
        print(f"[DEBUG actualiza_password] identificacion='{identificacion}' nueva_pass_len={len(nueva_pass)} hash_len={len(password_hash)}")
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "UPDATE users_rrhh SET password = %s, primer_ingreso = %s WHERE identificacion = %s"
        rows = cur.execute(sql, (password_hash, 0, identificacion))
        mysql.connection.commit()
        cur.close()
        if rows == 0:
            print(f"[DEBUG actualiza_password] ⚠️ ¡ADVERTENCIA! UPDATE afectó 0 filas. identificacion='{identificacion}' NO existe en users_rrhh")
        else:
            print(f"[DEBUG actualiza_password] ✅ UPDATE afectó {rows} fila(s). Hash almacenado (primeros 50): {password_hash[:50]}...")
        return True
    except Exception as e:
        print(f"[DEBUG actualiza_password] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    


#------------------------------------------------------
#----- GESTIÓN DE PRÓRROGAS INDIVIDUALES --------------
#------------------------------------------------------
def guardar_prorroga_individual(curso_id, identificacion, nueva_fecha_limite, motivo=None, otorgado_por=None, notificar=True):
    """Otorga o actualiza una prórroga individual a un empleado para un curso específico.
    
    Inserta el registro en curso_prorrogas y opcionalmente notifica al colaborador
    por correo y WhatsApp.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # 1. Obtener datos del empleado
        cursor.execute("SELECT id, nombres, apellidos, correo, celular FROM users_rrhh WHERE identificacion = %s AND activo = 1", (identificacion,))
        empleado = cursor.fetchone()
        if not empleado:
            return {'success': False, 'error': f'Empleado con identificación {identificacion} no encontrado o inactivo.'}

        # 2. Obtener datos del curso
        cursor.execute("SELECT id, nombre, descripcion, fecha_limite FROM cursos WHERE id = %s", (curso_id,))
        curso = cursor.fetchone()
        if not curso:
            return {'success': False, 'error': f'Curso {curso_id} no encontrado.'}

        fecha_limite_anterior = curso.get('fecha_limite')

        # 3. Desactivar prórrogas anteriores activas para este curso y empleado
        cursor.execute("""
            UPDATE curso_prorrogas 
            SET activo = 0 
            WHERE curso_id = %s AND identificacion = %s AND activo = 1
        """, (curso_id, identificacion))

        # 4. Insertar la nueva prórroga
        cursor.execute("""
            INSERT INTO curso_prorrogas (
                curso_id, empleado_id, identificacion, fecha_limite_anterior,
                nueva_fecha_limite, motivo, otorgado_por, activo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            curso_id,
            empleado['id'],
            identificacion,
            fecha_limite_anterior,
            nueva_fecha_limite,
            motivo,
            otorgado_por
        ))
        cursor.connection.commit()

        # 5. Notificaciones (opcional)
        notif_email = False
        notif_ws = False
        nombre_completo = f"{empleado.get('nombres', '')} {empleado.get('apellidos', '')}".strip()
        fecha_str = nueva_fecha_limite.strftime('%Y-%m-%d') if hasattr(nueva_fecha_limite, 'strftime') else str(nueva_fecha_limite)
        
        if notificar:
            if empleado.get('correo'):
                try:
                    from utils.email_utils import enviar_notificacion_prorroga
                    notif_email = enviar_notificacion_prorroga(
                        nombre_completo,
                        curso['nombre'],
                        fecha_str,
                        motivo or 'Plazo adicional autorizado por Administración/RRHH',
                        empleado['correo']
                    )
                except Exception as e:
                    print(f"⚠️ Error al enviar correo de prórroga: {e}")

            if empleado.get('celular'):
                try:
                    from utils.whatsapp_utils import enviar_notificacion_prorroga_whatsapp
                    notif_ws = enviar_notificacion_prorroga_whatsapp(
                        nombre_completo,
                        curso['nombre'],
                        fecha_str,
                        empleado['celular']
                    )
                except Exception as e:
                    print(f"⚠️ Error al enviar WhatsApp de prórroga: {e}")

        return {
            'success': True,
            'message': f'Prórroga concedida con éxito a {nombre_completo} hasta el {fecha_str}.',
            'notif_email': notif_email,
            'notif_ws': notif_ws
        }
    except Exception as e:
        cursor.connection.rollback()
        print(f"❌ Error al guardar prórroga: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        cursor.close()


def obtener_prorroga_activa(curso_id, identificacion):
    """Retorna la prórroga activa para un estudiante en un curso si existe y no ha vencido."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT id, nueva_fecha_limite, motivo, fecha_limite_anterior
        FROM curso_prorrogas
        WHERE curso_id = %s 
          AND identificacion = %s 
          AND activo = 1 
          AND nueva_fecha_limite >= CURDATE()
        ORDER BY nueva_fecha_limite DESC 
        LIMIT 1
    """, (curso_id, identificacion))
    prorroga = cursor.fetchone()
    cursor.close()
    return prorroga
