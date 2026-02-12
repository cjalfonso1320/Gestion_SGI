from flask import Blueprint, render_template, redirect, url_for, flash, make_response
from flask import request, jsonify, current_app, send_file
from flask_login import login_required, current_user
import os
from datetime import datetime
import zipfile
import shutil
from fpdf import FPDF

from controllers.rrhh_controller import total_empleados, empleados_lista, empleado_lista_completo, estado_civil, grupo_sanguineo, eps, afp, cesantias, ccf, arl, tipo_contrato, sede, escolaridad, bancos, grupo_nomina, cargos, ciudades, total_empleados_retirados
from controllers.rrhh_controller import crear_grupoNomina, editar_grupoNomina, eliminar_grupoNomina, crear_cargo, editar_cargo, eliminar_cargo, crear_empleado, guardar_documentos_estudio, lista_documentos_estudio_empleado, actualizar_empleado, desactivar_empleado
from controllers.rrhh_controller import activar_empleado, contratos_empleado, total_empleados_retirados
from utils.files import guardar_archivo, guardar_archivos_multiples

from controllers.rrhh_controller import importar_empleados_plantilla, actualizar_empleados_plantilla, empleado_existe, actualiza_foto, actualiza_cedula, guardar_documento_estudio, empleado_lista_completo_por_identificacion
from controllers.rrhh_controller import obtener_datos_certificado, tipoContrato_id, actualiza_consecutivo, genera_consecutivo
from controllers.rrhh_controller import procesar_otrosi_db
from utils.password_utils import hash_password


import pandas as pd
import io

rrhh_bp = Blueprint('rrhh', __name__, url_prefix='/rrhh')


#------------------------------------------------------
#---------------------- UTILIDADES --------------------
#------------------------------------------------------
def limpiar_fecha(val):
    if pd.isna(val) or val == '': return None
    try: return pd.to_datetime(val).strftime("%Y-%m-%d")
    except: return None   
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
            'ESCOLARIDAD': get_map(escolaridad())
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
        empleados_retirados = total_empleados_retirados()
        cuenta_nominas = len(nominaS)
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
            'empleados_retirados': empleados_retirados,
            'cuenta_nominas': cuenta_nominas,
            'consecutivo_contratos': tipoContrato
        }

#------------------------------------------------------
#----------------- ADMIN REQUIRED ---------------------
#------------------------------------------------------
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
    
    return render_template('rrhh/dashboard_admin.html', 
                           usuario=current_user, 
                           empleados=empleados, 
                           empleados_retirados=empleados_retirados, 
                           cuenta_nominas=cuenta_nominas,
                           consecutivo_contratos=conseccontratos)

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
            d['ruta'].replace('\\','/')
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
    empleado = empleado_lista_completo(id)
    empleado["fecha_ingreso"] = formatear_fecha(empleado.get("fecha_ingreso"))
    empleado["fecha_nacimiento"] = formatear_fecha(empleado.get("fecha_nacimiento"))
    if not empleado:
        return jsonify({"success": False})
    
    return jsonify({
        "success": True,
        "empleado": empleado
    })
 
