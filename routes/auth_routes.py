from urllib.parse import urljoin
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import current_user, login_user, logout_user, login_required
from extension import mysql, limiter



from models import obtener_roles
from models_rrhh import UsuariosRRHH, ROL_TALENTO_HUMANO
from controllers.user_controller import insertar_usuario
from utils.access import sgi_admin_required
from controllers.aula_controller import busca_estudiante, actualiza_password
from utils.security_logger import log_login_failed, log_login_success, logout as log_logout, password_changed
from flask import session as flask_session
from utils.email_utils import enviar_correo
from itsdangerous import URLSafeTimedSerializer as Serializer
from utils.password_utils import hash_password
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)


def validar_fortaleza_password(password):
    """Valida que la contraseña cumpla requisitos mínimos de seguridad."""
    errores = []
    if len(password) < 8:
        errores.append('Debe tener al menos 8 caracteres')
    if not any(c.isupper() for c in password):
        errores.append('Debe contener al menos una mayúscula')
    if not any(c.islower() for c in password):
        errores.append('Debe contener al menos una minúscula')
    if not any(c.isdigit() for c in password):
        errores.append('Debe contener al menos un número')
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for c in password):
        errores.append('Debe contener al menos un carácter especial')
    return errores


@auth_bp.route('/', methods=['GET', 'POST'])
@limiter.limit("10 per minute", methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        tipo_login = request.form.get('tipo_login')
        
        user = None
        
        # 1. Identificar al usuario según el tipo
        if tipo_login == 'sgi':
            from models import Usuarios
            user = Usuarios.obtener_por_username(username)
        elif tipo_login == 'rrhh':
            user = UsuariosRRHH.obtener_por_identificacion_correo(username)
        elif tipo_login == 'estudiante':
            from models_estudiante import Estudiante
            user = Estudiante.obtener_por_identificacion(username)

        # 2. Validar contraseña y loguear (Lógica única para todos)
        # ── DEBUG LOGIN ──
        if user:
            print(f"[DEBUG LOGIN] User encontrado: tipo={tipo_login}, identificacion={getattr(user, 'identificacion', 'N/A')}")
            print(f"[DEBUG LOGIN] password_hash (primeros 50): {str(getattr(user, 'password_hash', ''))[:50]}...")
            resultado_verify = user.verifica_contrasena(password)
            print(f"[DEBUG LOGIN] Resultado verifica_contrasena: {resultado_verify}")
        else:
            print(f"[DEBUG LOGIN] User NO encontrado para username='{username}' tipo={tipo_login}")

        if user and user.verifica_contrasena(password):
            # Empleados retirados (activo = 2) no pueden acceder a la aplicación
            if tipo_login in ('rrhh', 'estudiante') and getattr(user, 'activo', None) == 2:
                log_login_failed(
                    username=username,
                    tipo_login=tipo_login,
                    ip_address=request.remote_addr,
                    reason='Empleado retirado',
                )
                flash('Acceso denegado: tu cuenta está inactiva (empleado retirado). Contacta a Recursos Humanos.', 'error')
                return redirect(url_for('auth.login'))

            # El módulo RRHH es solo para el rol SGI Talento Humano
            if tipo_login == 'rrhh' and getattr(user, 'sgi_rol_id', None) != ROL_TALENTO_HUMANO:
                log_login_failed(
                    username=username,
                    tipo_login=tipo_login,
                    ip_address=request.remote_addr,
                    reason='Sin rol SGI Talento Humano',
                )
                flash('Acceso denegado: el módulo RRHH es solo para el rol SGI Talento Humano', 'error')
                return redirect(url_for('auth.login'))

            login_user(user)  # Registra la sesión en Flask-Login
            # Regenerar session ID (prevenir session fixation)
            session_data = dict(flask_session)
            flask_session.clear()
            flask_session.update(session_data)

            # Registrar login exitoso
            log_login_success(
                username=username,
                tipo_login=tipo_login,
                ip_address=request.remote_addr,
            )
            print(f"[DEBUG LOGIN] Login EXITOSO para {tipo_login}:{username}")
            print(f"[DEBUG LOGIN] primer_ingreso={getattr(user, 'primer_ingreso', 'N/A')}")

            # Verificar si el empleado necesita confirmar sus datos personales (cada 3 meses)
            if tipo_login == 'rrhh':
                from controllers.rrhh_controller import obtener_datos_confirmacion, necesita_confirmacion_datos
                fecha_conf = getattr(user, 'fecha_confirmacion_datos', None)
                if necesita_confirmacion_datos(fecha_conf):
                    session['requiere_confirmacion_datos'] = True
                else:
                    session.pop('requiere_confirmacion_datos', None)

            # 3. Redirecciones específicas
            if tipo_login == 'estudiante':
                estudiante = busca_estudiante(user.identificacion)
                if estudiante:
                    session['estudiante'] = {
                        'identificacion': estudiante['identificacion'],
                        'nombre': f"{estudiante['nombres']} {estudiante['apellidos']}",
                        'ciudad': estudiante['ciudad'] or 'N/A',
                        'cargo': estudiante['cargo'] or 'N/A',
                        'proceso': estudiante['proceso'] or 'N/A'
                    }

                if str(user.primer_ingreso) == '1':
                    session['post_password_change_endpoint'] = 'aula.cursos_estudiante'
                    flash('Debe cambiar su contraseña inicial', 'info')
                    return redirect(url_for('auth.cambiar_password_inicial'))
                return redirect(url_for('aula.cursos_estudiante'))

            if tipo_login == 'sgi':
                session.pop('selected_rol', None)
                if str(user.primer_ingreso) == '1':
                    session['post_password_change_endpoint'] = 'home.home'
                    flash('Debe cambiar su contraseña inicial', 'info')
                    return redirect(url_for('auth.cambiar_password_inicial'))
                return redirect(url_for('home.home'))
            
            if tipo_login == 'rrhh':
                session.pop('selected_rol', None)
                if str(user.primer_ingreso) == '1':
                    session['post_password_change_endpoint'] = 'rrhh.dashboard'
                    flash('Debe cambiar su contraseña inicial', 'info')
                    return redirect(url_for('auth.cambiar_password_inicial'))
                return redirect(url_for('rrhh.dashboard'))
            
            return redirect(url_for('auth.login'))
        
        # Si llega aquí, falló la autenticación
        log_login_failed(
            username=username,
            tipo_login=tipo_login,
            ip_address=request.remote_addr,
            reason='Credenciales inválidas',
        )
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('auth.login'))
        
    return render_template('log_reg/new_login.html')


