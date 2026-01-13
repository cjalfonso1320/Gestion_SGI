from extension import mysql
import MySQLdb.cursors
import os

UPDLOAD_FOLDER = 'static/uploads/cursos'

def get_cursos_db():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
                UPDATE cursos 
                SET estado = 'Cerrado'
                WHERE fecha_limite < NOW() AND estado = 'Abierto'
                """)
    cursor.connection.commit()
    query = "SELECT * FROM cursos"
    cursor.execute(query)
    cursos = cursor.fetchall()
    cursor.close()
    return cursos


def crear_curso_db(nombre, descripcion, archivo, fecha_limite, creado_por, estado):
    cursor = mysql.connection.cursor()
    
    cursor.execute(
        """INSERT INTO cursos (nombre, descripcion, archivo, fecha_limite, creado_por, estado)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (nombre, descripcion, archivo, fecha_limite, creado_por, estado))
    cursor.connection.commit()
    curso_id = cursor.lastrowid
    cursor.close()
    return curso_id

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

def eliminar_curso_db(curso_id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT archivo FROM cursos WHERE id = %s", (curso_id,))
        curso = cursor.fetchone()
        ruta_archivo = None
        if curso and curso[0]:
            ruta_archivo = os.path.join(os.getcwd(), 'static', curso[0])
        cursor.execute("DELETE FROM cursos WHERE id = %s", (curso_id,))
        cursor.connection.commit()
        if ruta_archivo and os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
    except Exception as e:
        cursor.connection.rollback()
        raise e
    finally:
        cursor.close()
        
def ya_presento_evaluacion(evaluacion_id, estudiaten_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT id FROM intentos_evaluacion WHERE evaluacion_id = %s AND estudiante_id = %s", (evaluacion_id, estudiaten_id))
    existe = cursor.fetchone()
    cursor.close()
    return existe is not None

def guardar_intento_respuestas(evaluacion, form, estudiante):
    cursor = mysql.connection.cursor()
    try:
        #crea intento
        cursor.execute("""
                       INSERT INTO intentos_evaluacion (
                           evaluacion_id, estudiante_id, nombre_estudiante, ciudad, cargo, proceso, estado
                       ) VALUES (
                           %s, %s, %s, %s, %s, %s, %s
                       )
                       """, (
                           evaluacion['id'],
                           estudiante['identificacion'],
                           estudiante['nombre'],
                           estudiante['ciudad'],
                           estudiante['cargo'],
                           estudiante['proceso'],
                           'Pendiente'
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
    except Exception as e:
        cursor.connection.rollback()
        raise e
    finally:
        cursor.close()
        
        
def get_resultados_cursos_db():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
                        ie.estado
                      FROM intentos_evaluacion ie
                      INNER JOIN evaluaciones e ON ie.evaluacion_id = e.id
                      INNER JOIN cursos c ON e.curso_id = c.id
                      ORDER BY c.nombre, ie.fecha_presentacion DESC
                      """)
    data = cursor.fetchall()
    cursor.close()
    return data

def get_intento_validar(intento_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
                   SELECT ie.id, ie.nombre_estudiante, ie.nota
                   FROM intentos_evaluacion ie
                   WHERE ie.id = %s
                   """, (intento_id,))
    intento = cursor.fetchone()
    print(intento)
    if not intento:
        cursor.close()
        return None
    cursor.execute("""
                   SELECT
                        re.id AS respuesta_id,
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

