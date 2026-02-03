from flask import Blueprint, render_template, redirect, url_for, flash
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
import os
from controllers.rrhh_controller import total_empleados, empleados_lista, empleado_lista_completo, estado_civil, grupo_sanguineo, eps, afp, cesantias, ccf, arl, tipo_contrato, sede, escolaridad, bancos, grupo_nomina, cargos, ciudades
from controllers.rrhh_controller import crear_grupoNomina, editar_grupoNomina, eliminar_grupoNomina, crear_cargo, editar_cargo, eliminar_cargo, crear_empleado, guardar_documentos_estudio, lista_documentos_estudio_empleado, actualizar_empleado, desactivar_empleado
from controllers.rrhh_controller import activar_empleado, contratos_empleado
from utils.files import guardar_archivo, guardar_archivos_multiples

rrhh_bp = Blueprint('rrhh', __name__, url_prefix='/rrhh')

def CONTEXTO():
        empleados_list = empleados_lista()
        estadoCivil = estado_civil()
        grupoSanguineo = grupo_sanguineo()
        epsS = eps()
        afpS = afp()
        cesantiasS = cesantias()
        ccfS = ccf()
        arlS = arl()
        tipoContrato = tipo_contrato()
        sedeS = sede()
        nivelEscolaridad = escolaridad()
        bancoS = bancos()
        nominaS = grupo_nomina()
        cargoS = cargos()
        ciudadS = ciudades()
        return {
            'empleados_list': empleados_list,
            'estadoCivil': estadoCivil,
            'grupoSanguineo': grupoSanguineo,
            'epsS': epsS,
            'afpS': afpS,
            'cesantiasS': cesantiasS,
            'ccfS': ccfS,
            'arlS': arlS,
            'tipoContrato': tipoContrato,
            'sedeS': sedeS,
            'nivelEscolaridad': nivelEscolaridad,
            'bancoS': bancoS,
            'nominaS': nominaS,
            'cargoS': cargoS,
            'ciudadS': ciudadS
        }

def admin_rrhh_required(func):
    def wrapper(*args, **kwargs):
        #verifica si current user tiene el atributo de cargo
        if not current_user.is_authenticated:
            flash("Debe iniciar sesion prmiero", "error")
            return redirect(url_for('auth.login'))
        
        #acceso denegado por cargo
        if not hasattr(current_user, 'cargo') or current_user.cargo not in [1, 9, 26, 29]:
            flash(f"Acceso denegado por cargo, su cargo es: {getattr(current_user, 'cargo', 'ninguno')}", 'error')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@rrhh_bp.route('/dashboard_admin')
@login_required
@admin_rrhh_required
def dashboard():
    empleados = total_empleados()
    return render_template('rrhh/dashboard_admin.html', usuario=current_user, empleados=empleados)


###########EMPLEADOS##########
@rrhh_bp.route('/empleados')
@login_required
@admin_rrhh_required
def empleados():
    return render_template('rrhh/empleados.html', 
                            usuario=current_user, 
                            **CONTEXTO()
                            )
    
