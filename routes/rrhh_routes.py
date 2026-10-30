from flask import Blueprint, render_template, redirect, url_for, flash, make_response
from flask import request, jsonify, current_app, send_file
from flask_login import login_required, current_user
import os
from datetime import datetime
import zipfile
import shutil
import unicodedata
from fpdf import FPDF

from controllers.rrhh_controller import total_empleados, empleados_lista, empleado_lista_completo, estado_civil, grupo_sanguineo, eps, afp, cesantias, ccf, arl, tipo_contrato, sede, escolaridad, bancos, grupo_nomina, cargos, ciudades, total_empleados_retirados, tipo_doc
from controllers.rrhh_controller import crear_grupoNomina, editar_grupoNomina, eliminar_grupoNomina, crear_cargo, editar_cargo, eliminar_cargo, crear_empleado, guardar_documentos_estudio, lista_documentos_estudio_empleado, actualizar_empleado, desactivar_empleado
from controllers.rrhh_controller import activar_empleado, contratos_empleado, total_empleados_retirados, eliminar_empleado_db
from utils.files import guardar_archivo, guardar_archivos_multiples

from controllers.rrhh_controller import importar_empleados_plantilla, actualizar_empleados_plantilla, empleado_existe, actualiza_foto, actualiza_cedula, guardar_documento_estudio, empleado_lista_completo_por_identificacion
from controllers.rrhh_controller import obtener_datos_certificado, tipoContrato_id, actualiza_consecutivo, genera_consecutivo
from controllers.rrhh_controller import empleados_para_mensajeria, enviar_mensaje_masivo
from controllers.rrhh_controller import obtener_mensajes_buzon, obtener_mensajes_enviados_buzon, marcar_mensaje_leido, contar_mensajes_no_leidos
from controllers.rrhh_controller import procesar_otrosi_db, habilita_evaluacion, consulta_evaluacion_habilitada, obtener_plantilla, consulta_tipo_competencias, consulta_criterios, consulta_preguntas, consulta_plantillas_evaluacion_desde_asignaciones, id_plantilla_existe_en_asignaciones_evaluacion, id_plantilla_aceptada_al_editar_pregunta
from controllers.rrhh_controller import obtener_datos_confirmacion, guardar_confirmacion_datos, necesita_confirmacion_datos
from controllers.rrhh_controller import editar_tipo_competencia, eliminar_tipo_competencia, editar_criterio_competencia, eliminar_criterio_competencia, editar_pregunta_evaluacion, eliminar_pregunta_evaluacion
from controllers.rrhh_controller import crear_tipo_competencia, crear_criterio_competencia, crear_pregunta_evaluacion, consulta_porcentajes_tipo, consulta_porcentajes_competencia, guardaEvaluacion, consulta_resultados_evaluacion
from controllers.rrhh_controller import consulta_evaluaciones_pendientes_evaluado, guardar_aprobacion_evaluado, guardar_aprobacion_rrhh, busca_asignacion_evaluacion, restablecer_password_db, importar_contratos_plantilla, asignar_rol_sgi_db
from controllers.rol_controller import list_roles
from utils.password_utils import hash_password
from utils.security_logger import password_changed as log_password_changed
from utils.security_logger import log_employee_deleted, log_employee_delete_failed
from models_rrhh import ROL_TALENTO_HUMANO


import pandas as pd
import io
import uuid

rrhh_bp = Blueprint('rrhh', __name__, url_prefix='/rrhh')


#------------------------------------------------------
#---------------------- UTILIDADES --------------------
#------------------------------------------------------
def limpiar_fecha(val):
    if pd.isna(val) or val == '': return None
    try:
        # Ya es un datetime/Timestamp → formatear directamente
        if hasattr(val, 'strftime'):
            return val.strftime("%Y-%m-%d")
        # Valor numérico → número de serie de Excel (ej: 45000 = 2023-03-15)
        if not isinstance(val, str):
            from datetime import timedelta
            try:
                n = float(val)
            except (ValueError, TypeError):
                return pd.to_datetime(val).strftime("%Y-%m-%d") if pd.notna(val) else None
            # Excel serial dates: day 1 = 1900-01-01, epoch = 1899-12-30
            # Valores entre 1 y ~2958465 son fechas Excel válidas
            if n < 1 or n > 100000:
                return None
            excel_epoch = datetime(1899, 12, 30)
            return (excel_epoch + timedelta(days=int(n))).strftime("%Y-%m-%d")
        # String → pandas to_datetime
        return pd.to_datetime(val).strftime("%Y-%m-%d")
    except:
        return None
def limpiar_texto(val, default="N/A"):
    if pd.isna(val) or str(val).strip().lower() == 'nan' or str(val).strip() == "":
        return default
    return str(val).strip().upper()   
def get_map(data_list, key='nombre'):
    return {str(item[key]).upper(): item['id'] for item in data_list}
