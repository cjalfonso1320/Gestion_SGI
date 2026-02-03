from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models import Usuarios
from models_rrhh import UsuariosRRHH
from models import obtener_roles
from controllers.user_controller import insertar_usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        tipo_login = request.form.get('tipo_login')
        
        user = None
        
        if tipo_login == 'sgi':
            user = Usuarios.obtener_por_username(username)
        elif tipo_login == 'rrhh':
            user = UsuariosRRHH.obtener_por_identificacion_correo(username)
        elif tipo_login == 'aula':
            flash('Modulo de aula vortual en contruccion', 'error')
            return redirect(url_for('auth.login'))
        
        if user and user.verifica_contrasena(password):
            session.pop('selected_rol', None)
            login_user(user)
            if tipo_login == 'rrhh':
                return redirect(url_for('rrhh.dashboard'))
            elif tipo_login == 'aula':
                return redirect(url_for('aula.aula'))
            else:
                return redirect(url_for('home.home'))
        
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('auth.login'))
    return render_template('log_reg/login.html')
            
        
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        rol = request.form.get('rol')

        insertar_usuario(name, username, password, rol)
        flash("Usuario creado correctamente")
        return redirect(url_for('auth.login'))
    roles =  obtener_roles()
    return render_template('log_reg/register.html', roles=roles)

@auth_bp.route('/logout')
@login_required
def logout():
    # Limpiar la sesión del rol seleccionado
    if 'selected_rol' in session:
        session.pop('selected_rol', None)
    
    logout_user()
    return redirect(url_for('auth.login'))