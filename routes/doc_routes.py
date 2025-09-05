from flask import Blueprint, render_template, send_file, abort, request, session
from flask_login import current_user
import os
from extension import mysql
from controllers.doc_controller import procedimientos, caracterizacion, formatos_digitales, formatos_fisicos, formatos_externos_digitales, formatos_externos_fisicos, plan_calidad, requisitos_cliente, actas_restauracion, instructivos, manuales
from controllers.doc_controller import auditorias_ifx, auditoria_integrum, auditoria_inter_servicios, ISECpoliticaContinuidad, ISECpoliticaProteccionDatos, ISECpoliticaSeguridadInf, comite_seguridad
from controllers.doc_controller import vulnerabilidades_2024, vulnerabilidades_2025, vulnerabilidades_ant
from controllers.doc_controller import revision_seguridad_2021, revision_seguridad_2022, revision_seguridad_2023, revision_seguridad_2024, sst, encuestas_2019, encuestas_2020, encuestas_2021, sagrilaft, ambiental
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES, nombre_rol




doc_bp = Blueprint('doc', __name__)

@doc_bp.route('/documentacion', defaults={'role_id': None})
@doc_bp.route('/documentacion/<int:role_id>')
def documentacion(role_id):
    is_role_override = role_id is not None

    if is_role_override:
        session['selected_rol'] = role_id
        rol = role_id
    else:
        rol = session.get('selected_rol', current_user.rol)

    def CONTEXTO(rol_actual):
        procesos = PROCESOS_ROL.get(rol, [])
        imagen_rol = ROL_IMAGES.get(rol, 'imgs/user.png')
        nombre_del_rol = nombre_rol(rol)
        archivos_procedimientos = procedimientos(rol)
        caracterizaciones = caracterizacion(rol)
        formatoDigital = formatos_digitales(rol)
        formatoFisico = formatos_fisicos(rol)
        formatoExternoDigital = formatos_externos_digitales(rol)
        formatoExternoFisico = formatos_externos_fisicos(rol)
        planCalidad = plan_calidad(rol)
        requisitosCliente = requisitos_cliente(rol)
        actasRestauracion = actas_restauracion(rol)
        archivos_instructivos = instructivos(rol)
        archivos_manuales = manuales(rol)
        archivos_auditorias_ifx = auditorias_ifx(rol)
        archivos_auditoria_integrum = auditoria_integrum(rol)
        archivos_auditoria_inter_servicios = auditoria_inter_servicios(rol)
        archivos_ISECpoliticaContinuidad = ISECpoliticaContinuidad(rol)
        archivos_ISECpoliticaProteccionDatos = ISECpoliticaProteccionDatos(rol)
        archivos_ISECpoliticaSeguridadInf = ISECpoliticaSeguridadInf(rol)
        comiteSeguridad = comite_seguridad(rol)
        archivos_vulnerabilidades_2024 = vulnerabilidades_2024(rol)
        archivos_vulnerabilidades_2025 = vulnerabilidades_2025(rol)
        archivos_vulnerabilidades_ant = vulnerabilidades_ant(rol)
        archivos_revision_seguridad_2021 = revision_seguridad_2021(rol)
        archivos_revision_seguridad_2022 = revision_seguridad_2022(rol)
        archivos_revision_seguridad_2023 = revision_seguridad_2023(rol)
        archivos_revision_seguridad_2024 = revision_seguridad_2024(rol)
        if rol == 17:
            sst_arbol_carpetas = sst(rol)
        else:
            sst_arbol_carpetas = None

        if rol == 18:
            archivos_encuestas_2019 = encuestas_2019(rol)
            archivos_encuestas_2020 = encuestas_2020(rol)
            archivos_encuestas_2021 = encuestas_2021(rol)
        else:
            archivos_encuestas_2019 = None
            archivos_encuestas_2020 = None
            archivos_encuestas_2021 = None
        
        if rol == 19:
            archivos_sagrilaft = sagrilaft(rol)
        else:
            archivos_sagrilaft = None

        if rol == 21:
            archivos_ambiental = ambiental(rol)
        else:
            archivos_ambiental = None

        return {
            'nombre_rol_seleccionado': nombre_del_rol,
            'archivos_procedimientos': archivos_procedimientos,
            'caracterizaciones': caracterizaciones,
            'formatoDigital': formatoDigital,
            'formatoFisico': formatoFisico,
            'formatoExternoDigital': formatoExternoDigital,
            'formatoExternoFisico': formatoExternoFisico,
            'planCalidad': planCalidad,
            'requisitosCliente': requisitosCliente,
            'actasRestauracion': actasRestauracion,
            'archivos_instructivos': archivos_instructivos,
            'archivos_manuales': archivos_manuales,
            'archivos_auditorias_ifx': archivos_auditorias_ifx,
            'archivos_auditoria_integrum': archivos_auditoria_integrum,
            'archivos_auditoria_inter_servicios': archivos_auditoria_inter_servicios,
            'archivos_ISECpoliticaContinuidad': archivos_ISECpoliticaContinuidad,
            'archivos_ISECpoliticaProteccionDatos': archivos_ISECpoliticaProteccionDatos,
            'archivos_ISECpoliticaSeguridadInf': archivos_ISECpoliticaSeguridadInf,
            'comiteSeguridad': comiteSeguridad,
            'archivos_vulnerabilidades_2024': archivos_vulnerabilidades_2024,
            'archivos_vulnerabilidades_2025': archivos_vulnerabilidades_2025,
            'archivos_vulnerabilidades_ant': archivos_vulnerabilidades_ant,
            'archivos_revision_seguridad_2021': archivos_revision_seguridad_2021,
            'archivos_revision_seguridad_2022': archivos_revision_seguridad_2022,
            'archivos_revision_seguridad_2023': archivos_revision_seguridad_2023,
            'archivos_revision_seguridad_2024': archivos_revision_seguridad_2024,
            'sst_arbol_carpetas': sst_arbol_carpetas,
            'archivos_encuestas_2019': archivos_encuestas_2019,
            'archivos_encuestas_2020': archivos_encuestas_2020,
            'archivos_encuestas_2021': archivos_encuestas_2021,
            'archivos_sagrilaft': archivos_sagrilaft,
            'archivos_ambiental': archivos_ambiental,
            'procesos': procesos,
            'imagen_rol': imagen_rol,
            'rol_seleccionado': rol,
            'is_especific_role': is_role_override,
            'is_role_override': is_role_override
        }
    return render_template('users/documentacion.html', 
                           usuario=current_user, 
                           **CONTEXTO(rol))

