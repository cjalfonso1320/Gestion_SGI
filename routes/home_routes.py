from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from controllers.user_controller import cuenta
from controllers.rol_controller import cuenta as cuenta_roles, PROCESOS_ROL, ROL_IMAGES
from controllers.procedimientos_controller import cuenta_pendientes, lista_cambios_pendientes, lista_cambios_rechazados, cuenta_rechazados
from controllers.rrhh_controller import busca_asignacion_evaluacion

home_bp = Blueprint('home', __name__)




@home_bp.route('/home')
@login_required
def home():
    evaluacion_asginada = busca_asignacion_evaluacion(current_user.id)['cuenta'] > 0
    return render_template('home.html', usuario=current_user, evaluacion_asginada=evaluacion_asginada)


@home_bp.route('/api/cambios/pendientes')
@login_required
def cambios_pendientes():
    user_id = current_user.get_id() or ''
    if not user_id.startswith('sgi-'):
        return jsonify({'success': False, 'message': 'Acceso no permitido'}), 403

    cambios = lista_cambios_pendientes(current_user.rol)
    data = [
        {
            'id': cambio[0],
            'version': cambio[2],
            'solicitante': cambio[3],
            'descripcion': cambio[7],
            'documento': cambio[8],
        }
        for cambio in cambios
    ]
    return jsonify({'success': True, 'cambios': data})


@home_bp.route('/api/cambios/rechazados')
@login_required
def cambios_rechazados():
    user_id = current_user.get_id() or ''
    if not user_id.startswith('sgi-'):
        return jsonify({'success': False, 'message': 'Acceso no permitido'}), 403

    cambios = lista_cambios_rechazados()
    data = [
        {
            'solicitante': cambio[3],
            'descripcion': cambio[7],
            'documento': cambio[8],
        }
        for cambio in cambios
    ]
    return jsonify({'success': True, 'cambios': data})
