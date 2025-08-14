from flask import Blueprint, render_template, send_file, abort, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
'''GESTION DE PRODUCCION'''
from controllers.ind_controller import uvt_rol
from controllers.ind_controller import guardar_calidadInformacion, lista__calidadInformacion, grafica_calidadInformacion
from controllers.ind_controller import lista_registrosExtemporaneos, guardar_registrosExtemporaneos, grafica_registrosExtemporaneos, obtener_r_extemporeaneo_mes
from controllers.ind_controller import lista_sancionesMagenticas, guardar_sancionesMagneticas, grafica_sancionesMagneticas
from controllers.ind_controller import grafica_registrosFisicos, guardar_registrosFisicos, lista_registrosFisicos, obtener_r_extemporeaneoFisico_mes
from controllers.ind_controller import guardar_sancionesFisicos, grafica_sancionesFisicos, lista_sancionesFisicos
from controllers.ind_controller import lista_cintasMagneticas, guardar_cintasMagneticas, grafica_cintasMagneticas
from controllers.ind_controller import lista_informesEntregados, guardar_informesEntregados, grafica_informesEntregados
from controllers.ind_controller import lista_sitio_web, guardar_sitio_web, grafica_sitio_web
from controllers.ind_controller import lista_calidad_informes, guardar_calidadInformes, grafica_calidadInformes
from controllers.ind_controller import lista_entregaImagenes, guardar_entregaImagenes, grafica_entregaImagenes
from controllers.ind_controller import lista_inconsistenciasSolucionadas, guardar_inconsistenciasSolucionadas, grafica_inconsistenciasSolucionadas
from controllers.ind_controller import lista_traslado, guardar_traslado, grafica_traslado
from controllers.ind_controller import lista_inconsitenciasPasivo, guardar_inconsitenciasPasivo, grafica_inconsitenciasPasivo
from controllers.ind_controller import lista_TRespuesta_credito, guardar_TRespuesta_credito, datos_mes_anterior, grafica_TRespuesta_credito
from controllers.ind_controller import lista_TransAduanas, guardar_TransAduanas, grafica_TransAduanas

'''ADMINISTRATIVO'''
from controllers.ind_controller import lista_Administrativo, grafica_Administrativo, guardar_Administrativo

ind_bp = Blueprint('ind', __name__)

