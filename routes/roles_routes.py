from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from controllers.rol_controller import list_roles, cuenta as count_roles, insertar_rol, modificar_rol, elimina_rol
from controllers.user_controller import cuenta as count_usuarios

rol_bp = Blueprint('rol', __name__)

@rol_bp.route('/roles')
def listar_roles():
    cuenta_usuarios = count_usuarios()
    cuenta_roles = count_roles()
    roles = list_roles()
    return render_template('admin/roles.html', roles=roles, usuario=current_user, usuarios_cuenta=cuenta_usuarios, roles_cuenta=cuenta_roles)

@rol_bp.route('/nuevo_rol', methods=['GET', 'POST'])
def nuevo_rol():
    cuenta_usuarios = count_usuarios()
    cuenta_roles = count_roles()
    if request.method == 'POST':
        rol = request.form['rol']
        insertar_rol(rol)
        flash('Rol creado con éxito')
        return redirect(url_for('rol.listar_roles'))
    return render_template('admin/nuevo_rol.html', usuario=current_user, usuarios_cuenta=cuenta_usuarios, roles_cuenta=cuenta_roles)

@rol_bp.route('/editar_rol/<int:id>', methods=['GET', 'POST'])
def editar_rol(id):
    cuenta_usuarios = count_usuarios()
    cuenta_roles = count_roles()
    if request.method == 'POST':
        rol = request.form['rol']
        modificar_rol(id, rol)
        flash('Rol modificado con éxito')
        return redirect(url_for('rol.listar_roles'))
    roles = list_roles()
    rol_actual = next((r for r in roles if r[0] == id), None)
    if not rol_actual:
        flash('Rol no encontrado')
        return redirect(url_for('rol.listar_roles'))
    return render_template('admin/editar_rol.html', rol=rol_actual, usuario=current_user, usuarios_cuenta=cuenta_usuarios, roles_cuenta=cuenta_roles)

@rol_bp.route('/eliminar_rol/<int:id>', methods=['GET', 'POST'])
def eliminar_rol(id):
    try:
        elimina_rol(id)
        flash('Rol eliminado con éxito')
    except Exception as e:
        flash(f'Error al eliminar rol: {e}')
    return redirect(url_for('rol.listar_roles'))