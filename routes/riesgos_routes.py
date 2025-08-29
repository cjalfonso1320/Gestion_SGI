from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES
from controllers.matriz_controller import  lista_para_riesgos
from controllers.riesgos_controller import guardar_riesgo, lista_riesgos

mRiesgos_bp = Blueprint('mRiesgos', __name__)
@mRiesgos_bp.route('/Matriz_Riesgos')
def Matriz_Riesgos():
    rol = current_user.rol
    imagen_rol = ROL_IMAGES.get(rol, 'imgs/user.png')
    # Determinar el tipo de riesgo basado en el rol
    if rol in [2, 4, 5, 6, 7, 10, 11, 12, 13]:
        riesgo_tipo = 'operacional'
    elif rol in [8, 14, 15, 16, 17, 18, 19, 20, 21]:
        riesgo_tipo = 'administrativo'
    elif rol == 9:
        riesgo_tipo = 'T-I'
    else:
        riesgo_tipo = None # Rol sin riesgo definido

    # Cargar datos solo si hay un tipo de riesgo
    if riesgo_tipo:
        activos = lista_para_riesgos(riesgo_tipo)
        datos_riesgos = lista_riesgos(riesgo_tipo)
    else:
        activos = []
        datos_riesgos = []
    procesos = PROCESOS_ROL.get(rol, [])

    return render_template(
        'MatrizRiesgos/Matriz_Riesgos.html',
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



