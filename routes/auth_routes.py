from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models import Usuarios
from models import obtener_roles
from controllers.user_controller import insertar_usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usuarios.obtener_por_username(username)
        if user and user.verifica_contrasena(password):
            # Limpiar la sesión del rol anterior si existe
            if 'selected_rol' in session:
                session.pop('selected_rol', None)
            
            login_user(user)
            return redirect(url_for('home.home'))  # ← usa el nombre del blueprint y la función
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