@rrhh_bp.route('/empleados/crear', methods=['POST'])
@login_required
@admin_rrhh_required
def crear_empleado_rrhh():
    try:
        data = request.form
        cedula = request.files.get('cedula')
        foto = request.files.get('foto')
        documentos_estudio = request.files.getlist('documentos_estudio[]')
        
        identificacion = data.get('identificacion')
        
        #carpeta por empleado
        carpeta_empleado = os.path.join(
            current_app.config['UPLOAD_FOLDER_EMPLEADOS'],
            identificacion,
        )
        ruta_cedula = guardar_archivo(cedula, carpeta_empleado, 'cedula')
        ruta_foto = guardar_archivo(foto, carpeta_empleado, 'foto')
        
        empleado_id = crear_empleado(data, ruta_cedula, ruta_foto)
        
        #documentos de estudio
        carpeta_estudios = os.path.join(carpeta_empleado, 'estudios')
        rutas_estudio = guardar_archivos_multiples(
            documentos_estudio,
            carpeta_estudios,
            'estudio'
        )
        guardar_documentos_estudio(empleado_id, rutas_estudio)
        empleado = empleado_lista_completo(empleado_id)
        documentos_estudio_empleado = lista_documentos_estudio_empleado(empleado_id)
        documentos_estudio_empleado = [
            d['ruta'].replace('\\','/')
            for d in documentos_estudio_empleado
        ]
        empleado = empleado[0]
        empleado['documentos_estudio'] = documentos_estudio_empleado
        return jsonify({'success':True, 'empleado':empleado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    

@rrhh_bp.route("/empleados/<int:id>/json", methods=["GET"])
@login_required
@admin_rrhh_required
def obtener_empleado(id):
    empleado = empleado_lista_completo(id)
    empleado["fecha_ingreso"] = formatear_fecha(empleado["fecha_ingreso"])
    empleado["fecha_nacimiento"] = formatear_fecha(empleado["fecha_nacimiento"])
    if not empleado:
        return jsonify({"success": False})
    
    return jsonify({
        "success": True,
        "empleado": empleado
    })
    
@rrhh_bp.route("/empleados/editar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def editar_empleado(id):
    data = request.form
    actualizar_empleado(id, data)
    empleado = empleado_lista_completo(id)
    return jsonify({
        "success": True,
        "empleado": empleado
    })
    
@rrhh_bp.route("/empleados/retirar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def retirar_empleado(id):
    try:
        data = request.get_json()
        fecha_retiro = data.get('fecha_retiro')
        print(fecha_retiro)
        desactivar_empleado(id, fecha_retiro)
        return jsonify({
            "success": True,
            "message": "Empleado Retirado Correctamente"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
##########GRUPOS DE NOMINA##########
@rrhh_bp.route('/grupos_nomina')
@login_required
@admin_rrhh_required
def grupos_nomina():
    nominaS = grupo_nomina()
    return render_template('rrhh/gruposNomina.html', usuario=current_user, nominaS=nominaS)

@rrhh_bp.route('/grupos_nomina/crear', methods=['POST'])
@login_required
@admin_rrhh_required
def crear_grupo_nomina():
    try:
        data = request.form
        grupo_nomina = crear_grupoNomina(data)
        
        return jsonify({
            'success': True,
            'GrupoNomina': {
                'id': grupo_nomina.id,
                'nombre': grupo_nomina.nombre
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
@rrhh_bp.route('/grupos_nomina/editar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def editar_grupo_nomina(id):
    try:
        data = request.get_json()
        editar_grupoNomina(id, data['nombre'])
        
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False, 'error':str(e)}), 400
    
@rrhh_bp.route('/grupos_nomina/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def eliminar_gurpo_nomina(id):
    try:
        eliminar_grupoNomina(id)
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False, 'error':str(e)}), 400
    
    
#########CARGOS##########
@rrhh_bp.route('/cargos')
@login_required
@admin_rrhh_required
def cargos_vista():
    cargoS = cargos()
    return render_template('rrhh/cargos.html', usuario=current_user, cargoS=cargoS)

@rrhh_bp.route('/cargos/crear', methods=['POST'])
@login_required
@admin_rrhh_required
def crear_cargos():
    try:
        data = request.form
        cargo = crear_cargo(data)
        
        return jsonify({
            'success': True,
            'Cargo': {
                'id': cargo.id,
                'nombre': cargo.nombre
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
@rrhh_bp.route('/cargos/editar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def editar_cargos(id):
    try:
        data = request.get_json()
        editar_cargo(id, data['nombre'])
        
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False, 'error':str(e)}), 400
        
@rrhh_bp.route('/cargos/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def eliminar_cargos(id):
    try:
        eliminar_cargo(id)
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False, 'error':str(e)}), 400


 #### documentos de estudio
@rrhh_bp.route('/empleados/<int:id>/documentos', methods=['GET'])
@login_required
@admin_rrhh_required
def documentos_estudio_empleado(id):
    try:
        docs = lista_documentos_estudio_empleado(id)
        rutas = [
            d["ruta"].replace("\\", "/")
            for d in docs
        ]
        return jsonify({"success": True, "documentos":rutas})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)}), 400


############EMPLEADOS RETIRADOS
@rrhh_bp.route('/empleados_retirados')
@login_required
@admin_rrhh_required
def empleados_retirados():
    empleados_list = empleados_lista()
    return render_template('rrhh/empleados_retirados.html', 
                            usuario=current_user, 
                            empleados_list=empleados_list
                            )
    
##reactivar usuario
@rrhh_bp.route("/empleados/activar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def reactivar_empleado(id):
    try:
        data = request.get_json()
        fecha_reingreso = data.get('fecha_ingreso')
        activar_empleado(id, fecha_reingreso)
        return jsonify({
            "success": True,
            "message": "Empleado Activado Correctamente"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
#contratos vista
@rrhh_bp.route('/empleados/<int:id>/contratos', methods=['GET'])
@login_required
@admin_rrhh_required
def contratos_empleado_ver(id):
    try:
        contratos = contratos_empleado(id)
        for contrato in contratos:
            contrato['fecha_ingreso'] = formatear_fecha(contrato['fecha_ingreso'])
            contrato['fecha_finalizacion'] = formatear_fecha(contrato['fecha_finalizacion'])
        return jsonify({
            "success": True,
            "contratos": contratos
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
#formato de fecha
def formatear_fecha(fecha):
    if fecha:
        return fecha.strftime("%Y-%m-%d")
    return ""