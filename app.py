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



#iniciar aplicacion
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')