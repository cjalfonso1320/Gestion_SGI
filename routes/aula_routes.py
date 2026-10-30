from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response, current_app, send_file, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
from utils.password_utils import hash_password, generate_password_hash
from utils.files import allowed_file
import re
import pdfkit

from controllers.aula_controller import crear_curso_db, get_cursos_db, get_cursos_estudiante_db, get_curso_db, get_curso_asignaciones, editar_curso_db, crear_evaluacion_db, get_evaluacion_curso_db, eliminar_curso_db, verificar_intentos_evaluacion, guardar_intento_respuestas, get_resultados_cursos_db, get_intento_validar, validar_respuestas_texto, recalcular_nota_final
from controllers.aula_controller import busca_estudiante, resultados_estudiante, curso_aprobado, actualiza_password
from controllers.aula_controller import guardar_video_curso, get_videos_curso, eliminar_videos_curso
from controllers.aula_controller import get_tabulacion_db, guardar_prorroga_individual, obtener_prorroga_activa

import pandas as pd
import io
from datetime import date, datetime
from controllers.rrhh_controller import empleados_lista_resumida
from models import obtener_roles



aula_bp = Blueprint('aula', __name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(BASE_DIR, '..')
UPLOAD_CURSOS = os.path.join(PROJECT_ROOT, 'static', 'uploads', 'cursos')
os.makedirs(UPLOAD_CURSOS, exist_ok=True)


def estudiante_en_session():
    estudiante = session.get('estudiante')
    if estudiante:
        return estudiante

    if not current_user.is_authenticated:
        return None

    user_id = current_user.get_id() or ''
    if not user_id.startswith('estu-'):
        return None

    estudiante_db = busca_estudiante(current_user.identificacion)
    if not estudiante_db:
        return None

    foto_path = estudiante_db.get('foto_path')
    if foto_path:
        foto_path = foto_path.replace('\\', '/')
    estudiante = {
        'identificacion': estudiante_db['identificacion'],
        'nombre': f"{estudiante_db['nombres']} {estudiante_db['apellidos']}",
        'ciudad': estudiante_db['ciudad'] or 'N/A',
        'cargo': estudiante_db['cargo'] or 'N/A',
        'proceso': estudiante_db['proceso'] or 'N/A',
        'foto_path': foto_path
    }
    session['estudiante'] = estudiante
    return estudiante


#convierte url a rutas de embed
def convert_url_to_embed(url):
    if not url:
        return None
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.search(youtube_regex, url)
    if match:
        video_id = match.group(6)
        return f"https://youtube.com/embed/{video_id}"
    return url



#------------------------------------------------------
#--- RUTA DEDICADA PARA SERVIR PDF DEL CURSO -----------
#--- (con headers explícitos para visibilidad en móvil) 
#------------------------------------------------------
@aula_bp.route('/aula/pdf/<int:curso_id>')
@login_required
def ver_pdf_curso(curso_id):
    """Sirve el PDF de un curso con headers explícitos para visualización inline.

    Esto es necesario porque al servir PDFs como archivos estáticos de Flask,
    los headers de seguridad globales (X-Frame-Options, CSP) pueden bloquear
    la visualización en dispositivos móviles. Esta ruta:
        - Fuerza Content-Type: application/pdf
        - Fuerza Content-Disposition: inline (para que el navegador no descargue)
        - NO aplica X-Frame-Options (para permitir rendering en <object>/<iframe>)
    """
    estudiante = estudiante_en_session()
    if not estudiante:
        abort(401)

    curso = get_curso_db(curso_id)
    if not curso or not curso.get('archivo'):
        abort(404)

    ruta_relativa = curso['archivo']
    pdf_path = os.path.join(PROJECT_ROOT, 'static', ruta_relativa)
    pdf_path = os.path.normpath(pdf_path)

    if not os.path.isfile(pdf_path):
        abort(404)

    filename = os.path.basename(pdf_path)

    response = send_file(pdf_path, mimetype='application/pdf', as_attachment=False)
    # Forzar visualización inline (no descarga)
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
    # NO establecer X-Frame-Options aquí; el after_request global solo lo agrega
    # si no está presente, por lo que los PDFs quedarán sin esta restricción
    # y podrán renderizarse en <object>/<iframe> en cualquier dispositivo.
    return response


@aula_bp.route('/aula/admin')
@login_required
def aulaAdmin():
    return render_template('aulaVirtual/admin.html', usuario=current_user)

@aula_bp.route('/aula/cursos')
@login_required
def gestionar_cursos():
    modo = request.args.get('modo', 'cursos')
    cursos = get_cursos_db()
    
    if modo == 'resultados':
        resultados = get_resultados_cursos_db()
        return render_template('aulaVirtual/_resultados_cursos.html', cursos=cursos, resultados=resultados, modo=modo, usuario=current_user)
    return render_template('aulaVirtual/cursos.html', usuario=current_user, cursos=cursos)

@aula_bp.route('/aula/cursos/crear', methods=['GET', 'POST'])
@login_required
def crear_curso():
    if request.method == 'POST':
        # Aquí iría la lógica para crear un curso con los datos del formulario
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        fecha_limite = request.form.get('duracion')
        file = request.files.get('documento')
        enlace_video = request.form.get('enlace_video')
        estado = 'Abierto'
        dirigido_a = request.form.get('dirigido_a')
        personas_seleccionadas = request.form.getlist('personas_seleccionadas')
        roles_seleccionados = request.form.getlist('roles_seleccionados')
        
        archivo_ruta = None
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('❌ El documento debe ser un archivo PDF. Selecciona un archivo con extensión .pdf.', 'error')
                return redirect(url_for('aula.crear_curso'))
            filename = secure_filename(file.filename)
            ruta_archivo = os.path.join(UPLOAD_CURSOS, filename)
            file.save(ruta_archivo)
            # Validar magic bytes post-grabado (firma real %PDF)
            if not allowed_file(file.filename, filepath=ruta_archivo):
                os.remove(ruta_archivo)
                flash('❌ El archivo no es un PDF válido. Su contenido no coincide con el formato esperado.', 'error')
                return redirect(url_for('aula.crear_curso'))
            archivo_ruta = 'uploads/cursos/' + filename
        
        #Crea curso
        resultado = crear_curso_db(
            nombre=nombre, 
            descripcion=descripcion,
            archivo=archivo_ruta,
            fecha_limite=fecha_limite,
            creado_por=current_user.id,
            estado=estado,
            enlace_video=enlace_video,
            dirigido_a=dirigido_a,
            personas=personas_seleccionadas if dirigido_a == 'personas' else None,
            roles=roles_seleccionados if dirigido_a == 'roles' else None
        )
        # resultado = (curso_id, email_enviado, whatsapp_enviado, cant_correos, cant_whatsapp)
        curso_id = resultado[0]
        email_enviado = resultado[1] if len(resultado) > 1 else False
        whatsapp_enviado = resultado[2] if len(resultado) > 2 else False
        cant_correos = resultado[3] if len(resultado) > 3 else 0
        cant_whatsapp = resultado[4] if len(resultado) > 4 else 0

        # Guardar archivos de video subidos
        videos = request.files.getlist('videos_curso')
        for v in videos:
            if v and v.filename:
                v_filename = secure_filename(v.filename)
                v_ruta = os.path.join(UPLOAD_CURSOS, 'videos', str(curso_id))
                os.makedirs(v_ruta, exist_ok=True)
                v_path = os.path.join(v_ruta, v_filename)
                v.save(v_path)
                guardar_video_curso(
                    curso_id,
                    v.filename,
                    f'uploads/cursos/videos/{curso_id}/{v_filename}'
                )
        
        #lee preguntas
        preguntas = []
        indices = set()
        
        for key in request.form.keys():
            if key.startswith('preguntas[') and key.endswith('][pregunta]'):
                indice = key.split('[')[1].split(']')[0]
                indices.add(indice)
                
        for i in sorted(indices, key=int):
            pregunta = request.form.get(f'preguntas[{i}][pregunta]')
            tipo = request.form.get(f'tipo_pregunta_{i}')
            opciones = request.form.getlist(f'preguntas[{i}][opciones][]')
            respuesta = None
            
            if tipo == 'opcion_multiple':
                correcta = request.form.get(f'preguntas[{i}][correcta]')
                mapa = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                
                if correcta in mapa and mapa[correcta] < len(opciones):
                    respuesta = opciones[mapa[correcta]]
            elif tipo in ('vf', 'texto'):
                respuesta = request.form.get(f'preguntas[{i}][respuesta]')
                
            if not pregunta or not respuesta:
                raise ValueError(f'Pregunta {int(i)+1} incompleta.')
            
            preguntas.append({
                'pregunta': pregunta,
                'tipo': tipo,
                'respuesta': respuesta,
                'opciones': opciones if tipo == 'opcion_multiple' else []
            })
        
        #crea evaluacion
        if preguntas:
            crear_evaluacion_db(curso_id, nombre, preguntas)

        # Feedback de notificaciones
        if dirigido_a in ('todos', 'personas', 'roles'):
            if email_enviado:
                flash(f'📧 Notificación enviada a {cant_correos} correo(s)', 'success')
            elif cant_correos > 0:
                flash(f'⚠️ No se pudo enviar la notificación por correo a {cant_correos} destinatario(s). Revisa logs/email.log para más detalles.', 'warning')
            else:
                flash('⚠️ No se encontraron correos válidos para notificar. Verifica que los empleados tengan correo registrado.', 'warning')

            if whatsapp_enviado:
                flash(f'💬 Notificación WhatsApp enviada a {cant_whatsapp} número(s)', 'success')

        flash('✅ Curso creado exitosamente', 'success')
        return redirect(url_for('aula.gestionar_cursos'))
    lista_empleados = empleados_lista_resumida()
    roles = obtener_roles()
    return render_template('aulaVirtual/crear_curso.html', usuario=current_user, lista_empleados=lista_empleados, roles=roles)

@aula_bp.route('/aula/cursos/<int:curso_id>/evaluacion')
@login_required
def ver_evaluacion(curso_id):
    evaluacion = get_evaluacion_curso_db(curso_id)
    return render_template('aulaVirtual/_evaluacion_modal.html', evaluacion=evaluacion)

@aula_bp.route('/aula/cursos/<int:curso_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_curso(curso_id):
    curso = get_curso_db(curso_id)
    if not curso:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('aula.gestionar_cursos'))
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        fecha_limite = request.form.get('duracion')
        file = request.files.get('documento')
        enlace_video = request.form.get('enlace_video')
        dirigido_a = request.form.get('dirigido_a')
        personas_seleccionadas = request.form.getlist('personas_seleccionadas')
        roles_seleccionados = request.form.getlist('roles_seleccionados')

        archivo_nuevo = None
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('❌ El documento debe ser un archivo PDF. Selecciona un archivo con extensión .pdf.', 'error')
                return redirect(url_for('aula.editar_curso', curso_id=curso_id))
            filename = secure_filename(file.filename)
            ruta_archivo = os.path.join(UPLOAD_CURSOS, filename)
            file.save(ruta_archivo)
            # Validar magic bytes post-grabado (firma real %PDF)
            if not allowed_file(file.filename, filepath=ruta_archivo):
                os.remove(ruta_archivo)
                flash('❌ El archivo no es un PDF válido. Su contenido no coincide con el formato esperado.', 'error')
                return redirect(url_for('aula.editar_curso', curso_id=curso_id))
            archivo_nuevo = 'uploads/cursos/' + filename

        try:
            editar_curso_db(
                curso_id=curso_id,
                nombre=nombre,
                descripcion=descripcion,
                archivo=archivo_nuevo,
                fecha_limite=fecha_limite,
                enlace_video=enlace_video,
                dirigido_a=dirigido_a,
                personas=personas_seleccionadas if dirigido_a == 'personas' else None,
                roles=roles_seleccionados if dirigido_a == 'roles' else None
            )

            # Guardar archivos de video subidos (edición)
            videos = request.files.getlist('videos_curso')
            for v in videos:
                if v and v.filename:
                    v_filename = secure_filename(v.filename)
                    v_ruta = os.path.join(UPLOAD_CURSOS, 'videos', str(curso_id))
                    os.makedirs(v_ruta, exist_ok=True)
                    v_path = os.path.join(v_ruta, v_filename)
                    v.save(v_path)
                    guardar_video_curso(
                        curso_id,
                        v.filename,
                        f'uploads/cursos/videos/{curso_id}/{v_filename}'
                    )

            flash('Curso actualizado exitosamente.', 'success')
        except Exception as e:
            print(f"Error editando curso {curso_id}: {e}")
            flash('Error al actualizar el curso. Intenta nuevamente.', 'error')
        return redirect(url_for('aula.gestionar_cursos'))

    asignaciones = get_curso_asignaciones(curso_id)
    lista_empleados = empleados_lista_resumida()
    roles = obtener_roles()
    return render_template(
        'aulaVirtual/editar_curso.html',
        usuario=current_user,
        curso=curso,
        lista_empleados=lista_empleados,
        roles=roles,
        roles_seleccionados=asignaciones['roles'],
        personas_seleccionadas=asignaciones['personas']
    )


@aula_bp.route('/aula/cursos/<int:curso_id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_curso(curso_id):
    if request.method != 'POST':
        flash('Acción no permitida. Usa el botón Eliminar para borrar un curso.', 'error')
        return redirect(url_for('aula.gestionar_cursos'))
    try:
        eliminar_curso_db(curso_id)
        flash('Curso eliminado exitosamente', 'success')
    except Exception as e:
        print(f"Error eliminando curso {curso_id}: {e}")
        flash('Error al eliminar el curso. Intenta nuevamente.', 'error')
    return redirect(url_for('aula.gestionar_cursos'))

@aula_bp.route('/aula/resultados/revisar/<int:intento_id>')
@login_required
def revisar_intento(intento_id):
    intento = get_intento_validar(intento_id)
    if not intento:
        return "<p>No se encontro el intento</p>"
    return render_template('aulaVirtual/_modal_revision.html', intento=intento)

@aula_bp.route('/aula/resultados/validar/<int:intento_id>', methods=['POST'])
@login_required
def validar_intento(intento_id):
    validar_respuestas_texto(intento_id, request.form)
    recalcular_nota_final(intento_id)
    flash('Evaluacion calificada correctamente, success')
    return redirect(url_for('aula.gestionar_cursos', modo='resultados'))

@aula_bp.route('/aula/prorrogas/guardar', methods=['POST'])
@login_required
def guardar_prorroga():
    """API para conceder o actualizar una prórroga individual a un empleado."""
    try:
        data = request.get_json(silent=True) or request.form
        curso_id = data.get('curso_id')
        identificacion = str(data.get('identificacion', '')).strip()
        nueva_fecha_limite = data.get('nueva_fecha_limite')
        motivo = data.get('motivo', '').strip() if data.get('motivo') else None
        notificar_raw = data.get('notificar')
        notificar = notificar_raw in [True, 'true', 'True', '1', 1, 'on']

        if not curso_id or not identificacion or not nueva_fecha_limite:
            return jsonify({'success': False, 'error': 'Faltan campos obligatorios (curso, empleado o fecha).'}), 400

        try:
            curso_id = int(curso_id)
        except ValueError:
            return jsonify({'success': False, 'error': 'ID de curso inválido.'}), 400

        otorgado_por = current_user.get_id() if hasattr(current_user, 'get_id') else 'admin'
        res = guardar_prorroga_individual(curso_id, identificacion, nueva_fecha_limite, motivo, otorgado_por, notificar)
        status_code = 200 if res.get('success') else 400
        return jsonify(res), status_code
    except Exception as e:
        print(f"❌ Error en endpoint guardar_prorroga: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



#ESTUDIANTES
@aula_bp.route('/aula/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password_obligatorio():
    session.setdefault('post_password_change_endpoint', 'aula.cursos_estudiante')
    return redirect(url_for('auth.cambiar_password_inicial'))

    estudiante = estudiante_en_session()
    if not estudiante:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        nueva_pass = request.form.get('nueva_password') or request.form.get('nuevo_password')
        confirma_pass = request.form.get('confirmar_password') or request.form.get('confirma_password')
        
        if nueva_pass != confirma_pass:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('aulaVirtual/cambiar_pass.html')
        
        identificacion = estudiante['identificacion']
        
        if actualiza_password(identificacion, nueva_pass):
            if hasattr(current_user, 'primer_ingreso'):
                current_user.primer_ingreso = 0
            flash('Contraseña Actualizada, Ya puedes acceder a tus cursos', 'success')
            return redirect(url_for('aula.cursos_estudiante'))
        flash('No se pudo actualizar la contraseña. Intenta nuevamente.', 'error')
    return render_template('aulaVirtual/cambiar_pass.html')
        
        



@aula_bp.route('/aula/cursos-estudiante')
@login_required
def cursos_estudiante():
    estudiante = estudiante_en_session()
    if not estudiante:
        return redirect(url_for('auth.login'))
    
    # ── Capturar resultado de evaluación (SweetAlert de aprobado) ──
    eval_aprobado = None
    if request.args.get('eval_nota') is not None:
        eval_aprobado = {
            'nota': request.args.get('eval_nota', type=float)
        }
    
    # ── Contar cursos disponibles (asignados, abiertos y no aprobados) ──
    cursos = get_cursos_estudiante_db(estudiante['identificacion'])
    cursos_disponibles = 0
    for c in cursos:
        if c['estado'] == 'Abierto' and not curso_aprobado(estudiante['identificacion'], c['id']):
            cursos_disponibles += 1
    
    # ── Contar certificados disponibles (nota >= 70 y calificado) ──
    resultados = resultados_estudiante(estudiante['identificacion'])
    certificados_count = sum(1 for r in resultados 
                             if r['nota'] is not None and r['nota'] >= 70 and r['estado'] == 'Calificado')
    # ── Evaluaciones pendientes de revisión (preguntas abiertas sin calificar) ──
    pendientes_revision = [r for r in resultados if r['estado'] == 'Pendiente']
    
    return render_template('aulaVirtual/estudiante.html',
                          estudiante=estudiante,
                          cursos_disponibles=cursos_disponibles,
                          certificados_count=certificados_count,
                          pendientes_revision=pendientes_revision,
                          eval_aprobado=eval_aprobado,
                          now=datetime.now())

@aula_bp.route('/aula/cursos-estudiante/cursos')
@login_required
def cursos_abiertos():
    estudiante = estudiante_en_session()
    if not estudiante:
        return redirect(url_for('auth.login'))
    cursos = get_cursos_estudiante_db(estudiante['identificacion'])
    
    #marca de curso
    for c in cursos:
        c['aprobado'] = curso_aprobado(estudiante['identificacion'], c['id'])
        # Verificar si el estudiante agotó los intentos (3 intentos fallidos)
        if not c['aprobado']:
            evaluacion = get_evaluacion_curso_db(c['id'])
            if evaluacion:
                verificacion = verificar_intentos_evaluacion(evaluacion['id'], estudiante['identificacion'])
                c['intentos_agotados'] = not verificacion['puede_presentar'] and verificacion['intentos_realizados'] >= verificacion['max_intentos']
                c['intentos_restantes'] = verificacion['intentos_restantes']
            else:
                c['intentos_agotados'] = False
                c['intentos_restantes'] = 0
        else:
            c['intentos_agotados'] = False
            c['intentos_restantes'] = 0
    
    return render_template('aulaVirtual/_cursos_estudiante.html', cursos=cursos, estudiante=estudiante)

@aula_bp.route('/aula/cursos-estudiante/cursos/<int:curso_id>')
@login_required
def curso(curso_id):
    estudiante = estudiante_en_session()
    if not estudiante:
        return redirect(url_for('auth.login'))
    
    # Obtener solo cursos asignados al estudiante
    cursos = get_cursos_estudiante_db(estudiante['identificacion'])
    curso = next((c for c in cursos if c['id'] == curso_id), None)
    if not curso:
        flash('Curso no encontrado o no tienes acceso a él.', 'error')
        return redirect(url_for('aula.cursos_estudiante'))
    
    # ── Capturar resultado de evaluación desde query params (SweetAlert) ──
    # Debe hacerse ANTES de los bloqueos para mostrar el SweetAlert
    eval_resultado = None
    if request.args.get('eval_nota') is not None:
        eval_resultado = {
            'nota': request.args.get('eval_nota', type=float),
            'aprobado': request.args.get('eval_aprobado', default=None) == '1',
            'estado': request.args.get('eval_estado'),
            'tiene_texto': request.args.get('eval_tiene_texto', default=None) == '1'
        }
    
    # Si venimos de presentar evaluación (hay eval_resultado), NO bloqueamos
    # para que se muestre el SweetAlert con el resultado
    if not eval_resultado:
        # Bloqueo: si ya aprobó no puede acceder
        if curso_aprobado(estudiante['identificacion'], curso_id):
            flash('Ya has completado este curso. Puedes ver tu certificado en la seccion de Resultados', 'info')
            return redirect(url_for('aula.cursos_abiertos'))
    
    #procesa video
    if curso.get('enlace_video'):
        curso['enlace_video_embed'] = convert_url_to_embed(curso['enlace_video'])
    evaluacion = get_evaluacion_curso_db(curso_id)
    videos = get_videos_curso(curso_id)
    
    # Verificar intentos restantes para mostrar en la vista
    info_intentos = None
    if evaluacion:
        verificacion = verificar_intentos_evaluacion(evaluacion['id'], estudiante['identificacion'])
        if not eval_resultado:
            # Solo bloquear si NO venimos de presentar evaluación
            if not verificacion['puede_presentar'] and verificacion['intentos_realizados'] >= verificacion['max_intentos']:
                flash(verificacion['mensaje'], 'warning')
                return redirect(url_for('aula.cursos_abiertos'))
        info_intentos = {
            'intentos_realizados': verificacion['intentos_realizados'],
            'intentos_restantes': verificacion['intentos_restantes'],
            'max_intentos': verificacion['max_intentos']
        }
    
    return render_template('aulaVirtual/_curso.html',
                          curso=curso,
                          evaluacion=evaluacion,
                          estudiante=estudiante,
                          videos=videos,
                          info_intentos=info_intentos,
                          eval_resultado=eval_resultado)

@aula_bp.route('/aula/cursos-estudiante/cursos/<int:curso_id>/evaluacion', methods=['GET', 'POST'])
@login_required
def presentar_evaluacion(curso_id):
    estudiante = estudiante_en_session()    
    if not estudiante:
        return redirect(url_for('auth.login'))

    evaluacion = get_evaluacion_curso_db(curso_id)
    if not evaluacion:
        flash('No hay evaluación disponible para este curso.', 'error')
        return redirect(url_for('aula.cursos_estudiante'))
    evaluacion_id = evaluacion['id']
    
    # ── Verificar si puede presentar la evaluación (hasta 3 intentos) ──
    verificacion = verificar_intentos_evaluacion(evaluacion_id, estudiante['identificacion'])
    if not verificacion['puede_presentar']:
        flash(verificacion['mensaje'], 'warning')
        return redirect(url_for('aula.cursos_estudiante'))
    
    # ── Guardar intento y respuestas ──
    if request.method == 'POST':
        resultado = guardar_intento_respuestas(
            evaluacion,
            request.form,
            estudiante
        )
        if resultado['aprobado']:
            # ✅ Aprobó → ir al inicio con SweetAlert
            return redirect(url_for(
                'aula.cursos_estudiante',
                eval_nota=resultado['nota']
            ))
        else:
            # ❌ Reprobó o pendiente → ir al curso para reintentar
            return redirect(url_for(
                'aula.curso',
                curso_id=curso_id,
                eval_nota=resultado['nota'],
                eval_aprobado='0',
                eval_estado=resultado['estado'],
                eval_tiene_texto='1' if resultado['tiene_texto'] else '0'
            ))
    
    # Mostrar información de intentos en la vista
    info_intentos = {
        'intentos_realizados': verificacion['intentos_realizados'],
        'intentos_restantes': verificacion['intentos_restantes'],
        'max_intentos': verificacion['max_intentos'],
        'es_repeticion': verificacion['intentos_realizados'] > 0
    }
    
    return render_template('aulaVirtual/_evaluacion.html',
                          evaluacion=evaluacion,
                          estudiante=estudiante,
                          curso_id=curso_id,
                          info_intentos=info_intentos)

@aula_bp.route('/aula/mis_resultados')
@login_required
def mis_resultados():
    estudiante = estudiante_en_session()
    if not estudiante:
        return redirect(url_for('auth.login'))
    
    resultados = resultados_estudiante(estudiante['identificacion'])
    
    return render_template('aulaVirtual/mis_resultados.html',
                           estudiante=estudiante,
                           resultados=resultados)
    
@aula_bp.route('/aula/mis_certificados')
@login_required
def mis_certificados():
    estudiante = estudiante_en_session()
    if not estudiante:
        return redirect(url_for('auth.login'))
    
    resultados = resultados_estudiante(estudiante['identificacion'])
    
    # Solo certificados aprobados Y calificados (preguntas de texto revisadas)
    certificados = [r for r in resultados if r['nota'] is not None and r['nota'] >= 70 and r['estado'] == 'Calificado']
    # Resultados que están pendientes de revisión (tienen nota >= 70 pero estado Pendiente)
    pendientes_revision = [r for r in resultados if r['nota'] is not None and r['nota'] >= 70 and r['estado'] == 'Pendiente']
    
    return render_template('aulaVirtual/mis_certificados.html',
                            estudiante=estudiante,
                            certificados=certificados,
                            pendientes_revision=pendientes_revision)

@aula_bp.route('/aula/descargar_certificado/<id_resultado>')
@login_required
def descargar_certificado(id_resultado):
    # 1. Obtener datos del estudiante y el resultado
    estudiante = estudiante_en_session()
    if not estudiante:
        return redirect(url_for('auth.login'))
    
    # Buscar el resultado específico por ID
    resultado = next((r for r in resultados_estudiante(estudiante['identificacion']) if str(r['id']) == id_resultado), None)
    if not resultado:
        flash('Resultado no encontrado.', 'error')
        return redirect(url_for('aula.mis_certificados'))
    
    # ── Bloquear descarga si la evaluación está pendiente de revisión ──
    if resultado['estado'] == 'Pendiente':
        flash('⚠️ Tu evaluación tiene preguntas abiertas que aún no han sido revisadas. Una vez el administrador las califique, podrás descargar tu certificado.', 'warning')
        return redirect(url_for('aula.mis_certificados'))
    
    # 2. Renderizar el HTML del certificado
    ahora = resultado['fecha_presentacion'].strftime('%d de %B de %Y')
    path_logo = os.path.join(current_app.root_path, 'static', 'imgs', 'logo.png')
    path_premio = os.path.join(current_app.root_path, 'static', 'imgs', 'premio.png')
    
    # Foto del estudiante para el PDF (ruta absoluta)
    foto_absoluta = None
    if estudiante.get('foto_path'):
        rel_path = estudiante['foto_path']
        if rel_path.startswith('static/'):
            rel_path = rel_path[len('static/'):]
        foto_absoluta = os.path.join(current_app.root_path, 'static', rel_path)
        if not os.path.exists(foto_absoluta):
            foto_absoluta = None
    
    html_template = render_template('aulaVirtual/_certificado.html', 
                                    estudiante=estudiante, 
                                    resultado=resultado,
                                    fecha=ahora,
                                    logo=path_logo,
                                    premio=path_premio,
                                    foto_estudiante=foto_absoluta)
    
    # 3. Configuración de opciones para el PDF
    options = {
        'page-size': 'Letter',
        'orientation': 'Landscape',
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in',
        'encoding': "UTF-8",
        'enable-local-file-access': None,
        'no-outline': None
    }
    
    # 4. Configurar la ruta del ejecutable en el servidor Windows
    # Asegúrate de que esta ruta sea exacta en tu servidor
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    
    # 5. Generar el PDF (llamada única pasando la configuración)
    try:
        pdf = pdfkit.from_string(html_template, False, options=options, configuration=config)
    except Exception as e:
        # En caso de que falle el binario, capturamos el error para no tumbar la app
        flash(f'Error al generar el PDF: {str(e)}', 'error')
        return redirect(url_for('aula.mis_certificados'))

    # 6. Responder con el archivo para descarga
    nombre_archivo = f"Certificado_{resultado['curso'].replace(' ', '_')}.pdf"
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={nombre_archivo}'

    return response


#------------------------------------------------------
#------------------- TABULACIÓN ------------------------
#------------------------------------------------------
@aula_bp.route('/aula/tabulacion')
@login_required
def tabulacion():
    datos = get_tabulacion_db()
    return render_template('aulaVirtual/tabulacion.html', usuario=current_user, cursos=datos)


def _generar_excel_curso(c):
    """Genera un Excel en memoria para un curso de tabulación.

    Args:
        c: dict con datos del curso (curso_nombre, estudiantes, preguntas, estadísticas)

    Returns:
        BytesIO: Buffer con el archivo Excel generado.
    """
    curso_nombre = c['curso_nombre']
    sheet_name = curso_nombre[:31]

    xl_buffer = io.BytesIO()

    with pd.ExcelWriter(xl_buffer, engine='xlsxwriter') as writer:
        workbook = writer.book

        # --- Construir filas de datos ---
        col_names = ['Estudiante', 'Identificación', 'Cargo', 'Ciudad']
        for idx in range(1, len(c['preguntas']) + 1):
            col_names.append(f'Pregunta {idx}')
        col_names.extend(['Nota', 'Estado', 'Fecha'])

        data_rows = []
        for est in c['estudiantes']:
            row = [
                est['nombre_estudiante'],
                est['estudiante_id'],
                est['cargo'] or '',
                est['ciudad'] or '',
            ]
            for preg in c['preguntas']:
                resp_val = ''
                for r in est['respuestas']:
                    if r['pregunta_id'] == preg['id']:
                        if r['es_correcta'] == 1:
                            resp_val = 1
                        elif r['es_correcta'] == 0:
                            resp_val = 0
                        else:
                            resp_val = r['respuesta_texto'] or ''
                        break
                row.append(resp_val)
            nota = est['nota']
            if nota is not None and nota >= 70:
                estado = 'Aprobado'
            elif nota is not None:
                estado = 'Reprobado'
            else:
                estado = 'Pendiente'
            row.append(nota if nota is not None else '')
            row.append(estado)
            row.append(str(est['fecha_presentacion'] or ''))
            data_rows.append(row)

        # --- Escribir hoja principal ---
        ws = workbook.add_worksheet(sheet_name)

        # Formatos
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#1e3a8a', 'font_color': '#ffffff',
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True
        })
        cell_fmt = workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'vcenter'
        })
        center_fmt = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        pct_fmt = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'num_format': '0.00'
        })
        badge_aprobado = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#dcfce7', 'font_color': '#166534', 'bold': True
        })
        badge_reprobado = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#fef2f2', 'font_color': '#991b1b', 'bold': True
        })
        badge_pendiente = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#fef3c7', 'font_color': '#92400e', 'bold': True
        })

        # --- Estadísticas del curso ---
        total_asignados = c.get('total_asignados', c['total_estudiantes'])
        evaluados = c.get('total_evaluados', c.get('total_estudiantes', 0))
        aprob = c['total_aprobados']
        reprob = c['total_reprobados']
        pend = c['total_pendientes']
        no_pres = c.get('total_no_presentaron', max(0, total_asignados - evaluados))
        pct_aprob = f"{c['porcentaje_aprobados']}%"
        pct_reprob = f"{c['porcentaje_reprobados']}%"
    
        stat_title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'font_color': '#1e3a8a'
        })
        stat_label_fmt = workbook.add_format({
            'bold': True, 'font_size': 11, 'font_color': '#475569', 'border': 1,
            'bg_color': '#f1f5f9', 'align': 'left'
        })
        stat_val_fmt = workbook.add_format({
            'font_size': 11, 'font_color': '#1e293b', 'border': 1,
            'align': 'center', 'bold': True
        })
        stat_green = workbook.add_format({
            'font_size': 11, 'font_color': '#166534', 'border': 1,
            'align': 'center', 'bold': True, 'bg_color': '#dcfce7'
        })
        stat_red = workbook.add_format({
            'font_size': 11, 'font_color': '#991b1b', 'border': 1,
            'align': 'center', 'bold': True, 'bg_color': '#fef2f2'
        })
        stat_amber = workbook.add_format({
            'font_size': 11, 'font_color': '#92400e', 'border': 1,
            'align': 'center', 'bold': True, 'bg_color': '#fef3c7'
        })

        ws.merge_range('A1:B1', curso_nombre, stat_title_fmt)
        ws.write('A2', 'Total Asignados (Población)', stat_label_fmt)
        ws.write('B2', total_asignados, stat_val_fmt)
        ws.write('A3', 'Total Evaluados (Presentaron)', stat_label_fmt)
        ws.write('B3', evaluados, stat_val_fmt)
        ws.write('A4', 'Sin Realizar (Faltantes)', stat_label_fmt)
        ws.write('B4', no_pres, stat_amber)
        ws.write('A5', 'Aprobados (% sobre evaluados)', stat_label_fmt)
        ws.write('B5', f"{aprob} ({pct_aprob})", stat_green)
        ws.write('A6', 'Reprobados (% sobre evaluados)', stat_label_fmt)
        ws.write('B6', f"{reprob} ({pct_reprob})", stat_red)
        ws.set_column('A:A', 26)
        ws.set_column('B:B', 22)

        # --- Datos para el gráfico (ocultos en columna Z y AA, lejos de la tabla) ---
        CHART_DATA_COL = 25  # Columna Z
        CHART_VAL_COL = 26   # Columna AA
        ws.write(0, CHART_DATA_COL, 'Estado', stat_label_fmt)
        ws.write(1, CHART_DATA_COL, 'Cantidad', stat_label_fmt)
        ws.write(2, CHART_DATA_COL, 'Aprobados', stat_label_fmt)
        ws.write(3, CHART_DATA_COL, 'Reprobados', stat_label_fmt)
        ws.write(2, CHART_VAL_COL, aprob, stat_val_fmt)
        ws.write(3, CHART_VAL_COL, reprob, stat_val_fmt)

        # --- Gráfico de dona ---
        chart = workbook.add_chart({'type': 'doughnut'})
        chart.add_series({
            'name': 'Resultados',
            'categories': [sheet_name, 2, CHART_DATA_COL, 3, CHART_DATA_COL],  # Z3:Z5 - labels
            'values': [sheet_name, 2, CHART_VAL_COL, 3, CHART_VAL_COL],       # AA3:AA5 - values
            'points': [
                {'fill': {'color': '#22c55e'}},  # Aprobados
                {'fill': {'color': '#ef4444'}},   # Reprobados
            ],
            'data_labels': {
                'percentage': True,
                'category': True,
                'separator': '\n',
                'font': {'size': 10, 'bold': True}
            },
            'gap': 100,
        })
        chart.set_title({
            'name': f'{curso_nombre} — Resultados',
            'name_font': {'size': 12, 'bold': True}
        })
        chart.set_size({'width': 420, 'height': 320})
        chart.set_legend({'none': True})
        # Incluir datos de celdas ocultas (D y E están ocultas, 
        # y Excel por defecto no gráfica datos ocultos)
        chart.show_hidden_data()

        ws.insert_chart('D7', chart)

        # --- Tabla de estudiantes ---
        TABLE_START_ROW = 25

        for col_idx, col_name in enumerate(col_names):
            ws.write(TABLE_START_ROW, col_idx, col_name, header_fmt)

        for row_idx, row_data in enumerate(data_rows):
            excel_row = TABLE_START_ROW + 1 + row_idx
            for col_idx, val in enumerate(row_data):
                col_name_at_idx = col_names[col_idx] if col_idx < len(col_names) else ''
                if col_name_at_idx == 'Estado':
                    if val == 'Aprobado':
                        ws.write(excel_row, col_idx, val, badge_aprobado)
                    elif val == 'Reprobado':
                        ws.write(excel_row, col_idx, val, badge_reprobado)
                    elif val == 'Pendiente':
                        ws.write(excel_row, col_idx, val, badge_pendiente)
                    else:
                        ws.write(excel_row, col_idx, val, center_fmt)
                elif col_name_at_idx == 'Nota':
                    if val != '':
                        ws.write_number(excel_row, col_idx, val, pct_fmt)
                    else:
                        ws.write(excel_row, col_idx, '', center_fmt)
                elif col_name_at_idx == 'Identificación':
                    ws.write(excel_row, col_idx, str(val) if val else '', center_fmt)
                else:
                    ws.write(excel_row, col_idx, val, cell_fmt)

        col_widths = {
            0: 30, 1: 18, 2: 22, 3: 18,
        }
        for p_idx in range(len(c['preguntas'])):
            col_widths[4 + p_idx] = 25
        num_cols = len(col_names)
        if num_cols >= 5 + len(c['preguntas']):
            col_widths[num_cols - 3] = 10
            col_widths[num_cols - 2] = 14
            col_widths[num_cols - 1] = 20

        for col_idx, width in col_widths.items():
            ws.set_column(col_idx, col_idx, width)

        ws.set_column('Z:Z', None, None, {'hidden': True})
        ws.set_column('AA:AA', None, None, {'hidden': True})

        # --- Hoja de empleados sin realizar ---
        if c.get('estudiantes_no_presentaron'):
            ws_pend = workbook.add_worksheet('Sin Realizar')
            ws_pend.merge_range('A1:G1', f"{curso_nombre} — Empleados Pendientes por Realizar ({len(c['estudiantes_no_presentaron'])})", stat_title_fmt)
            pend_headers = ['Identificación', 'Nombre Completo', 'Cargo', 'Ciudad', 'Correo', 'Celular', 'Prórroga Concedida']
            for c_idx, h_text in enumerate(pend_headers):
                ws_pend.write(2, c_idx, h_text, header_fmt)
            for r_idx, emp in enumerate(c['estudiantes_no_presentaron']):
                e_row = 3 + r_idx
                ws_pend.write(e_row, 0, str(emp.get('identificacion', '')), center_fmt)
                ws_pend.write(e_row, 1, emp.get('nombre_completo', ''), cell_fmt)
                ws_pend.write(e_row, 2, emp.get('cargo', '') or '', cell_fmt)
                ws_pend.write(e_row, 3, emp.get('ciudad', '') or '', cell_fmt)
                ws_pend.write(e_row, 4, emp.get('correo', '') or '', cell_fmt)
                ws_pend.write(e_row, 5, emp.get('celular', '') or '', center_fmt)
                pr = emp.get('prorroga')
                pr_text = f"Hasta {pr['nueva_fecha_limite']}" if pr else "Sin prórroga"
                ws_pend.write(e_row, 6, pr_text, center_fmt)
            ws_pend.set_column(0, 0, 18)
            ws_pend.set_column(1, 1, 32)
            ws_pend.set_column(2, 2, 26)
            ws_pend.set_column(3, 3, 20)
            ws_pend.set_column(4, 4, 30)
            ws_pend.set_column(5, 5, 18)
            ws_pend.set_column(6, 6, 24)

    xl_buffer.seek(0)
    return xl_buffer


@aula_bp.route('/aula/tabulacion/descargar_excel/<int:curso_id>')
@login_required
def descargar_tabulacion_excel(curso_id):
    """Descarga un Excel individual para un curso específico."""
    datos = get_tabulacion_db()
    curso = next((c for c in datos if c['curso_id'] == curso_id), None)

    if not curso:
        flash('Curso no encontrado en la tabulación.', 'error')
        return redirect(url_for('aula.tabulacion'))

    xl_buffer = _generar_excel_curso(curso)
    hoy = date.today().strftime('%Y-%m-%d')
    nombre_limpio = re.sub(r'[\\/*?:"<>|]', '_', curso['curso_nombre'])
    nombre_archivo = f"{nombre_limpio}_{hoy}.xlsx"

    return send_file(
        xl_buffer,
        download_name=nombre_archivo,
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )