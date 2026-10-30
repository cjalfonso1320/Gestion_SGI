from flask import Blueprint, render_template, send_file, abort, request, session, jsonify, redirect, url_for
from datetime import datetime
from flask_login import current_user
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES, nombre_rol
from controllers.procedimientos_controller import actualizar_seccion_procedimiento, registra_cambio_pendiente, lista_cambios, registra_cambio, registra_lista_maestra, revertir_cambio_html, cuenta_pendientes, lista_cambios_pendientes, lista_cambios_rechazados, cuenta_rechazados

proc_bp = Blueprint('proc', __name__)

@proc_bp.route('/procedimientos')
def procedimientos():
    rol = current_user.rol
    return render_template('procedimientos/procedimientos.html', usuario=current_user, nombre_rol=nombre_rol(rol))



@proc_bp.route('/procedimiento/<string:doc_id>')
def procedimiento(doc_id):
    rol = current_user.rol
    
    # Mapeo de documentos de tecnología
    if rol == 9:  # Rol TI
        documentos_tecnologia = {
        f"{rol}-001": ("TEC-PR-001 REGISTRO, MONITOREO Y MANEJO DE LOGS", "procedimientos/TI/Tec_pr_001.html"),
        f"{rol}-002": ("TEC-PR-002 Soporte Técnico", "procedimientos/TI/Tec_pr_002.html"),
        f"{rol}-003": ("TEC-PR-003 Copias de Respaldo", "procedimientos/TI/Tec_pr_003.html"),
        f"{rol}-004": ("TEC-PR-004 Gestión de Usuarios", "procedimientos/TI/Tec_pr_004.html"),
        f"{rol}-005": ("TEC-PR-005 Alistamiento de Equipos", "procedimientos/TI/Tec_pr_005.html"),
        f"{rol}-006": ("TEC-PR-006 Creación y Manejo de carpetas", "procedimientos/TI/Tec_pr_006.html"),
        f"{rol}-008": ("TEC-PR-008 Backup de Roles", "procedimientos/TI/Tec_pr_008.html"),
        f"{rol}-009": ("TEC-PR-009 Retiro de equipos de computo", "procedimientos/TI/Tec_pr_009.html"),
        f"{rol}-010": ("TEC-PR-010 Gestión de Redes", "procedimientos/TI/Tec_pr_010.html"),
        f"{rol}-011": ("TEC-PR-011 Administración de Firewall", "procedimientos/TI/Tec_pr_011.html"),
        f"{rol}-012": ("TEC-PR-012 Manejo de medios removibles", "procedimientos/TI/Tec_pr_012.html"),
        f"{rol}-013": ("TEC-PR-013 Destrucción, Eliminación o Borrado Seguro de la Información", "procedimientos/TI/Tec_pr_013.html"),
    }
    elif rol == 2:  # Rol Bancolombia
        documentos_tecnologia = {
        f"{rol}-012": ("PRO-PR-012 Impuestos Departamentales Bancolombia", "procedimientos/Produccion/PRO-PR-012 Impuestos Departamentales Bancolombia.html"),
        f"{rol}-013": ("PRO-PR-013 Impuestos Distritales Bancolombia", "procedimientos/Produccion/PRO-PR-013 Impuestos Distritales Bancolombia.html"),
        f"{rol}-014": ("PRO-PR-014 Impuestos Nacionales y Tributos Aduaneros de Bancolombia", "procedimientos/Produccion/PRO-PR-014 Impuestos Nacionales y Tributos Aduaneros de Bancolombia.html"),
        f"{rol}-033": ("TEC-PR-004 Gestión de Usuarios", "procedimientos/Produccion/PRO-PR-033 Procedimiento Convenios Bancolombia.html"),
        }
    elif rol == 4:
        documentos_tecnologia = {
            f"{rol}-015": ("PRO-PR-012 Impuestos Departamentales Bancolombia", "procedimientos/Produccion/PRO-PR-015 Impuestos Distritales Occidente.html"),
            f"{rol}-026": ("PRO-PR-012 Impuestos Departamentales Bancolombia", "procedimientos/Produccion/PRO-PR-026 Impuestos Nacionales  y Tributos Aduaneros Occidente.html"),
        }
    elif rol == 5:
        documentos_tecnologia = {
            f"{rol}-005": ("PRO-PR-005 Impuestos Nacionales y Tributos Aduaneros Banagrario", "procedimientos/Produccion/PRO-PR-005 Impuestos Nacionales y Tributos Aduaneros Banagrario.html"),
        }
    elif rol == 6:
        documentos_tecnologia = {
            f"{rol}-007": ("PRO-PR-007 Impuestos Distritales Davivienda", "procedimientos/Produccion/PRO-PR-007 Impuestos Distritales Davivienda.html"),
            f"{rol}-011": ("PRO-PR-011 Impuestos Departamentales Davivienda", "procedimientos/Produccion/PRO-PR-011 Impuestos Departamentales Davivienda.html"),
            f"{rol}-016": ("PRO-PR-016 Convenios Especiales Davivienda", "procedimientos/Produccion/PRO-PR-016 Convenios Especiales Davivienda.html"),
            f"{rol}-019": ("PRO-PR-019 Impuestos Nacionales y Tributos Aduaneros de Davivienda", "procedimientos/Produccion/PRO-PR-019 Impuestos Nacionales y Tributos Aduaneros de Davivienda.html"),
            f"{rol}-023": ("PRO-PR-023 Convenios Davivienda", "procedimientos/Produccion/PRO-PR-023 Convenios  Davivienda.html"),
        }
    elif rol == 7:
        documentos_tecnologia = {
            f"{rol}-028": ("PRO-PR-028 Impuestos Nacionales y Tributos Aduaneros Itau", "procedimientos/Produccion/PRO-PR-028 Impuestos Nacionales y Tributos Aduaneros Itau.html"),
            f"{rol}-029": ("PRO-PR-029 Impuesto Departamentales Itau", "procedimientos/Produccion/PRO-PR-029 Impuesto Departamentales Itau.html"),
            f"{rol}-030": ("PRO-PR-030 Impuesto Municipales Cali Itau", "procedimientos/Produccion/PRO-PR-030 Impuesto Municipales Cali Itau.html"),
            f"{rol}-031": ("PRO-PR-031 Impuesto Municipales Cartagena Itau", "procedimientos/Produccion/PRO-PR-031 Impuesto Municipales Cartagena Itau.html"),
        }
    elif rol == 8:
        documentos_tecnologia = {
            f"{rol}-001": ("PRO-TH-001 Impuestos Nacionales y Tributos Aduaneros AV Villas", "procedimientos/Produccion/PRO-PR-021 Impuestos Nacionales y Tributos Aduaneros AV Villas.html"),
            f"{rol}-002": ("PRO-TH-002 Impuestos Departamentales AV Villas", "procedimientos/Produccion/PRO-PR-022 Impuestos Departamentales AV Villas.html"),
            f"{rol}-003": ("PRO-TH-003 Impuestos Departamentales AV Villas", "procedimientos/Produccion/PRO-PR-022 Impuestos Departamentales AV Villas.html"),
            f"{rol}-004": ("PRO-TH-004 Impuestos Departamentales AV Villas", "procedimientos/Produccion/PRO-PR-022 Impuestos Departamentales AV Villas.html"),
        }
    elif rol == 10:
        documentos_tecnologia = {
            f"{rol}-008": ("PRO-PR-008 Impuestos Departamentales Popular - SANTANDER Y VALLE", "procedimientos/Produccion/PRO-PR-008 Impuestos Departamentales Popular - SANTANDER Y VALLE.html"),
            f"{rol}-027": ("PRO-PR-027 Convenios Popular", "procedimientos/Produccion/PRO-PR-027 Convenios Popular.html"),
            f"{rol}-034": ("PRO-PR-034 Impuestos Departamentales Popular - ANTIOQUIA", "procedimientos/Produccion/PRO-PR-034 Impuestos Departamentales Popular - ANTIOQUIA.html"),
        }
    elif rol == 11:
        documentos_tecnologia = {
            f"{rol}-001": ("PRO-PR-001 Convenios Av Villas", "procedimientos/Produccion/PRO-PR-001 Convenios Av Villas.html"),
            f"{rol}-009": ("PRO-PR-009 Impuestos Departamentales Av Villas", "procedimientos/Produccion/PRO-PR-009 Impuestos Departamentales Av Villas.html"),
            f"{rol}-010": ("PRO-PR-010 Impuestos Distritales Av Villas", "procedimientos/Produccion/PRO-PR-010 Impuestos Distritales Av Villas.html"),
            f"{rol}-017": ("PRO-PR-017  Radicación AV Villas", "procedimientos/Produccion/PRO-PR-017  Radicación AV Villas.html"),
            f"{rol}-022": ("PRO-PR-022 Impuestos Nacionales y Tributos Aduaneros Av Villas", "procedimientos/Produccion/PRO-PR-022 Impuestos Nacionales y Tributos Aduaneros Av Villas.html"),
        }
    elif rol == 12:
        documentos_tecnologia = {
            f"{rol}-018": ("PRO-PR-018 Impuestos Departamentales Bancoomeva", "procedimientos/Produccion/PRO-PR-018 Impuestos Departamentales Bancoomeva.html"),
        }
    elif rol == 13:
        documentos_tecnologia = {
            f"{rol}-006": ("PRO-PR-006 Impuestos Nacionales y Tributos Aduaneros Banco Caja Social", "procedimientos/Produccion/PRO-PR-006 Impuestos Nacionales y Tributos Aduaneros Banco Caja Social.html"),
            f"{rol}-020": ("PRO-PR-020 Procedimiento Recaudos Banco Caja Social", "procedimientos/Produccion/PRO-PR-020 Procedimiento Recaudos Banco Caja Social.html"),
        }
    # Busca el documento en el mapeo
    doc_info = documentos_tecnologia.get(doc_id)

    if not doc_info:
        abort(404)

    nombre_doc_db, template_path = doc_info

    # Contexto común para todas las plantillas
    contexto = {
        'usuario': current_user,
        'nombre_rol': nombre_rol(rol),
        'cambios': lista_cambios(nombre_doc_db),
    }

    return render_template(template_path, **contexto)

