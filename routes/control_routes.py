from flask import Blueprint, render_template, send_file, abort, request
from flask_login import current_user
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES

control_bp = Blueprint('control', __name__)

@control_bp.route('/control')
def control():
    rol = current_user.rol
    imagen_rol = ROL_IMAGES.get(rol, 'imgs/user.png')
    procesos = PROCESOS_ROL.get(rol, [])
    return render_template('Control/Control.html', imagen_rol=imagen_rol, procesos=procesos, usuario=current_user)