@doc_bp.route('/ver/<path:filepath>')
def ver_documento(filepath):
    from urllib.parse import unquote
    filepath = unquote(filepath)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=False)
    else:
        abort(404, description="El archivo no existe o no se puede acceder.")


@doc_bp.route('/descargar/<path:filepath>')
def descargar_documento(filepath):
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        abort(404, description="El archivo no existe o no se puede acceder.")

@doc_bp.route('/ver_caracterizacion/<path:filepath>')
def ver_caracterizacion(filepath):
    if os.path.exists(filepath):
        return send_file(filepath)
    else:
        abort(404, description="El archivo no existe o no se puede acceder.")

@doc_bp.route('/documentacion/subir', methods=['POST'])
def subir_documento():
    from flask import jsonify
    import os
    from werkzeug.utils import secure_filename
    
    try:
        # Verificar si se recibió el archivo
        if 'documento' not in request.files:
            return jsonify({'success': False, 'message': 'No se recibió ningún archivo'})
        
        file = request.files['documento']
        carpeta = request.form.get('carpeta')
        replace = request.form.get('replace', 'false').lower() == 'true'
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'})
        
        if not carpeta:
            return jsonify({'success': False, 'message': 'No se especificó la carpeta'})
        
        # Resolver rol para carpetas compartidas (roles que usan la misma ruta de 'Occidente')
        roles_compartidos = [2, 4, 5, 6, 7, 10, 11, 12, 13]
        rol_id_para_buscar = current_user.rol
        
        if current_user.rol in roles_compartidos:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM rol WHERE rol = %s LIMIT 1", ('Occidente',))
            row = cur.fetchone()
            cur.close()
            if row and row[0]:
                rol_id_para_buscar = row[0]
            else:
                # Fallback: si no existe 'Occidente' en la tabla, usar 4 como estaba acordado
                rol_id_para_buscar = 4
        
        # Obtener la ruta de la carpeta desde la base de datos
        cur = mysql.connection.cursor()
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = %s", (rol_id_para_buscar, carpeta))
        result = cur.fetchone()
        cur.close()
        
        if not result:
            return jsonify({'success': False, 'message': 'Carpeta no encontrada para este rol'})
        
        carpeta_path = result[0]
        
        # Verificar que la carpeta existe
        if not os.path.exists(carpeta_path):
            return jsonify({'success': False, 'message': 'La carpeta de destino no existe'})
        
        # Obtener el nombre seguro del archivo
        filename = secure_filename(file.filename)
        file_path = os.path.join(carpeta_path, filename)
        
        # Verificar si el archivo ya existe
        if os.path.exists(file_path) and not replace:
            return jsonify({
                'success': False, 
                'exists': True, 
                'message': 'El archivo ya existe'
            })
        
        # Guardar el archivo
        file.save(file_path)
        
        return jsonify({
            'success': True, 
            'message': 'Documento subido exitosamente',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al subir el archivo: {str(e)}'})