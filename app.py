from flask import Flask
from flask_login import LoginManager
from extension import mysql
from urllib.parse import quote
from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.user_routes import user_bp
from routes.roles_routes import rol_bp
from routes.indicadores_routes import ind_bp
from routes.rutas_routes import rutas_bp
from routes.usoInt_routes import usoInt_bp
from routes.matrizActivos_routes import mActivos_bp
from routes.listaMaestra_routes import lMaestra_bp
from routes.riesgos_routes import mRiesgos_bp
from routes.control_routes import control_bp
from routes.procedimientos_routes import proc_bp

from routes.aula_routes import aula_bp

from controllers.procedimientos_controller import cuenta_pendientes, lista_cambios_pendientes, lista_cambios_rechazados, cuenta_rechazados
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES


from routes.doc_routes import doc_bp

app = Flask(__name__)
app.config.from_object('config.Config')

mysql.init_app(app)

#login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from models import Usuarios

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.obtener_por_id(user_id)

@app.context_processor
def inject_global_context():
    """Inyecta variables comunes en TODAS las plantillas de la aplicación."""
    try:
        # Solo inyecta si hay un usuario logueado para evitar errores en páginas públicas
        from flask_login import current_user
        if current_user.is_authenticated:
            rol = current_user.rol
            return dict(
                pendientes=cuenta_pendientes(rol),
                rechazados=cuenta_rechazados(),
                cambios_pendientes=lista_cambios_pendientes(rol),
                cambios_rechazados=lista_cambios_rechazados(),
                # Añadimos procesos e imagen_rol para que estén disponibles globalmente
                procesos=PROCESOS_ROL.get(rol, []),
                imagen_rol=ROL_IMAGES.get(rol, 'imgs/user.png')
            )
    except ImportError:
        # Si flask_login no está disponible o hay otro error, no inyecta nada
        pass
    return {}


#registrar blueprints

            # Blueprints admin
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(user_bp)
app.register_blueprint(rol_bp)
app.register_blueprint(rutas_bp)

        # Blueprints user
app.register_blueprint(doc_bp)
app.register_blueprint(ind_bp)
app.register_blueprint(usoInt_bp)
app.register_blueprint(mActivos_bp)
app.register_blueprint(mRiesgos_bp)

    # Blueprints SGI
app.register_blueprint(lMaestra_bp)  
app.register_blueprint(control_bp)

#procedimeintos
app.register_blueprint(proc_bp)

#aula virtual
app.register_blueprint(aula_bp)



#iniciar aplicacion
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')