#------------------------------------------------------
#-----------------EDITAR EMPLEADO ---------------------
#------------------------------------------------------   
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
    empleados_list = empleados_lista()
    contratos = tipo_contrato()
    cuenta_nominas = len(grupo_nomina())
    empleados_retirados = total_empleados_retirados()
    conseccontratos = tipo_contrato()
    return render_template('rrhh/empleados_retirados.html', 
                            usuario=current_user, 
                            empleados_list=empleados_list,
                            contratos = contratos,
                            cuenta_nominas=cuenta_nominas,
                           empleados_retirados=empleados_retirados,
                           consecutivo_contratos=conseccontratos
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
        'ESTADO_CIVIL', 'GRUPO_SANGUINEO', 'NUMERO_HIJOS', 'DIRECCION',
        'CIUDAD_BARRIO', 'LOCALIDAD', 'TELEFONO_FIJO', 'CELULAR',
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
            
        ]
        #escribir las listas en columnas de la hoja oculta
        for col, data in listas_db:
            for row, value in enumerate(data):
                hidden_sheet.write(row, col, value)
        #definir ranfos de validacion
        def aplicar_validacion(col_index, list_col_letter, num_items):
            #valida desde la fila 2 a la 1000
            worksheet.data_validation(1, col_index, 1000, col_index, {
                'validate': 'list',
                'source': f'=ListasDesplegables!{list_col_letter}1:{list_col_letter}${num_items}'
            })
        #aplicar validaciones a las columnas correspondientes
        worksheet.data_validation(1, 4, 1000, 4, {'validate': 'list', 'source': ['M', 'F']})
        
        #dinamicos desde BD
        aplicar_validacion(7, 'A', len(listas_db[0][1]))  # estado_civil
        aplicar_validacion(8, 'B', len(listas_db[1][1]))  # grupo_sanguineo
        aplicar_validacion(11, 'C', len(listas_db[2][1]))  # ciudad_barrio
        aplicar_validacion(19, 'D', len(listas_db[3][1]))  # eps
        aplicar_validacion(20, 'E', len(listas_db[4][1]))  # afp
        aplicar_validacion(21, 'F', len(listas_db[5][1]))  # cesantias
        aplicar_validacion(22, 'G', len(listas_db[6][1]))  # ccf
        aplicar_validacion(23, 'H', len(listas_db[7][1]))  # arl
        aplicar_validacion(24, 'I', len(listas_db[8][1]))  # tipo_contrato
        aplicar_validacion(25, 'J', len(listas_db[9][1]))  # cargo
        aplicar_validacion(27, 'K', len(listas_db[10][1]))  # sede
        aplicar_validacion(32, 'L', len(listas_db[11][1]))  # banco
        aplicar_validacion(33, 'M', len(listas_db[12][1]))  # grupo_nomina
        aplicar_validacion(34, 'N', len(listas_db[13][1]))  # nivel_escolaridad
        
        #jornada y estudia actualmente (Estaticos)
        worksheet.data_validation(1, 26, 1000, 26, {'validate': 'list', 'source': ['DIURNO', 'TARDE', 'NOCTURNO']})
        worksheet.data_validation(1, 36, 1000, 36, {'validate': 'list', 'source': ['SI', 'NO']})
                
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 25)  # Ancho de columna de 25
            
    output.seek(0)
    
    return send_file(output, 
                     download_name="plantilla_empleados.xlsx",
                     as_attachment=True,                      
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
       
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
        for _, row in df.iterrows():
            r = row.to_dict()
            
            ident = str(r.get('IDENTIFICACION')).split('.')[0]
            f_nacimiento = limpiar_fecha(r.get('FECHA_NACIMIENTO (AAAA-MM-DD)'))
            f_ingreso = limpiar_fecha(r.get('FECHA_INGRESO (AAAA-MM-DD)'))
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
                'numero_hijos': int(r.get('NUMERO_HIJOS', 0)),
                'direccion': limpiar_texto(r.get('DIRECCION')),
                'barrio_id': get_id_mapas(mapas, 'CIUDAD', r.get('CIUDAD_BARRIO')),
                'localidad': limpiar_texto(r.get('LOCALIDAD', 'N/A')),
                'estrato': int(r.get('ESTRATO', 1)),
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
                'tipo_contrato_id': get_id_mapas(mapas, 'TIPO_CONTRATO', r.get('TIPO_CONTRATO')),
                'cargo_id': get_id_mapas(mapas, 'CARGO', r.get('CARGO')),
                'jornada': str(r.get('JORNADA', 'DIURNO')).upper(),
                'sede_id': get_id_mapas(mapas, 'SEDE', r.get('SEDE')),
                'antiguedad': calcula_antiguedad(f_ingreso),
                'fecha_ingreso': f_ingreso,
                'salario_basico': float(str(r.get('SALARIO_BASICO', 0)).replace(',', '')),
                'factor_no_salarial': float(str(r.get('FACTOR_NO_SALARIAL', 0)).replace(',', '')),
                'numero_cuenta': r.get('NUMERO_CUENTA'),
                'banco_id': get_id_mapas(mapas, 'BANCO', r.get('BANCO')),
                'grupo_nomina_id': get_id_mapas(mapas, 'NOMINA', r.get('GRUPO_NOMINA')),
                'nivel_escolaridad_id': get_id_mapas(mapas, 'ESCOLARIDAD', r.get('NIVEL_ESCOLARIDAD')),
                'programa_academico': str(r.get('PROGRAMA_ACADEMICO')).upper(),
                'estudia_actualmente': str(r.get('ESTUDIA_ACTUALMENTE (SI/NO)', 'NO')).upper(),
                'nombre_programa_actual': limpiar_texto(r.get('NOMBRE_PROGRAMA_ACTUAL', 'N/A')),
                'password': hash_password(ident)
            }
            importar_empleados_plantilla(data_limpia)
            insertados += 1
        return jsonify({'success': True, 'insertados': insertados})
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
        for _, row in df.iterrows():
            r = row.to_dict()
            ident = str(r.get('IDENTIFICACION')).split('.')[0]
            f_ingreso = limpiar_fecha(r.get('FECHA_INGRESO (AAAA-MM-DD)'))
            f_nacimiento = limpiar_fecha(r.get('FECHA_NACIMIENTO (AAAA-MM-DD)'))
            
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
                'numero_hijos': int(r.get('NUMERO_HIJOS', 0)),
                'direccion': limpiar_texto(r.get('DIRECCION')),
                'barrio_id': get_id_mapas(mapas, 'CIUDAD', r.get('CIUDAD_BARRIO')),
                'localidad': limpiar_texto(r.get('LOCALIDAD', 'N/A')),
                'estrato': int(r.get('ESTRATO', 1)),
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
                'tipo_contrato_id': get_id_mapas(mapas, 'TIPO_CONTRATO', r.get('TIPO_CONTRATO')),
                'cargo_id': get_id_mapas(mapas, 'CARGO', r.get('CARGO')),
                'jornada': str(r.get('JORNADA', 'DIURNO')).upper(),
                'sede_id': get_id_mapas(mapas, 'SEDE', r.get('SEDE')),
                'antiguedad': calcula_antiguedad(f_ingreso),
                'fecha_ingreso': f_ingreso,
                'salario_basico': float(str(r.get('SALARIO_BASICO', 0)).replace(',', '')),
                'factor_no_salarial': float(str(r.get('FACTOR_NO_SALARIAL', 0)).replace(',', '')),
                'numero_cuenta': r.get('NUMERO_CUENTA'),
                'banco_id': get_id_mapas(mapas, 'BANCO', r.get('BANCO')),
                'grupo_nomina_id': get_id_mapas(mapas, 'NOMINA', r.get('GRUPO_NOMINA')),
                'nivel_escolaridad_id': get_id_mapas(mapas, 'ESCOLARIDAD', r.get('NIVEL_ESCOLARIDAD')),
                'programa_academico': str(r.get('PROGRAMA_ACADEMICO')).upper(),
                'estudia_actualmente': str(r.get('ESTUDIA_ACTUALMENTE (SI/NO)', 'NO')).upper(),
                'nombre_programa_actual': limpiar_texto(r.get('NOMBRE_PROGRAMA_ACTUAL', 'N/A')),
                'password': hash_password(ident)
            }
            if empleado_existe(ident):
                print(data_limpia)
                actualizar_empleados_plantilla(data_limpia)
            else:
                importar_empleados_plantilla(data_limpia)
            procesados += 1
        actualizados = procesados
        
        return jsonify({'success': True, 'actualizados': actualizados})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
