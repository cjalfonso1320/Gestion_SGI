from flask import Blueprint, render_template
from flask_login import login_required, current_user
from controllers.user_controller import cuenta
from controllers.rol_controller import cuenta as cuenta_roles, PROCESOS_ROL, ROL_IMAGES
from controllers.procedimientos_controller import cuenta_pendientes, lista_cambios_pendientes, lista_cambios_rechazados, cuenta_rechazados

home_bp = Blueprint('home', __name__)




@home_bp.route('/home')
@login_required
def home():
    rol =  current_user.rol
    usuarios_cuenta = cuenta()
    roles_cuenta = cuenta_roles()
    
    if rol == 1:
        return render_template('home_admin.html', usuario=current_user, usuarios_cuenta=usuarios_cuenta, roles_cuenta=roles_cuenta)
    else:
        return render_template('home.html', usuario=current_user)