@proc_bp.route('/procedimientos/actualizar_seccion', methods=['POST'])
def handle_actualizar_seccion():
    data = request.get_json()
    nombre_documento = data.get('documento')
    seccion_id = data.get('id')
    contenido = data.get('contenido')
    nombre_usuario = current_user.username
    descripcion_cambio = data.get('descripcion', '').strip()
    nombre_documento_legible = data.get('nombre_documento', '').strip()
    rol = current_user.rol
    
    if not all([nombre_documento, seccion_id, contenido is not None]):
        return jsonify({'success': False, 'message': 'Faltan datos: documento, ID de sección y contenido son requeridos.'}), 400

    exito, contenido_original = actualizar_seccion_procedimiento(nombre_documento, seccion_id, contenido)
    if exito:
        if descripcion_cambio:
            registra_cambio_pendiente(nombre_usuario, descripcion_cambio, nombre_documento_legible, rol, contenido_original)
        return jsonify({'success': True, 'message': 'Sección actualizada correctamente en el archivo.'})
    else:
        return jsonify({'success': False, 'message': 'Error al guardar los cambios en el archivo del procedimiento.'}), 500
    

@proc_bp.route('/aprobar_cambio', methods=['POST'])
def aprobar_cambio():
    estado = request.form['aprobacion']
    id_cambio = request.form['id']
    nombre_usuario = current_user.username
    fecha_aprobacion = datetime.now().date()
    nombre_documento = request.form['nombre_documento'] # Lo mantenemos para la lógica
    version = request.form['version'] # Obtenemos la versión directamente del formulario

    registra_cambio(nombre_usuario, fecha_aprobacion, estado, id_cambio)

    if estado == 'Aprobado':
        registra_lista_maestra(fecha_aprobacion, nombre_usuario, nombre_documento, version)
    elif estado == 'Rechazado':
        revertir_cambio_html(id_cambio)

    return redirect(url_for('home.home'))
    