@ind_bp.route('/indicadores')
@login_required
def indicadores():
    def CONTEXTO():
        '''GESTION DE PRODUCCION'''
        uvt_valor = uvt_rol(current_user.rol)
        datos_calidadInformacion_nacionales = lista__calidadInformacion(current_user.rol, 'nacionales')
        datos_registrosExtemporaneos = lista_registrosExtemporaneos(current_user.rol)
        datos_sancionesMagneticas = lista_sancionesMagenticas(current_user.rol)
        datos_entrega_fisicos_nacionales = lista_registrosFisicos(current_user.rol, 'nacionales')
        datos_entrega_fisicos_distritales = lista_registrosFisicos(current_user.rol, 'distritales')
        datos_entrega_fisicos_convenios = lista_registrosFisicos(current_user.rol, 'convenios')
        datos_entrega_fisicos_departamentales = lista_registrosFisicos(current_user.rol, 'departamentales')
        datos_entrega_fisicos_municipalesCali = lista_registrosFisicos(current_user.rol, 'municipalesCali')
        datos_sancionesFisicos = lista_sancionesFisicos(current_user.rol)
        datos_cintas_magneticas_distritales = lista_cintasMagneticas(current_user.rol, 'distritales')
        datos_entrega_informes_departamentales = lista_informesEntregados(current_user.rol, 'departamentales')
        datos_entrega_informes_convenios = lista_informesEntregados(current_user.rol, 'convenios')
        datos_entrega_informes_nacionales = lista_informesEntregados(current_user.rol, 'nacionales')
        datos_entrega_informes_distritales = lista_informesEntregados(current_user.rol, 'distritales')
        datos_entrega_informes_municipalesCali = lista_informesEntregados(current_user.rol, 'municipalesCali')
        datos_sitio_web_convenios = lista_sitio_web(current_user.rol, 'convenios')
        datos_calidad_informes_nacionales = lista_calidad_informes(current_user.rol, 'nacionales')
        datos_calidad_informes_distritales = lista_calidad_informes(current_user.rol, 'distritales')
        datos_calidad_informes_convenios = lista_calidad_informes(current_user.rol, 'convenios')
        datos_calidad_informes_departamentales = lista_calidad_informes(current_user.rol, 'departamentales')
        datos_entrega_imagenes_nacionales = lista_entregaImagenes(current_user.rol, 'nacionales')
        datos_entrega_imagenes_distritales = lista_entregaImagenes(current_user.rol, 'distritales')
        datos_entrega_imagenes_convenios = lista_entregaImagenes(current_user.rol, 'convenios')
        datos_entrega_imagenes_departamentales = lista_entregaImagenes(current_user.rol, 'departamentales')
        datos_solucion_inconsistencias_nacionales = lista_inconsistenciasSolucionadas(current_user.rol, 'nacionales')
        datos_solucion_inconsistencias_distritales = lista_inconsistenciasSolucionadas(current_user.rol, 'distritales')
        datos_solucion_inconsistencias_convenios = lista_inconsistenciasSolucionadas(current_user.rol, 'convenios')
        datos_solucion_inconsistencias_departamentales = lista_inconsistenciasSolucionadas(current_user.rol, 'departamentales')
        datos_traslados_nacionales = lista_traslado(current_user.rol, 'nacionales')
        datos_traslados_distritales = lista_traslado(current_user.rol, 'distritales')
        datos_traslados_convenios = lista_traslado(current_user.rol, 'convenios')
        datos_traslados_departamentales = lista_traslado(current_user.rol, 'departamentales')
        datos_inconsistencias_pasivo = lista_inconsitenciasPasivo(current_user.rol, 'complementacion_pasivo')
        datos_inconsistencias_activo = lista_inconsitenciasPasivo(current_user.rol, 'complementacion_activo')
        datos_inconsistencias_repsuestaTradicional = lista_inconsitenciasPasivo(current_user.rol, 'complementacion_repsuestaTradicional')
        datos_inconsistencias_repsuestaOCI = lista_inconsitenciasPasivo(current_user.rol, 'complementacion_repsuestaOCI')
        datos_repsuestaCreditoOCI = lista_TRespuesta_credito(current_user.rol, 'complementacion_repsuestaCreditoOCI')
        datos_repsuestaCreditoTradicional = lista_TRespuesta_credito(current_user.rol, 'complementacion_repsuestaCreditoTradicional')
        datos_calidadInformacion_radicacion = lista__calidadInformacion(current_user.rol, 'radicacion')
        datos_entrega_informes_radicacion = lista_informesEntregados(current_user.rol, 'radicacion')
        datos_entrega_imagenes_radicacion = lista_entregaImagenes(current_user.rol, 'radicacion')
        datos_entrega_fisicos_TarjetasDigital = lista_registrosFisicos(current_user.rol, 'TarjetasDigital')
        datos_entrega_fisicos_TarjetasFisico = lista_registrosFisicos(current_user.rol, 'TarjetasFisico')
        datos_transmision_aduanas_nacionales = lista_TransAduanas(current_user.rol, 'nacionales')

        '''ADMINISTRATIVO'''
        datos_administrativo_sistemas = lista_Administrativo(current_user.rol, 'sistemas')
        datos_administrativo_tecnologia = lista_Administrativo(current_user.rol, 'tecnologia')
        datos_administrativo_financiera = lista_Administrativo(current_user.rol, 'financiera')
        datos_administrativo_comercial_propuestas = lista_Administrativo(current_user.rol, 'comercial_propuestas')
        datos_administrativo_comercial_efectividad = lista_Administrativo(current_user.rol, 'comercial_efectividad')
        datos_administrativo_comercial_pqr = lista_Administrativo(current_user.rol, 'comercial_pqr')
        datos_administrativo_TH_clima_organizacional = lista_Administrativo(current_user.rol, 'TH_clima_organizacional')
        datos_administrativo_TH_Cumplimiento_Capacitaciones = lista_Administrativo(current_user.rol, 'TH_Cumplimiento_Capacitaciones')
        datos_administrativo_TH_Eficacia_Capacitaciones = lista_Administrativo(current_user.rol, 'TH_Eficacia_Capacitaciones')
        datos_administrativo_TH_Evaluacion_Desempeño = lista_Administrativo(current_user.rol, 'TH_Evaluacion_Desempeño')
        datos_administrativo_SGI_Acciones_Correctivas = lista_Administrativo(current_user.rol, 'SGI_Acciones_Correctivas')
        datos_administrativo_SGI_Continuidad_Negocio = lista_Administrativo(current_user.rol, 'SGI_Continuidad_Negocio')
        datos_administrativo_SGI_Incidentes_Seguridad = lista_Administrativo(current_user.rol, 'SGI_Incidentes_Seguridad')
        datos_administrativo_SGI_Producto_No_Conforme = lista_Administrativo(current_user.rol, 'SGI_Producto_No_Conforme')
        datos_administrativo_SGI_Riesgos = lista_Administrativo(current_user.rol, 'SGI_Riesgos')
        return {
            'uvt_valor': uvt_valor,
            'datos_calidadInformacion_nacionales': datos_calidadInformacion_nacionales,
            'usuario': current_user,
            'datos_registrosExtemporaneos': datos_registrosExtemporaneos,
            'datos_sancionesMagneticas': datos_sancionesMagneticas,
            'datos_entrega_fisicos_nacionales': datos_entrega_fisicos_nacionales,
            'datos_entrega_fisicos_distritales': datos_entrega_fisicos_distritales,
            'datos_sancionesFisicos': datos_sancionesFisicos,
            'datos_cintas_magneticas_distritales': datos_cintas_magneticas_distritales,
            'datos_entrega_informes_departamentales': datos_entrega_informes_departamentales,
            'datos_entrega_informes_convenios': datos_entrega_informes_convenios,
            'datos_entrega_fisicos_convenios': datos_entrega_fisicos_convenios,
            'datos_sitio_web_convenios': datos_sitio_web_convenios,
            'datos_entrega_informes_nacionales': datos_entrega_informes_nacionales,
            'datos_entrega_informes_distritales': datos_entrega_informes_distritales,
            'datos_calidad_informes_nacionales': datos_calidad_informes_nacionales,
            'datos_entrega_imagenes_nacionales': datos_entrega_imagenes_nacionales,
            'datos_solucion_inconsistencias_nacionales': datos_solucion_inconsistencias_nacionales,
            'datos_traslados_nacionales': datos_traslados_nacionales,
            'datos_calidad_informes_distritales': datos_calidad_informes_distritales,
            'datos_entrega_imagenes_distritales': datos_entrega_imagenes_distritales,
            'datos_solucion_inconsistencias_distritales': datos_solucion_inconsistencias_distritales,
            'datos_traslados_distritales': datos_traslados_distritales,
            'datos_calidad_informes_convenios': datos_calidad_informes_convenios,
            'datos_entrega_imagenes_convenios': datos_entrega_imagenes_convenios,
            'datos_solucion_inconsistencias_convenios': datos_solucion_inconsistencias_convenios,
            'datos_traslados_convenios': datos_traslados_convenios,
            'datos_entrega_fisicos_departamentales': datos_entrega_fisicos_departamentales,
            'datos_calidad_informes_departamentales': datos_calidad_informes_departamentales,
            'datos_entrega_imagenes_departamentales': datos_entrega_imagenes_departamentales,
            'datos_solucion_inconsistencias_departamentales': datos_solucion_inconsistencias_departamentales,
            'datos_traslados_departamentales': datos_traslados_departamentales,
            'datos_entrega_fisicos_municipalesCali': datos_entrega_fisicos_municipalesCali,
            'datos_entrega_informes_municipalesCali': datos_entrega_informes_municipalesCali,
            'datos_inconsistencias_pasivo': datos_inconsistencias_pasivo,
            'datos_inconsistencias_activo': datos_inconsistencias_activo,
            'datos_inconsistencias_repsuestaTradicional': datos_inconsistencias_repsuestaTradicional,
            'datos_inconsistencias_repsuestaOCI': datos_inconsistencias_repsuestaOCI,
            'datos_repsuestaCreditoOCI': datos_repsuestaCreditoOCI,
            'datos_repsuestaCreditoTradicional': datos_repsuestaCreditoTradicional,
            'datos_calidadInformacion_radicacion': datos_calidadInformacion_radicacion,
            'datos_entrega_informes_radicacion': datos_entrega_informes_radicacion,
            'datos_entrega_imagenes_radicacion': datos_entrega_imagenes_radicacion,
            'datos_entrega_fisicos_TarjetasDigital': datos_entrega_fisicos_TarjetasDigital,
            'datos_entrega_fisicos_TarjetasFisico': datos_entrega_fisicos_TarjetasFisico,
            'datos_transmision_aduanas_nacionales': datos_transmision_aduanas_nacionales,
            
            
            


            'datos_administrativo_sistemas': datos_administrativo_sistemas,
            'datos_administrativo_tecnologia': datos_administrativo_tecnologia,
            'datos_administrativo_financiera': datos_administrativo_financiera,
            'datos_administrativo_comercial_propuestas':datos_administrativo_comercial_propuestas,
            'datos_administrativo_comercial_efectividad': datos_administrativo_comercial_efectividad,
            'datos_administrativo_comercial_pqr': datos_administrativo_comercial_pqr,
            'datos_administrativo_TH_clima_organizacional': datos_administrativo_TH_clima_organizacional,
            'datos_administrativo_TH_Cumplimiento_Capacitaciones': datos_administrativo_TH_Cumplimiento_Capacitaciones,
            'datos_administrativo_TH_Eficacia_Capacitaciones': datos_administrativo_TH_Eficacia_Capacitaciones,
            'datos_administrativo_TH_Evaluacion_Desempeño': datos_administrativo_TH_Evaluacion_Desempeño,
            'datos_administrativo_SGI_Acciones_Correctivas': datos_administrativo_SGI_Acciones_Correctivas,
            'datos_administrativo_SGI_Continuidad_Negocio': datos_administrativo_SGI_Continuidad_Negocio,
            'datos_administrativo_SGI_Incidentes_Seguridad': datos_administrativo_SGI_Incidentes_Seguridad,
            'datos_administrativo_SGI_Producto_No_Conforme': datos_administrativo_SGI_Producto_No_Conforme,
            'datos_administrativo_SGI_Riesgos': datos_administrativo_SGI_Riesgos,


        }
    def CONTEXTO_GRAFICA():
        '''GESTION DE PRODUCCION'''
        meses_calidadInformacion_nacionales, porcentajes_calidadInformacion_nacionales = grafica_calidadInformacion(current_user.rol, 'nacionales')
        meses_registrosExtemporaneos, porcentajes_registrosExtemporaneos = grafica_registrosExtemporaneos(current_user.rol)
        meses_sancionesMagneticas, multas_sancionesMagneticas = grafica_sancionesMagneticas(current_user.rol)
        meses_entregaFisicos_nacionales, porcentajes_entregaFisicos_nacionales = grafica_registrosFisicos(current_user.rol, 'nacionales')
        meses_entregaFisicos_distritales, porcentajes_entregaFisicos_distritales = grafica_registrosFisicos(current_user.rol, 'distritales')
        meses_entregaFisicos_convenios, porcentajes_entregaFisicos_convenios = grafica_registrosFisicos(current_user.rol, 'convenios')
        meses_entregaFisicos_departamentales, porcentajes_entregaFisicos_departamentales = grafica_registrosFisicos(current_user.rol, 'departamentales')
        meses_entregaFisicos_municipalesCali, porcentajes_entregaFisicos_municipalesCali = grafica_registrosFisicos(current_user.rol, 'municipalesCali')
        meses_sancionesFisicos, multas_sancionesFisicos = grafica_sancionesFisicos(current_user.rol)
        meses_cintasMagneticas_distritales, porcentajes_cintasMagneticas_distritales = grafica_cintasMagneticas(current_user.rol, 'distritales')
        meses_entrega_informes_departamentales, porcentajes_entrega_informes_departamentales = grafica_informesEntregados(current_user.rol, 'departamentales')
        meses_entrega_informes_convenios, porcentajes_entrega_informes_convenios = grafica_informesEntregados(current_user.rol, 'convenios')
        meses_entrega_informes_nacionales, porcentajes_entrega_informes_nacionales = grafica_informesEntregados(current_user.rol, 'nacionales')
        meses_entrega_informes_distritales, porcentajes_entrega_informes_distritales = grafica_informesEntregados(current_user.rol, 'distritales')
        meses_entrega_informes_municipalesCali, porcentajes_entrega_informes_municipalesCali = grafica_informesEntregados(current_user.rol, 'municipalesCali')
        meses_sitio_web_convenios, porcentajes_sitio_web_convenios = grafica_sitio_web(current_user.rol, 'convenios')
        meses_calidad_informes_nacionales, porcentajes_calidad_informes_nacionales = grafica_calidadInformes(current_user.rol, 'nacionales')
        meses_calidad_informes_distritales, porcentajes_calidad_informes_distritales = grafica_calidadInformes(current_user.rol, 'distritales')
        meses_calidad_informes_departamentales, porcentajes_calidad_informes_departamentales = grafica_calidadInformes(current_user.rol, 'departamentales')
        meses_calidad_informes_convenios, porcentajes_calidad_informes_convenios = grafica_calidadInformes(current_user.rol, 'convenios')
        meses_entregaImagenes_nacionales, porcentajes_entregaImagenes_nacionales = grafica_entregaImagenes(current_user.rol, 'nacionales')
        meses_entregaImagenes_distritales, porcentajes_entregaImagenes_distritales = grafica_entregaImagenes(current_user.rol, 'distritales')
        meses_entregaImagenes_convenios, porcentajes_entregaImagenes_convenios = grafica_entregaImagenes(current_user.rol, 'convenios')
        meses_entregaImagenes_departamentales, porcentajes_entregaImagenes_departamentales = grafica_entregaImagenes(current_user.rol, 'departamentales')
        meses_inconsistencias_nacionales, porcentajes_inconsistencias_nacionales = grafica_inconsistenciasSolucionadas(current_user.rol, 'nacionales')
        meses_inconsistencias_distritales, porcentajes_inconsistencias_distritales = grafica_inconsistenciasSolucionadas(current_user.rol, 'distritales')
        meses_inconsistencias_convenios, porcentajes_inconsistencias_convenios = grafica_inconsistenciasSolucionadas(current_user.rol, 'convenios')
        meses_inconsistencias_departamentales, porcentajes_inconsistencias_departamentales = grafica_inconsistenciasSolucionadas(current_user.rol, 'departamentales')
        meses_traslados_nacionales, porcentajes_traslados_nacionales = grafica_traslado(current_user.rol, 'nacionales')
        meses_traslados_distritales, porcentajes_traslados_distritales = grafica_traslado(current_user.rol, 'distritales')
        meses_traslados_convenios, porcentajes_traslados_convenios = grafica_traslado(current_user.rol, 'convenios')
        meses_traslados_departamentales, porcentajes_traslados_departamentales = grafica_traslado(current_user.rol, 'departamentales')
        meses_inconsistenciasPasivo, porcentajes_inconsistenciasPasivo = grafica_inconsitenciasPasivo(current_user.rol, 'complementacion_pasivo')
        meses_inconsistenciasActivo, porcentajes_inconsistenciasActivo = grafica_inconsitenciasPasivo(current_user.rol, 'complementacion_activo')
        meses_inconsistenciasrepsuestaTradicional, porcentajes_inconsistenciasrepsuestaTradicional = grafica_inconsitenciasPasivo(current_user.rol, 'complementacion_repsuestaTradicional')
        meses_inconsistenciasrepsuestaOCI, porcentajes_inconsistenciasrepsuestaOCI = grafica_inconsitenciasPasivo(current_user.rol, 'complementacion_repsuestaOCI')
        meses_repsuestaCrerditoOCI, tiempo_repsuestaCreditoOCI = grafica_TRespuesta_credito(current_user.rol, 'complementacion_repsuestaCreditoOCI')
        meses_repsuestaCrerditoTradicional, tiempo_repsuestaCreditoTradicional = grafica_TRespuesta_credito(current_user.rol, 'complementacion_repsuestaCreditoTradicional')
        meses_calidadInformacion_radicacion, porcentajes_calidadInformacion_radicacion = grafica_calidadInformacion(current_user.rol, 'radicacion')
        meses_entrega_informes_radicacion, porcentajes_entrega_informes_radicacion = grafica_informesEntregados(current_user.rol, 'radicacion')
        meses_entregaImagenes_radicacion, porcentajes_entregaImagenes_radicacion = grafica_entregaImagenes(current_user.rol, 'radicacion')
        meses_entregaFisicos_TarjetasDigital, porcentajes_entrega_fisicos_TarjetasDigital = grafica_registrosFisicos(current_user.rol, 'TarjetasDigital')
        meses_entregaFisicos_TarjetasFisico, porcentajes_entrega_fisicos_TarjetasFisico = grafica_registrosFisicos(current_user.rol, 'TarjetasFisico')
        meses_Taduanas_nacionales, procentajes_Taduanas_nacionales = grafica_TransAduanas(current_user.rol, 'nacionales')

        '''ADMINISTRATIVO'''
        meses_administrativo_sistemas, porcentajes_administrativo_sistemas = grafica_Administrativo(current_user.rol, 'sistemas')
        meses_administrativo_tecnologia, porcentajes_administrativo_tecnologia = grafica_Administrativo(current_user.rol, 'tecnologia')
        meses_administrativo_financiera, porcentajes_administrativo_financiera = grafica_Administrativo(current_user.rol, 'financiera')
        meses_administrativo_comercial_propuestas, porcentajes_administrativo_comercial_propuestas = grafica_Administrativo(current_user.rol, 'comercial_propuestas')
        meses_administrativo_comercial_efectividad, porcentajes_administrativo_comercial_efectividad = grafica_Administrativo(current_user.rol, 'comercial_efectividad')
        meses_administrativo_comercial_pqr, porcentajes_administrativo_comercial_pqr = grafica_Administrativo(current_user.rol, 'comercial_pqr')
        meses_administrativo_TH_clima_organizacional, porcentajes_administrativo_TH_clima_organizacional = grafica_Administrativo(current_user.rol, 'TH_clima_organizacional')
        meses_administrativo_TH_Cumplimiento_Capacitaciones, porcentajes_administrativo_TH_Cumplimiento_Capacitaciones = grafica_Administrativo(current_user.rol, 'TH_Cumplimiento_Capacitaciones')
        meses_administrativo_TH_Eficacia_Capacitaciones, porcentajes_administrativo_TH_Eficacia_Capacitaciones = grafica_Administrativo(current_user.rol, 'TH_Eficacia_Capacitaciones')
        meses_administrativo_TH_Evaluacion_Desempeño, porcentajes_administrativo_TH_Evaluacion_Desempeño = grafica_Administrativo(current_user.rol, 'TH_Evaluacion_Desempeño')
        meses_administrativo_SGI_Acciones_Correctivas, porcentajes_administrativo_SGI_Acciones_Correctivas = grafica_Administrativo(current_user.rol, 'SGI_Acciones_Correctivas')
        meses_administrativo_SGI_Continuidad_Negocio, porcentajes_administrativo_SGI_Continuidad_Negocio = grafica_Administrativo(current_user.rol, 'SGI_Continuidad_Negocio')
        meses_administrativo_SGI_Incidentes_Seguridad, porcentajes_administrativo_SGI_Incidentes_Seguridad = grafica_Administrativo(current_user.rol, 'SGI_Incidentes_Seguridad')
        meses_administrativo_SGI_Producto_No_Conforme, porcentajes_administrativo_SGI_Producto_No_Conforme = grafica_Administrativo(current_user.rol, 'SGI_Producto_No_Conforme')
        meses_administrativo_SGI_Riesgos, porcentajes_administrativo_SGI_Riesgos = grafica_Administrativo(current_user.rol, 'SGI_Riesgos')
        return {
            'meses_calidadInformacion_nacionales': meses_calidadInformacion_nacionales,
            'porcentajes_calidadInformacion_nacionales': porcentajes_calidadInformacion_nacionales,
            'meses_registrosExtemporaneos': meses_registrosExtemporaneos,
            'porcentajes_registrosExtemporaneos': porcentajes_registrosExtemporaneos,
            'meses_sancionesMagneticas': meses_sancionesMagneticas,
            'multas_sancionesMagneticas': multas_sancionesMagneticas,
            'meses_entregaFisicos_nacionales': meses_entregaFisicos_nacionales,
            'porcentajes_entrega_fisicos_nacionales': porcentajes_entregaFisicos_nacionales,
            'meses_entregaFisicos_distritales': meses_entregaFisicos_distritales,
            'porcentajes_entrega_fisicos_distritales': porcentajes_entregaFisicos_distritales,
            'meses_sancionesFisicos': meses_sancionesFisicos,
            'multas_sancionesFisicos': multas_sancionesFisicos,
            'meses_cintas_magneticas_distritales': meses_cintasMagneticas_distritales,
            'porcentajes_cintas_magneticas_distritales': porcentajes_cintasMagneticas_distritales,
            'meses_entrega_informes_departamentales': meses_entrega_informes_departamentales,
            'porcentajes_entrega_informes_departamentales': porcentajes_entrega_informes_departamentales,
            'meses_entrega_informes_convenios': meses_entrega_informes_convenios,
            'porcentajes_entrega_informes_convenios': porcentajes_entrega_informes_convenios,
            'meses_entregaFisicos_convenios': meses_entregaFisicos_convenios,
            'porcentajes_entregaFisicos_convenios': porcentajes_entregaFisicos_convenios,
            'meses_sitio_web_convenios': meses_sitio_web_convenios,
            'porcentajes_sitio_web_convenios': porcentajes_sitio_web_convenios,
            'meses_entrega_informes_nacionales': meses_entrega_informes_nacionales,
            'porcentajes_entrega_informes_nacionales': porcentajes_entrega_informes_nacionales,
            'meses_calidad_informes_nacionales': meses_calidad_informes_nacionales,
            'porcentajes_calidad_informes_nacionales': porcentajes_calidad_informes_nacionales,
            'meses_entregaImagenes_nacionales': meses_entregaImagenes_nacionales,
            'porcentajes_entregaImagenes_nacionales': porcentajes_entregaImagenes_nacionales,
            'meses_inconsistencias_nacionales': meses_inconsistencias_nacionales,
            'porcentajes_inconsistencias_nacionales': porcentajes_inconsistencias_nacionales,
            'meses_traslados_nacionales': meses_traslados_nacionales,
            'porcentajes_traslados_nacionales': porcentajes_traslados_nacionales,
            'meses_entrega_informes_distritales': meses_entrega_informes_distritales,
            'porcentajes_entrega_informes_distritales': porcentajes_entrega_informes_distritales,
            'meses_calidad_informes_distritales': meses_calidad_informes_distritales,
            'porcentajes_calidad_informes_distritales': porcentajes_calidad_informes_distritales,
            'meses_entregaImagenes_distritales': meses_entregaImagenes_distritales,
            'porcentajes_entregaImagenes_distritales': porcentajes_entregaImagenes_distritales,
            'meses_inconsistencias_distritales': meses_inconsistencias_distritales,
            'porcentajes_inconsistencias_distritales': porcentajes_inconsistencias_distritales,
            'meses_traslados_distritales': meses_traslados_distritales,
            'porcentajes_traslados_distritales': porcentajes_traslados_distritales,
            'meses_calidad_informes_convenios': meses_calidad_informes_convenios,
            'porcentajes_calidad_informes_convenios': porcentajes_calidad_informes_convenios,
            'meses_entregaImagenes_convenios': meses_entregaImagenes_convenios,
            'porcentajes_entregaImagenes_convenios': porcentajes_entregaImagenes_convenios,
            'meses_inconsistencias_convenios': meses_inconsistencias_convenios,
            'porcentajes_inconsistencias_convenios': porcentajes_inconsistencias_convenios,
            'meses_traslados_convenios': meses_traslados_convenios,
            'porcentajes_traslados_convenios': porcentajes_traslados_convenios,
            'meses_entregaFisicos_departamentales': meses_entregaFisicos_departamentales,
            'porcentajes_entregaFisicos_departamentales': porcentajes_entregaFisicos_departamentales,
            'meses_calidad_informes_departamentales': meses_calidad_informes_departamentales,
            'porcentajes_calidad_informes_departamentales': porcentajes_calidad_informes_departamentales,
            'meses_entregaImagenes_departamentales': meses_entregaImagenes_departamentales,
            'porcentajes_entregaImagenes_departamentales': porcentajes_entregaImagenes_departamentales,
            'meses_inconsistencias_departamentales': meses_inconsistencias_departamentales,
            'porcentajes_inconsistencias_departamentales': porcentajes_inconsistencias_departamentales,
            'meses_traslados_departamentales': meses_traslados_departamentales,
            'porcentajes_traslados_departamentales': porcentajes_traslados_departamentales,
            'meses_entregaFisicos_municipalesCali': meses_entregaFisicos_municipalesCali,
            'porcentajes_entregaFisicos_municipalesCali': porcentajes_entregaFisicos_municipalesCali,
            'meses_entrega_informes_municipalesCali': meses_entrega_informes_municipalesCali,
            'porcentajes_entrega_informes_municipalesCali': porcentajes_entrega_informes_municipalesCali,
            'meses_inconsistenciasPasivo': meses_inconsistenciasPasivo,
            'porcentajes_inconsistenciasPasivo': porcentajes_inconsistenciasPasivo,
            'meses_inconsistenciasActivo': meses_inconsistenciasActivo,
            'porcentajes_inconsistenciasActivo': porcentajes_inconsistenciasActivo,
            'meses_inconsistenciasrepsuestaTradicional': meses_inconsistenciasrepsuestaTradicional,
            'porcentajes_inconsistenciasrepsuestaTradicional': porcentajes_inconsistenciasrepsuestaTradicional,
            'meses_inconsistenciasrepsuestaOCI': meses_inconsistenciasrepsuestaOCI,
            'porcentajes_inconsistenciasrepsuestaOCI': porcentajes_inconsistenciasrepsuestaOCI,
            'meses_repsuestaCrerditoOCI': meses_repsuestaCrerditoOCI,
            'tiempo_repsuestaCreditoOCI': tiempo_repsuestaCreditoOCI,
            'meses_repsuestaCrerditoTradicional': meses_repsuestaCrerditoTradicional,
            'tiempo_repsuestaCreditoTradicional': tiempo_repsuestaCreditoTradicional,
            'meses_calidadInformacion_radicacion': meses_calidadInformacion_radicacion,
            'porcentajes_calidadInformacion_radicacion': porcentajes_calidadInformacion_radicacion,
            'meses_entrega_informes_radicacion': meses_entrega_informes_radicacion,
            'porcentajes_entrega_informes_radicacion': porcentajes_entrega_informes_radicacion,
            'meses_entregaImagenes_radicacion': meses_entregaImagenes_radicacion,
            'porcentajes_entregaImagenes_radicacion': porcentajes_entregaImagenes_radicacion,
            'meses_entregaFisicos_TarjetasDigital': meses_entregaFisicos_TarjetasDigital,
            'porcentajes_entrega_fisicos_TarjetasDigital': porcentajes_entrega_fisicos_TarjetasDigital,
            'meses_entregaFisicos_TarjetasFisico': meses_entregaFisicos_TarjetasFisico,
            'porcentajes_entrega_fisicos_TarjetasFisico': porcentajes_entrega_fisicos_TarjetasFisico,
            'meses_Taduanas_nacionales':meses_Taduanas_nacionales,
            'procentajes_Taduanas_nacionales':procentajes_Taduanas_nacionales,


            'meses_administrativo_sistemas': meses_administrativo_sistemas,
            'porcentajes_administrativo_sistemas': porcentajes_administrativo_sistemas,
            'meses_administrativo_tecnologia': meses_administrativo_tecnologia,
            'porcentajes_administrativo_tecnologia': porcentajes_administrativo_tecnologia,
            'meses_administrativo_financiera': meses_administrativo_financiera,
            'porcentajes_administrativo_financiera': porcentajes_administrativo_financiera,
            'meses_administrativo_comercial_propuestas': meses_administrativo_comercial_propuestas,
            'porcentajes_administrativo_comercial_propuestas': porcentajes_administrativo_comercial_propuestas,
            'meses_administrativo_comercial_efectividad': meses_administrativo_comercial_efectividad,
            'porcentajes_administrativo_comercial_efectividad': porcentajes_administrativo_comercial_efectividad,
            'meses_administrativo_comercial_pqr': meses_administrativo_comercial_pqr,
            'porcentajes_administrativo_comercial_pqr': porcentajes_administrativo_comercial_pqr,
            'meses_administrativo_TH_clima_organizacional': meses_administrativo_TH_clima_organizacional,
            'porcentajes_administrativo_TH_clima_organizacional': porcentajes_administrativo_TH_clima_organizacional,
            'meses_administrativo_TH_Cumplimiento_Capacitaciones': meses_administrativo_TH_Cumplimiento_Capacitaciones,
            'porcentajes_administrativo_TH_Cumplimiento_Capacitaciones': porcentajes_administrativo_TH_Cumplimiento_Capacitaciones,
            'meses_administrativo_TH_Eficacia_Capacitaciones': meses_administrativo_TH_Eficacia_Capacitaciones,
            'porcentajes_administrativo_TH_Eficacia_Capacitaciones': porcentajes_administrativo_TH_Eficacia_Capacitaciones,
            'meses_administrativo_TH_Evaluacion_Desempeño': meses_administrativo_TH_Evaluacion_Desempeño,
            'porcentajes_administrativo_TH_Evaluacion_Desempeño': porcentajes_administrativo_TH_Evaluacion_Desempeño,
            'meses_administrativo_SGI_Acciones_Correctivas': meses_administrativo_SGI_Acciones_Correctivas,
            'porcentajes_administrativo_SGI_Acciones_Correctivas': porcentajes_administrativo_SGI_Acciones_Correctivas,
            'meses_administrativo_SGI_Continuidad_Negocio': meses_administrativo_SGI_Continuidad_Negocio,
            'porcentajes_administrativo_SGI_Continuidad_Negocio': porcentajes_administrativo_SGI_Continuidad_Negocio,
            'meses_administrativo_SGI_Incidentes_Seguridad': meses_administrativo_SGI_Incidentes_Seguridad,
            'porcentajes_administrativo_SGI_Incidentes_Seguridad': porcentajes_administrativo_SGI_Incidentes_Seguridad,
            'meses_administrativo_SGI_Producto_No_Conforme': meses_administrativo_SGI_Producto_No_Conforme,
            'porcentajes_administrativo_SGI_Producto_No_Conforme': porcentajes_administrativo_SGI_Producto_No_Conforme,
            'meses_administrativo_SGI_Riesgos': meses_administrativo_SGI_Riesgos,
            'porcentajes_administrativo_SGI_Riesgos': porcentajes_administrativo_SGI_Riesgos,
        }
    return render_template('indicadores/indicadores.html', **CONTEXTO(), **CONTEXTO_GRAFICA())


