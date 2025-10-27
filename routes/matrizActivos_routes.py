from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user, login_required
from controllers.matriz_controller import guardar_matriz, lista_matriz, modificar_matriz, lista_para_riesgos
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES, nombre_rol

mActivos_bp = Blueprint('mActivos', __name__)


@mActivos_bp.route('/Matriz_Activos', defaults={'role_id': None})
@mActivos_bp.route('/Matriz_Activos/<int:role_id>')
@login_required
def Matriz_Activos(role_id):
    is_role_override = role_id is not None

    if is_role_override:
        session['selected_rol'] = role_id
        rol = role_id
    else:
        rol = session.get('selected_rol', current_user.rol)

    nombre_del_rol = nombre_rol(rol)
    lista_procesos = PROCESOS_ROL.get(rol, [])

    if not lista_procesos:
        return render_template('MatrizActivos/Matriz_Activos.html',
                               usuario=current_user,
                               lista_procesos=[],
                               proceso_actual=None,
                               datos_matriz=[],
                               rol_seleccionado=rol,
                               nombre_rol_seleccionado=nombre_del_rol,
                               is_role_override=is_role_override)

    proceso_solicitado = request.args.get('proceso')

    if proceso_solicitado in lista_procesos:
        proceso_actual = proceso_solicitado
    else:
        proceso_actual = lista_procesos[0]

    datos_matriz = lista_matriz(rol, proceso_actual)
    return render_template('MatrizActivos/Matriz_Activos.html',
                           usuario=current_user,
                           lista_procesos=lista_procesos,
                           proceso_actual=proceso_actual,
                           datos_matriz=datos_matriz,
                           rol_seleccionado=rol,
                           nombre_rol_seleccionado=nombre_del_rol,
                           is_role_override=is_role_override)

@mActivos_bp.route('/cargar_matriz_proceso')
@login_required
def cargar_matriz_proceso():
    rol_id = session.get('selected_rol', current_user.rol)
    proceso_solicitado = request.args.get('proceso')
    lista_procesos = PROCESOS_ROL.get(rol_id, [])

    # Validación de seguridad: Asegúrate de que el usuario tiene permiso para ver este proceso.
    if proceso_solicitado not in lista_procesos:
        return "<p>Error: Proceso no válido o no autorizado.</p>", 403

    # Carga los datos solo para el proceso solicitado
    datos_matriz = lista_matriz(rol_id, proceso_solicitado)

    # Renderiza SOLO la plantilla parcial y la devuelve como HTML
    return render_template('MatrizActivos/_matriz_template.html',
                           proceso=proceso_solicitado,
                           datos_matriz=datos_matriz)



@mActivos_bp.route('/guardarMatriz', methods=['POST'])
@login_required # Añadido por seguridad
def guardarMatriz():
    if request.method == 'POST':
        try:
            datos_form = {
                'tipoActivo': request.form.get('tipoActivo'),
                'nombre_activo': request.form.get('nombre_activo'),
                'cant_activo': request.form.get('cant_activo'),
                'responsable_activo': request.form.get('responsable_activo'),
                'clasificacionActivo': request.form.get('clasificacionActivo'),
                'ConfidencialidadActivo': request.form.get('ConfidencialidadActivo'),
                'IntegridadActivo': request.form.get('IntegridadActivo'),
                'DisponibilidadActivo': request.form.get('DisponibilidadActivo'),
                'TotalActivo': request.form.get('TotalActivo')
            }
            proceso = request.form.get('proceso')

            rol = current_user.rol
            nuevo_registro_tupla = guardar_matriz(rol, proceso, datos_form)
            
            # --- DICCIONARIO CORREGIDO ---
            # Las claves aquí deben coincidir con las que usa 'updateUiMatrizActivos' en JS
            nuevo_registro_dict = {
                "id": nuevo_registro_tupla[0],
                "tipoActivo": nuevo_registro_tupla[1],
                "nombre_activo": nuevo_registro_tupla[2], # Clave corregida
                "cant_activo": nuevo_registro_tupla[3],
                "responsable_activo": nuevo_registro_tupla[4],
                "clasificacionActivo": nuevo_registro_tupla[5],
                "ConfidencialidadActivo": nuevo_registro_tupla[6],
                "IntegridadActivo": nuevo_registro_tupla[7],
                "DisponibilidadActivo": nuevo_registro_tupla[8],
                "TotalActivo": nuevo_registro_tupla[9]
            }

            return jsonify({
                'success': True,
                'message': 'Matriz de Activos guardada Correctamente',
                'newData': nuevo_registro_dict
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error al guardar: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})
@mActivos_bp.route('/actualizar_activo', methods=['POST'])
@login_required
def actualizar_activo():
    try:
        data = request.get_json()
        activo_id = data.get('id')
        columna = data.get('columna')
        valor = data.get('valor')

        if not all([activo_id, columna, valor is not None]):
            return jsonify({
                'success': False,
                'message': 'Faltan Datos'
            }), 400
        nuevo_total = modificar_matriz(activo_id, columna, valor)
        return jsonify({
            'success': True,
            'message': 'Activo Actualizado Correctamente',
            'nuevo_total': nuevo_total
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500