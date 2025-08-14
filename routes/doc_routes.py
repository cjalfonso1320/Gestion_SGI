from flask import Blueprint, render_template, send_file, abort, request
from flask_login import current_user
import os
from controllers.doc_controller import procedimientos, caracterizacion, formatos_digitales, formatos_fisicos, formatos_externos_digitales, formatos_externos_fisicos, plan_calidad, requisitos_cliente, actas_restauracion, instructivos, manuales
from controllers.doc_controller import auditorias_ifx, auditoria_integrum, auditoria_inter_servicios, ISECpoliticaContinuidad, ISECpoliticaProteccionDatos, ISECpoliticaSeguridadInf, comite_seguridad
from controllers.doc_controller import vulnerabilidades_2024, vulnerabilidades_2025, vulnerabilidades_ant
from controllers.doc_controller import revision_seguridad_2021, revision_seguridad_2022, revision_seguridad_2023, revision_seguridad_2024, sst, encuestas_2019, encuestas_2020, encuestas_2021, sagrilaft, ambiental




doc_bp = Blueprint('doc', __name__)

@doc_bp.route('/documentacion')
def documentacion():
    def CONTEXTO():
        rol = current_user.rol
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
            'archivos_ambiental': archivos_ambiental
        }
    return render_template('users/documentacion.html', 
                           usuario=current_user, 
                           **CONTEXTO())

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