@auth_bp.route('/cambiar-password-inicial', methods=['GET', 'POST'])
@login_required
def cambiar_password_inicial():
    user_id = current_user.get_id() if hasattr(current_user, 'get_id') else ''
    if not user_id or not (user_id.startswith('sgi-') or user_id.startswith('estu-') or user_id.startswith('rrhh-')):
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nueva_pass = request.form.get('nueva_password') or request.form.get('nuevo_password')
        confirma_pass = request.form.get('confirmar_password') or request.form.get('confirma_password')

        if not nueva_pass or nueva_pass != confirma_pass:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('aulaVirtual/cambiar_pass.html')

        # Validar fortaleza de la contraseña
        errores = validar_fortaleza_password(nueva_pass)
        if errores:
            for err in errores:
                flash(f'Contraseña débil: {err}', 'error')
            return render_template('aulaVirtual/cambiar_pass.html')

        resultado = actualiza_password(current_user.identificacion, nueva_pass)
        print(f"[DEBUG CAMBIAR_PASS] actualiza_password retornó: {resultado}")
        print(f"[DEBUG CAMBIAR_PASS] user_id={user_id}, identificacion={current_user.identificacion}")
        
        if resultado:
            if hasattr(current_user, 'primer_ingreso'):
                current_user.primer_ingreso = 0
            endpoint = session.pop('post_password_change_endpoint', None)
            log_username = getattr(current_user, 'username', None) or getattr(current_user, 'nombres', 'desconocido')
            password_changed(
                user_id=current_user.get_id(),
                username=log_username,
            )
            flash('Contraseña actualizada correctamente', 'success')
            if endpoint:
                return redirect(url_for(endpoint))
            if user_id.startswith('sgi-'):
                return redirect(url_for('home.home'))
            elif user_id.startswith('rrhh-'):
                return redirect(url_for('rrhh.dashboard'))
            return redirect(url_for('aula.cursos_estudiante'))

        flash('No se pudo actualizar la contraseña. Intenta nuevamente.', 'error')

    return render_template('aulaVirtual/cambiar_pass.html')
            
        
        
