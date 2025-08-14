from flask import Blueprint, render_template, request, flash, redirect, url_for
from controllers.rutas_controller import listar_rutas, modificar_ruta, elimina_ruta
from controllers.user_controller import cuenta as cuentaRoles
from controllers.rol_controller import cuenta as cuentaUsuarios
from flask_login import current_user


rutas_bp = Blueprint('rutas', __name__)

@rutas_bp.route('/listaRutas')
def lista_rutas():
    usuarios_cuenta = cuentaUsuarios()
    roles_cuenta = cuentaRoles()
    rutas = listar_rutas()
    return render_template('admin/rutas.html', usuarios_cuenta=usuarios_cuenta, roles_cuenta=roles_cuenta, usuario=current_user, rutas=rutas)

@rutas_bp.route('/editar_ruta/<int:id>', methods=['GET', 'POST'])
def editar_ruta(id):
    cuenta_usuarios = cuentaUsuarios()
    cuenta_roles = cuentaRoles()
    if request.method == 'POST':
        ruta = request.form['ruta']
        modificar_ruta(id, ruta)
        flash('Rol modificado con éxito')
        return redirect(url_for('rutas.lista_rutas'))
    rutas = listar_rutas()
    ruta_actual = next((r for r in rutas if r[0] == id), None)
    if not ruta_actual:
        flash('Ruta no encontrado')
        return redirect(url_for('rutas.lista_rutas'))
    return render_template('admin/editar_ruta.html', rutas=rutas, usuario=current_user, cuenta_usuarios=cuenta_usuarios, roles_cuenta=cuenta_roles, ruta_actual=ruta_actual)
    


