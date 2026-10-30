"""Aplicación principal del Sistema de Gestión Integral (SGI).

Inicializa y configura la aplicación Flask con todas sus extensiones:
base de datos MySQL, autenticación Flask-Login, protección CSRF,
limitación de tasa (rate limiting), cabeceras de seguridad HTTP,
gestión de sesiones y registro de blueprints.

Configuración de seguridad:
    - Cookies HttpOnly, SameSite=Strict, Secure en producción.
    - Timeout de sesión por inactividad (20 minutos) con regeneración periódica.
    - CSRF habilitado con expiración de 1 hora.
    - Cabeceras HTTP (CSP, HSTS, X-Frame-Options, etc.).
    - Rate limiting: 200 req/día, 50 req/hora.
"""

from flask import Flask, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, timedelta, timezone
from flask_login import LoginManager, current_user, logout_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from extension import mysql, limiter
from models_rrhh import ROL_TALENTO_HUMANO
from utils.security_logger import logout as log_logout
import os


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

from routes.rrhh_routes import rrhh_bp

from routes.aula_routes import aula_bp
from routes.whatsapp_webhook import webhook_bp

from controllers.procedimientos_controller import cuenta_pendientes, lista_cambios_pendientes, lista_cambios_rechazados, cuenta_rechazados
from controllers.rrhh_controller import total_empleados, total_empleados_retirados
from controllers.rrhh_controller import grupo_nomina, tipo_contrato
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES


from routes.doc_routes import doc_bp


app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/gestion'
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1, x_host=1)
app.config.from_object('config.Config')
UPLOAD_FOLDER_EMPLEADOS = os.path.join('static', 'uploads', 'empleados')
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', ' png', 'tiff'}
app.config['UPLOAD_FOLDER_EMPLEADOS'] = UPLOAD_FOLDER_EMPLEADOS

# --- SEGURIDAD: Cookies ---
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Strict'
app.config['REMEMBER_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'

# --- SEGURIDAD: Timeout de sesión ---
# La sesión se cierra por inactividad: 20 minutos sin actividad/requests.
# PERMANENT_SESSION_LIFETIME rige la expiración de la cookie (se renueva con
# cada respuesta, por lo que equivale a una ventana móvil de 20 min de inactividad).
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)
SESSION_INACTIVITY_MINUTES = 20  # Cerrar sesión tras 20 min sin actividad
SESSION_REFRESH_MINUTES = 30  # Regenerar session ID cada 30 min