@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
@sgi_admin_required
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        rol = request.form.get('rol')

        # Validar fortaleza de la contraseña
        errores = validar_fortaleza_password(password)
        if errores:
            for err in errores:
                flash(f'Contraseña débil: {err}', 'error')
            roles = obtener_roles()
            return render_template('log_reg/register.html', roles=roles)

        insertar_usuario(name, username, password, rol)
        flash("Usuario creado correctamente")
        return redirect(url_for('auth.login'))
    roles =  obtener_roles()
    return render_template('log_reg/register.html', roles=roles)

@auth_bp.route('/olvide-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=['POST'])
def forgot_password():
    """Muestra el formulario para solicitar restablecimiento de contraseña
    y envía el correo con el enlace de recuperación.
    """
    if request.method == 'POST':
        identificacion = request.form.get('identificacion', '').strip()

        if not identificacion:
            flash('Por favor ingresa tu número de identificación', 'error')
            return render_template('log_reg/forgot_password.html')

        # Buscar empleado por identificación y obtener su correo
        user = UsuariosRRHH.obtener_por_identificacion_correo(identificacion)

        if not user or not user.correo:
            # No revelar si la identificación existe o no por seguridad
            flash('Si la identificación está registrada, recibirás un enlace al correo asociado.', 'info')
            return render_template('log_reg/forgot_password.html')

        # Generar token con expiración de 1 hora
        s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset')
        token = s.dumps({'user_id': user.id, 'email': user.correo})
        expira = datetime.now() + timedelta(hours=1)

        # Construir enlace de restablecimiento
        base_url = current_app.config.get('BASE_URL', '')
        if base_url:
            reset_url = urljoin(base_url, url_for('auth.reset_password', token=token))
        else:
            reset_url = url_for('auth.reset_password', token=token, _external=True)

        asunto = "🔐 Restablecimiento de contraseña - SGI DIGICOM"
        mensaje_html = f"""\
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Restablecer Contraseña</title></head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
  <table role="presentation" width="100%%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8;padding:30px 10px;">
    <tr><td align="center">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.10);">
        <tr><td style="background:linear-gradient(135deg,#1e3a8a,#2563eb);padding:40px 36px 32px;text-align:center;">
          <div style="font-size:48px;line-height:1;margin-bottom:12px;">🔐</div>
          <h1 style="margin:0 0 6px;color:#ffffff;font-size:26px;font-weight:700;">Restablece tu Contraseña</h1>
          <p style="margin:0;color:#bfdbfe;font-size:15px;">Has solicitado un cambio de contraseña en el SGI</p>
        </td></tr>
        <tr><td style="padding:36px 36px 28px;">
          <p style="margin:0 0 22px;color:#1e293b;font-size:16px;line-height:1.6;">
            Hola <strong>{user.nombres} {user.apellidos}</strong>, hemos recibido una solicitud
            para restablecer la contraseña de tu cuenta en el
            <strong>Sistema de Gestión Integral (SGI)</strong>.
          </p>
          <p style="margin:0 0 22px;color:#475569;font-size:14px;line-height:1.6;">
            Para crear una nueva contraseña, haz clic en el siguiente botón:
          </p>
          <table role="presentation" width="100%%" cellpadding="0" cellspacing="0">
            <tr><td align="center" style="padding:4px 0 10px;">
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr><td align="center" style="border-radius:10px;">
                  <a href="{reset_url}"
                     style="display:inline-block;padding:14px 40px;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;border-radius:10px;box-shadow:0 4px 12px rgba(37,99,235,0.30);">
                    🔐 Restablecer Contraseña
                  </a>
                </td></tr>
              </table>
            </td></tr>
          </table>
          <p style="margin:22px 0 0;color:#94a3b8;font-size:13px;line-height:1.5;">
            Este enlace expira en <strong>1 hora</strong>. Si no solicitaste este cambio,
            ignora este mensaje y tu contraseña seguirá siendo la misma.
          </p>
          <p style="margin:14px 0 0;color:#94a3b8;font-size:13px;line-height:1.5;text-align:center;border-top:1px solid #e2e8f0;padding-top:18px;">
            Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
            <span style="color:#3b82f6;word-break:break-all;">{reset_url}</span>
          </p>
        </td></tr>
        <tr><td style="background-color:#f8fafc;padding:22px 36px;text-align:center;border-top:1px solid #e2e8f0;">
          <p style="margin:0;color:#64748b;font-size:12px;">
            <strong>Sistema de Gestión Integral (SGI)</strong><br>
            © {datetime.now().year} Digicom Colombia
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""
        mensaje_texto = f"""
🔐 RESTABLECIMIENTO DE CONTRASEÑA

Hola {user.nombres} {user.apellidos},

Hemos recibido una solicitud para restablecer la contraseña de tu cuenta.

Para crear una nueva contraseña, visita el siguiente enlace:
{reset_url}

Este enlace expira en 1 hora.
Si no solicitaste este cambio, ignora este mensaje.

---
Sistema de Gestión Integral (SGI)
© {datetime.now().year} Digicom Colombia
"""

        enviado = enviar_correo([user.correo], asunto, mensaje_html, mensaje_texto)

        if not enviado:
            print(f"⚠️ No se pudo enviar el correo de restablecimiento a {user.correo}")
            # No revelar el error al usuario por seguridad

        flash('Si la identificación está registrada, recibirás un enlace al correo asociado.', 'info')
        return render_template('log_reg/forgot_password.html')

    return render_template('log_reg/forgot_password.html')


@auth_bp.route('/restablecer-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Verifica el token y permite al usuario establecer una nueva contraseña.

    El token tiene una validez de 1 hora. Si es válido, muestra el formulario
    para ingresar la nueva contraseña. Si es inválido o expiró, muestra error.
    """
    s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset')

    try:
        data = s.loads(token, max_age=3600)  # 1 hora de expiración
        user_id = data.get('user_id')
        email = data.get('email')
    except Exception:
        flash('El enlace de restablecimiento es inválido o ha expirado. Solicita uno nuevo.', 'error')
        return render_template('log_reg/forgot_password.html')

    if request.method == 'POST':
        nueva_pass = request.form.get('nueva_password')
        confirma_pass = request.form.get('confirmar_password')

        if not nueva_pass or nueva_pass != confirma_pass:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('log_reg/reset_password.html', token=token, email=email)

        # Validar fortaleza
        errores = validar_fortaleza_password(nueva_pass)
        if errores:
            for err in errores:
                flash(f'Contraseña débil: {err}', 'error')
            return render_template('log_reg/reset_password.html', token=token, email=email)

        # Actualizar contraseña en la base de datos
        user = UsuariosRRHH.obtener_por_id(f"rrhh-{user_id}")
        if not user:
            flash('Usuario no encontrado', 'error')
            return render_template('log_reg/forgot_password.html')

        try:
            cur = mysql.connection.cursor()
            nuevo_hash = hash_password(nueva_pass)
            cur.execute(
                "UPDATE users_rrhh SET password = %s, primer_ingreso = 0 WHERE id = %s",
                (nuevo_hash, user_id)
            )
            mysql.connection.commit()
            cur.close()

            password_changed(
                user_id=f"rrhh-{user_id}",
                username=user.nombres or email
            )

            flash('¡Contraseña actualizada correctamente! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Error al actualizar password: {e}")
            flash('Error al actualizar la contraseña. Intenta nuevamente.', 'error')
            return render_template('log_reg/reset_password.html', token=token, email=email)

    return render_template('log_reg/reset_password.html', token=token, email=email)


@auth_bp.route('/logout')
@login_required
def logout():
    # Limpiar datos de sesión
    session.pop('selected_rol', None)
    session.pop('estudiante', None)

    # Registrar cierre de sesión (no crítico - si falla, igual cerramos sesión)
    try:
        username = getattr(current_user, 'username', None) or getattr(current_user, 'nombres', 'desconocido')
        log_logout(user_id=current_user.get_id(), username=username)
    except Exception as e:
        print(f"[LOGOUT] Warning: no se pudo registrar el logout: {e}")

    # Cerrar sesión Flask-Login
    try:
        logout_user()
    except Exception as e:
        print(f"[LOGOUT] Warning: logout_user falló, forzando limpieza: {e}")
        session.clear()

    # Si el cierre fue por inactividad, el login mostrará el aviso correspondiente
    if request.args.get('expirada'):
        return redirect(url_for('auth.login', expirada=1))
    return redirect(url_for('auth.login'))