def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento:
        return 0
    try:
        fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        hoy = datetime.now()
        
        edad = hoy.year - fecha_nac.year -((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad
    except:
        return 0  
def calcula_antiguedad(fecha_ingreso):
    if not fecha_ingreso:
        return 0
    try:
        fecha_ing = datetime.strptime(fecha_ingreso, "%Y-%m-%d")
        hoy = datetime.now()
        
        antiguedad = hoy.year - fecha_ing.year -((hoy.month, hoy.day) < (fecha_ing.month, fecha_ing.day))
        return antiguedad
    except:
        return 0
def obtener_mapas():
    return {
            'ESTADO_CIVIL': get_map(estado_civil()),
            'GS': get_map(grupo_sanguineo(), 'tipo'),
            'CIUDAD': get_map(ciudades()),
            'EPS': get_map(eps()),
            'AFP': get_map(afp()),
            'CESANTIAS': get_map(cesantias()),
            'CCF': get_map(ccf()),
            'ARL': get_map(arl()),
            'TIPO_CONTRATO': get_map(tipo_contrato()),
            'CARGO': get_map(cargos()),
            'SEDE': get_map(sede()),
            'BANCO': get_map(bancos()),
            'NOMINA': get_map(grupo_nomina()),
            'ESCOLARIDAD': get_map(escolaridad()),
            'TIPO_DOC': get_map(tipo_doc())
        }
def get_id_mapas(mapas, map_name, val):
    if pd.isna(val): return None
    return mapas[map_name].get(str(val).strip().upper())
def formatear_fecha(fecha):
    if not fecha:
        return ""
    if isinstance(fecha, str):
        return fecha
    try:
        return fecha.strftime("%Y-%m-%d")
    except AttributeError:
        return str(fecha)
def clave_alfabetica(texto):
    """Clave de ordenamiento alfabético que ignora tildes y mayúsculas.

    Ej: 'Término Fijo' y 'TERMINO FIJO' ordenan juntos; con el orden
    normal de Python, los caracteres acentuados en mayúscula (É, Í, Ó...)
    quedarían después de la Z.
    """
    texto_norm = unicodedata.normalize('NFD', str(texto).upper())
    return ''.join(c for c in texto_norm if unicodedata.category(c) != 'Mn')

def guardar_excel_errores(errores):
    """
    Genera un Excel con la lista de errores y lo guarda temporalmente.
    Retorna el nombre del archivo (para el endpoint de descarga).
    """
    if not errores:
        return None
    df_errores = pd.DataFrame(errores)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_errores.to_excel(writer, index=False, sheet_name='Errores')
        workbook = writer.book
        worksheet = writer.sheets['Errores']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#FF4444', 'font_color': '#FFFFFF', 'border': 1})
        for col_num, value in enumerate(df_errores.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 30)
        # Aplicar color rojo suave a las filas de error
        error_format = workbook.add_format({'bg_color': '#FFF0F0'})
        for row_num in range(1, len(errores) + 1):
            worksheet.set_row(row_num, None, error_format)
    output.seek(0)
    # Directorio temporal para archivos de error
    errores_dir = os.path.join(current_app.root_path, 'static', 'tmp_errores')
    os.makedirs(errores_dir, exist_ok=True)
    # Limpiar archivos antiguos (> 1 hora)
    ahora = datetime.now()
    for f in os.listdir(errores_dir):
        fpath = os.path.join(errores_dir, f)
        if os.path.isfile(fpath):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                if (ahora - mtime).total_seconds() > 3600:
                    os.remove(fpath)
            except:
                pass
    filename = f"errores_importacion_{uuid.uuid4().hex[:8]}.xlsx"
    filepath = os.path.join(errores_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(output.getvalue())
    return filename

#------------------------------------------------------
#---------------------- CONTEXTO ----------------------
#------------------------------------------------------      
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
        roles_sgi = list_roles()
        empleados_retirados = total_empleados_retirados()
        cuenta_nominas = len(nominaS)
        tipoDoc = tipo_doc()
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
            'ciudadS': ciudadS,
            'roles_sgi': roles_sgi,
            'empleados_retirados': empleados_retirados,
            'cuenta_nominas': cuenta_nominas,
            'consecutivo_contratos': tipoContrato,
            'tipoDoc': tipoDoc
        }

#------------------------------------------------------
#----------------- ADMIN REQUIRED ---------------------
#------------------------------------------------------
def admin_rrhh_required(func):
    def wrapper(*args, **kwargs):
        #verifica si current user tiene el atributo de cargo
        if not current_user.is_authenticated:
            # Si es petición AJAX, devolver JSON en vez de redirect
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json':
                return jsonify({'success': False, 'error': 'Debe iniciar sesión primero'}), 401
            flash("Debe iniciar sesion primero", "error")
            return redirect(url_for('auth.login'))
        
        #acceso denegado: el módulo RRHH es solo para el rol SGI Talento Humano
        if getattr(current_user, 'sgi_rol_id', None) != ROL_TALENTO_HUMANO:
            mensaje = 'Acceso denegado: el módulo RRHH es solo para el rol SGI Talento Humano'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json':
                return jsonify({'success': False, 'error': mensaje}), 403
            flash(mensaje, 'error')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

#------------------------------------------------------
#---------------- DASHBOARD ADMIN ---------------------
#------------------------------------------------------
@rrhh_bp.route('/dashboard_admin')
@login_required
@admin_rrhh_required
def dashboard():
    empleados = total_empleados()
    empleados_retirados = total_empleados_retirados()
    cuenta_nominas = len(grupo_nomina())
    conseccontratos = tipo_contrato()
    evaluacion_asginada = busca_asignacion_evaluacion(current_user.id)['cuenta'] > 0
    
    return render_template('home.html', 
                           usuario=current_user, 
                           empleados=empleados, 
                           empleados_retirados=empleados_retirados, 
                           cuenta_nominas=cuenta_nominas,
                           consecutivo_contratos=conseccontratos,
                           evaluacion_asginada=evaluacion_asginada)

#------------------------------------------------------
#---------------------- EMPLEADOS ---------------------
#------------------------------------------------------
@rrhh_bp.route('/empleados')
@login_required
@admin_rrhh_required
def empleados():
    return render_template('rrhh/empleados.html', 
                            usuario=current_user, 
                            **CONTEXTO()
                            )

#------------------------------------------------------
#---------------------- CREA EMPLEADOS ----------------
#------------------------------------------------------    
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
            d['ruta'].replace('\\', '/')
            for d in documentos_estudio_empleado
        ]
        empleado['documentos_estudio'] = documentos_estudio_empleado
        return jsonify({'success':True, 'empleado':empleado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
#------------------------------------------------------
#--------------- OBTENER EMPLEADO ---------------------
#------------------------------------------------------
@rrhh_bp.route("/empleados/<int:id>/json", methods=["GET"])
@login_required
@admin_rrhh_required
def obtener_empleado(id):
    try:
        empleado = empleado_lista_completo(id)
        if not empleado:
            return jsonify({"success": False, "error": "Empleado no encontrado"})
        
        empleado["fecha_ingreso"] = formatear_fecha(empleado.get("fecha_ingreso"))
        empleado["fecha_nacimiento"] = formatear_fecha(empleado.get("fecha_nacimiento"))
        
        return jsonify({
            "success": True,
            "empleado": empleado
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error interno: {str(e)}"
        }), 500
 
#------------------------------------------------------
#-----------------EDITAR EMPLEADO ---------------------
#------------------------------------------------------   
@rrhh_bp.route("/empleados/editar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def editar_empleado(id):
    try:
        data = request.form
        cedula = request.files.get('cedula')
        foto = request.files.get('foto')
        documentos_estudio = request.files.getlist('documentos_estudio[]')
        
        identificacion = data.get('identificacion')
        
        actualizar_empleado(id, data)
        
        # Manejar subida de cédula al editar
        if cedula and cedula.filename:
            carpeta_empleado = os.path.join(
                current_app.config['UPLOAD_FOLDER_EMPLEADOS'],
                identificacion,
            )
            ruta_cedula = guardar_archivo(cedula, carpeta_empleado, 'cedula')
            if ruta_cedula:
                actualiza_cedula(id, ruta_cedula)
        
        # Manejar subida de foto al editar
        if foto and foto.filename:
            carpeta_empleado = os.path.join(
                current_app.config['UPLOAD_FOLDER_EMPLEADOS'],
                identificacion,
            )
            ruta_foto = guardar_archivo(foto, carpeta_empleado, 'foto')
            if ruta_foto:
                actualiza_foto(id, ruta_foto)
        
        # Manejar subida de documentos de estudio al editar
        if documentos_estudio and any(d.filename for d in documentos_estudio):
            carpeta_estudios = os.path.join(
                current_app.config['UPLOAD_FOLDER_EMPLEADOS'],
                identificacion,
                'estudios'
            )
            rutas_estudio = guardar_archivos_multiples(
                documentos_estudio,
                carpeta_estudios,
                'estudio'
            )
            if rutas_estudio:
                guardar_documentos_estudio(id, rutas_estudio)
        
        empleado = empleado_lista_completo(id)
        
        # Devolver también documentos de estudio actualizados
        documentos_estudio_empleado = lista_documentos_estudio_empleado(id)
        documentos_estudio_empleado = [
            d['ruta'].replace('\\', '/')
            for d in documentos_estudio_empleado
        ]
        empleado['documentos_estudio'] = documentos_estudio_empleado
        
        return jsonify({
            "success": True,
            "empleado": empleado
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": traceback.format_exc()
        }), 500

#------------------------------------------------------
#--------------- RETIRAR EMPLEADO ---------------------
#------------------------------------------------------   
@rrhh_bp.route("/empleados/retirar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def retirar_empleado(id):
    try:
        data = request.get_json()
        fecha_retiro = data.get('fecha_retiro')
        motivo_retiro = data.get('motivo_retiro')
        desactivar_empleado(id, fecha_retiro, motivo_retiro)
        return jsonify({
            "success": True,
            "message": "Empleado Retirado Correctamente"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

#------------------------------------------------------
#---------- ELIMINAR EMPLEADO (DEFINITIVO) ------------
#------------------------------------------------------
@rrhh_bp.route("/empleados/eliminar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def eliminar_empleado(id):
    """Elimina definitivamente un empleado de la base de datos.

    Requiere la contraseña del usuario con la sesión abierta como
    validación adicional antes de ejecutar el borrado.
    """
    try:
        data = request.get_json() or {}
        password = (data.get('password') or '').strip()

        if not password:
            return jsonify({"success": False, "error": "Debe ingresar su contraseña"}), 400

        # Validar la contraseña del usuario con la sesión abierta
        if not current_user.verifica_contrasena(password):
            log_employee_delete_failed(
                getattr(current_user, 'id', None),
                getattr(current_user, 'identificacion', ''),
                id,
                'Contraseña incorrecta'
            )
            return jsonify({"success": False, "error": "Contraseña incorrecta"}), 403

        success, error = eliminar_empleado_db(id)
        if not success:
            return jsonify({"success": False, "error": error}), 500

        log_employee_deleted(
            getattr(current_user, 'id', None),
            getattr(current_user, 'identificacion', ''),
            id
        )
        return jsonify({"success": True, "message": "Empleado eliminado definitivamente"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

#------------------------------------------------------
#------------------ GRUPOS NOMINA ---------------------
#------------------------------------------------------
@rrhh_bp.route('/grupos_nomina')
@login_required
@admin_rrhh_required
def grupos_nomina():
    nominaS = grupo_nomina()
    cuenta_nominas = len(nominaS)
    empleados_retirados = total_empleados_retirados()
    conseccontratos = tipo_contrato()
    return render_template('rrhh/gruposNomina.html', 
                           usuario=current_user, 
                           nominaS=nominaS, 
                           cuenta_nominas=cuenta_nominas,
                           empleados_retirados=empleados_retirados,
                           consecutivo_contratos=conseccontratos)

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
    
    
#------------------------------------------------------
#---------------------- CARGOS ------------------------
#------------------------------------------------------
@rrhh_bp.route('/cargos')
@login_required
@admin_rrhh_required
def cargos_vista():
    cargoS = cargos()
    cuenta_nominas = len(grupo_nomina())
    empleados_retirados = total_empleados_retirados()
    conseccontratos = tipo_contrato()
    return render_template('rrhh/cargos.html',
                           usuario=current_user,
                           cargoS=cargoS,
                           cuenta_nominas=cuenta_nominas,
                           empleados_retirados=empleados_retirados,
                           consecutivo_contratos=conseccontratos)

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

#------------------------------------------------------
#---------------------- ESCOLARIDAD -------------------
#------------------------------------------------------
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


#------------------------------------------------------
#-------------- EMPLEADOS RETIRADOS -------------------
#------------------------------------------------------
@rrhh_bp.route('/empleados_retirados')
@login_required
@admin_rrhh_required
def empleados_retirados():
    contratos = tipo_contrato()
    ctx = CONTEXTO()
    # Ordenar por fecha de retiro (fecha_finalizacion del último contrato),
    # de más reciente a más antigua. Los que no tengan fecha van al final.
    ctx['empleados_list'] = sorted(
        ctx['empleados_list'],
        key=lambda e: str(e.get('fecha_finalizacion') or ''),
        reverse=True
    )
    return render_template('rrhh/empleados_retirados.html', 
                            usuario=current_user, 
                            contratos=contratos,
                            **ctx
                            )
    
#------------------------------------------------------
#---------------- ACTIVAR EMPLEADO --------------------
#------------------------------------------------------
@rrhh_bp.route("/empleados/activar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def reactivar_empleado(id):
    try:
        data = request.get_json()
        fecha_reingreso = data.get('fecha_ingreso')
        salario_basico = data.get('salario_basico')
        factor_no_salarial = data.get('factor_no_salarial')
        tipoContrato = data.get('tipo_contrato')
        print(tipoContrato)
        activar_empleado(id, fecha_reingreso, salario_basico, factor_no_salarial, tipoContrato)
        return jsonify({
            "success": True,
            "message": "Empleado Activado Correctamente"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
#------------------------------------------------------
#---------------------- CONTRATOS ---------------------
#------------------------------------------------------
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



#------------------------------------------------------
#------------------ ACCIONES MASIVAS ------------------
#------------------------------------------------------
@rrhh_bp.route('/descargar_plantilla_excel')
@login_required
@admin_rrhh_required
def descargar_plantilla_excel():
    #definimos columnas
    columnas = [
        'IDENTIFICACION', 'NOMBRES', 'APELLIDOS', 'CEDULA_EXPEDIDA_EN',
        'SEXO (M/F)', 'FECHA_NACIMIENTO (AAAA-MM-DD)', 'LUGAR_NACIMIENTO',
        'TIPO_DOC',
        'ESTADO_CIVIL', 'GRUPO_SANGUINEO', 'NUMERO_HIJOS', 'DIRECCION',
        'CIUDAD_BARRIO', 'BARRIO', 'LOCALIDAD', 'ESTRATO', 'TELEFONO_FIJO', 'CELULAR',
        'CORREO', 'CONTACTO_EMERGENCIA', 'TELEFONO_EMERGENCIA', 'PARENTESCO',
        'EPS', 'AFP', 'CESANTIAS', 'CCF', 'ARL', 'TIPO_CONTRATO', 'CARGO',
        'JORNADA', 'SEDE', 'FECHA_INGRESO (AAAA-MM-DD)', 'SALARIO_BASICO',
        'FACTOR_NO_SALARIAL', 'NUMERO_CUENTA', 'BANCO', 'GRUPO_NOMINA',
        'NIVEL_ESCOLARIDAD', 'PROGRAMA_ACADEMICO', 'ESTUDIA_ACTUALMENTE (SI/NO)',
        'NOMBRE_PROGRAMA_ACTUAL'
    ]
    #creamos dataframe con las columnas 
    df = pd.DataFrame(columns=columnas)
    
    #guardamos excel en buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla Empleados')
        
        #ajusta el ancho de las columnas
        workbook = writer.book
        worksheet = writer.sheets['Plantilla Empleados']
        
        #creamos hoja oculta para las listas desplegables
        hidden_sheet = workbook.add_worksheet('ListasDesplegables')
        hidden_sheet.hide()
        
        #obtenemos los datos de DB y los escribimos en la hoja oculta
        listas_db = [
            (0, [str(e['nombre']).upper()  for e in estado_civil()]),
            (1, [str(g['tipo']).upper()  for g in grupo_sanguineo()]),
            (2, [str(c['nombre']).upper()  for c in ciudades()]),
            (3, [str(e['nombre']).upper()  for e in eps()]),
            (4, [str(a['nombre']).upper()  for a in afp()]),
            (5, [str(c['nombre']).upper()  for c in cesantias()]),
            (6, [str(c['nombre']).upper()  for c in ccf()]),
            (7, [str(a['nombre']).upper()  for a in arl()]),
            (8, [str(t['nombre']).upper()  for t in tipo_contrato()]),
            (9, [str(c['nombre']).upper()  for c in cargos()]),
            (10, [str(s['nombre']).upper()  for s in sede()]),
            (11, [str(b['nombre']).upper()  for b in bancos()]),
            (12, [str(g['nombre']).upper()  for g in grupo_nomina()]),
            (13, [str(e['nombre']).upper()  for e in escolaridad()]),
            (14, [str(t['nombre']).upper()  for t in tipo_doc()]),
        ]
        # Ordenar alfabéticamente cada lista (ignora tildes y mayúsculas)
        listas_db = [(col, sorted(data, key=clave_alfabetica)) for col, data in listas_db]
        #escribir las listas en columnas de la hoja oculta
        for col, data in listas_db:
            for row, value in enumerate(data):
                hidden_sheet.write(row, col, value)
        #definir ranfos de validacion
        def aplicar_validacion(col_index, list_col_letter, num_items):
            #valida desde la fila 2 a la 10000
            worksheet.data_validation(1, col_index, 10000, col_index, {
                'validate': 'list',
                'source': f'=ListasDesplegables!{list_col_letter}1:{list_col_letter}${num_items}'
            })
        #aplicar validaciones a las columnas correspondientes
        worksheet.data_validation(1, 5, 10000, 5, {'validate': 'list', 'source': ['M', 'F']})
        worksheet.data_validation(1, 15, 10000, 15, {'validate': 'list', 'source': ['1', '2', '3', '4', '5', '6']})  # estrato
        
        #dinamicos desde BD
        aplicar_validacion(0, 'O', len(listas_db[14][1]))  # tipo_doc (col A)
        aplicar_validacion(8, 'A', len(listas_db[0][1]))  # estado_civil
        aplicar_validacion(9, 'B', len(listas_db[1][1]))  # grupo_sanguineo
        aplicar_validacion(12, 'C', len(listas_db[2][1]))  # ciudad_barrio
        aplicar_validacion(22, 'D', len(listas_db[3][1]))  # eps
        aplicar_validacion(23, 'E', len(listas_db[4][1]))  # afp
        aplicar_validacion(24, 'F', len(listas_db[5][1]))  # cesantias
        aplicar_validacion(25, 'G', len(listas_db[6][1]))  # ccf
        aplicar_validacion(26, 'H', len(listas_db[7][1]))  # arl
        aplicar_validacion(27, 'I', len(listas_db[8][1]))  # tipo_contrato
        aplicar_validacion(28, 'J', len(listas_db[9][1]))  # cargo
        aplicar_validacion(30, 'K', len(listas_db[10][1]))  # sede
        aplicar_validacion(35, 'L', len(listas_db[11][1]))  # banco
        aplicar_validacion(36, 'M', len(listas_db[12][1]))  # grupo_nomina
        aplicar_validacion(37, 'N', len(listas_db[13][1]))  # nivel_escolaridad
        
        #jornada y estudia actualmente (Estaticos)
        worksheet.data_validation(1, 29, 10000, 29, {'validate': 'list', 'source': ['DIURNO', 'TARDE', 'NOCTURNO']})
        worksheet.data_validation(1, 39, 10000, 39, {'validate': 'list', 'source': ['SI', 'NO']})
                
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 25)  # Ancho de columna de 25
            
    output.seek(0)
    
    return send_file(output, 
                     download_name="plantilla_empleados.xlsx",
                     as_attachment=True,                      
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

#------------------------------------------------------
#----------- PLANTILLA CONTRATOS --------
#------------------------------------------------------
@rrhh_bp.route("/descargar_plantilla_contratos")
@login_required
@admin_rrhh_required
def descargar_plantilla_contratos():
    """Genera plantilla Excel para carga masiva de contratos."""
    columnas = [
        "IDENTIFICACION",
        "SALARIO_BASICO",
        "FACTOR_NO_SALARIAL",
        "TIPO_CONTRATO",
        "CODIGO_CONTRATO",
        "FECHA_INICIAL",
        "FECHA_FINALIZACION",
        "ESTADO",
        "MOTIVO",
    ]
    df = pd.DataFrame(columns=columnas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Plantilla Contratos")
        workbook = writer.book
        worksheet = writer.sheets["Plantilla Contratos"]
        hidden_sheet = workbook.add_worksheet("ListasDesplegables")
        hidden_sheet.hide()
        tipos = sorted(
            (str(t["nombre"]).upper() for t in tipo_contrato()),
            key=clave_alfabetica
        )
        for row, value in enumerate(tipos):
            hidden_sheet.write(row, 0, value)
        worksheet.data_validation(1, 3, 10000, 3, {
            "validate": "list",
            "source": "=ListasDesplegables!$A$1:$A$" + str(len(tipos))
        })

        # --- ESTADO (columna H): formula que calcula ACTIVO/INACTIVO ---
        # Si FECHA_FINALIZACION (col G) está vacía => ACTIVO; si tiene fecha => INACTIVO.
        # Si no hay identificacion (col A) la fila no aplica (queda vacía).
        for row in range(2, 10001):
            worksheet.write_formula(
                row - 1, 7,
                f'=IF(A{row}="","",IF(G{row}="","ACTIVO","INACTIVO"))'
            )

        # --- MOTIVO (columna I): lista desplegable ---
        # Mismos motivos que el modal de retiro de empleados. Se guardan en la columna
        # B de la hoja oculta ListasDesplegables (la A es de TIPO_CONTRATO).
        motivos = sorted([
            "Con Justa Causa",
            "Mutuo Acuerdo",
            "Pensionado",
            "Sin Justa Causa",
            "Vencimiento de Contrato",
            "Voluntario",
            "Cambio a Productiva",
        ], key=clave_alfabetica)
        for row, value in enumerate(motivos):
            hidden_sheet.write(row, 1, value)
        worksheet.data_validation(1, 8, 10000, 8, {
            "validate": "list",
            "source": "=ListasDesplegables!$B$1:$B$" + str(len(motivos))
        })

        # --- MOTIVO obligatorio si FECHA_FINALIZACION no está vacía ---
        # La validación se aplica en FECHA_FINALIZACION (col G): Excel solo la dispara
        # al editar la celda, así que validar en MOTIVO no hacía nada cuando el usuario
        # ingresaba la fecha sin haber tocado MOTIVO. Con la validación en G el error
        # salta en el momento de escribir la fecha.
        worksheet.data_validation(1, 6, 10000, 6, {
            "validate": "custom",
            "value": '=OR($I2<>"",$G2="")',
            "ignore_blank": False,
            "error_title": "Motivo obligatorio",
            "error_message": "Si FECHA_FINALIZACION tiene valor, la columna MOTIVO es obligatoria.",
            "error_type": "stop"
        })

        header_format = workbook.add_format({"bold": True, "bg_color": "#D7E4BC", "border": 1})
        # Formato de texto para evitar que Excel elimine ceros a la izquierda
        text_format = workbook.add_format({'num_format': '@'})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            # Columna CODIGO_CONTRATO (indice 4) como texto para preservar ceros a la izquierda
            if col_num == 4:
                worksheet.set_column(col_num, col_num, 25, text_format)
            else:
                worksheet.set_column(col_num, col_num, 25)

    # --- Forzar allowBlank="0" en la validación de MOTIVO ---
    # xlsxwriter omite el atributo allowBlank cuando ignore_blank=False y, según
    # OOXML, la omisión equivale a "permitir vacío" (allowBlank=1), lo que dejaría
    # sin efecto la obligatoriedad de MOTIVO. Se inyecta el atributo reempaquetando
    # el zip con el XML de la hoja modificado.
    import zipfile
    raw = output.getvalue()
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "xl/worksheets/sheet1.xml":
                xml = data.decode("utf-8")
                # Aplicar a las validaciones custom (la de FECHA_FINALIZACION)
                xml = xml.replace('type="custom"', 'type="custom" allowBlank="0"')
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    output = buf
    output.seek(0)
    return send_file(
        output,
        download_name="plantilla_contratos.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@login_required
@admin_rrhh_required
@rrhh_bp.route('/descargar_plantilla_excel_debug')
def descargar_plantilla_excel_debug():
    """
    Genera la misma plantilla que descargar_plantilla_excel pero con la hoja
    de listas desplegables VISIBLE, para que el usuario pueda inspeccionar
    los valores de cada lista de validacion.
    """
    columnas = [
        'TIPO_DOC',
        'IDENTIFICACION', 'NOMBRES', 'APELLIDOS', 'CEDULA_EXPEDIDA_EN',
        'SEXO (M/F)', 'FECHA_NACIMIENTO (AAAA-MM-DD)', 'LUGAR_NACIMIENTO',
        'ESTADO_CIVIL', 'GRUPO_SANGUINEO', 'NUMERO_HIJOS', 'DIRECCION',
        'CIUDAD_BARRIO', 'BARRIO', 'LOCALIDAD', 'ESTRATO', 'TELEFONO_FIJO', 'CELULAR',
        'CORREO', 'CONTACTO_EMERGENCIA', 'TELEFONO_EMERGENCIA', 'PARENTESCO',
        'EPS', 'AFP', 'CESANTIAS', 'CCF', 'ARL', 'TIPO_CONTRATO', 'CARGO',
        'JORNADA', 'SEDE', 'FECHA_INGRESO (AAAA-MM-DD)', 'SALARIO_BASICO',
        'FACTOR_NO_SALARIAL', 'NUMERO_CUENTA', 'BANCO', 'GRUPO_NOMINA',
        'NIVEL_ESCOLARIDAD', 'PROGRAMA_ACADEMICO', 'ESTUDIA_ACTUALMENTE (SI/NO)',
        'NOMBRE_PROGRAMA_ACTUAL'
    ]
    df = pd.DataFrame(columns=columnas)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla Empleados')
        workbook = writer.book
        worksheet = writer.sheets['Plantilla Empleados']

        # HOJA DE LISTAS VISIBLE (sin .hide())
        listas_sheet = workbook.add_worksheet('ListasDesplegables')

        # Datos desde BD
        listas_db = [
            ('ESTADO_CIVIL',       [str(e['nombre']).upper()  for e in estado_civil()]),
            ('GRUPO_SANGUINEO',    [str(g['tipo']).upper()    for g in grupo_sanguineo()]),
            ('CIUDAD',             [str(c['nombre']).upper()  for c in ciudades()]),
            ('EPS',                [str(e['nombre']).upper()  for e in eps()]),
            ('AFP',                [str(a['nombre']).upper()  for a in afp()]),
            ('CESANTIAS',          [str(c['nombre']).upper()  for c in cesantias()]),
            ('CCF',                [str(c['nombre']).upper()  for c in ccf()]),
            ('ARL',                [str(a['nombre']).upper()  for a in arl()]),
            ('TIPO_CONTRATO',      [str(t['nombre']).upper()  for t in tipo_contrato()]),
            ('CARGO',              [str(c['nombre']).upper()  for c in cargos()]),
            ('SEDE',               [str(s['nombre']).upper()  for s in sede()]),
            ('BANCO',              [str(b['nombre']).upper()  for b in bancos()]),
            ('GRUPO_NOMINA',       [str(g['nombre']).upper()  for g in grupo_nomina()]),
            ('ESCOLARIDAD',        [str(e['nombre']).upper()  for e in escolaridad()]),
            ('TIPO_DOC',           [str(t['nombre']).upper()  for t in tipo_doc()]),
        ]

        # Escribir encabezados de lista en fila 0 y datos desde fila 1
        header_list_format = workbook.add_format({
            'bold': True, 'bg_color': '#E8EAF6', 'border': 1, 'align': 'center'
        })
        for col_idx, (nombre_lista, datos) in enumerate(listas_db):
            listas_sheet.write(0, col_idx, nombre_lista, header_list_format)
            for row_idx, value in enumerate(datos):
                listas_sheet.write(row_idx + 1, col_idx, value)
            listas_sheet.set_column(col_idx, col_idx, 35)

        # Mapeo: columna Excel (0-indexed) -> letra de columna en ListasDesplegables (A,B,C,...)
        def col_letter(idx):
            return chr(65 + idx)

        def aplicar_validacion(col_index, list_col_idx, num_items):
            letter = col_letter(list_col_idx)
            worksheet.data_validation(1, col_index, 10000, col_index, {
                'validate': 'list',
                'source': f'=ListasDesplegables!${letter}$2:${letter}${num_items + 1}'
            })

        # Aplicar validaciones
        worksheet.data_validation(1, 5, 10000, 5, {'validate': 'list', 'source': ['M', 'F']})
        worksheet.data_validation(1, 15, 10000, 15, {'validate': 'list', 'source': ['1', '2', '3', '4', '5', '6']})  # estrato

        aplicar_validacion(0,  14, len(listas_db[14][1]))  # tipo_doc (col A)
        aplicar_validacion(8,  0, len(listas_db[0][1]))   # estado_civil
        aplicar_validacion(9,  1, len(listas_db[1][1]))   # grupo_sanguineo
        aplicar_validacion(12, 2, len(listas_db[2][1]))   # ciudad_barrio
        aplicar_validacion(22, 3, len(listas_db[3][1]))   # eps
        aplicar_validacion(23, 4, len(listas_db[4][1]))   # afp
        aplicar_validacion(24, 5, len(listas_db[5][1]))   # cesantias
        aplicar_validacion(25, 6, len(listas_db[6][1]))   # ccf
        aplicar_validacion(26, 7, len(listas_db[7][1]))   # arl
        aplicar_validacion(27, 8, len(listas_db[8][1]))   # tipo_contrato
        aplicar_validacion(28, 9, len(listas_db[9][1]))   # cargo
        aplicar_validacion(30, 10, len(listas_db[10][1])) # sede
        aplicar_validacion(35, 11, len(listas_db[11][1])) # banco
        aplicar_validacion(36, 12, len(listas_db[12][1])) # grupo_nomina
        aplicar_validacion(37, 13, len(listas_db[13][1])) # nivel_escolaridad

        worksheet.data_validation(1, 29, 10000, 29, {'validate': 'list', 'source': ['DIURNO', 'TARDE', 'NOCTURNO']})
        worksheet.data_validation(1, 39, 10000, 39, {'validate': 'list', 'source': ['SI', 'NO']})

        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 25)

    output.seek(0)
    return send_file(
        output,
        download_name="plantilla_empleados_debug.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
       
@rrhh_bp.route('/empleados/importar_empleados', methods=['POST'])
@login_required
@admin_rrhh_required
def importar_empleados():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo.'}), 400
    file = request.files['file']
    try:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().upper() for c in df.columns]  
        mapas = obtener_mapas()  
        insertados = 0
        errores = []
        for idx, (_, row) in enumerate(df.iterrows()):
            r = row.to_dict()
            numero_fila = idx + 2  # +2 porque Excel fila 1 es encabezado
            
            ident = str(r.get('IDENTIFICACION')).split('.')[0]
            f_nacimiento = limpiar_fecha(r.get('FECHA_NACIMIENTO (AAAA-MM-DD)'))
            f_ingreso = limpiar_fecha(r.get('FECHA_INGRESO (AAAA-MM-DD)'))
            
            # Manejar tipo de contrato - OPCIONAL
            tipo_contrato_val = r.get('TIPO_CONTRATO')
            tipo_contrato_id = None if pd.isna(tipo_contrato_val) or str(tipo_contrato_val).strip() == '' else get_id_mapas(mapas, 'TIPO_CONTRATO', tipo_contrato_val)
            
            # Manejar salario básico - OPCIONAL
            salario_val = r.get('SALARIO_BASICO', 0)
            try:
                salario_basico = float(str(salario_val).replace(',', '')) if not pd.isna(salario_val) and str(salario_val).strip() != '' else 0
            except:
                salario_basico = 0
            
            # Manejar factor no salarial - OPCIONAL
            factor_val = r.get('FACTOR_NO_SALARIAL', 0)
            try:
                factor_no_salarial = float(str(factor_val).replace(',', '')) if not pd.isna(factor_val) and str(factor_val).strip() != '' else 0
            except:
                factor_no_salarial = 0
            
            # Manejar número de hijos - SEGURO
            try:
                numero_hijos = int(float(str(r.get('NUMERO_HIJOS', 0)).replace(',', ''))) if not pd.isna(r.get('NUMERO_HIJOS')) and str(r.get('NUMERO_HIJOS')).strip() != '' else 0
            except:
                numero_hijos = 0
            
            # Manejar estrato - SEGURO
            try:
                estrato = int(float(str(r.get('ESTRATO', 1)).replace(',', ''))) if not pd.isna(r.get('ESTRATO')) and str(r.get('ESTRATO')).strip() != '' else 1
            except:
                estrato = 1
            
            data_limpia = {
                'identificacion': ident,
                'nombres': limpiar_texto(r.get('NOMBRES')),
                'apellidos': limpiar_texto(r.get('APELLIDOS')),
                'cedula_expedida_en': limpiar_texto(r.get('CEDULA_EXPEDIDA_EN')),
                'sexo': str(r.get('SEXO (M/F)', 'M')).upper()[0],
                'fecha_nacimiento': f_nacimiento,
                'lugar_nacimiento': limpiar_texto(r.get('LUGAR_NACIMIENTO')),
                'edad': calcular_edad(f_nacimiento),
                'estado_civil_id': get_id_mapas(mapas, 'ESTADO_CIVIL', r.get('ESTADO_CIVIL')),
                'grupo_sanguineo_id': get_id_mapas(mapas, 'GS', r.get('GRUPO_SANGUINEO')),
                'numero_hijos': numero_hijos,
                'direccion': limpiar_texto(r.get('DIRECCION')),
                'barrio_id': get_id_mapas(mapas, 'CIUDAD', r.get('CIUDAD_BARRIO')),
                'barrio2': limpiar_texto(r.get('BARRIO', 'N/A')),
                'localidad': limpiar_texto(r.get('LOCALIDAD', 'N/A')),
                'estrato': estrato,
                'telefono_fijo': r.get('TELEFONO_FIJO'),
                'celular': r.get('CELULAR'),
                'correo': str(r.get('CORREO')).lower(),
                'contacto_emergencia': str(r.get('CONTACTO_EMERGENCIA')).upper(),
                'telefono_emergencia': r.get('TELEFONO_EMERGENCIA'),
                'parentesco': str(r.get('PARENTESCO')).upper(),
                'eps_id': get_id_mapas(mapas, 'EPS', r.get('EPS')),
                'afp_id': get_id_mapas(mapas, 'AFP', r.get('AFP')),
                'cesantias_id': get_id_mapas(mapas, 'CESANTIAS', r.get('CESANTIAS')),
                'ccf_id': get_id_mapas(mapas, 'CCF', r.get('CCF')),
                'arl_id': get_id_mapas(mapas, 'ARL', r.get('ARL')),
                'tipo_contrato_id': tipo_contrato_id,
                'cargo_id': get_id_mapas(mapas, 'CARGO', r.get('CARGO')),
                'jornada': str(r.get('JORNADA', 'DIURNO')).upper(),
                'sede_id': get_id_mapas(mapas, 'SEDE', r.get('SEDE')),
                'antiguedad': calcula_antiguedad(f_ingreso),
                'fecha_ingreso': f_ingreso,
                'salario_basico': salario_basico,
                'factor_no_salarial': factor_no_salarial,
                'numero_cuenta': r.get('NUMERO_CUENTA'),
                'banco_id': get_id_mapas(mapas, 'BANCO', r.get('BANCO')),
                'grupo_nomina_id': get_id_mapas(mapas, 'NOMINA', r.get('GRUPO_NOMINA')),
                'nivel_escolaridad_id': get_id_mapas(mapas, 'ESCOLARIDAD', r.get('NIVEL_ESCOLARIDAD')),
                'programa_academico': str(r.get('PROGRAMA_ACADEMICO')).upper(),
                'estudia_actualmente': str(r.get('ESTUDIA_ACTUALMENTE (SI/NO)', 'NO')).upper(),
                'nombre_programa_actual': limpiar_texto(r.get('NOMBRE_PROGRAMA_ACTUAL', 'N/A')),
                'tipo_identificacion_id': get_id_mapas(mapas, 'TIPO_DOC', r.get('TIPO_DOC')),
                'password': hash_password(ident)
            }
            try:
                importar_empleados_plantilla(data_limpia)
                insertados += 1
            except Exception as row_error:
                error_msg = str(row_error)
                print(f"Error procesando empleado {ident} (fila {numero_fila}): {error_msg}")
                errores.append({
                    'FILA EXCEL': numero_fila,
                    'IDENTIFICACION': ident,
                    'NOMBRES': data_limpia.get('nombres', ''),
                    'ERROR': error_msg
                })
                continue
        
        response_data = {'success': True, 'insertados': insertados, 'total_filas': len(df)}
        if errores:
            filename = guardar_excel_errores(errores)
            response_data['errores'] = errores
            response_data['errores_count'] = len(errores)
            if filename:
                response_data['error_excel_url'] = url_for('static', filename=f'tmp_errores/{filename}')
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
@rrhh_bp.route('/empleados/actualizar_empleados', methods=['POST'])
@login_required
@admin_rrhh_required
def actualizar_empleados():
    file = request.files.get('file')
    if  not file: return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo.'}), 400
    try:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapas = obtener_mapas()
        procesados = 0
        errores = []
        for idx, (_, row) in enumerate(df.iterrows()):
            r = row.to_dict()
            numero_fila = idx + 2  # +2 porque Excel fila 1 es encabezado
            ident = str(r.get('IDENTIFICACION')).split('.')[0]
            f_ingreso = limpiar_fecha(r.get('FECHA_INGRESO (AAAA-MM-DD)'))
            f_nacimiento = limpiar_fecha(r.get('FECHA_NACIMIENTO (AAAA-MM-DD)'))
            
            # Manejar tipo de contrato - OPCIONAL
            tipo_contrato_val = r.get('TIPO_CONTRATO')
            tipo_contrato_id = None if pd.isna(tipo_contrato_val) or str(tipo_contrato_val).strip() == '' else get_id_mapas(mapas, 'TIPO_CONTRATO', tipo_contrato_val)
            
            # Manejar salario básico - OPCIONAL
            salario_val = r.get('SALARIO_BASICO', 0)
            try:
                salario_basico = float(str(salario_val).replace(',', '')) if not pd.isna(salario_val) and str(salario_val).strip() != '' else 0
            except:
                salario_basico = 0
            
            # Manejar factor no salarial - OPCIONAL
            factor_val = r.get('FACTOR_NO_SALARIAL', 0)
            try:
                factor_no_salarial = float(str(factor_val).replace(',', '')) if not pd.isna(factor_val) and str(factor_val).strip() != '' else 0
            except:
                factor_no_salarial = 0
            
            # Manejar número de hijos - SEGURO
            try:
                numero_hijos = int(float(str(r.get('NUMERO_HIJOS', 0)).replace(',', ''))) if not pd.isna(r.get('NUMERO_HIJOS')) and str(r.get('NUMERO_HIJOS')).strip() != '' else 0
            except:
                numero_hijos = 0
            
            # Manejar estrato - SEGURO
            try:
                estrato = int(float(str(r.get('ESTRATO', 1)).replace(',', ''))) if not pd.isna(r.get('ESTRATO')) and str(r.get('ESTRATO')).strip() != '' else 1
            except:
                estrato = 1
            
            data_limpia = {
                'identificacion': ident,
                'nombres': limpiar_texto(r.get('NOMBRES')),
                'apellidos': limpiar_texto(r.get('APELLIDOS')),
                'cedula_expedida_en': limpiar_texto(r.get('CEDULA_EXPEDIDA_EN')),
                'sexo': str(r.get('SEXO (M/F)', 'M')).upper()[0],
                'fecha_nacimiento': f_nacimiento,
                'lugar_nacimiento': limpiar_texto(r.get('LUGAR_NACIMIENTO')),
                'edad': calcular_edad(f_nacimiento),
                'estado_civil_id': get_id_mapas(mapas, 'ESTADO_CIVIL', r.get('ESTADO_CIVIL')),
                'grupo_sanguineo_id': get_id_mapas(mapas, 'GS', r.get('GRUPO_SANGUINEO')),
                'numero_hijos': numero_hijos,
                'direccion': limpiar_texto(r.get('DIRECCION')),
                'barrio_id': get_id_mapas(mapas, 'CIUDAD', r.get('CIUDAD_BARRIO')),
                'barrio2': limpiar_texto(r.get('BARRIO', 'N/A')),
                'localidad': limpiar_texto(r.get('LOCALIDAD', 'N/A')),
                'estrato': estrato,
                'telefono_fijo': r.get('TELEFONO_FIJO'),
                'celular': r.get('CELULAR'),
                'correo': str(r.get('CORREO')).lower(),
                'contacto_emergencia': str(r.get('CONTACTO_EMERGENCIA')).upper(),
                'telefono_emergencia': r.get('TELEFONO_EMERGENCIA'),
                'parentesco': str(r.get('PARENTESCO')).upper(),
                'eps_id': get_id_mapas(mapas, 'EPS', r.get('EPS')),
                'afp_id': get_id_mapas(mapas, 'AFP', r.get('AFP')),
                'cesantias_id': get_id_mapas(mapas, 'CESANTIAS', r.get('CESANTIAS')),
                'ccf_id': get_id_mapas(mapas, 'CCF', r.get('CCF')),
                'arl_id': get_id_mapas(mapas, 'ARL', r.get('ARL')),
                'tipo_contrato_id': tipo_contrato_id,
                'cargo_id': get_id_mapas(mapas, 'CARGO', r.get('CARGO')),
                'jornada': str(r.get('JORNADA', 'DIURNO')).upper(),
                'sede_id': get_id_mapas(mapas, 'SEDE', r.get('SEDE')),
                'antiguedad': calcula_antiguedad(f_ingreso),
                'fecha_ingreso': f_ingreso,
                'salario_basico': salario_basico,
                'factor_no_salarial': factor_no_salarial,
                'numero_cuenta': r.get('NUMERO_CUENTA'),
                'banco_id': get_id_mapas(mapas, 'BANCO', r.get('BANCO')),
                'grupo_nomina_id': get_id_mapas(mapas, 'NOMINA', r.get('GRUPO_NOMINA')),
                'nivel_escolaridad_id': get_id_mapas(mapas, 'ESCOLARIDAD', r.get('NIVEL_ESCOLARIDAD')),
                'programa_academico': str(r.get('PROGRAMA_ACADEMICO')).upper(),
                'estudia_actualmente': str(r.get('ESTUDIA_ACTUALMENTE (SI/NO)', 'NO')).upper(),
                'nombre_programa_actual': limpiar_texto(r.get('NOMBRE_PROGRAMA_ACTUAL', 'N/A')),
                'tipo_identificacion_id': get_id_mapas(mapas, 'TIPO_DOC', r.get('TIPO_DOC')),
                'password': hash_password(ident)
            }
            try:
                if empleado_existe(ident):
                    actualizar_empleados_plantilla(data_limpia)
                else:
                    importar_empleados_plantilla(data_limpia)
                procesados += 1
            except Exception as row_error:
                error_msg = str(row_error)
                print(f"Error procesando empleado {ident} (fila {numero_fila}): {error_msg}")
                errores.append({
                    'FILA EXCEL': numero_fila,
                    'IDENTIFICACION': ident,
                    'NOMBRES': data_limpia.get('nombres', ''),
                    'ERROR': error_msg
                })
                continue
        
        response_data = {'success': True, 'actualizados': procesados, 'total_filas': len(df)}
        if errores:
            filename = guardar_excel_errores(errores)
            response_data['errores'] = errores
            response_data['errores_count'] = len(errores)
            if filename:
                response_data['error_excel_url'] = url_for('static', filename=f'tmp_errores/{filename}')
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
#------------------------------------------------------
#----------- IMPORTAR CONTRATOS MASIVOS --------
#------------------------------------------------------
@rrhh_bp.route("/empleados/importar_contratos", methods=["POST"])
@login_required
@admin_rrhh_required
def importar_contratos():
    """Procesa carga masiva de contratos desde Excel."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No se ha proporcionado ningun archivo."}), 400
    file = request.files["file"]
    try:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        mapas = obtener_mapas()
        procesados = 0
        errores = []
        for idx, (_, row) in enumerate(df.iterrows()):
            r = row.to_dict()
            numero_fila = idx + 2
            ident = str(r.get("IDENTIFICACION", "")).split(".")[0]
            if not ident or ident == "nan":
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": "", "ERROR": "Identificacion vacia"})
                continue

            # --- FECHA INICIAL (obligatoria si no hay CODIGO_CONTRATO) ---
            fecha_ingreso = limpiar_fecha(r.get("FECHA_INICIAL")) if "FECHA_INICIAL" in r else None

            # --- FECHA FINALIZACION (opcional) ---
            fecha_finalizacion = limpiar_fecha(r.get("FECHA_FINALIZACION")) if "FECHA_FINALIZACION" in r else None

            # --- MOTIVO (obligatorio si FECHA_FINALIZACION no está vacía) ---
            motivo_val = r.get("MOTIVO")
            motivo = str(motivo_val).strip() if not pd.isna(motivo_val) and str(motivo_val).strip() != "" and str(motivo_val).strip().lower() != "nan" else None
            if fecha_finalizacion and not motivo:
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": "Si FECHA_FINALIZACION tiene valor, la columna MOTIVO es obligatoria"})
                continue

            salario_val = r.get("SALARIO_BASICO", 0)
            try:
                salario_basico = float(str(salario_val).replace(",", "")) if not pd.isna(salario_val) and str(salario_val).strip() != "" else 0
            except:
                salario_basico = 0
            factor_val = r.get("FACTOR_NO_SALARIAL", 0)
            try:
                factor_no_salarial = float(str(factor_val).replace(",", "")) if not pd.isna(factor_val) and str(factor_val).strip() != "" else 0
            except:
                factor_no_salarial = 0
            tipo_contrato_val = r.get("TIPO_CONTRATO")
            tipo_contrato_id = None if pd.isna(tipo_contrato_val) or str(tipo_contrato_val).strip() == "" else get_id_mapas(mapas, "TIPO_CONTRATO", tipo_contrato_val)
            codigo_contrato = r.get("CODIGO_CONTRATO")
            codigo_contrato = str(codigo_contrato).strip() if not pd.isna(codigo_contrato) and str(codigo_contrato).strip() != "" and str(codigo_contrato).strip().lower() != "nan" else None

            # Validar: si no hay codigo_contrato y no hay fecha_inicial, no se puede crear/actualizar
            if not codigo_contrato and not fecha_ingreso:
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": "Debe proporcionar CODIGO_CONTRATO o FECHA_INICIAL"})
                continue

            data = {
                "identificacion": ident,
                "salario_basico": salario_basico,
                "factor_no_salarial": factor_no_salarial,
                "tipo_contrato_id": tipo_contrato_id,
                "codigo_contrato": codigo_contrato,
                "fecha_ingreso": fecha_ingreso,
                "fecha_finalizacion": fecha_finalizacion,
                "motivo": motivo,
            }
            try:
                exito, error = importar_contratos_plantilla(data)
                if exito:
                    procesados += 1
                else:
                    errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": error})
            except Exception as row_error:
                error_msg = str(row_error)
                print(f"Error procesando contrato {ident} (fila {numero_fila}): {error_msg}")
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": error_msg})
                continue
        response_data = {"success": True, "procesados": procesados, "total_filas": len(df)}
        if errores:
            filename = guardar_excel_errores(errores)
            response_data["errores"] = errores
            response_data["errores_count"] = len(errores)
            if filename:
                response_data["error_excel_url"] = url_for("static", filename=f"tmp_errores/{filename}")
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


#------------------------------------------------------
#----------- ASIGNAR ROL SGI MASIVO --------
#------------------------------------------------------
@rrhh_bp.route("/descargar_plantilla_rol_sgi")
@login_required
@admin_rrhh_required
def descargar_plantilla_rol_sgi():
    """Genera plantilla Excel para asignar Rol SGI masivamente."""
    columnas = [
        "IDENTIFICACION",
        "ROL_SGI",
    ]
    df = pd.DataFrame(columns=columnas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Plantilla Rol SGI")
        workbook = writer.book
        worksheet = writer.sheets["Plantilla Rol SGI"]
        hidden_sheet = workbook.add_worksheet("ListasDesplegables")
        hidden_sheet.hide()
        roles = [str(r[1]).upper() for r in list_roles()]
        roles.append("SIN ACCESO")
        for row, value in enumerate(roles):
            hidden_sheet.write(row, 0, value)
        worksheet.data_validation(1, 1, 10000, 1, {
            "validate": "list",
            "source": "=ListasDesplegables!$A$1:$A$" + str(len(roles))
        })
        header_format = workbook.add_format({"bold": True, "bg_color": "#D7E4BC", "border": 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 25)
    output.seek(0)
    return send_file(
        output,
        download_name="plantilla_rol_sgi.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@rrhh_bp.route("/empleados/asignar_rol_sgi", methods=["POST"])
@login_required
@admin_rrhh_required
def asignar_rol_sgi():
    """Procesa carga masiva para asignar Rol SGI desde Excel."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No se ha proporcionado ningun archivo."}), 400
    file = request.files["file"]
    try:
        df = pd.read_excel(file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        roles_sgi = {str(r[1]).upper(): r[0] for r in list_roles()}
        roles_sgi["SIN ACCESO"] = None
        procesados = 0
        errores = []
        for idx, (_, row) in enumerate(df.iterrows()):
            r = row.to_dict()
            numero_fila = idx + 2
            ident = str(r.get("IDENTIFICACION", "")).split(".")[0]
            if not ident or ident == "nan":
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": "", "ERROR": "Identificacion vacia"})
                continue
            rol_nombre = str(r.get("ROL_SGI", "")).strip().upper() if not pd.isna(r.get("ROL_SGI")) else ""
            if not rol_nombre or rol_nombre == "NAN":
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": "ROL_SGI vacio"})
                continue
            sgi_rol_id = roles_sgi.get(rol_nombre)
            if sgi_rol_id is None and rol_nombre != "SIN ACCESO":
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": f"Rol '{rol_nombre}' no encontrado"})
                continue
            data = {
                "identificacion": ident,
                "sgi_rol_id": sgi_rol_id,
            }
            try:
                exito, error = asignar_rol_sgi_db(data)
                if exito:
                    procesados += 1
                else:
                    errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": error})
            except Exception as row_error:
                error_msg = str(row_error)
                print(f"Error asignando rol SGI a {ident} (fila {numero_fila}): {error_msg}")
                errores.append({"FILA EXCEL": numero_fila, "IDENTIFICACION": ident, "ERROR": error_msg})
                continue
        response_data = {"success": True, "procesados": procesados, "total_filas": len(df)}
        if errores:
            filename = guardar_excel_errores(errores)
            response_data["errores"] = errores
            response_data["errores_count"] = len(errores)
            if filename:
                response_data["error_excel_url"] = url_for("static", filename=f"tmp_errores/{filename}")
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400



@rrhh_bp.route('/empleados/descargar_reporte_empleados', methods=['GET'])
@login_required
@admin_rrhh_required
def descargar_reporte_empleados():

    filtro = request.args.get('filtro', '1')
    try:
        datos_empleado = empleados_lista()
        if not datos_empleado:
            flash("No hay datos de empleados para generar el reporte.", "error")
            return redirect(url_for('rrhh.empleados'))
        df = pd.DataFrame(datos_empleado)
        df = df[df['activo'] == int(filtro)]
        mapeo_columnas = {
            'identificacion': 'IDENTIFICACION',
            'nombres': 'NOMBRES',        
            'apellidos': 'APELLIDOS',
            'cedula_expedida_en': 'CEDULA_EXPEDIDA_EN',
            'sexo': 'SEXO (M/F)',
            'fecha_nacimiento': 'FECHA_NACIMIENTO (AAAA-MM-DD)',
            'lugar_nacimiento': 'LUGAR_NACIMIENTO',
            'tipo_doc_nombre': 'TIPO_DOC',
            'estado_civil': 'ESTADO_CIVIL',
            'grupo_sanguineo': 'GRUPO_SANGUINEO',
            'numero_hijos': 'NUMERO_HIJOS',
            'direccion': 'DIRECCION',
            'barrio': 'CIUDAD_BARRIO',
            'localidad': 'LOCALIDAD',
            'estrato': 'ESTRATO',
            'telefono_fijo': 'TELEFONO_FIJO',
            'celular': 'CELULAR',
            'correo': 'CORREO',
            'contacto_emergencia': 'CONTACTO_EMERGENCIA',
            'telefono_emergencia': 'TELEFONO_EMERGENCIA',
            'parentesco': 'PARENTESCO',
            'eps': 'EPS',
            'afp': 'AFP',
            'cesantias': 'CESANTIAS',
            'ccf': 'CCF',
            'arl': 'ARL',
            'tipo_contrato': 'TIPO_CONTRATO',
            'cargos': 'CARGO',
            'jornada': 'JORNADA',
            'sedes': 'SEDE',
            'fecha_ingreso': 'FECHA_INGRESO (AAAA-MM-DD)', 
            'salario_basico': 'SALARIO_BASICO',
            'factor_no_salarial': 'FACTOR_NO_SALARIAL',
            'numero_cuenta': 'NUMERO_CUENTA',
            'bancos': 'BANCO',
            'grupo_nomina': 'GRUPO_NOMINA',
            'nivel_escolaridad': 'NIVEL_ESCOLARIDAD',
            'programa_academico': 'PROGRAMA_ACADEMICO',
            'estudia_actualmente': 'ESTUDIA_ACTUALMENTE (SI/NO)',
            'nombre_programa_actual': 'NOMBRE_PROGRAMA_ACTUAL'
        }
        df_reporte = df.rename(columns=mapeo_columnas)
        columnas_finales = [v for k, v in mapeo_columnas.items() if v in df_reporte.columns]
        df_reporte = df_reporte[columnas_finales]
        
        for col in df_reporte.columns:
            if 'FECHA' in col:
                df_reporte[col] = pd.to_datetime(df_reporte[col]).dt.strftime('%Y-%m-%d')
            else:
                df_reporte[col] = df_reporte[col].apply(lambda x: str(x).upper() if pd.notna(x) else "")
                
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_reporte.to_excel(writer, index=False, sheet_name='Reporte Empleados')
            
            workbook = writer.book
            worksheet = writer.sheets['Reporte Empleados']
            
            hidde_sheet = workbook.add_worksheet('ListasDesplegables')
            hidde_sheet.hide()
            
            listas_db = [
                (0, [str(e['nombre']).upper() for e in estado_civil()]),
                (1, [str(g['tipo']).upper() for g in grupo_sanguineo()]),
                (2, [str(c['nombre']).upper() for c in ciudades()]),
                (3, [str(e['nombre']).upper() for e in eps()]),
                (4, [str(a['nombre']).upper() for a in afp()]),
                (5, [str(c['nombre']).upper() for c in cesantias()]),
                (6, [str(c['nombre']).upper() for c in ccf()]),
                (7, [str(a['nombre']).upper() for a in arl()]),
                (8, [str(t['nombre']).upper() for t in tipo_contrato()]),
                (9, [str(c['nombre']).upper() for c in cargos()]),
                (10, [str(s['nombre']).upper() for s in sede()]),
                (11, [str(b['nombre']).upper() for b in bancos()]),
                (12, [str(g['nombre']).upper() for g in grupo_nomina()]),
                (13, [str(e['nombre']).upper() for e in escolaridad()]),
            ]
            for col, data in listas_db:
                for row, value in enumerate(data):
                    hidde_sheet.write(row, col, value)
            
            def aplicar_validacion(col_index, list_col_letter, num_items):
                worksheet.data_validation(1, col_index, 2000, col_index, {
                    'validate': 'list',
                    'source': f'=ListasDesplegables!${list_col_letter}$1:${list_col_letter}${num_items}'
                })
            
            worksheet.data_validation(1, 4, 10000, 4, {'validate': 'list', 'source': ['M', 'F']})
            aplicar_validacion(7, 'A', len(listas_db[0][1]))   # estado_civil
            aplicar_validacion(8, 'B', len(listas_db[1][1]))   # grupo_sanguineo
            aplicar_validacion(11, 'C', len(listas_db[2][1]))  # ciudad_barrio
            aplicar_validacion(19, 'D', len(listas_db[3][1]))  # eps
            aplicar_validacion(20, 'E', len(listas_db[4][1]))  # afp
            aplicar_validacion(21, 'F', len(listas_db[5][1]))  # cesantias
            aplicar_validacion(22, 'G', len(listas_db[6][1]))  # ccf
            aplicar_validacion(23, 'H', len(listas_db[7][1]))  # arl
            aplicar_validacion(24, 'I', len(listas_db[8][1]))  # tipo_contrato
            aplicar_validacion(25, 'J', len(listas_db[9][1]))  # cargo
            worksheet.data_validation(1, 26, 10000, 26, {'validate': 'list', 'source': ['DIURNO', 'TARDE', 'NOCTURNO']})
            aplicar_validacion(27, 'K', len(listas_db[10][1])) # sede
            aplicar_validacion(32, 'L', len(listas_db[11][1])) # banco
            aplicar_validacion(33, 'M', len(listas_db[12][1])) # grupo_nomina
            aplicar_validacion(34, 'N', len(listas_db[13][1])) # nivel_escolaridad
            worksheet.data_validation(1, 36, 10000, 36, {'validate': 'list', 'source': ['SI', 'NO']})
            
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1, 'align':'center'})
            text_format = workbook.add_format({'align':'left'})
            
            for col_num, value in enumerate(df_reporte.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 20, text_format)
                
        output.seek(0)
        prefijo = "Activos" if filtro == '1' else "Retirados"
        nombre_archivo = f"Reporte_Empleados_{prefijo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(output,
                            download_name=nombre_archivo,
                            as_attachment=True,
                            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        flash(f"Error al generar el reporte: {str(e)}", "error")
        return redirect(url_for('rrhh.empleados'))
    
#------------------------------------------------------
#----- ACCIONES MASIVAS DOCUMENTACION -----------------
#------------------------------------------------------
@rrhh_bp.route('/empleados/importar_zip', methods=['POST'])
@login_required
@admin_rrhh_required
def importar_zip():
    # 1. Validar archivo antes de intentar acceder a él
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Archivo sin nombre.'}), 400

    tmp_folder = os.path.join(current_app.config['UPLOAD_FOLDER_EMPLEADOS'], 'temp_zip')
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    try:
        zip_path = os.path.join(tmp_folder, file.filename)
        file.save(zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_folder)
        
        procesados = 0

        for root, disr, files in os.walk(tmp_folder):
            for filename in files:
                if filename == file.filename: 
                    continue
                
                parts = filename.upper().split('_')
                if len(parts) < 2: 
                    continue
                
                identificacion = parts[0] 
                tipo_documento = parts[1] 
                
                # CORRECCIÓN AQUÍ: 
                # Buscamos el empleado. Si tu función devuelve un diccionario (por el DictCursor):
                empleado = empleado_lista_completo_por_identificacion(identificacion) 
                if not empleado:
                    continue
                
                # Si es un diccionario, accedemos por llave ['id'], si es tupla por índice [0]
                empleado_id = empleado['id'] 
                
                carpeta_empleado = os.path.join(current_app.config['UPLOAD_FOLDER_EMPLEADOS'], identificacion)
                if not os.path.exists(carpeta_empleado):
                    os.makedirs(carpeta_empleado)
                    
                src_path = os.path.join(root, filename)
                
                if 'FOTO' in tipo_documento:
                    dest_name = f"foto_{filename}"
                    dest_path = os.path.join(carpeta_empleado, dest_name)
                    shutil.move(src_path, dest_path)
                    db_path = f"static/uploads/empleados/{identificacion}/{dest_name}"
                    actualiza_foto(empleado_id, db_path)
                    
                elif 'CEDULA' in tipo_documento:
                    dest_name = f"cedula_{filename}"
                    dest_path = os.path.join(carpeta_empleado, dest_name)
                    shutil.move(src_path, dest_path)
                    db_path = f"static/uploads/empleados/{identificacion}/{dest_name}"
                    actualiza_cedula(empleado_id, db_path)
                    
                elif 'ESTUDIO' in tipo_documento:
                    dest_name = f"estudio_{filename}"
                    # Asegurar que existe la subcarpeta 'estudios'
                    ruta_estudios = os.path.join(carpeta_empleado, 'estudios')
                    if not os.path.exists(ruta_estudios):
                        os.makedirs(ruta_estudios)
                        
                    dest_path = os.path.join(ruta_estudios, dest_name)
                    shutil.move(src_path, dest_path)
                    db_path = f"static/uploads/empleados/{identificacion}/estudios/{dest_name}"
                    # Guardar en plural como lo definimos antes
                    guardar_documentos_estudio(empleado_id, [db_path]) 
                    
                procesados += 1

        shutil.rmtree(tmp_folder)
        return jsonify({'success': True, 'archivos': procesados})
                    
    except Exception as e:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
        print(f"Error en ZIP: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400
    
    
#------------------------------------------------------
#---------- RESTABLECER CONTRASEÑA -----------------
#------------------------------------------------------
@rrhh_bp.route('/empleados/restablecer-password/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def restablecer_password(id):
    """Restablece la contraseña de un empleado a su número de identificación
    y marca primer_ingreso = 1 para forzar cambio en el próximo inicio de sesión."""
    try:
        exito, identificacion, error = restablecer_password_db(id)
        if exito:
            log_password_changed(
                user_id=current_user.get_id(),
                username=getattr(current_user, 'nombres', 'admin'),
            )
            return jsonify({
                'success': True,
                'message': f'Contraseña restablecida a la identificación: {identificacion}'
            })
        else:
            return jsonify({'success': False, 'error': error}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


#------------------------------------------------------
#-------------------- CERTIFICADO ---------------------
#------------------------------------------------------
@rrhh_bp.route('/empleados/certificado/<int:id>')
@login_required
@admin_rrhh_required
def generar_certificado_laboral(id):
    datos = obtener_datos_certificado(id)
    if not datos:
        return "Empleado no encontrado", 404
    
    #configura el pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(25,25,25)
    
    #encabezado espacio para el logo
    pdf.set_font('Arial', 'B', 16)
    pdf.ln(10)
    pdf.cell(0, 50, "CERTIFICADO LABORAL", ln=True, align='C')
    pdf.ln(10)
    
    #cuerpo del mensaje
    pdf.set_font('Arial', size=12)
    pdf.ln(10)
    
    meses = {
        "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
        "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
        "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }
    
    nombre_empresa = datos['grupo_nomina'].upper()
    nit = "830146124-3"
    nombre_completo = f"{datos['nombres']} {datos['apellidos']}".upper()
    fecha_ingreso = datos['fecha_ingreso']
    mes_ingreso = meses[fecha_ingreso.strftime('%B')]
    fecha_ingreso_texto = f"{fecha_ingreso.day} de {mes_ingreso} de {fecha_ingreso.year}"
    fecha_hoy = datetime.now()
    mes_hoy = meses[fecha_hoy.strftime('%B')]
    
    
    texto = f"""La empresa {nombre_empresa}, identificada con NIT {nit}, hace constar que el(la) señor(a) {nombre_completo}, identificado(a) con cédula de ciudadanía número {datos['identificacion']}, trabaja en nuestra organización desde el {fecha_ingreso_texto}, bajo un contrato de {datos['tipo_contrato']} desempeñando el cargo de {datos['cargo']}.

A la fecha de expedición de este documento, devenga un salario básico mensual de ${datos['salario_basico']:,.0f} pesos m/cte."""
    texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, texto_seguro, align='J')
    
    pdf.ln(10)
    pdf.cell(0, 10, "Para constancia de lo anterior, se firma en Bogotá D.C.,", ln=True)
    pdf.cell(0, 10, f"a los {fecha_hoy.day} días del mes de {mes_hoy} de {fecha_hoy.year}.", ln=True)
    
    #firma
    pdf.ln(30)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "_____________________________", ln=True, align='L')
    pdf.cell(0, 10, "DEPARTAMNENTO DE RECURSOS HUMANOS", ln=True, align='L')
    pdf.cell(0, 10, f"{nombre_empresa}", ln=True, align='L')
    
    #retorna el pdf
    pdf_output = pdf.output()
    if isinstance(pdf_output, (bytearray, str)):
        pdf_output = bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output.encode('latin-1')
    
    response = make_response(pdf_output)    
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"inline; filenameCertifica_{datos['identificacion']}.pdf"
    
    return response


#------------------------------------------------------
#--------------- API: LISTADOS PARA MODALES -----------
#------------------------------------------------------
@rrhh_bp.route('/api/empleados_activos')
@login_required
@admin_rrhh_required
def api_empleados_activos():
    """Retorna lista de empleados activos para el modal."""
    try:
        empleados = empleados_lista()
        activos = [
            {
                'id': e['id'],
                'identificacion': e['identificacion'],
                'nombres': e['nombres'],
                'apellidos': e['apellidos'],
                'cargo': e.get('cargos', ''),
                'grupo_nomina': e.get('grupo_nomina', ''),
                'tipo_contrato': e.get('tipo_contrato', ''),
            }
            for e in empleados if e.get('activo') == 1
        ]
        return jsonify({'success': True, 'empleados': activos, 'total': len(activos)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rrhh_bp.route('/api/empleados_retirados')
@login_required
@admin_rrhh_required
def api_empleados_retirados():
    """Retorna lista de empleados retirados para el modal."""
    try:
        empleados = empleados_lista()
        retirados = [
            {
                'id': e['id'],
                'identificacion': e['identificacion'],
                'nombres': e['nombres'],
                'apellidos': e['apellidos'],
                'cargo': e.get('cargos', ''),
                'grupo_nomina': e.get('grupo_nomina', ''),
                'tipo_contrato': e.get('tipo_contrato', ''),
            }
            for e in empleados if e.get('activo') == 2
        ]
        return jsonify({'success': True, 'empleados': retirados, 'total': len(retirados)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


#------------------------------------------------------
#------------------- MENSAJERÍA -----------------------
#------------------------------------------------------
@rrhh_bp.route('/mensajeria')
@login_required
@admin_rrhh_required
def mensajeria():
    """Página de mensajería para enviar correos a empleados filtrados."""
    cargos_list = cargos()
    sedes_list = sede()
    return render_template('rrhh/mensajeria.html',
                           usuario=current_user,
                           cargos=cargos_list,
                           sedes=sedes_list,
                           empleados_list=empleados_lista())


@rrhh_bp.route('/api/empleados_filtrados', methods=['GET'])
@login_required
@admin_rrhh_required
def api_empleados_filtrados():
    """Retorna empleados activos filtrados por cargo, sede y/o búsqueda."""
    cargo_id = request.args.get('cargo_id', type=int)
    sede_id = request.args.get('sede_id', type=int)
    busqueda = request.args.get('busqueda', '').strip()
    try:
        empleados = empleados_para_mensajeria(cargo_id, sede_id, busqueda)
        return jsonify({'success': True, 'empleados': empleados, 'total': len(empleados)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rrhh_bp.route('/api/enviar_mensaje', methods=['POST'])
@login_required
@admin_rrhh_required
def api_enviar_mensaje():
    """Envía un correo a los empleados seleccionados."""
    try:
        data = request.get_json()
        asunto = (data.get('asunto') or '').strip()
        mensaje_html = (data.get('mensaje_html') or '').strip()
        destinatarios_ids = data.get('destinatarios_ids', [])

        if not asunto:
            return jsonify({'success': False, 'error': 'El asunto es obligatorio'}), 400
        if not mensaje_html:
            return jsonify({'success': False, 'error': 'El mensaje no puede estar vacío'}), 400
        if not destinatarios_ids or not isinstance(destinatarios_ids, list):
            return jsonify({'success': False, 'error': 'Debes seleccionar al menos un destinatario'}), 400

        # Registrar quién envía (para el buzón de salida del usuario)
        user_id = current_user.get_id()
        try:
            real_id = int(str(user_id).split('-')[1])
        except (ValueError, IndexError):
            real_id = None

        if hasattr(current_user, 'nombres') and hasattr(current_user, 'apellidos'):
            remitente_nombre = f"{current_user.nombres} {current_user.apellidos}".strip()
        else:
            remitente_nombre = getattr(current_user, 'name', None) or getattr(current_user, 'username', None)

        enviados, total, errores = enviar_mensaje_masivo(
            asunto, mensaje_html, destinatarios_ids,
            enviado_por_id=real_id,
            enviado_por_nombre=remitente_nombre
        )

        return jsonify({
            'success': True,
            'enviados': enviados,
            'total': total,
            'errores': errores
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rrhh_bp.route('/api/grupos_nomina')
@login_required
@admin_rrhh_required
def api_grupos_nomina():
    """Retorna lista de grupos de nómina para el modal."""
    try:
        grupos = grupo_nomina()
        return jsonify({'success': True, 'grupos': grupos, 'total': len(grupos)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


#------------------------------------------------------
#--------------- CONSECUTIVOS CONTRATO ----------------
#------------------------------------------------------
@rrhh_bp.route("/contratos/<int:id>", methods=['GET'])
@login_required
@admin_rrhh_required
def consecutivo_contrato(id):
    try:
        contratos = tipoContrato_id(id)
        if not contratos: 
            return jsonify({'success': False, 'error': 'Contrato no encontrado'}), 404
        
        return jsonify({'success':True, 'contratos': contratos})
    except Exception as e:
        return jsonify({'success':False, 'error': str(e)}), 400
    
@rrhh_bp.route("/contratos/consecutivo/editar/<int:id>", methods=['POST'])
@login_required
@admin_rrhh_required
def editar_consecutivo(id):
    try:
        data = request.get_json()
        valor = data.get('ult_consecutivo')
        
        if valor is None:
            return jsonify({'success': False, 'error': 'Valor no Proporcionado'}), 500
        
        actualiza_consecutivo(id, valor)
        
        return jsonify({'success': True, 'message': 'Consecutivo actualizado con extio'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
 
#------------------------------------------------------
#--------------- OTRO SI ----------------
#------------------------------------------------------      
@rrhh_bp.route('/otrosi/procesar_otrosi/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def procesar_otrosi_contrato(id):
    try:
        data = request.get_json()
        procesar_otrosi_db(id, data)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, "error": str(e)}), 500


#------------------------------------------------------
#--------------- EXPORTAR PDF EVALUACIONES ------------
#------------------------------------------------------
@rrhh_bp.route('/evaluacion/exportar_pdf')
@login_required
@admin_rrhh_required
def exportar_evaluaciones_pdf():
    """
    Genera un PDF con todas las evaluaciones de desempeño agrupadas por empleado evaluado.
    """
    import io
    from datetime import datetime

    resultados = consulta_resultados_evaluacion()
    if not resultados:
        flash("No hay evaluaciones para exportar.", "warning")
        return redirect(url_for('rrhh.evaluacion'))

    # Filtrar por usuario si se especifica
    usuario_id = request.args.get('usuario_id')
    if usuario_id:
        usuario_id = int(usuario_id)
        resultados = [
            r for r in resultados
            if r['evaluador_id'] == usuario_id or r['evaluado_id'] == usuario_id
        ]
        if not resultados:
            flash("No hay evaluaciones para el usuario seleccionado.", "warning")
            return redirect(url_for('rrhh.evaluacion'))

    # Agrupar por evaluado
    from collections import OrderedDict
    grupos = OrderedDict()
    for r in resultados:
        key = (r['evaluado_id'], r['evaluado_nombres'], r['evaluado_apellidos'], r['evaluado_identificacion'])
        if key not in grupos:
            grupos[key] = []
        grupos[key].append(r)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    path_logo = os.path.join(current_app.root_path, 'static', 'imgs', 'logo.png')

    def encabezado():
        # Logo
        if os.path.exists(path_logo):
            pdf.image(path_logo, x=10, y=8, w=40)
        pdf.set_font('Arial', 'B', 14)
        pdf.ln(12)
        pdf.cell(0, 10, 'REPORTE DE EVALUACIONES DE DESEMPENO', ln=True, align='C')
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 5, f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=True, align='C')
        pdf.ln(5)

    for (evaluado_id, nombres, apellidos, identificacion), evals in grupos.items():
        pdf.add_page()
        encabezado()

        # ── Datos del empleado ──
        pdf.set_font('Arial', 'B', 11)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, f'Evaluado: {nombres} {apellidos}  |  ID: {identificacion}', ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)

        for idx, ev in enumerate(evals, 1):
            if idx > 1:
                pdf.ln(4)

            # ── Cabecera de evaluación ──
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(241, 245, 249)
            pdf.cell(0, 6, f'Evaluacion #{idx} - Ano {ev["anio_evaluacion"]}', ln=True, fill=True)
            pdf.set_font('Arial', '', 8)

            # Info
            pdf.cell(0, 5, f'Evaluador: {ev["evaluador_nombres"]} {ev["evaluador_apellidos"]}', ln=True)
            pdf.cell(0, 5, f'Cargo: {ev["plantilla_nombre"] or "Sin cargo"}', ln=True)
            fecha_eval = ev['fecha_evaluacion'].strftime('%d/%m/%Y') if ev['fecha_evaluacion'] else 'Sin fecha'
            pdf.cell(0, 5, f'Fecha: {fecha_eval}', ln=True)

            # Estado aprobacion
            aprob = []
            if ev.get('aprobado_evaluado') == 1:
                aprob.append('Evaluado OK')
            else:
                aprob.append('Evaluado Pend.')
            if ev.get('aprobado_rrhh') == 1:
                aprob.append('RRHH OK')
            else:
                aprob.append('RRHH Pend.')
            pdf.cell(0, 5, f'Aprobacion: {" | ".join(aprob)}', ln=True)

            pdf.ln(2)

            # ── Resultados por tipo ──
            tipos = ev.get('resultados_tipo', [])
            if tipos:
                # Header de tabla
                pdf.set_font('Arial', 'B', 7)
                pdf.set_fill_color(30, 58, 138)
                pdf.set_text_color(255, 255, 255)
                col_w = [58, 18, 24, 42, 22, 22]
                headers = ['Tipo Competencia', '%Tipo', 'Resultado', 'Competencia', '%Comp', 'Nota Pond.']
                for i, h in enumerate(headers):
                    pdf.cell(col_w[i], 6, h, border=1, fill=True, align='C')
                pdf.ln()
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 7)

                for rt in tipos:
                    comps = rt.get('competencias', [])
                    if comps:
                        for ci, rc in enumerate(comps):
                            pdf.cell(col_w[0], 5, rt['nombre_tipo'] if ci == 0 else '', border=1, align='C')
                            pdf.cell(col_w[1], 5, f"{rt['porcentaje']}%" if ci == 0 else '', border=1, align='C')
                            pdf.cell(col_w[2], 5, f"{rt['resultado']:.2f}" if rt['resultado'] else '' if ci == 0 else '', border=1, align='C')
                            pdf.cell(col_w[3], 5, rc['nombre_competencia'][:35], border=1)
                            pdf.cell(col_w[4], 5, f"{rc['porcentaje']}%", border=1, align='C')
                            pond = rc['resultado'] if rc['resultado'] else 0
                            pdf.cell(col_w[5], 5, f"{pond:.2f}", border=1, align='C')
                            pdf.ln()
                    else:
                        pdf.cell(col_w[0], 5, rt['nombre_tipo'], border=1, align='C')
                        pdf.cell(col_w[1], 5, f"{rt['porcentaje']}%", border=1, align='C')
                        rv = rt['resultado'] or 0
                        pdf.cell(col_w[2], 5, f"{rv:.2f}", border=1, align='C')
                        pdf.cell(col_w[3] + col_w[4] + col_w[5], 5, 'Sin competencias detalladas', border=1)
                        pdf.ln()

                # Total general
                pdf.ln(1)
                pdf.set_font('Arial', 'B', 8)
                general = ev.get('resultado_general')
                if general is not None:
                    safe_text = f'RESULTADO GENERAL: {general:.2f}%'.encode('latin-1', 'replace').decode('latin-1')
                else:
                    safe_text = 'RESULTADO GENERAL: -'.encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 6, safe_text, ln=True, align='R')

            # Observaciones
            obs_eval = ev.get('observaciones_evaluador')
            if obs_eval:
                pdf.ln(2)
                pdf.set_font('Arial', 'I', 7)
                safe_obs = obs_eval.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 4, f'Obs. Evaluador: {safe_obs}')

    # ── Salida ──
    pdf_output = pdf.output()
    if isinstance(pdf_output, bytearray):
        pdf_output = bytes(pdf_output)
    elif isinstance(pdf_output, str):
        pdf_output = pdf_output.encode('latin-1')

    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Evaluaciones_Desempeno_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return response


#------------------------------------------------------
#--------------- EXPORTAR PDF RESUMEN -----------------
#------------------------------------------------------
@rrhh_bp.route('/evaluacion/exportar_resumen_pdf')
@login_required
@admin_rrhh_required
def exportar_resumen_evaluaciones_pdf():
    """
    Genera un PDF con el resumen completo de evaluaciones:
    estadísticas (stats), tabla de datos del gráfico y acordeones.
    """
    resultados = consulta_resultados_evaluacion()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    path_logo = os.path.join(current_app.root_path, 'static', 'imgs', 'logo.png')
    pdf.add_page()

    # ── Encabezado ──
    # Logo
    if os.path.exists(path_logo):
        pdf.image(path_logo, x=10, y=8, w=40)
    pdf.set_font('Arial', 'B', 16)
    pdf.ln(12)
    pdf.cell(0, 10, 'RESUMEN DE EVALUACIONES DE DESEMPENO', ln=True, align='C')
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 5, f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', ln=True, align='C')
    pdf.ln(5)

    # ── Calcular estadísticas ──
    total = len(resultados)
    presentadas = sum(1 for r in resultados if r.get('estado_asignacion') == 1)
    no_presentadas = total - presentadas
    aprob_eval = sum(1 for r in resultados if r.get('aprobado_evaluado') == 1)
    no_aprob_eval = presentadas - aprob_eval
    aprob_rrhh = sum(1 for r in resultados if r.get('aprobado_rrhh') == 1)
    no_aprob_rrhh = presentadas - aprob_rrhh

    # Promedio general
    suma_resultados = 0
    contador_resultados = 0
    for r in resultados:
        if r.get('estado_asignacion') == 1 and r.get('resultado_general') is not None:
            val = r['resultado_general']
            if val > 0:
                suma_resultados += val
                contador_resultados += 1
    promedio = suma_resultados / contador_resultados if contador_resultados > 0 else 0

    # ── Stats Cards ──
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(0, 7, 'ESTADISTICAS GENERALES', ln=True, fill=True)
    pdf.ln(2)

    stats_data = [
        ('Total Asignadas', str(total)),
        ('Presentadas', str(presentadas)),
        ('No Presentadas', str(no_presentadas)),
        ('Aprob. Evaluado', str(aprob_eval)),
        ('No Aprob. Evaluado', str(no_aprob_eval)),
        ('Aprob. RRHH', str(aprob_rrhh)),
        ('No Aprob. RRHH', str(no_aprob_rrhh)),
        ('Promedio General', f'{promedio:.2f}'),
    ]

    col_w_stats = [65, 30]
    pdf.set_font('Arial', '', 9)
    for label, value in stats_data:
        pdf.set_fill_color(248, 250, 252)
        pdf.cell(col_w_stats[0], 6, f'  {label}', border=1, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_w_stats[1], 6, value, border=1, fill=True, align='C')
        pdf.ln()

    pdf.ln(5)

    # ── Tabla de datos del gráfico ──
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(0, 7, 'DATOS DEL GRAFICO (Presentacion / Aprobaciones)', ln=True, fill=True)
    pdf.ln(2)

    col_w_chart = [50, 35, 35]
    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(['Indicador', 'Si', 'No']):
        pdf.cell(col_w_chart[i], 6, h, border=1, fill=True, align='C')
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8)

    chart_rows = [
        ('Presentacion', presentadas, no_presentadas),
        ('Aprob. Evaluado', aprob_eval, no_aprob_eval),
        ('Aprob. RRHH', aprob_rrhh, no_aprob_rrhh),
    ]
    for label, si, no in chart_rows:
        pdf.cell(col_w_chart[0], 5, f'  {label}', border=1)
        pdf.cell(col_w_chart[1], 5, str(si), border=1, align='C')
        pdf.cell(col_w_chart[2], 5, str(no), border=1, align='C')
        pdf.ln()

    pdf.ln(5)

    # ── Evaluaciones Presentadas ──
    if presentadas > 0:
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(22, 163, 74)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 7, f'EVALUACIONES PRESENTADAS ({presentadas})', ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        col_w = [40, 40, 30, 35, 35]
        pdf.set_font('Arial', 'B', 7)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(['Evaluador', 'Evaluado', 'Cargo', 'Resultado', 'Fecha']):
            pdf.cell(col_w[i], 6, h, border=1, fill=True, align='C')
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 7)

        for r in resultados:
            if r.get('estado_asignacion') != 1:
                continue
            evaluador = f"{r['evaluador_nombres']} {r['evaluador_apellidos']}"[:20]
            evaluado = f"{r['evaluado_nombres']} {r['evaluado_apellidos']}"[:20]
            cargo = (r['plantilla_nombre'] or '-')[:15]
            resultado = f"{r['resultado_general']:.2f}" if r.get('resultado_general') is not None else '-'
            fecha = r['fecha_evaluacion'].strftime('%d/%m/%Y') if r.get('fecha_evaluacion') else '-'
            pdf.cell(col_w[0], 5, evaluador, border=1)
            pdf.cell(col_w[1], 5, evaluado, border=1)
            pdf.cell(col_w[2], 5, cargo, border=1, align='C')
            pdf.cell(col_w[3], 5, resultado, border=1, align='C')
            pdf.cell(col_w[4], 5, fecha, border=1, align='C')
            pdf.ln()

    pdf.ln(5)

    # ── Observaciones ──
    if no_presentadas > 0:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(217, 119, 6)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 7, f'EVALUACIONES SIN REALIZAR ({no_presentadas})', ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        col_w2 = [40, 40, 30, 35, 35]
        pdf.set_font('Arial', 'B', 7)
        pdf.set_fill_color(30, 58, 138)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(['Evaluador', 'Evaluado', 'Cargo', 'Resultado', 'Fecha']):
            pdf.cell(col_w2[i], 6, h, border=1, fill=True, align='C')
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 7)

        for r in resultados:
            if r.get('estado_asignacion') == 1:
                continue
            evaluador = f"{r['evaluador_nombres']} {r['evaluador_apellidos']}"[:20]
            evaluado = f"{r['evaluado_nombres']} {r['evaluado_apellidos']}"[:20]
            cargo = (r['plantilla_nombre'] or '-')[:15]
            resultado = 'Pendiente'
            fecha = r['fecha_evaluacion'].strftime('%d/%m/%Y') if r.get('fecha_evaluacion') else '-'
            pdf.cell(col_w2[0], 5, evaluador, border=1)
            pdf.cell(col_w2[1], 5, evaluado, border=1)
            pdf.cell(col_w2[2], 5, cargo, border=1, align='C')
            pdf.cell(col_w2[3], 5, resultado, border=1, align='C')
            pdf.cell(col_w2[4], 5, fecha, border=1, align='C')
            pdf.ln()

    # ── Salida ──
    pdf_output = pdf.output()
    if isinstance(pdf_output, bytearray):
        pdf_output = bytes(pdf_output)
    elif isinstance(pdf_output, str):
        pdf_output = pdf_output.encode('latin-1')

    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Resumen_Evaluaciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    return response


#------------------------------------------------------
#--------------- EVALUACION DESEMPEÑO -----------------
#------------------------------------------------------
@rrhh_bp.route('/evaluacion')
@login_required
@admin_rrhh_required
def evaluacion():
    empleados_list = empleados_lista()
    tipo_competencias = consulta_tipo_competencias()
    criterios = consulta_criterios()
    preguntas = consulta_preguntas()
    lista_cargos = consulta_plantillas_evaluacion_desde_asignaciones()
    porcentajes_tipo = consulta_porcentajes_tipo()
    porcentajes_competencia = consulta_porcentajes_competencia()
    resultados_evaluacion = consulta_resultados_evaluacion()
    return render_template(
        'rrhh/construccion_evaluacion.html',
        usuario=current_user,
        empleados_list=empleados_list,
        tipo_competencias=tipo_competencias,
        criterios=criterios,
        preguntas=preguntas,
        lista_cargos=lista_cargos,
        porcentajes_tipo=porcentajes_tipo,
        porcentajes_competencia=porcentajes_competencia,
        resultados_evaluacion=resultados_evaluacion,
        active_main_tab='habilitar',
    )

@rrhh_bp.route('/evaluacion/usuario')
@login_required
def evaluacion_usuario():
    evaluaciones_habilitadas = consulta_evaluacion_habilitada(current_user.id)
    return render_template('rrhh/evaluacion_usuario.html', usuario=current_user, evaluaciones_habilitadas=evaluaciones_habilitadas)

@rrhh_bp.route('/habilitar_evaluacion', methods=['POST'])
@login_required
@admin_rrhh_required
def habilitar_evaluacion():
    try:
        anio_evaluacion = request.form.get('anio_evaluacion')
        inicio = request.form.get('fecha_inicio')
        fin = request.form.get('fecha_fin')
        evaluador = request.form.get('evaluador_id')
        evaluados = request.form.getlist('evaluado_id')
        
        if not anio_evaluacion or not inicio or not fin or not evaluador or not evaluados:
            return jsonify({'success': False, 'error': 'Todos los campos son requeridos'}), 400
        
        inicio = datetime.strptime(inicio, '%Y-%m-%d')
        fin = datetime.strptime(fin, '%Y-%m-%d')
        
        habilita_evaluacion(anio_evaluacion, inicio, fin, evaluador, evaluados)

        return jsonify({'success': True, 'message': 'Evaluación habilitada con éxito'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@rrhh_bp.route('/evaluar_empleado/<int:id_asignacion>')
@login_required
def evaluar_empleado(id_asignacion):
    datos_evaluado, listas_preguntas, tipo_competencias, competencias = obtener_plantilla(id_asignacion)
    return render_template('rrhh/ejecutar_evaluacion_desempeno.html', usuario=current_user, evaluado=datos_evaluado, preguntas=listas_preguntas, tipo_competencias=tipo_competencias, competencias=competencias)

@rrhh_bp.route('/evaluaciones_pendientes_evaluado')
@login_required
def mis_evaluaciones_pendientes():
    """
    Retorna las evaluaciones completadas donde el usuario actual es evaluado
    y aún no han sido aprobadas por él.
    """
    try:
        evaluaciones = consulta_evaluaciones_pendientes_evaluado(current_user.id)
        return jsonify({'success': True, 'evaluaciones': evaluaciones})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/aprobar_evaluacion_rrhh', methods=['POST'])
@login_required
@admin_rrhh_required
def aprobar_evaluacion_rrhh():
    """
    Marca aprobado_rrhh = 1 para la asignacion indicada.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        id_asignacion = data.get('id_asignacion')
        if not id_asignacion:
            return jsonify({'success': False, 'error': 'id_asignacion es requerido'}), 400
        
        exito, error = guardar_aprobacion_rrhh(id_asignacion)
        if exito:
            return jsonify({'success': True, 'message': 'Evaluación aprobada por RRHH correctamente'})
        else:
            return jsonify({'success': False, 'error': error}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/aprobar_evaluacion_evaluado', methods=['POST'])
@login_required
def aprobar_evaluacion_evaluado():
    """
    Guarda las observaciones del evaluado y marca aprobado_evaluado = 1.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        id_asignacion = data.get('id_asignacion')
        observaciones = data.get('observaciones', '')
        
        if not id_asignacion:
            return jsonify({'success': False, 'error': 'id_asignacion es requerido'}), 400
        
        exito, error = guardar_aprobacion_evaluado(id_asignacion, observaciones)
        if exito:
            return jsonify({'success': True, 'message': 'Evaluación aprobada correctamente'})
        else:
            return jsonify({'success': False, 'error': error}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/guardar_evaluacion', methods=['POST'])
def guardar_evaluacion():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No se recibieron Datos"
            }), 400
        
        id_asginacion = data.get('id_asignacion')
        competencias = data.get('competencias', [])
        totales_tipo = data.get('totales_por_tipo', [])
        resultado_general = data.get('resultado_general', {})
        observaciones_evaluador = data.get('observacionesEvaluador')
        aspectos_sobresalientes = data.get('aspectos_sobresalientes')
        aspectos_mejorar = data.get('aspectos_mejorar')

        exito, mensaje = guardaEvaluacion(
            id_asginacion,
            competencias,
            totales_tipo,
            resultado_general,
            observaciones_evaluador,
            aspectos_sobresalientes,
            aspectos_mejorar
        )
        if exito:
            return jsonify({
            "success": True, 
            "message": mensaje
            })
        else:
            return jsonify({
            "success": False, 
            "message": mensaje
            })

    except Exception as e:
        print(f"error: {e}")
        return jsonify({"success": False, "message": "Error interno en el controlador."}), 500

# construcción de evaluación
@rrhh_bp.route('/const_evaluacion')
@login_required
@admin_rrhh_required
def const_evaluacion():
    empleados_list = empleados_lista()
    tipo_competencias = consulta_tipo_competencias()
    criterios = consulta_criterios()
    preguntas = consulta_preguntas()
    lista_cargos = consulta_plantillas_evaluacion_desde_asignaciones()
    porcentajes_tipo = consulta_porcentajes_tipo()
    porcentajes_competencia = consulta_porcentajes_competencia()
    resultados_evaluacion = consulta_resultados_evaluacion()
    return render_template(
        'rrhh/construccion_evaluacion.html',
        usuario=current_user,
        empleados_list=empleados_list,
        tipo_competencias=tipo_competencias,
        criterios=criterios,
        preguntas=preguntas,
        lista_cargos=lista_cargos,
        porcentajes_tipo=porcentajes_tipo,
        porcentajes_competencia=porcentajes_competencia,
        resultados_evaluacion=resultados_evaluacion,
        active_main_tab='construccion',
    )


@rrhh_bp.route('/const_evaluacion/tipo_competencia/crear', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_crear_tipo_competencia():
    try:
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre es obligatorio'}), 400
        new_id = crear_tipo_competencia(nombre)
        return jsonify({'success': True, 'id': new_id, 'nombre': nombre})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/criterio/crear', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_crear_criterio():
    try:
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        id_tipo = data.get('id_tipo')
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre es obligatorio'}), 400
        if id_tipo is None:
            return jsonify({'success': False, 'error': 'Debe seleccionar un tipo de competencia'}), 400
        id_tipo = int(id_tipo)
        new_id = crear_criterio_competencia(nombre, id_tipo)
        tipo_row = next((t for t in consulta_tipo_competencias() if int(t['id']) == id_tipo), None)
        competencia_nombre = tipo_row['nombre'] if tipo_row else ''
        return jsonify({
            'success': True,
            'id_criterio': new_id,
            'nombre': nombre,
            'id_tipo': id_tipo,
            'competencia': competencia_nombre,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/pregunta/crear', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_crear_pregunta():
    try:
        data = request.get_json() or {}
        pregunta = (data.get('pregunta') or '').strip()
        id_plantilla = data.get('id_plantilla')
        tipo = data.get('tipo')
        competencia = data.get('competencia')
        porcentaje_tipo = data.get('porc_tipo')
        porcentaje_criterio = data.get('porc_criterio')
        if not pregunta:
            return jsonify({'success': False, 'error': 'La pregunta no puede estar vacía'}), 400
        if id_plantilla is None or tipo is None or competencia is None:
            return jsonify({'success': False, 'error': 'Cargo, tipo y criterio son obligatorios'}), 400
        id_plantilla = int(id_plantilla)
        tipo = int(tipo)
        competencia = int(competencia)
        if not id_plantilla_existe_en_asignaciones_evaluacion(id_plantilla):
            return jsonify({
                'success': False,
                'error': (
                    'El cargo/plantilla seleccionado no existe en la tabla cargos.'
                ),
            }), 400
        new_id = crear_pregunta_evaluacion(pregunta, id_plantilla, tipo, competencia, porcentaje_tipo, porcentaje_criterio)
        cargo_row = next((c for c in consulta_plantillas_evaluacion_desde_asignaciones() if int(c['id']) == id_plantilla), None)
        asignado = cargo_row['nombre'] if cargo_row else ''
        return jsonify({
            'success': True,
            'id': new_id,
            'pregunta': pregunta,
            'asignado': asignado,
            'id_plantilla': id_plantilla,
            'tipo': tipo,
            'competencia': competencia,
            'porcentaje_tipo': porcentaje_tipo,
            'porcentaje_criterio': porcentaje_criterio
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/tipo_competencia/editar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_editar_tipo_competencia(id):
    try:
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre es obligatorio'}), 400
        editar_tipo_competencia(id, nombre)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/tipo_competencia/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_eliminar_tipo_competencia(id):
    try:
        eliminar_tipo_competencia(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/criterio/editar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_editar_criterio(id):
    try:
        data = request.get_json() or {}
        nombre = (data.get('nombre') or '').strip()
        id_tipo = data.get('id_tipo')
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre es obligatorio'}), 400
        if id_tipo is None:
            return jsonify({'success': False, 'error': 'Debe seleccionar un tipo de competencia'}), 400
        editar_criterio_competencia(id, nombre, int(id_tipo))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/criterio/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_eliminar_criterio(id):
    try:
        eliminar_criterio_competencia(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/pregunta/editar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_editar_pregunta(id):
    try:
        data = request.get_json() or {}
        pregunta = (data.get('pregunta') or '').strip()
        id_plantilla = data.get('id_plantilla')
        tipo = data.get('tipo')
        competencia = data.get('competencia')
        porc_tipo = data.get('porc_tipo')
        porc_competencia = data.get('porc_competencia', data.get('porc_criterio'))
        if not pregunta:
            return jsonify({'success': False, 'error': 'La pregunta no puede estar vacía'}), 400
        if id_plantilla is None or tipo is None or competencia is None or porc_tipo is None or porc_competencia is None:
            return jsonify({'success': False, 'error': 'Todos los campos y porcentajes son obligatorios'}), 400
        id_plantilla = int(id_plantilla)
        tipo = int(tipo)
        competencia = int(competencia)
        porc_tipo = float(porc_tipo)
        porc_competencia = float(porc_competencia)
        if not id_plantilla_aceptada_al_editar_pregunta(id, id_plantilla):
            return jsonify({
                'success': False,
                'error': (
                    'El cargo/plantilla seleccionado no es valido: debe existir en la tabla cargos.'
                ),
            }), 400
        editar_pregunta_evaluacion(
            id,
            pregunta,
            id_plantilla,
            tipo,
            competencia,
            porc_tipo,
            porc_competencia
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@rrhh_bp.route('/const_evaluacion/pregunta/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_rrhh_required
def const_eval_eliminar_pregunta(id):
    try:
        data = request.get_json(silent=True) or {}
        id_plantilla = data.get('id_plantilla')
        eliminadas = eliminar_pregunta_evaluacion(id, int(id_plantilla) if id_plantilla else None)
        if not eliminadas:
            return jsonify({'success': False, 'error': 'No se encontró la pregunta para ese cargo.'}), 404
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


#------------------------------------------------------
#---------------------- BUZON -------------------------
#------------------------------------------------------
@rrhh_bp.route('/buzon')
@login_required
def buzon():
    """Pagina del buzon de mensajes del empleado actual."""
    user_id = current_user.get_id()
    try:
        real_id = int(str(user_id).split('-')[1])
    except (ValueError, IndexError):
        flash('Error al identificar el usuario', 'error')
        return redirect(url_for('auth.login'))

    mensajes = obtener_mensajes_buzon(real_id)
    no_leidos = contar_mensajes_no_leidos(real_id)
    # El buzón de salida solo es visible para usuarios con rol Talento Humano
    # (los que tienen acceso al módulo RRHH).
    es_talento_humano = getattr(current_user, 'sgi_rol_id', None) == ROL_TALENTO_HUMANO
    mensajes_enviados = obtener_mensajes_enviados_buzon(real_id) if es_talento_humano else []
    return render_template('rrhh/buzon.html',
                           usuario=current_user,
                           mensajes=mensajes,
                           no_leidos=no_leidos,
                           es_talento_humano=es_talento_humano,
                           mensajes_enviados=mensajes_enviados)


@rrhh_bp.route('/api/buzon/mensajes')
@login_required
def api_buzon_mensajes():
    """API: Retorna los mensajes del buzon del empleado actual."""
    try:
        user_id = current_user.get_id()
        real_id = int(str(user_id).split('-')[1])
        solo_no_leidos = request.args.get('no_leidos', '').lower() == 'true'
        mensajes = obtener_mensajes_buzon(real_id, solo_no_leidos=solo_no_leidos)
        no_leidos = contar_mensajes_no_leidos(real_id)
        return jsonify({'success': True, 'mensajes': mensajes, 'no_leidos': no_leidos, 'total': len(mensajes)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rrhh_bp.route('/api/buzon/marcar_leido/<int:mensaje_id>', methods=['POST'])
@login_required
def api_buzon_marcar_leido(mensaje_id):
    """API: Marca un mensaje como leido."""
    try:
        user_id = current_user.get_id()
        real_id = int(str(user_id).split('-')[1])
        marcar_mensaje_leido(mensaje_id, real_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rrhh_bp.route('/api/buzon/no_leidos')
@login_required
def api_buzon_no_leidos():
    """API: Retorna el conteo de mensajes no leidos."""
    try:
        user_id = current_user.get_id()
        real_id = int(str(user_id).split('-')[1])
        count = contar_mensajes_no_leidos(real_id)
        return jsonify({'success': True, 'no_leidos': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


#------------------------------------------------------
#-------- CONFIRMACIÓN DE DATOS PERSONALES -----------
#------------------------------------------------------
@rrhh_bp.route('/api/confirmar_datos/empleado', methods=['GET'])
@login_required
def api_obtener_datos_confirmacion():
    """API: Retorna los datos personales del empleado para el modal de confirmación."""
    try:
        user_id = current_user.get_id()
        real_id = int(str(user_id).split('-')[1])
        empleado = obtener_datos_confirmacion(real_id)
        if not empleado:
            return jsonify({'success': False, 'error': 'Empleado no encontrado'}), 404
        return jsonify({
            'success': True,
            'empleado': {
                'nombres': empleado.get('nombres', ''),
                'apellidos': empleado.get('apellidos', ''),
                'identificacion': empleado.get('identificacion', ''),
                'correo': empleado.get('correo', ''),
                'celular': empleado.get('celular', ''),
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@rrhh_bp.route('/api/confirmar_datos', methods=['POST'])
@login_required
def api_confirmar_datos():
    """API: Guarda la confirmación de datos del empleado y actualiza la fecha.

    Si el body contiene { _limpiar_flag: true }, solo limpia el flag de sesión
    sin guardar datos (usado después de la primera llamada exitosa).
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400

        # Si solo se pide limpiar el flag de sesión
        if data.get('_limpiar_flag'):
            session.pop('requiere_confirmacion_datos', None)
            return jsonify({'success': True})

        correo = (data.get('correo') or '').strip()
        celular = (data.get('celular') or '').strip()

        if not correo:
            return jsonify({'success': False, 'error': 'El correo electrónico es obligatorio'}), 400
        if not celular:
            return jsonify({'success': False, 'error': 'El número de celular es obligatorio'}), 400

        user_id = current_user.get_id()
        real_id = int(str(user_id).split('-')[1])

        guardar_confirmacion_datos(real_id, correo, celular)

        # Limpiar el flag de sesión para que no vuelva a mostrar el modal
        session.pop('requiere_confirmacion_datos', None)

        return jsonify({
            'success': True,
            'message': 'Datos confirmados correctamente'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