'''GESTION DE PRODUCCIOIN'''
@ind_bp.route('/guardar_calidad_informacion', methods=['POST'])
@login_required
def guardar_calidad_informacion():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'form_digitados': request.form['form_digitados'],
            'err_digitacion': request.form['err_digitacion'],
            'resultado': request.form['resultado_calidadInformacion'],
            'meta': request.form['meta_calidadInformacion'],
            'analisis': request.form['analisis_calidadInformacion'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_calidadInformacion(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)  
@ind_bp.route('/guardar_registros_magneticos', methods=['POST'])
@login_required
def guardar_registros_magneticos():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'T_registros': request.form['T_registros'],
            'R_extemporaneos': request.form['R_extemporaneos'],
            'resultado': request.form['resultado_resgitrosExtemporaneos'],
            'meta': request.form['meta_resgitrosExtemporaneos'],
            'analisis': request.form['analisis_resgitrosExtemporaneos']
        }
        rol = current_user.rol
        guardar_registrosExtemporaneos(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/registro_extemporaneo', methods=['POST'])
def obtener_registro_extemporaneo():
    mes = request.json.get('mes')
    rol = current_user.rol
    resultado = obtener_r_extemporeaneo_mes(mes, rol)
    if resultado:
        return jsonify({'r_extemporaneo': resultado[0],
                        't_registros': resultado[1]})
    else:
        return jsonify({'r_extemporaneo': 0,
                        't_registros': 0})
@ind_bp.route('/registro_extemporaneo_fisico', methods=['POST'])
def registro_extemporaneo_fisico():
    mes = request.json.get('mes')
    rol = current_user.rol
    resultado = obtener_r_extemporeaneoFisico_mes(mes, rol)
    if resultado:
        return jsonify({'d_extemporaneo': resultado[0],
                        'd_registros': resultado[1]})
    else:
        return jsonify({'d_extemporaneo': 0,
                        'd_registros': 0})    
@ind_bp.route('/guardar_sanciones_magneticas', methods=['POST'])
@login_required
def guardar_sanciones_magneticas():
    if request.method == 'POST':
        valor_porcentaje = request.form['P_aceptacion'].replace('%', '').replace(',', '.')
        valor_uvt = request.form['UVT_sancionesMagneticas'].replace('$', '').replace(',', '.')
        valor_multa = request.form['multa_sancionesMagneticas'].replace('$', '').replace(',', '.')
        datos = {
            'mes': request.form['mes2'],
            'R_extemporaneos2': request.form['R_extemporaneos2'],
            'r_digicom': request.form['r_digicom'],
            'P_aceptacion': valor_porcentaje,
            'resultado': request.form['resultado_sancionesMagneticas'],
            'meta': request.form['meta_sancionesMagneticas'],
            'uvt': valor_uvt,
            'multa': valor_multa,
            'analisis': request.form['analisis_sancionesMagneticas']
        }
        rol = current_user.rol

        print(datos)
        guardar_sancionesMagneticas(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_sanciones_fisicos', methods=['POST'])
@login_required
def guardar_sanciones_fisicos():
    if request.method == 'POST':
        valor_porcentaje = request.form['P_aceptacion_fisicos'].replace('%', '').replace(',', '.')
        valor_uvt = request.form['UVT_sancionesFisicos'].replace('$', '').replace(',', '.')
        valor_multa = request.form['multa_sancionesFisicos'].replace('$', '').replace(',', '.')
        datos = {
            'mes': request.form['mes_fisicos'],
            'D_extemporaneos2': request.form['D_extemporaneos2'],
            'dr_digicom': request.form['dr_digicom'],
            'P_aceptacion_fisicos': valor_porcentaje,
            'resultado_sancionesFisicos': request.form['resultado_sancionesFisicos'],
            'meta_sancionesFisicos': request.form['meta_sancionesFisicos'],
            'uvt_sancionesFisicos': valor_uvt,
            'multa_sancionesFisicos': valor_multa,
            'analisis_sancionesFisicos': request.form['analisis_sancionesFisicos']
        }
        rol = current_user.rol

        guardar_sancionesFisicos(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_entrega_fisicos', methods=['POST'])
@login_required
def guardar_entrega_fisicos():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'documentos_entregados': request.form['doc_entregados'],
            'documentos_extemporaneos': request.form['doc_extemporaneos'],
            'resultado': request.form['resultado_entrgeaFisicos'],
            'meta': request.form['meta_entregaFisicos'],
            'analisis': request.form['analisis_entregaFisicos'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        print(datos)
        guardar_registrosFisicos(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_cintas_magneticas', methods=['POST'])
@login_required
def guardar_cintas_magneticas():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'cintas_enviadas': request.form['cin_enviadas'],
            'cintas_rechazadas': request.form['cin_rechazadas'],
            'resultado': request.form['resultado_cintasMagneticas'],
            'meta': request.form['meta_cintasMagneticas'],
            'analisis': request.form['analisis_cintasMagneticas'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        print(datos)
        guardar_cintasMagneticas(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_informes_entregados', methods=['POST'])
@login_required
def guardar_informes_entregados():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'informes_entregados': request.form['inf_enviados'],
            'informes_extemporaneos': request.form['inf_fueraTiempo'],
            'resultado': request.form['resultado_informes'],
            'meta': request.form['meta_informes'],
            'analisis': request.form['analisis_informes'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_informesEntregados(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_sitioWeb', methods=['POST'])
@login_required
def guardar_sitioWeb():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'img_enviados': request.form['img_enviados'],
            'img_fueraTiempo': request.form['img_fueraTiempo'],
            'resultado': request.form['resultado_sitio_web'],
            'meta': request.form['meta_sitio_web'],
            'analisis': request.form['analisis_sitio_web'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_sitio_web(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_calidad_informes', methods=['POST'])
@login_required
def guardar_calidad_informes():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'inf_entregados': request.form['inf_entregados'],
            'inf_errados': request.form['inf_errados'],
            'resultado': request.form['resultado_calidad_informes'],
            'meta': request.form['meta_calidad_informes'],
            'analisis': request.form['analisis_calidad_informes'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_calidadInformes(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_entrega_imagenes', methods=['POST'])
@login_required
def guardar_entrega_imagenes():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'img_entregadas': request.form['img_entregadas'],
            'img_extemporaneas': request.form['img_extemporaneas'],
            'resultado': request.form['resultado_entrgeaImagenes'],
            'meta': request.form['meta_entregaImagenes'],
            'analisis': request.form['analisis_entregaImagenes'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_entregaImagenes(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_solucion_inconsistencias', methods=['POST'])
@login_required
def guardar_solucion_inconsistencias():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'inc_repotadas': request.form['inc_repotadas'],
            'inc_solucionadas': request.form['inc_solucionadas'],
            'resultado': request.form['resultado_inconstencias'],
            'meta': request.form['meta_inconstencias'],
            'analisis': request.form['analisis_inconstencias'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_inconsistenciasSolucionadas(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_traslados', methods=['POST'])
@login_required
def guardar_traslados():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'traslados': request.form['traslados'],
            'traslados_extemporaneos': request.form['traslados_extemporaneos'],
            'resultado': request.form['resultado_traslados'],
            'meta': request.form['meta_traslados'],
            'analisis': request.form['analisis_traslados'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_traslado(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_inconsistencias_pasivo', methods=['POST'])
@login_required
def guardar_inconsistencias_pasivo():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            't_casos': request.form['t_casos'],
            'e_grabacion_analisis': request.form['e_grabacion_analisis'],
            'resultado': request.form['resultado_inconsistenciasPasivo'],
            'meta': request.form['meta_inconsistenciasPasivo'],
            'analisis': request.form['analisis_inconsistenciasPasivo'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_inconsitenciasPasivo(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/guardar_TRespuesta_Credito', methods=['POST'])
@login_required
def guardar_TRespuesta_Credito():
    
    if request.method == 'POST':
        def convertir_time(cadena):
            cadena = cadena.strip().lower().replace("seg", "").replace(" segundos", "").strip()

            if ":" in cadena:
                # Caso formato MM:SS
                partes = cadena.split(":")
                if len(partes) == 2:  # mm:ss
                    minutos, segundos = map(int, partes)
                    horas = 0
                elif len(partes) == 3:  # hh:mm:ss
                    horas, minutos, segundos = map(int, partes)
                else:
                    raise ValueError("Formato de tiempo no válido")
            else:
                # Caso solo segundos
                segundos = int(cadena)
                horas = segundos // 3600
                minutos = (segundos % 3600) // 60
                segundos = segundos % 60

            return f"{horas:02}:{minutos:02}:{segundos:02}"
        #convertir tiempo de respuesta
        t_respuesta = request.form['t_respuesta']
        t_segundos_respuesta = convertir_time(t_respuesta)
        #convertir resultado
        t_resultado = request.form['resultado_TRespuesta']
        t_segundos_resultado = convertir_time(t_resultado)
        datos = {
            'mes': request.form['mes_TRespuesta'],
            't_creditos': request.form['t_creditos'],
            't_respuesta': t_segundos_respuesta,
            'resultado': t_segundos_resultado,
            'analisis': request.form['Analisis_TRespuesta'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        #print(datos)
        guardar_TRespuesta_credito(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
@ind_bp.route('/get_tiempo_mes_anterior', methods=['GET'])
def get_tiempo_mes_anterior():
    proceso = request.args.get('proceso')
    mes = request.args.get(f'mes')
    rol = current_user.rol
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    idx = meses.index(mes)
    mes_anterior = meses[idx - 1] if idx > 0 else None
    if not mes_anterior:
        return jsonify({"tiempo_respuesta": None})
    resultado_mes = datos_mes_anterior(mes_anterior, proceso, rol)
    if resultado_mes: 
        tiempo_str = str(resultado_mes[0]) 
        partes = tiempo_str.split(':')
        horas, minutos, segundos = partes
        if horas == '00:00':
            mmss = f'{minutos}:{segundos}'
        else:
            mmss = f'{horas}:{minutos}:{segundos}'
        return jsonify({"tiempo_respuesta": mmss})
    else:
        return jsonify({"tiempo_respuesta": None})    
@ind_bp.route('/guardar_transmision_aduanas', methods=['POST'])
@login_required
def guardar_transmision_aduanas():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            't_aduanas': request.form['t_aduanas'],
            't_aduanasFueraTiempo': request.form['t_aduanasFueraTiempo'],
            'resultado': request.form['resultado_Taduanas'],
            'meta': request.form['meta_Taduanas'],
            'analisis': request.form['analisis_Taduanas'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_TransAduanas(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)


'''ADMINISTRATIVO'''
@ind_bp.route('/guardar_administrativo', methods=['POST'])
@login_required
def guardar_administrativo():
    if request.method == 'POST':
        datos = {
            'mes': request.form['mes'],
            'Sol_atendidas': request.form['Sol_atendidas'],
            'Sol_realizadas': request.form['Sol_realizadas'],
            'resultado': request.form['resultado_administrativo'],
            'meta': request.form['meta_administrativo'],
            'analisis': request.form['analisis_administrativo'],
            'proceso': request.form['proceso']
        }
        rol = current_user.rol
        guardar_Administrativo(datos, rol)
        return redirect(url_for('ind.indicadores'))
    return render_template('indicadores/indicadores.html', usuario=current_user)