@rrhh_bp.route('/empleados/descargar_reporte_empleados')
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
            
            worksheet.data_validation(1, 4, 2000, 4, {'validate': 'list', 'source': ['M', 'F']})
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
            worksheet.data_validation(1, 26, 2000, 26, {'validate': 'list', 'source': ['DIURNO', 'TARDE', 'NOCTURNO']})
            aplicar_validacion(27, 'K', len(listas_db[10][1])) # sede
            aplicar_validacion(32, 'L', len(listas_db[11][1])) # banco
            aplicar_validacion(33, 'M', len(listas_db[12][1])) # grupo_nomina
            aplicar_validacion(34, 'N', len(listas_db[13][1])) # nivel_escolaridad
            worksheet.data_validation(1, 36, 2000, 36, {'validate': 'list', 'source': ['SI', 'NO']})
            
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
                if filename == file.filename: continue
                
                parts = filename.upper().split('_')
                if len(parts) < 2: continue
                
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
#--------------- CONSECUTIVOS CONTRATO ----------------
#------------------------------------------------------
@rrhh_bp.route("/contratos/<int:id>", methods=['GET'])
@login_required
@admin_rrhh_required
def consecutivo_contrato(id):
    try:
        contratos = tipoContrato_id(id)
        if not contratos: return jsonify({'success': False, 'error': 'Contrato no encontrado'}), 404
        
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