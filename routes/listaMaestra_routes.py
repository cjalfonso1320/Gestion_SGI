from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES
from controllers.lista_controller import lista_maestra, guardar_lista_maestra, actualizar_documento_maestro

lMaestra_bp = Blueprint('lMaestra', __name__)

@lMaestra_bp.route('/Lista_Maestra')
@login_required
def Lista_Maestra():
    rol = current_user.rol
    procesos = PROCESOS_ROL.get(rol, [])
    imagen_rol = ROL_IMAGES.get(rol, 'imgs/user.png')
    datos = lista_maestra()
    return render_template('ListaMaestra/Lista_Maestra.html', usuario=current_user, procesos=procesos, datos_lista_maestra=datos, imagen_rol=imagen_rol)

@lMaestra_bp.route('/guardaListaMaestra', methods=['POST'])
@login_required
def guardaListaMaestra():
    if request.method == 'POST':
        datos_form = {
            'area': request.form.get('Area'),
            'tipo_documento': request.form.get('tipoDoc'),
            'consecutivo': request.form.get('consecutivo'),
            'int_ext': request.form.get('int_ext'),
            'medio': request.form.get('medio'),
            'nombre_documento': request.form.get('nombre_documento'),
            'procedimiento': request.form.get('procedimiento'),
            'fecha_aprobacion': request.form.get('fecha_aprobacion'),
            'version': request.form.get('version'),
            'responsable_aprobacion': request.form.get('responsable_aprobacion'),
            'fecha_ultima_revision': request.form.get('fecha_revision'),
            'almacenamiento_como': request.form.get('como_almacenamiento'),
            'almacenamiento_donde': request.form.get('donde_almacenamiento'),
            'clasificacion': request.form.get('clasificacionActivo'),
            'disponible_para': request.form.get('disponible'),
            'proteccion': request.form.get('proteccion'),
            'tiempo_activo': request.form.get('activo_tiempo'),
            'tiempo_inactivo': request.form.get('inactivo_tiempo'),
            'disposicion': request.form.get('disposicion'),
            'estado': request.form.get('estado'),
        }
        guardar_lista_maestra(datos_form)
        return jsonify({
            'success': True,
            'message': 'Lista Maestra Guardada Correctamente',
            'newData': datos_form
        })
    else:
        return jsonify({
            'success': False,
            'message': "No se logro guardar en lista maestra"
        })
    
@lMaestra_bp.route('/actualizar_documento_maestro', methods=['POST'])
@login_required
def actualizar_documento_maestro_ruta():
    try:
        data = request.get_json()
        doc_id = data.get('id')
        columna = data.get('columna')
        valor = data.get('valor')

        # Validación para asegurarse de que todos los datos necesarios están presentes
        if not all([doc_id, columna, valor is not None]):
            return jsonify({'success': False, 'message': 'Faltan datos en la petición.'}), 400

        # Llama a la función del controlador para ejecutar la actualización
        actualizar_documento_maestro(doc_id, columna, valor)
        
        return jsonify({'success': True, 'message': 'Documento actualizado correctamente.'})

    except ValueError as e: # Captura errores de "Columna no permitida"
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        print(f"Error inesperado al actualizar documento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error interno del servidor.'}), 500
    
