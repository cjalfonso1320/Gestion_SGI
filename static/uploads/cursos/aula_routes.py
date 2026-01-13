from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename

from controllers.aula_controller import crear_curso_db, get_cursos_db, crear_evaluacion_db


aula_bp = Blueprint('aula', __name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_CURSOS = os.path.join(BASE_DIR, '..', 'static', 'uploads', 'cursos')
os.makedirs(UPLOAD_CURSOS, exist_ok=True)



@aula_bp.route('/aula')
def aula():
    return render_template('aulaVirtual/index.html')

@aula_bp.route('/aula/admin')
@login_required
def aulaAdmin():
    return render_template('aulaVirtual/admin.html', usuario=current_user)

@aula_bp.route('/aula/cursos')
@login_required
def gestionar_cursos():
    cursos = get_cursos_db()
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
            creado_por=current_user.id
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
        
        
        