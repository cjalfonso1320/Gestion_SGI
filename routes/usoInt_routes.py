from flask import Blueprint, render_template
from flask_login import current_user, login_required
from controllers.usoInt_controller import subC_doc_UsoInt
from controllers.rol_controller import PROCESOS_ROL

usoInt_bp = Blueprint('usoInt', __name__)

@usoInt_bp.route('/UsoInterno')
@login_required
def UsoInterno():
    def CONTEXTO():
        archivos_UsoInterno = subC_doc_UsoInt('Información de Uso Interno')
        rol = current_user.rol
        procesos = PROCESOS_ROL.get(rol, [])
        return {
            'archivos_UsoInterno': archivos_UsoInterno,
            'procesos': procesos
        }
    return render_template('UsoInterno/UsoInterno.html', usuario=current_user, **CONTEXTO())