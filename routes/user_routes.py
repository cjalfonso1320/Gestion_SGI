from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from controllers.user_controller import insertar_usuario, modificar_usuario, list_usuarios, eliminar, cuenta
from controllers.rol_controller import cuenta as count_roles
from models import obtener_roles, Usuarios

user_bp = Blueprint('user', __name__)

@user_bp.route('/usuarios')
def listar_usuarios():
    usuarios = list_usuarios()
    usuarios_cuenta = cuenta()
    cuenta_roles = count_roles()
    return render_template('admin/usuarios.html', usuarios=usuarios, usuario=current_user, usuarios_cuenta=usuarios_cuenta, roles_cuenta=cuenta_roles)

@user_bp.route('/nuevo_usuario', methods=['GET', 'POST'])
def nuevo_usuario():
    usuarios_cuenta = cuenta()
    roles_cuenta = count_roles()
    if request.method == 'POST':
        nombre = request.form['name']
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']
        insertar_usuario(nombre, username, password, rol)
        flash('Usuario Creado con exito')
        return redirect(url_for('user.listar_usuarios'))
    roles = obtener_roles()
    return render_template('admin/nuevo.html', roles=roles, usuario=current_user, usuarios_cuenta=usuarios_cuenta, roles_cuenta=roles_cuenta)

@user_bp.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    usuarios_cuenta = cuenta()
    roles_cuenta = count_roles()
    if request.method == 'POST':
        nombre = request.form['name']
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']
        modificar_usuario(id, nombre, username, password, rol)
        flash('Usuario modificado con exito')
        return redirect(url_for('user.listar_usuarios'))
    usuario = Usuarios.obtener_por_id(id)
    roles = obtener_roles()
    if not usuario:
        flash('Usuario no encontrado')
        return redirect(url_for('user.listar_usuarios'))
    return render_template('admin/editar.html', usuario=usuario, roles=roles, current_user=current_user, usuarios_cuenta=usuarios_cuenta, roles_cuenta=roles_cuenta)

@user_bp.route('/eliminar_usuario/<int:id>', methods=['GET', 'POST'])
def eliminar_usuario(id):
    try:
        eliminar(id)
        flash('Usuario eliminado con éxito')
    except Exception as e:
        flash(f'Error al eliminar usuario: {e}')
    return redirect(url_for('user.listar_usuarios'))