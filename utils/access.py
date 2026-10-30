"""Control de acceso y permisos de usuarios.

Proporciona decoradores para restringir el acceso a rutas según
el tipo de usuario y su rol en el sistema SGI.

Roles:
    - sgi_admin_required: Solo usuarios SGI con rol de administrador (rol=1).
"""

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def sgi_admin_required(view_func):
    """Decorador que restringe el acceso a usuarios administradores SGI.

    Verifica que el usuario esté autenticado, que su ID comience con 'sgi-'
    y que tenga rol igual a 1 (administrador). Si no cumple, redirige con
    un mensaje de error.

    Args:
        view_func: Función de vista a proteger.

    Returns:
        callable: Función decorada con la verificación de permisos.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        user_id = current_user.get_id() or ""
        if not user_id.startswith("sgi-") or getattr(current_user, "rol", None) != 1:
            flash("No tiene permisos para acceder a esta seccion.", "error")
            return redirect(url_for("home.home"))

        return view_func(*args, **kwargs)

    return wrapped_view
