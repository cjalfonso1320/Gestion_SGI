from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user, login_required
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES, nombre_rol
from controllers.matriz_controller import  lista_para_riesgos
from controllers.riesgos_controller import guardar_riesgo, lista_riesgos

mRiesgos_bp = Blueprint('mRiesgos', __name__)

@mRiesgos_bp.route('/Matriz_Riesgos', defaults={'role_id': None})
@mRiesgos_bp.route('/Matriz_Riesgos/<int:role_id>')
@login_required
def Matriz_Riesgos(role_id):
    is_role_override = role_id is not None

    if is_role_override:
        # Si se pasa un role_id en la URL, se usa ese y se guarda en sesión
        session['selected_rol'] = role_id
        rol = role_id
    else:
        # Si no, se usa el de la sesión (si existe) o el del usuario actual
        rol = session.get('selected_rol', current_user.rol)

    nombre_del_rol = nombre_rol(rol)
    imagen_rol = ROL_IMAGES.get(rol, 'imgs/user.png')

    if rol in [2, 4, 5, 6, 7, 10, 11, 12, 13]:
        riesgo_tipo = 'operacional'
    elif rol in [8, 14, 15, 16, 17, 18, 19, 20, 21]:
        riesgo_tipo = 'administrativo'
    elif rol == 9:
        riesgo_tipo = 'T-I'
    else:
        riesgo_tipo = None # Rol sin riesgo definido

    if riesgo_tipo:
        activos = lista_para_riesgos(riesgo_tipo)
        datos_riesgos = lista_riesgos(riesgo_tipo)
    else:
        activos = []
        datos_riesgos = []
    procesos = PROCESOS_ROL.get(rol, [])

    return render_template(
        'MatrizRiesgos/Matriz_Riesgos.html',
        rol_seleccionado=rol,
        nombre_rol_seleccionado=nombre_del_rol,
        is_especific_role=is_role_override,
        is_role_override=is_role_override,
        usuario=current_user,
        activos=activos,
        datos_riesgos=datos_riesgos,
        riesgo=riesgo_tipo,
        imagen_rol=imagen_rol,
        procesos=procesos
    )

@mRiesgos_bp.route('/guardar_riesgo', methods=['POST'])
@login_required
def guardar_riesgos():
    if request.method == 'POST':
        try:
            datos_form = request.form.to_dict()
            nuevo_registro_dict = guardar_riesgo(datos_form)

            if not nuevo_registro_dict:
                raise Exception("No se pudo recuperar el registro despues de guardarlo.")
            return jsonify({
                'success': True,
                'message': 'Riesgo guardado correctamente',
                'newData': nuevo_registro_dict
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f"Errro al guardar: {str(e)}"
            })
    return jsonify({
        'success': False,
        'message': 'Metodo no permitido'
    })