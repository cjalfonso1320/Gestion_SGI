from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename

from controllers.aula_controller import crear_curso_db, get_cursos_db, crear_evaluacion_db, get_evaluacion_curso_db, eliminar_curso_db, ya_presento_evaluacion, guardar_intento_respuestas, get_resultados_cursos_db, get_intento_validar, validar_respuestas_texto, recalcular_nota_final



aula_bp = Blueprint('aula', __name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_CURSOS = os.path.join(BASE_DIR, '..', 'static', 'uploads', 'cursos')
os.makedirs(UPLOAD_CURSOS, exist_ok=True)





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
        estado = 'Abierto'
        
        if not file or file.filename == '':
            flash('No se ha seleccionado ningún archivo.', 'error')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        ruta_archivo = os.path.join(UPLOAD_CURSOS, filename)
        file.save(ruta_archivo)
        
        #Crea curso
        curso_id = crear_curso_db(
            nombre=nombre, 
            descripcion=descripcion,
            archivo='uploads/cursos/' + filename,
            fecha_limite=fecha_limite,
            creado_por=current_user.id,
            estado=estado
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
            
        flash('Curso creado exitosamente', 'success')
        return redirect(url_for('aula.gestionar_cursos'))
    return render_template('aulaVirtual/crear_curso.html', usuario=current_user)

@aula_bp.route('/aula/cursos/<int:curso_id>/evaluacion')
@login_required
def ver_evaluacion(curso_id):
    evaluacion = get_evaluacion_curso_db(curso_id)
    return render_template('aulaVirtual/_evaluacion_modal.html', evaluacion=evaluacion)

@aula_bp.route('/aula/cursos/<int:curso_id>/eliminar', methods=['POST'])
@login_required
def eliminar_curso(curso_id):
    eliminar_curso_db(curso_id)
    flash('Curso eliminado exitosamente', 'success')
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


#ESTUDIANTES
@aula_bp.route('/aula', methods=['GET', 'POST'])
def aula():
    if request.method == 'POST':
        session['estudiante'] = {
            'identificacion': request.form.get('identificacion'),
            'nombre': request.form.get('fullname'),
            'ciudad': request.form.get('ciudad'),
            'cargo': request.form.get('cargo'),
            'proceso': request.form.get('proceso')
        }
        return redirect(url_for('aula.cursos_estudiante'))
    return render_template('aulaVirtual/index.html')

@aula_bp.route('/aula/cursos-estudiante')
def cursos_estudiante():
    estudiante = session.get('estudiante')
    if not estudiante:
        return redirect(url_for('aula.aula'))
    
    return render_template('aulaVirtual/estudiante.html', estudiante=estudiante)

@aula_bp.route('/aula/cursos-estudiante/cursos')
def cursos_abiertos():
    cursos = get_cursos_db()
    estudiante = session.get('estudiante')
    return render_template('aulaVirtual/_cursos_estudiante.html', cursos=cursos, estudiante=estudiante)

@aula_bp.route('/aula/cursos-estudiante/cursos/<int:curso_id>')
def curso(curso_id):
    estudiante = session.get('estudiante')
    if not estudiante:
        return redirect(url_for('aula.aula'))
    
    cursos = get_cursos_db()
    curso = next((c for c in cursos if c['id'] == curso_id), None)
    if not curso:
        flash('Curso no encontrado.', 'error')
        return redirect(url_for('aula.cursos_estudiante'))
    
    evaluacion = get_evaluacion_curso_db(curso_id)
    return render_template('aulaVirtual/_curso.html', curso=curso, evaluacion=evaluacion, estudiante=estudiante)

@aula_bp.route('/aula/cursos-estudiante/cursos/<int:curso_id>/evaluacion', methods=['GET', 'POST'])
def presentar_evaluacion(curso_id):
    estudiante = session.get('estudiante')    
    if not estudiante:
        return redirect(url_for('aula.aula'))

    evaluacion = get_evaluacion_curso_db(curso_id)
    if not evaluacion:
        flash('No hay evaluación disponible para este curso.', 'error')
        return redirect(url_for('aula.cursos_estudiante'))
    evaluacion_id = evaluacion['id']
    
    #verifica intentos (solo permite uno)
    if ya_presento_evaluacion(evaluacion_id, estudiante['identificacion']):
        flash('Ya has presentado esta evaluación.', 'info')
        return redirect(url_for('aula.cursos_estudiante'))
    
    #guarda intento y respuesta
    if request.method == 'POST':
        guardar_intento_respuestas(
        evaluacion,
        request.form,
        estudiante
    )
        flash('Evaluacion enviada correctamente', 'success')
        return redirect(url_for('aula.cursos_estudiante'))
    return render_template('aulaVirtual/_evaluacion.html', evaluacion=evaluacion, estudiante=estudiante, curso_id=curso_id)

