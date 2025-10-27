from flask import Blueprint, render_template, send_file, abort, request
from flask_login import current_user
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES

control_bp = Blueprint('control', __name__)

@control_bp.route('/control')
def control():
    return render_template('Control/Control.html', usuario=current_user)