# --- SEGURIDAD: CSRF Protection ---
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hora
csrf = CSRFProtect(app)
# Excluir webhook de WhatsApp de CSRF (Meta no envía token)
csrf.exempt(webhook_bp)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Responde correctamente cuando el token CSRF falla.

    Suele ocurrir cuando la sesión expira o se regenera y el token que tenía
    la página ya no coincide. En peticiones AJAX/API se responde JSON para que
    el frontend lo maneje; en formularios HTML se muestra un aviso y se vuelve
    al login (sin asumir que fue por inactividad, ya que un token puede vencer
    por otras razones como el WTF_CSRF_TIME_LIMIT).
    """
    es_api = '/api/' in request.path or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if es_api:
        return jsonify({
            'success': False,
            'error': 'Tu sesión expiró. Inicia sesión nuevamente.',
            'expirada': True
        }), 403
    flash('La sesión expiró o el token de seguridad no es válido. Inicia sesión nuevamente.', 'error')
    return redirect(url_for('auth.login'))

# --- SEGURIDAD: Rate Limiting ---
limiter.init_app(app)

# --- SEGURIDAD: Cabeceras HTTP (after_request) ---
@app.after_request
def add_security_headers(response):
    """Agrega cabeceras de seguridad HTTP a todas las respuestas.

    Incluye protección contra:
        - MIME sniffing (X-Content-Type-Options).
        - Clickjacking (X-Frame-Options).
        - XSS reflejado (X-XSS-Protection).
        - Fugas de referer (Referrer-Policy).
        - APIs no utilizadas (Permissions-Policy).
        - Ataques XSS/inyección (Content-Security-Policy).
        - Strikes de seguridad (HSTS en producción con preload).

    Args:
        response: Objeto Response de Flask a modificar.

    Returns:
        Response: La misma respuesta con las cabeceras agregadas.
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

    # --- X-Frame-Options / CSP: manejo especial para PDFs ---
    # Las rutas de PDF ya definen sus propios headers (ALLOWALL para permitir
    # visualización en <object>/<iframe> en dispositivos móviles).
    # No sobrescribir si la ruta ya definió X-Frame-Options.
    es_pdf = response.content_type and 'application/pdf' in response.content_type

    if 'X-Frame-Options' not in response.headers:
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # CSP - Content Security Policy
    # Incluye blob: para visores de PDF internos del navegador (móvil y escritorio),
    # https: para recursos externos, y frame-ancestors para restringir framing.
    # NOTA: Para respuestas PDF, el CSP no aplica (el navegador usa su visor interno).
    if not es_pdf:
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: "
                "https://fonts.googleapis.com https://www.google.com https://pro.fontawesome.com "
                "https://cdn.jsdelivr.net https://code.jquery.com "
                "https://maxcdn.bootstrapcdn.com https://stackpath.bootstrapcdn.com "
                "https://www.youtube.com; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: blob: https:; "
            "font-src 'self' data: blob: https:; "
            "connect-src 'self' https: blob:; "
            "frame-ancestors 'self' https://servicios.digicom.com.co; "
            "object-src 'self' blob:; "
            "frame-src 'self' blob: https://www.youtube.com https:; "
            "worker-src 'self' blob:; "
        )

    # Forzar visualización inline de PDFs en lugar de descarga
    if es_pdf:
        if 'Content-Disposition' not in response.headers:
            filename = request.path.split('/')[-1] or 'documento.pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{filename}"'

    if os.getenv('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return response


# --- SEGURIDAD: Timeout por inactividad y regeneración periódica de sesión ---
@app.before_request
def session_timeout_and_refresh():
    """Cierra la sesión por inactividad y regenera el session ID periódicamente.

    Se ejecuta antes de cada request. Si el usuario está autenticado:
        1. Marca session.permanent = True para que PERMANENT_SESSION_LIFETIME aplique.
        2. Si pasaron más de SESSION_INACTIVITY_MINUTES desde la última actividad
           (request), cierra la sesión: registra el evento, hace logout y redirige
           al login (o responde 401 JSON si es una petición AJAX/API).
        3. Cada SESSION_REFRESH_MINUTES minutos, rota el session ID copiando
           los datos de sesión, limpiando y restaurándolos (previene session fixation).
    """
    try:
        if not current_user.is_authenticated:
            return
        session.permanent = True
        now = datetime.now(timezone.utc)

        # 1. Cierre por inactividad (20 minutos sin actividad)
        last_activity = session.get('_last_activity')
        if last_activity:
            try:
                last_dt = datetime.fromisoformat(str(last_activity))
                if (now - last_dt).total_seconds() > SESSION_INACTIVITY_MINUTES * 60:
                    # Registrar cierre por inactividad (no crítico)
                    try:
                        username = getattr(current_user, 'username', None) or getattr(current_user, 'nombres', 'desconocido')
                        log_logout(user_id=current_user.get_id(), username=username)
                    except Exception:
                        pass
                    try:
                        logout_user()
                    except Exception as e:
                        print(f"[SESSION] logout_user falló al expirar por inactividad: {e}")
                    session.clear()
                    # Respuesta según el tipo de request
                    es_api = '/api/' in request.path or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                    if es_api:
                        return jsonify({
                            'success': False,
                            'error': 'Tu sesión expiró por inactividad. Inicia sesión nuevamente.',
                            'expirada': True
                        }), 401
                    return redirect(url_for('auth.login', expirada=1))
            except (ValueError, TypeError):
                pass

        # 2. Regeneración periódica del session ID
        last_refresh = session.get('_last_regeneration')
        if last_refresh:
            try:
                last_dt = datetime.fromisoformat(str(last_refresh))
                elapsed = (now - last_dt).total_seconds()
                if elapsed > SESSION_REFRESH_MINUTES * 60:
                    # Rotar session ID: copiar datos, limpiar, restaurar
                    data = dict(session)
                    session.clear()
                    session.update(data)
            except (ValueError, TypeError):
                pass
        session['_last_activity'] = now.isoformat()
        session['_last_regeneration'] = now.isoformat()
    except Exception as e:
        # NUNCA dejar que la gestión de sesión genere un error 500:
        # si algo falla aquí, se registra y el request continúa normalmente.
        import traceback
        traceback.print_exc()
        print(f"[SESSION] Error inesperado en session_timeout_and_refresh: {e}")


mysql.init_app(app)

# login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos según su tipo (prefijo del ID).

    Los IDs tienen prefijos para distinguir tipos de usuario:
        - 'sgi-': Usuario administrativo SGI (models.Usuarios).
        - 'rrhh-': Empleado de RRHH (models_rrhh.UsuariosRRHH).
        - 'estu-': Estudiante de aula virtual (models_estudiante.Estudiante).

    Args:
        user_id: ID único del usuario con prefijo de tipo.

    Returns:
        UserMixin: Instancia del usuario correspondiente, o None si no existe.
    """
    user_id = str(user_id)

    try:
        if user_id.startswith("sgi-"):
            from models import Usuarios
            return Usuarios.obtener_por_id(user_id)

        if user_id.startswith("rrhh-"):
            from models_rrhh import UsuariosRRHH
            return UsuariosRRHH.obtener_por_id(user_id)

        if user_id.startswith("estu-"):
            from models_estudiante import Estudiante
            return Estudiante.obtener_por_id(user_id)
    except Exception as e:
        print(f"Error en load_user: {e}")
        return None

    return None


@app.context_processor
def inject_global_context():
    """Inyecta variables de contexto global en todas las plantillas Jinja2.

    Proporciona valores como pendientes de aprobación, foto del usuario,
    procesos del rol, imagen del rol, y conteos de RRHH según el tipo
    de usuario autenticado.

    Returns:
        dict: Diccionario con las variables de contexto.
    """
    from flask_login import current_user
    try:
        # Valores por defecto para evitar errores de "undefined"
        context = {
            'pendientes': 0,
            'rechazados': 0,
            'procesos': [],
            'imagen_rol': 'imgs/user.png'
        }

        # Solo ejecutamos lógica de base de datos si el usuario es de Flask-Login (Admin/RRHH)
        if current_user.is_authenticated:
            user_id = current_user.get_id()

            # Consultar foto del empleado desde users_rrhh
            foto_usuario = None
            try:
                real_id = int(str(user_id).split('-')[1])
                cur = mysql.connection.cursor()
                cur.execute("SELECT foto_path FROM users_rrhh WHERE id = %s", (real_id,))
                row = cur.fetchone()
                cur.close()
                if row and row[0]:
                    foto = row[0].replace('\\', '/')
                    if foto.startswith('static/'):
                        foto = foto[7:]
                    foto_usuario = foto
            except Exception:
                pass
            context['foto_usuario'] = foto_usuario

            if user_id and user_id.startswith('sgi-'):
                rol = current_user.rol
                context.update(dict(
                    pendientes=cuenta_pendientes(rol),
                    rechazados=cuenta_rechazados(),
                    procesos=PROCESOS_ROL.get(rol, []),
                    imagen_rol=ROL_IMAGES.get(rol, 'imgs/user.png')
                ))
            elif user_id and user_id.startswith('rrhh-'):
                # Solo el rol SGI Talento Humano tiene acceso al módulo RRHH
                if getattr(current_user, 'sgi_rol_id', None) == ROL_TALENTO_HUMANO:
                    context['empleados'] = total_empleados()
                    context['empleados_retirados'] = total_empleados_retirados()
                    context['cuenta_nominas'] = len(grupo_nomina())
                    context['consecutivo_contratos'] = tipo_contrato()

        return context
    except Exception as e:
        print(f"Error en context_procesos: {e}")
        return context  # Retorna los valores por defecto en lugar de tronar


# registrar blueprints

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

# procedimeintos
app.register_blueprint(proc_bp)

# aula virtual
app.register_blueprint(aula_bp)

# rrhh
app.register_blueprint(rrhh_bp)

# whatsapp webhook
app.register_blueprint(webhook_bp)


# iniciar aplicacion
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5001)
