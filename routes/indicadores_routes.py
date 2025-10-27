from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import current_user, login_required
'''GESTION DE PRODUCCION'''
from controllers.ind_controller import uvt_rol
from controllers.ind_controller import obtener_r_extemporeaneo_mes
from controllers.ind_controller import lista_sancionesMagenticas, guardar_sancionesMagneticas, grafica_sancionesMagneticas
from controllers.ind_controller import grafica_registrosFisicos, guardar_registrosFisicos, lista_registrosFisicos, obtener_r_extemporeaneoFisico_mes
from controllers.ind_controller import guardar_sancionesFisicos, grafica_sancionesFisicos, lista_sancionesFisicos
from controllers.ind_controller import lista_inconsitenciasPasivo, guardar_inconsitenciasPasivo, grafica_inconsitenciasPasivo
from controllers.ind_controller import lista_TRespuesta_credito, guardar_TRespuesta_credito, datos_mes_anterior, grafica_TRespuesta_credito
from controllers.rol_controller import PROCESOS_ROL, ROL_IMAGES, nombre_rol

'''ADMINISTRATIVO'''
from controllers.ind_controller import lista_Administrativo, grafica_Administrativo, guardar_Administrativo

ind_bp = Blueprint('ind', __name__)

@ind_bp.route('/indicadores')
@login_required
def indicadores():
    # Usar el rol del usuario por defecto, a menos que se haya seleccionado uno específico
    rol = current_user.rol
    
    # Solo usar el rol de la sesión si se ha seleccionado explícitamente
    if 'selected_rol' in session and session['selected_rol'] is not None:
        rol = session['selected_rol']
    def CONTEXTO():
        
        nombre_del_rol = nombre_rol(rol)
        procesos = PROCESOS_ROL.get(rol, [])
        imagen_rol = ROL_IMAGES.get(rol, 'imgs/user.png')
        '''GESTION DE PRODUCCION'''
        uvt_valor = uvt_rol(rol)

        #agrario
        datos_calidadInformacion_nacionales_agrario = lista_registrosFisicos(rol, 'Nacionales_Agrario_CalidadInformacion')
        datos_registrosMagneticos_nacionales_agrario = lista_registrosFisicos(rol, 'Nacionales_Agrario_RegistrosMagneticos')
        #bancolombia
        datos_entrega_fisicos_nacionales_bancolombia = lista_registrosFisicos(rol, 'Nacionales_Bancolombia_Fisicos')
        datos_registrosMagneticos_nacionales_bancolombia = lista_registrosFisicos(rol, 'Nacionales_Bancolombia_Magneticos')
        datos_entrega_fisicos_Distritales_Bancolombia_Fisicos = lista_registrosFisicos(rol, 'Distritales_Bancolombia_Fisicos')
        datos_entrega_fisicos_Distritales_Bancolombia_CMagneticas = lista_registrosFisicos(rol, 'Distritales_Bancolombia_CMagneticas')
        datos_Departamentales_Bancolombia_informes = lista_registrosFisicos(rol, 'Departamentales_Bancolombia_informes')
        datos_Convenios_Bancolombia_Informes = lista_registrosFisicos(rol, 'Convenios_Bancolombia_Informes')
        datos_Convenios_Bancolombia_Fisicos = lista_registrosFisicos(rol, 'Convenios_Bancolombia_Fisicos')
        datos_Convenios_Bancolombia_Web = lista_registrosFisicos(rol, 'Convenios_Bancolombia_Web')
        #occidnete
        datos_entrega_fisicos_nacionales_occidente = lista_registrosFisicos(rol, 'Nacionales_Occidente_Fisicos')
        datos_registrosMagneticos_nacionales_occidente = lista_registrosFisicos(rol, 'Nacionales_Occidente_Magneticos')
        datos_entrega_fisicos_Distritales_Occidente_Fisicos = lista_registrosFisicos(rol, 'Distritales_Occidente_Fisicos')
        datos_entrega_fisicos_Distritales_Occidente_CMagneticas = lista_registrosFisicos(rol, 'Distritales_Occidente_CMagneticas')
        #itau
        datos_entrega_fisicos_nacionales_itau = lista_registrosFisicos(rol, 'Nacionales_Itau_Fisicos')
        datos_registrosMagneticos_nacionales_itau = lista_registrosFisicos(rol, 'Nacionales_Itau_Magneticos')
        datos_Departamentales_Itau_Fisicos = lista_registrosFisicos(rol, 'Departamentales_Itau_Fisicos')
        datos_Departamentales_Itau_Informes = lista_registrosFisicos(rol, 'Departamentales_Itau_Informes')
        datos_MunicipalesCali_Iatu_Fisicos = lista_registrosFisicos(rol, 'MunicipalesCali_Iatu_Fisicos')
        datos_MunicipalesCali_Iatu_Informes = lista_registrosFisicos(rol, 'MunicipalesCali_Iatu_Informes')
        #cajasocial
        datos_entrega_fisicos_nacionales_cajasocial = lista_registrosFisicos(rol, 'Nacionales_CajaSocial_Fisicos')
        datos_registrosMagneticos_nacionales_cajasocial = lista_registrosFisicos(rol, 'Nacionales_CajaSocial_Magneticos')
        datos_Nacionales_Aduanas_CajaSocial = lista_registrosFisicos(rol, 'Nacionales_Aduanas_CajaSocial')
        datos_Convenios_CajaSocial_Informes = lista_registrosFisicos(rol, 'Convenios_CajaSocial_Informes')
        datos_Convenios_CajaSocial_Fisicos = lista_registrosFisicos(rol, 'Convenios_CajaSocial_Fisicos')
        datos_Convenios_CajaSocial_Web = lista_registrosFisicos(rol, 'Convenios_CajaSocial_Web')
        #davivienda
        datos_Nacionales_Informes_Davivienda = lista_registrosFisicos(rol, 'Nacionales_Informes_Davivienda')
        datos_Nacionales_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Nacionales_CalidadInformes_Davivienda')
        datos_Nacionales_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Nacionales_EntregaImagenes_Davivienda')
        datos_Nacionales_Davivienda_Fisicos = lista_registrosFisicos(rol, 'Nacionales_Davivienda_Fisicos')
        datos_Nacionales_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Nacionales_Inconsistencias_Davivienda')
        datos_Nacionales_Traslados_Davivienda = lista_registrosFisicos(rol, 'Nacionales_Traslados_Davivienda')
        datos_Distritales_Informes_Davivienda = lista_registrosFisicos(rol, 'Distritales_Informes_Davivienda')
        datos_Distritales_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Distritales_CalidadInformes_Davivienda')
        datos_Distritales_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Distritales_EntregaImagenes_Davivienda')
        datos_Distritales_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Distritales_Inconsistencias_Davivienda')
        datos_Distritales_Traslados_Davivienda = lista_registrosFisicos(rol, 'Distritales_Traslados_Davivienda')
        datos_Departamentales_Informes_Davivienda = lista_registrosFisicos(rol, 'Departamentales_Informes_Davivienda')
        datos_Departamentales_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Departamentales_CalidadInformes_Davivienda')
        datos_Departamentales_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Departamentales_EntregaImagenes_Davivienda')
        datos_Departamentales_Davivienda_Fisicos = lista_registrosFisicos(rol, 'Departamentales_Davivienda_Fisicos')
        datos_Departamentales_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Departamentales_Inconsistencias_Davivienda')
        datos_Departamentales_Traslados_Davivienda = lista_registrosFisicos(rol, 'Departamentales_Traslados_Davivienda')
        datos_Convenios_Informes_Davivienda = lista_registrosFisicos(rol, 'Convenios_Informes_Davivienda')
        datos_Convenios_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Convenios_CalidadInformes_Davivienda')
        datos_Convenios_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Convenios_EntregaImagenes_Davivienda')
        datos_Convenios_Davivienda_Fisicos = lista_registrosFisicos(rol, 'Convenios_Davivienda_Fisicos')
        datos_Convenios_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Convenios_Inconsistencias_Davivienda')
        datos_Convenios_Traslados_Davivienda = lista_registrosFisicos(rol, 'Convenios_Traslados_Davivienda')
        #avvillas
        datos_inconsistencias_pasivo = lista_inconsitenciasPasivo(rol, 'complementacion_pasivo')
        datos_inconsistencias_activo = lista_inconsitenciasPasivo(rol, 'complementacion_activo')
        datos_inconsistencias_repsuestaTradicional = lista_inconsitenciasPasivo(rol, 'complementacion_repsuestaTradicional')
        datos_inconsistencias_repsuestaOCI = lista_inconsitenciasPasivo(rol, 'complementacion_repsuestaOCI')
        datos_repsuestaCreditoOCI = lista_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoOCI')
        datos_repsuestaCreditoTradicional = lista_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoTradicional')
        datos_Radicacion_AvVillas_CalidadInformacion = lista_registrosFisicos(rol, 'Radicacion_AvVillas_CalidadInformacion')
        datos_Radicacion_AvVillas_Informes = lista_registrosFisicos(rol, 'Radicacion_AvVillas_Informes')
        datos_Radicacion_AvVillas_Imagenes = lista_registrosFisicos(rol, 'Radicacion_AvVillas_Imagenes')
        datos_entrega_fisicos_TarjetasDigital = lista_registrosFisicos(rol, 'TarjetasDigital')
        datos_entrega_fisicos_TarjetasFisico = lista_registrosFisicos(rol, 'TarjetasFisico')
        #aplica para to0dos los bancos
        datos_sancionesMagneticas = lista_sancionesMagenticas(rol)
        datos_sancionesFisicos = lista_sancionesFisicos(rol)
        

        '''ADMINISTRATIVO'''
        datos_administrativo_sistemas = lista_Administrativo(rol, 'sistemas')
        datos_administrativo_tecnologia = lista_Administrativo(rol, 'tecnologia')
        datos_administrativo_financiera = lista_Administrativo(rol, 'financiera')
        datos_administrativo_comercial_propuestas = lista_Administrativo(rol, 'comercial_propuestas')
        datos_administrativo_comercial_efectividad = lista_Administrativo(rol, 'comercial_efectividad')
        datos_administrativo_comercial_pqr = lista_Administrativo(rol, 'comercial_pqr')
        datos_administrativo_TH_clima_organizacional = lista_Administrativo(rol, 'TH_clima_organizacional')
        datos_administrativo_TH_Cumplimiento_Capacitaciones = lista_Administrativo(rol, 'TH_Cumplimiento_Capacitaciones')
        datos_administrativo_TH_Eficacia_Capacitaciones = lista_Administrativo(rol, 'TH_Eficacia_Capacitaciones')
        datos_administrativo_TH_Evaluacion_Desempeño = lista_Administrativo(rol, 'TH_Evaluacion_Desempeño')
        datos_administrativo_SGI_Acciones_Correctivas = lista_Administrativo(rol, 'SGI_Acciones_Correctivas')
        datos_administrativo_SGI_Continuidad_Negocio = lista_Administrativo(rol, 'SGI_Continuidad_Negocio')
        datos_administrativo_SGI_Incidentes_Seguridad = lista_Administrativo(rol, 'SGI_Incidentes_Seguridad')
        datos_administrativo_SGI_Producto_No_Conforme = lista_Administrativo(rol, 'SGI_Producto_No_Conforme')
        datos_administrativo_SGI_Riesgos = lista_Administrativo(rol, 'SGI_Riesgos')
        return {
            'uvt_valor': uvt_valor,
            'imagen_rol': imagen_rol,
            'rol_seleccionado': rol,
            'nombre_rol_seleccionado': nombre_del_rol,
            'is_especific_role': False,
            'is_role_override': rol != current_user.rol,
            #agrario
            'datos_calidadInformacion_nacionales_agrario': datos_calidadInformacion_nacionales_agrario,
            'datos_registrosMagneticos_nacionales_agrario': datos_registrosMagneticos_nacionales_agrario,
            #bancolombia
            'datos_entrega_fisicos_nacionales_bancolombia': datos_entrega_fisicos_nacionales_bancolombia,
            'datos_registrosMagneticos_nacionales_bancolombia': datos_registrosMagneticos_nacionales_bancolombia,
            'datos_entrega_fisicos_Distritales_Bancolombia_Fisicos': datos_entrega_fisicos_Distritales_Bancolombia_Fisicos,
            'datos_entrega_fisicos_Distritales_Bancolombia_CMagneticas': datos_entrega_fisicos_Distritales_Bancolombia_CMagneticas,
            'datos_Departamentales_Bancolombia_informes': datos_Departamentales_Bancolombia_informes,
            'datos_Convenios_Bancolombia_Informes': datos_Convenios_Bancolombia_Informes,
            'datos_Convenios_Bancolombia_Fisicos': datos_Convenios_Bancolombia_Fisicos,
            'datos_Convenios_Bancolombia_Web': datos_Convenios_Bancolombia_Web,
            #occidente
            'datos_entrega_fisicos_nacionales_occidente': datos_entrega_fisicos_nacionales_occidente,
            'datos_registrosMagneticos_nacionales_occidente': datos_registrosMagneticos_nacionales_occidente,
            'datos_entrega_fisicos_Distritales_Occidente_Fisicos': datos_entrega_fisicos_Distritales_Occidente_Fisicos,
            'datos_entrega_fisicos_Distritales_Occidente_CMagneticas': datos_entrega_fisicos_Distritales_Occidente_CMagneticas,
            #itau
            'datos_entrega_fisicos_nacionales_itau': datos_entrega_fisicos_nacionales_itau,
            'datos_registrosMagneticos_nacionales_itau': datos_registrosMagneticos_nacionales_itau,
            'datos_Departamentales_Itau_Fisicos': datos_Departamentales_Itau_Fisicos,
            'datos_Departamentales_Itau_Informes': datos_Departamentales_Itau_Informes,
            'datos_MunicipalesCali_Iatu_Fisicos': datos_MunicipalesCali_Iatu_Fisicos,
            'datos_MunicipalesCali_Iatu_Informes': datos_MunicipalesCali_Iatu_Informes,
            #cajaSocial
            'datos_entrega_fisicos_nacionales_cajasocial': datos_entrega_fisicos_nacionales_cajasocial,
            'datos_registrosMagneticos_nacionales_cajasocial': datos_registrosMagneticos_nacionales_cajasocial,
            'datos_Nacionales_Aduanas_CajaSocial': datos_Nacionales_Aduanas_CajaSocial,
            'datos_Convenios_CajaSocial_Informes': datos_Convenios_CajaSocial_Informes,
            'datos_Convenios_CajaSocial_Fisicos': datos_Convenios_CajaSocial_Fisicos,
            'datos_Convenios_CajaSocial_Web': datos_Convenios_CajaSocial_Web,
            #davivienda
            'datos_Nacionales_Informes_Davivienda': datos_Nacionales_Informes_Davivienda,
            'datos_Nacionales_CalidadInformes_Davivienda': datos_Nacionales_CalidadInformes_Davivienda,
            'datos_Nacionales_EntregaImagenes_Davivienda': datos_Nacionales_EntregaImagenes_Davivienda,
            'datos_Nacionales_Davivienda_Fisicos': datos_Nacionales_Davivienda_Fisicos,
            'datos_Nacionales_Inconsistencias_Davivienda': datos_Nacionales_Inconsistencias_Davivienda,
            'datos_Nacionales_Traslados_Davivienda': datos_Nacionales_Traslados_Davivienda,
            'datos_Distritales_Informes_Davivienda': datos_Distritales_Informes_Davivienda,
            'datos_Distritales_CalidadInformes_Davivienda': datos_Distritales_CalidadInformes_Davivienda,
            'datos_Distritales_EntregaImagenes_Davivienda': datos_Distritales_EntregaImagenes_Davivienda,
            'datos_Distritales_Inconsistencias_Davivienda': datos_Distritales_Inconsistencias_Davivienda,
            'datos_Distritales_Traslados_Davivienda': datos_Distritales_Traslados_Davivienda,
            'datos_Departamentales_Informes_Davivienda': datos_Departamentales_Informes_Davivienda,
            'datos_Departamentales_CalidadInformes_Davivienda': datos_Departamentales_CalidadInformes_Davivienda,
            'datos_Departamentales_EntregaImagenes_Davivienda': datos_Departamentales_EntregaImagenes_Davivienda,
            'datos_Departamentales_Davivienda_Fisicos': datos_Departamentales_Davivienda_Fisicos,
            'datos_Departamentales_Inconsistencias_Davivienda': datos_Departamentales_Inconsistencias_Davivienda,
            'datos_Departamentales_Traslados_Davivienda': datos_Departamentales_Traslados_Davivienda,
            'datos_Convenios_Informes_Davivienda': datos_Convenios_Informes_Davivienda,
            'datos_Convenios_CalidadInformes_Davivienda': datos_Convenios_CalidadInformes_Davivienda,
            'datos_Convenios_EntregaImagenes_Davivienda': datos_Convenios_EntregaImagenes_Davivienda,
            'datos_Convenios_Davivienda_Fisicos': datos_Convenios_Davivienda_Fisicos,
            'datos_Convenios_Inconsistencias_Davivienda': datos_Convenios_Inconsistencias_Davivienda,
            'datos_Convenios_Traslados_Davivienda': datos_Convenios_Traslados_Davivienda,
            #avvillas
            'datos_inconsistencias_pasivo': datos_inconsistencias_pasivo,
            'datos_inconsistencias_activo': datos_inconsistencias_activo,
            'datos_inconsistencias_repsuestaTradicional': datos_inconsistencias_repsuestaTradicional,
            'datos_inconsistencias_repsuestaOCI': datos_inconsistencias_repsuestaOCI,
            'datos_repsuestaCreditoOCI': datos_repsuestaCreditoOCI,
            'datos_repsuestaCreditoTradicional': datos_repsuestaCreditoTradicional,
            'datos_Radicacion_AvVillas_CalidadInformacion': datos_Radicacion_AvVillas_CalidadInformacion,
            'datos_Radicacion_AvVillas_Informes': datos_Radicacion_AvVillas_Informes,
            'datos_Radicacion_AvVillas_Imagenes': datos_Radicacion_AvVillas_Imagenes,
            'datos_entrega_fisicos_TarjetasDigital': datos_entrega_fisicos_TarjetasDigital,
            'datos_entrega_fisicos_TarjetasFisico': datos_entrega_fisicos_TarjetasFisico,
            #todos los bancos
            'usuario': current_user,
            'datos_sancionesMagneticas': datos_sancionesMagneticas,
            'datos_sancionesFisicos': datos_sancionesFisicos,
            'procesos': procesos,
            #administrativo
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
        #Agrario
        meses_calidadInformacion_nacionales_agrario, porcentajes_calidadInformacion_nacionales_agrario = grafica_registrosFisicos(rol, 'Nacionales_Agrario_CalidadInformacion')
        meses_registrosMagneticos_nacionales_agrario, porcentajes_registrosMagneticos_nacionales_agrario = grafica_registrosFisicos(rol, 'Nacionales_Agrario_RegistrosMagneticos')
        #bancolombia
        meses_entregaFisicos_nacionales_bancolombia, porcentajes_entrega_fisicos_nacionales_bancolombia = grafica_registrosFisicos(rol, 'Nacionales_Bancolombia_Fisicos')
        meses_registrosMagneticos_nacionales_bancolombia, porcentajes_registrosMagneticos_nacionales_bancolombia = grafica_registrosFisicos(rol, 'Nacionales_Bancolombia_Magneticos')
        meses_entregaFisicos_Distritales_Bancolombia_Fisicos, porcentajes_entrega_fisicos_Distritales_Bancolombia_Fisicos = grafica_registrosFisicos(rol, 'Distritales_Bancolombia_Fisicos')
        meses_entregaFisicos_Distritales_Bancolombia_CMagneticas, porcentajes_entrega_fisicos_Distritales_Bancolombia_CMagneticas = grafica_registrosFisicos(rol, 'Distritales_Bancolombia_CMagneticas')
        meses_entrega_Departamentales_Bancolombia_informes, porcentajes_Departamentales_Bancolombia_informes = grafica_registrosFisicos(rol, 'Departamentales_Bancolombia_informes')
        meses_Convenios_Bancolombia_Informes, porcentajes_Convenios_Bancolombia_Informes = grafica_registrosFisicos(rol, 'Convenios_Bancolombia_Informes')
        meses_Convenios_Bancolombia_Fisicos, porcentajes_Convenios_Bancolombia_Fisicos = grafica_registrosFisicos(rol, 'Convenios_Bancolombia_Fisicos')
        meses_Convenios_Bancolombia_Web, porcentajes_Convenios_Bancolombia_Web = grafica_registrosFisicos(rol, 'Convenios_Bancolombia_Web')
        #occidente
        meses_entregaFisicos_nacionales_occidente, porcentajes_entrega_fisicos_nacionales_occidente = grafica_registrosFisicos(rol, 'Nacionales_Occidente_Fisicos')
        meses_registrosMagneticos_nacionales_occidente, porcentajes_registrosMagneticos_nacionales_occidente = grafica_registrosFisicos(rol, 'Nacionales_Occidente_Magneticos')
        meses_entregaFisicos_Distritales_Occidente_Fisicos, porcentajes_entrega_fisicos_Distritales_Occidente_Fisicos = grafica_registrosFisicos(rol, 'Distritales_Occidente_Fisicos')
        meses_entregaFisicos_Distritales_Occidente_CMagneticas, porcentajes_entrega_fisicos_Distritales_Occidente_CMagneticas = grafica_registrosFisicos(rol, 'Distritales_Occidente_CMagneticas')
        #itau
        meses_entregaFisicos_nacionales_itau, porcentajes_entrega_fisicos_nacionales_itau = grafica_registrosFisicos(rol, 'Nacionales_Itau_Fisicos')
        meses_registrosMagneticos_nacionales_itau, porcentajes_registrosMagneticos_nacionales_itau = grafica_registrosFisicos(rol, 'Nacionales_Itau_Magneticos')
        meses_Departamentales_Itau_Fisicos, porcentajes_Departamentales_Itau_Fisicos = grafica_registrosFisicos(rol, 'Departamentales_Itau_Fisicos')
        meses_Departamentales_Itau_Informes, porcentajes_Departamentales_Itau_Informes = grafica_registrosFisicos(rol, 'Departamentales_Itau_Informes')
        meses_MunicipalesCali_Iatu_Fisicos, porcentajes_MunicipalesCali_Iatu_Fisicos = grafica_registrosFisicos(rol, 'MunicipalesCali_Iatu_Fisicos')
        meses_MunicipalesCali_Iatu_Informes, porcentajes_MunicipalesCali_Iatu_Informes = grafica_registrosFisicos(rol, 'MunicipalesCali_Iatu_Informes')
        #cajaSocial
        meses_entregaFisicos_nacionales_cajasocial, porcentajes_entrega_fisicos_nacionales_cajasocial = grafica_registrosFisicos(rol, 'Nacionales_CajaSocial_Fisicos')
        meses_registrosMagneticos_nacionales_cajasocial, porcentajes_registrosMagneticos_nacionales_cajasocial = grafica_registrosFisicos(rol, 'Nacionales_CajaSocial_Magneticos')
        meses_Nacionales_Aduanas_CajaSocial, procentajes_Nacionales_Aduanas_CajaSocial = grafica_registrosFisicos(rol, 'Nacionales_Aduanas_CajaSocial')
        meses_Convenios_CajaSocial_Informes, porcentajes_Convenios_CajaSocial_Informes = grafica_registrosFisicos(rol, 'Convenios_CajaSocial_Informes')
        meses_Convenios_CajaSocial_Fisicos, porcentajes_Convenios_CajaSocial_Fisicos = grafica_registrosFisicos(rol, 'Convenios_CajaSocial_Fisicos')
        meses_Convenios_CajaSocial_Web, porcentajes_Convenios_CajaSocial_Web = grafica_registrosFisicos(rol, 'Convenios_CajaSocial_Web')
        #davivienda
        meses_entrega_Nacionales_Informes_Davivienda, porcentajes_Nacionales_Informes_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_Informes_Davivienda')
        meses_Nacionales_CalidadInformes_Davivienda, porcentajes_Nacionales_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_CalidadInformes_Davivienda')
        meses_Nacionales_EntregaImagenes_Davivienda, porcentajes_Nacionales_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_EntregaImagenes_Davivienda')
        meses_Nacionales_Davivienda_Fisicos, porcentajes_Nacionales_Davivienda_Fisicos = grafica_registrosFisicos(rol, 'Nacionales_Davivienda_Fisicos')
        meses_Nacionales_Inconsistencias_Davivienda, porcentajes_Nacionales_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_Inconsistencias_Davivienda')
        meses_Nacionales_Traslados_Davivienda, porcentajes_Nacionales_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_Traslados_Davivienda')
        meses_entrega_Distritales_Informes_Davivienda, porcentajes_Distritales_Informes_Davivienda = grafica_registrosFisicos(rol, 'Distritales_Informes_Davivienda')
        meses_Distritales_CalidadInformes_Davivienda, porcentajes_Distritales_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Distritales_CalidadInformes_Davivienda')
        meses_Distritales_EntregaImagenes_Davivienda, porcentajes_Distritales_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Distritales_EntregaImagenes_Davivienda')
        meses_Distritales_Inconsistencias_Davivienda, porcentajes_Distritales_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Distritales_Inconsistencias_Davivienda')
        meses_Distritales_Traslados_Davivienda, porcentajes_Distritales_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Distritales_Traslados_Davivienda')
        meses_entrega_Departamentales_Informes_Davivienda, porcentajes_Departamentales_Informes_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_Informes_Davivienda')
        meses_Departamentales_CalidadInformes_Davivienda, porcentajes_Departamentales_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_CalidadInformes_Davivienda')
        meses_Departamentales_EntregaImagenes_Davivienda, porcentajes_Departamentales_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_EntregaImagenes_Davivienda')
        meses_Departamentales_Davivienda_Fisicos, porcentajes_Departamentales_Davivienda_Fisicos = grafica_registrosFisicos(rol, 'Departamentales_Davivienda_Fisicos')
        meses_Departamentales_Inconsistencias_Davivienda, porcentajes_Departamentales_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_Inconsistencias_Davivienda')
        meses_Departamentales_Traslados_Davivienda, porcentajes_Departamentales_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_Traslados_Davivienda')
        meses_entrega_Convenios_Informes_Davivienda, porcentajes_Convenios_Informes_Davivienda = grafica_registrosFisicos(rol, 'Convenios_Informes_Davivienda')
        meses_Convenios_CalidadInformes_Davivienda, porcentajes_Convenios_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Convenios_CalidadInformes_Davivienda')
        meses_Convenios_EntregaImagenes_Davivienda, porcentajes_Convenios_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Convenios_EntregaImagenes_Davivienda')
        meses_Convenios_Davivienda_Fisicos, porcentajes_Convenios_Davivienda_Fisicos = grafica_registrosFisicos(rol, 'Convenios_Davivienda_Fisicos')
        meses_Convenios_Inconsistencias_Davivienda, porcentajes_Convenios_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Convenios_Inconsistencias_Davivienda')
        meses_Convenios_Traslados_Davivienda, porcentajes_Convenios_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Convenios_Traslados_Davivienda')
        #avvillas
        meses_inconsistenciasPasivo, porcentajes_inconsistenciasPasivo = grafica_inconsitenciasPasivo(rol, 'complementacion_pasivo')
        meses_inconsistenciasActivo, porcentajes_inconsistenciasActivo = grafica_inconsitenciasPasivo(rol, 'complementacion_activo')
        meses_inconsistenciasrepsuestaTradicional, porcentajes_inconsistenciasrepsuestaTradicional = grafica_inconsitenciasPasivo(rol, 'complementacion_repsuestaTradicional')
        meses_inconsistenciasrepsuestaOCI, porcentajes_inconsistenciasrepsuestaOCI = grafica_inconsitenciasPasivo(rol, 'complementacion_repsuestaOCI')
        meses_repsuestaCrerditoOCI, tiempo_repsuestaCreditoOCI = grafica_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoOCI')
        meses_repsuestaCrerditoTradicional, tiempo_repsuestaCreditoTradicional = grafica_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoTradicional')
        meses_Radicacion_AvVillas_CalidadInformacion, porcentajes_Radicacion_AvVillas_CalidadInformacion = grafica_registrosFisicos(rol, 'Radicacion_AvVillas_CalidadInformacion')
        meses_Radicacion_AvVillas_Informes, porcentajes_Radicacion_AvVillas_Informes = grafica_registrosFisicos(rol, 'Radicacion_AvVillas_Informes')
        meses_Radicacion_AvVillas_Imagenes, porcentajes_Radicacion_AvVillas_Imagenes = grafica_registrosFisicos(rol, 'Radicacion_AvVillas_Imagenes')
        meses_entregaFisicos_TarjetasDigital, porcentajes_entrega_fisicos_TarjetasDigital = grafica_registrosFisicos(rol, 'TarjetasDigital')
        meses_entregaFisicos_TarjetasFisico, porcentajes_entrega_fisicos_TarjetasFisico = grafica_registrosFisicos(rol, 'TarjetasFisico')
        #aplica para todos los bancos
        meses_sancionesMagneticas, multas_sancionesMagneticas = grafica_sancionesMagneticas(rol)
        meses_sancionesFisicos, multas_sancionesFisicos = grafica_sancionesFisicos(rol)       
        '''ADMINISTRATIVO'''
        meses_administrativo_sistemas, porcentajes_administrativo_sistemas = grafica_Administrativo(rol, 'sistemas')
        meses_administrativo_tecnologia, porcentajes_administrativo_tecnologia = grafica_Administrativo(rol, 'tecnologia')
        meses_administrativo_financiera, porcentajes_administrativo_financiera = grafica_Administrativo(rol, 'financiera')
        meses_administrativo_comercial_propuestas, porcentajes_administrativo_comercial_propuestas = grafica_Administrativo(rol, 'comercial_propuestas')
        meses_administrativo_comercial_efectividad, porcentajes_administrativo_comercial_efectividad = grafica_Administrativo(rol, 'comercial_efectividad')
        meses_administrativo_comercial_pqr, porcentajes_administrativo_comercial_pqr = grafica_Administrativo(rol, 'comercial_pqr')
        meses_administrativo_TH_clima_organizacional, porcentajes_administrativo_TH_clima_organizacional = grafica_Administrativo(rol, 'TH_clima_organizacional')
        meses_administrativo_TH_Cumplimiento_Capacitaciones, porcentajes_administrativo_TH_Cumplimiento_Capacitaciones = grafica_Administrativo(rol, 'TH_Cumplimiento_Capacitaciones')
        meses_administrativo_TH_Eficacia_Capacitaciones, porcentajes_administrativo_TH_Eficacia_Capacitaciones = grafica_Administrativo(rol, 'TH_Eficacia_Capacitaciones')
        meses_administrativo_TH_Evaluacion_Desempeño, porcentajes_administrativo_TH_Evaluacion_Desempeño = grafica_Administrativo(rol, 'TH_Evaluacion_Desempeño')
        meses_administrativo_SGI_Acciones_Correctivas, porcentajes_administrativo_SGI_Acciones_Correctivas = grafica_Administrativo(rol, 'SGI_Acciones_Correctivas')
        meses_administrativo_SGI_Continuidad_Negocio, porcentajes_administrativo_SGI_Continuidad_Negocio = grafica_Administrativo(rol, 'SGI_Continuidad_Negocio')
        meses_administrativo_SGI_Incidentes_Seguridad, porcentajes_administrativo_SGI_Incidentes_Seguridad = grafica_Administrativo(rol, 'SGI_Incidentes_Seguridad')
        meses_administrativo_SGI_Producto_No_Conforme, porcentajes_administrativo_SGI_Producto_No_Conforme = grafica_Administrativo(rol, 'SGI_Producto_No_Conforme')
        meses_administrativo_SGI_Riesgos, porcentajes_administrativo_SGI_Riesgos = grafica_Administrativo(rol, 'SGI_Riesgos')
        return {
            #agrario
            'meses_calidadInformacion_nacionales_agrario': meses_calidadInformacion_nacionales_agrario,
            'porcentajes_calidadInformacion_nacionales_agrario': porcentajes_calidadInformacion_nacionales_agrario,
            'meses_registrosMagneticos_nacionales_agrario': meses_registrosMagneticos_nacionales_agrario,
            'porcentajes_registrosMagneticos_nacionales_agrario': porcentajes_registrosMagneticos_nacionales_agrario,
            #bancolombia
            'meses_entregaFisicos_nacionales_bancolombia': meses_entregaFisicos_nacionales_bancolombia,
            'porcentajes_entrega_fisicos_nacionales_bancolombia': porcentajes_entrega_fisicos_nacionales_bancolombia,
            'meses_registrosMagneticos_nacionales_bancolombia': meses_registrosMagneticos_nacionales_bancolombia,
            'porcentajes_registrosMagneticos_nacionales_bancolombia': porcentajes_registrosMagneticos_nacionales_bancolombia,
            'meses_entregaFisicos_Distritales_Bancolombia_Fisicos': meses_entregaFisicos_Distritales_Bancolombia_Fisicos,
            'porcentajes_entrega_fisicos_Distritales_Bancolombia_Fisicos': porcentajes_entrega_fisicos_Distritales_Bancolombia_Fisicos,
            'meses_entregaFisicos_Distritales_Bancolombia_CMagneticas': meses_entregaFisicos_Distritales_Bancolombia_CMagneticas,
            'porcentajes_entrega_fisicos_Distritales_Bancolombia_CMagneticas': porcentajes_entrega_fisicos_Distritales_Bancolombia_CMagneticas,
            'meses_entrega_Departamentales_Bancolombia_informes': meses_entrega_Departamentales_Bancolombia_informes,
            'porcentajes_Departamentales_Bancolombia_informes': porcentajes_Departamentales_Bancolombia_informes,
            'meses_Convenios_Bancolombia_Informes': meses_Convenios_Bancolombia_Informes,
            'porcentajes_Convenios_Bancolombia_Informes': porcentajes_Convenios_Bancolombia_Informes,
            'meses_Convenios_Bancolombia_Fisicos': meses_Convenios_Bancolombia_Fisicos,
            'porcentajes_Convenios_Bancolombia_Fisicos': porcentajes_Convenios_Bancolombia_Fisicos,
            'meses_Convenios_Bancolombia_Web': meses_Convenios_Bancolombia_Web,
            'porcentajes_Convenios_Bancolombia_Web': porcentajes_Convenios_Bancolombia_Web,
            #occiedente
            'meses_entregaFisicos_nacionales_occidente': meses_entregaFisicos_nacionales_occidente,
            'porcentajes_entrega_fisicos_nacionales_occidente': porcentajes_entrega_fisicos_nacionales_occidente,
            'meses_registrosMagneticos_nacionales_occidente': meses_registrosMagneticos_nacionales_occidente,
            'porcentajes_registrosMagneticos_nacionales_occidente': porcentajes_registrosMagneticos_nacionales_occidente,
            'meses_entregaFisicos_Distritales_Occidente_Fisicos': meses_entregaFisicos_Distritales_Occidente_Fisicos,
            'porcentajes_entrega_fisicos_Distritales_Occidente_Fisicos': porcentajes_entrega_fisicos_Distritales_Occidente_Fisicos,
            'meses_entregaFisicos_Distritales_Occidente_CMagneticas': meses_entregaFisicos_Distritales_Occidente_CMagneticas,
            'porcentajes_entrega_fisicos_Distritales_Occidente_CMagneticas': porcentajes_entrega_fisicos_Distritales_Occidente_CMagneticas,
            #itau
            'meses_entregaFisicos_nacionales_itau': meses_entregaFisicos_nacionales_itau,
            'porcentajes_entrega_fisicos_nacionales_itau': porcentajes_entrega_fisicos_nacionales_itau,
            'meses_registrosMagneticos_nacionales_itau': meses_registrosMagneticos_nacionales_itau,
            'porcentajes_registrosMagneticos_nacionales_itau': porcentajes_registrosMagneticos_nacionales_itau,
            'meses_Departamentales_Itau_Fisicos': meses_Departamentales_Itau_Fisicos,
            'porcentajes_Departamentales_Itau_Fisicos': porcentajes_Departamentales_Itau_Fisicos,
            'meses_Departamentales_Itau_Informes': meses_Departamentales_Itau_Informes,
            'porcentajes_Departamentales_Itau_Informes': porcentajes_Departamentales_Itau_Informes,
            'meses_MunicipalesCali_Iatu_Fisicos': meses_MunicipalesCali_Iatu_Fisicos,
            'porcentajes_MunicipalesCali_Iatu_Fisicos': porcentajes_MunicipalesCali_Iatu_Fisicos,
            'meses_MunicipalesCali_Iatu_Informes': meses_MunicipalesCali_Iatu_Informes,
            'porcentajes_MunicipalesCali_Iatu_Informes': porcentajes_MunicipalesCali_Iatu_Informes,
            #cajaSocial
            'meses_entregaFisicos_nacionales_cajasocial': meses_entregaFisicos_nacionales_cajasocial,
            'porcentajes_entrega_fisicos_nacionales_cajasocial': porcentajes_entrega_fisicos_nacionales_cajasocial,
            'meses_registrosMagneticos_nacionales_cajasocial': meses_registrosMagneticos_nacionales_cajasocial,
            'porcentajes_registrosMagneticos_nacionales_cajasocial': porcentajes_registrosMagneticos_nacionales_cajasocial,
            'meses_Nacionales_Aduanas_CajaSocial': meses_Nacionales_Aduanas_CajaSocial,
            'procentajes_Nacionales_Aduanas_CajaSocial': procentajes_Nacionales_Aduanas_CajaSocial,
            'meses_Convenios_CajaSocial_Informes': meses_Convenios_CajaSocial_Informes,
            'porcentajes_Convenios_CajaSocial_Informes': porcentajes_Convenios_CajaSocial_Informes,
            'meses_Convenios_CajaSocial_Fisicos': meses_Convenios_CajaSocial_Fisicos,
            'porcentajes_Convenios_CajaSocial_Fisicos': porcentajes_Convenios_CajaSocial_Fisicos,
            'meses_Convenios_CajaSocial_Web': meses_Convenios_CajaSocial_Web,
            'porcentajes_Convenios_CajaSocial_Web': porcentajes_Convenios_CajaSocial_Web,
            #davivienda
            'meses_entrega_Nacionales_Informes_Davivienda': meses_entrega_Nacionales_Informes_Davivienda,
            'porcentajes_Nacionales_Informes_Davivienda': porcentajes_Nacionales_Informes_Davivienda,
            'meses_Nacionales_CalidadInformes_Davivienda': meses_Nacionales_CalidadInformes_Davivienda,
            'porcentajes_Nacionales_CalidadInformes_Davivienda': porcentajes_Nacionales_CalidadInformes_Davivienda,
            'meses_Nacionales_EntregaImagenes_Davivienda': meses_Nacionales_EntregaImagenes_Davivienda,
            'porcentajes_Nacionales_EntregaImagenes_Davivienda': porcentajes_Nacionales_EntregaImagenes_Davivienda,
            'meses_Nacionales_Davivienda_Fisicos': meses_Nacionales_Davivienda_Fisicos,
            'porcentajes_Nacionales_Davivienda_Fisicos': porcentajes_Nacionales_Davivienda_Fisicos,
            'meses_Nacionales_Inconsistencias_Davivienda': meses_Nacionales_Inconsistencias_Davivienda,
            'porcentajes_Nacionales_Inconsistencias_Davivienda': porcentajes_Nacionales_Inconsistencias_Davivienda,
            'meses_Nacionales_Traslados_Davivienda': meses_Nacionales_Traslados_Davivienda,
            'porcentajes_Nacionales_Traslados_Davivienda': porcentajes_Nacionales_Traslados_Davivienda,
            'meses_entrega_Distritales_Informes_Davivienda': meses_entrega_Distritales_Informes_Davivienda,
            'porcentajes_Distritales_Informes_Davivienda': porcentajes_Distritales_Informes_Davivienda,
            'meses_Distritales_CalidadInformes_Davivienda': meses_Distritales_CalidadInformes_Davivienda,
            'porcentajes_Distritales_CalidadInformes_Davivienda': porcentajes_Distritales_CalidadInformes_Davivienda,
            'meses_Distritales_EntregaImagenes_Davivienda': meses_Distritales_EntregaImagenes_Davivienda,
            'porcentajes_Distritales_EntregaImagenes_Davivienda': porcentajes_Distritales_EntregaImagenes_Davivienda,
            'meses_Distritales_Inconsistencias_Davivienda': meses_Distritales_Inconsistencias_Davivienda,
            'porcentajes_Distritales_Inconsistencias_Davivienda': porcentajes_Distritales_Inconsistencias_Davivienda,
            'meses_Distritales_Traslados_Davivienda': meses_Distritales_Traslados_Davivienda,
            'porcentajes_Distritales_Traslados_Davivienda': porcentajes_Distritales_Traslados_Davivienda,
            'meses_entrega_Departamentales_Informes_Davivienda': meses_entrega_Departamentales_Informes_Davivienda,
            'porcentajes_Departamentales_Informes_Davivienda': porcentajes_Departamentales_Informes_Davivienda,
            'meses_Departamentales_CalidadInformes_Davivienda': meses_Departamentales_CalidadInformes_Davivienda,
            'porcentajes_Departamentales_CalidadInformes_Davivienda': porcentajes_Departamentales_CalidadInformes_Davivienda,
            'meses_Departamentales_EntregaImagenes_Davivienda': meses_Departamentales_EntregaImagenes_Davivienda,
            'porcentajes_Departamentales_EntregaImagenes_Davivienda': porcentajes_Departamentales_EntregaImagenes_Davivienda,
            'meses_Departamentales_Davivienda_Fisicos': meses_Departamentales_Davivienda_Fisicos,
            'porcentajes_Departamentales_Davivienda_Fisicos': porcentajes_Departamentales_Davivienda_Fisicos,
            'meses_Departamentales_Inconsistencias_Davivienda': meses_Departamentales_Inconsistencias_Davivienda,
            'porcentajes_Departamentales_Inconsistencias_Davivienda': porcentajes_Departamentales_Inconsistencias_Davivienda,
            'meses_Departamentales_Traslados_Davivienda': meses_Departamentales_Traslados_Davivienda,
            'porcentajes_Departamentales_Traslados_Davivienda': porcentajes_Departamentales_Traslados_Davivienda,
            'meses_entrega_Convenios_Informes_Davivienda': meses_entrega_Convenios_Informes_Davivienda,
            'porcentajes_Convenios_Informes_Davivienda': porcentajes_Convenios_Informes_Davivienda,
            'meses_Convenios_CalidadInformes_Davivienda': meses_Convenios_CalidadInformes_Davivienda,
            'porcentajes_Convenios_CalidadInformes_Davivienda': porcentajes_Convenios_CalidadInformes_Davivienda,
            'meses_Convenios_EntregaImagenes_Davivienda': meses_Convenios_EntregaImagenes_Davivienda,
            'porcentajes_Convenios_EntregaImagenes_Davivienda': porcentajes_Convenios_EntregaImagenes_Davivienda,
            'meses_Convenios_Davivienda_Fisicos': meses_Convenios_Davivienda_Fisicos,
            'porcentajes_Convenios_Davivienda_Fisicos': porcentajes_Convenios_Davivienda_Fisicos,
            'meses_Convenios_Inconsistencias_Davivienda': meses_Convenios_Inconsistencias_Davivienda,
            'porcentajes_Convenios_Inconsistencias_Davivienda': porcentajes_Convenios_Inconsistencias_Davivienda,
            'meses_Convenios_Traslados_Davivienda': meses_Convenios_Traslados_Davivienda,
            'porcentajes_Convenios_Traslados_Davivienda': porcentajes_Convenios_Traslados_Davivienda,
            #avvillas
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
            'meses_Radicacion_AvVillas_CalidadInformacion': meses_Radicacion_AvVillas_CalidadInformacion,
            'porcentajes_Radicacion_AvVillas_CalidadInformacion': porcentajes_Radicacion_AvVillas_CalidadInformacion,
            'meses_Radicacion_AvVillas_Informes': meses_Radicacion_AvVillas_Informes,
            'porcentajes_Radicacion_AvVillas_Informes': porcentajes_Radicacion_AvVillas_Informes,
            'meses_Radicacion_AvVillas_Imagenes': meses_Radicacion_AvVillas_Imagenes,
            'porcentajes_Radicacion_AvVillas_Imagenes': porcentajes_Radicacion_AvVillas_Imagenes,
            'meses_entregaFisicos_TarjetasDigital': meses_entregaFisicos_TarjetasDigital,
            'porcentajes_entrega_fisicos_TarjetasDigital': porcentajes_entrega_fisicos_TarjetasDigital,
            'meses_entregaFisicos_TarjetasFisico': meses_entregaFisicos_TarjetasFisico,
            'porcentajes_entrega_fisicos_TarjetasFisico': porcentajes_entrega_fisicos_TarjetasFisico,
            #aplica para todos los bancos
            'meses_sancionesMagneticas': meses_sancionesMagneticas,
            'multas_sancionesMagneticas': multas_sancionesMagneticas,
            'meses_sancionesFisicos': meses_sancionesFisicos,
            'multas_sancionesFisicos': multas_sancionesFisicos,
            #administrativo
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
    print(lista_registrosFisicos(rol, 'Nacionales_Agrario_CalidadInformacion'))   
    return render_template('indicadores/indicadores.html', **CONTEXTO(), **CONTEXTO_GRAFICA())

@ind_bp.route('/limpiar_rol_seleccionado', methods=['POST'])
@login_required
def limpiar_rol_seleccionado():
    """Limpia la sesión del rol seleccionado y vuelve al rol por defecto del usuario"""
    try:
        # Limpiar la sesión del rol seleccionado
        if 'selected_rol' in session:
            session.pop('selected_rol', None)
        
        return jsonify({'success': True, 'message': 'Rol seleccionado limpiado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


'''GESTION DE PRODUCCIOIN'''


@ind_bp.route('/registro_extemporaneo', methods=['POST'])
def obtener_registro_extemporaneo():
    mes = request.json.get('mes')
    proceso = request.json.get('proceso')
    rol = session.get('selected_rol', current_user.rol)
    resultado = obtener_r_extemporeaneo_mes(mes, rol, proceso)
    if resultado:
        return jsonify({'r_extemporaneo': resultado[0],
                        't_registros': resultado[1]})
    else:
        return jsonify({'r_extemporaneo': 0,
                        't_registros': 0})
@ind_bp.route('/registro_extemporaneo_fisico', methods=['POST'])
def registro_extemporaneo_fisico():
    mes = request.json.get('mes')
    proceso = request.json.get('proceso')
    rol = session.get('selected_rol', current_user.rol)
    resultado = obtener_r_extemporeaneoFisico_mes(mes, rol, proceso)
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
        try:
            # Leemos los nombres EXACTOS del formulario de Sanciones Magnéticas
            valor_porcentaje = request.form.get('P_aceptacion', '0').replace('%', '').replace(',', '.')
            valor_uvt = request.form.get('UVT_sancionesMagneticas', '0').replace('$', '').replace('.', '').replace(',', '.')
            valor_multa = request.form.get('multa_sancionesMagneticas', '0').replace('$', '').replace('.', '').replace(',', '.')
            
            # Creamos el diccionario 'datos' con las claves que espera el controlador
            datos = {
                'mes': request.form.get('mes2', ''),
                'R_extemporaneos': request.form.get('R_extemporaneos2', '0'),
                'r_digicom': request.form.get('r_digicom', '0'),
                'P_aceptacion': valor_porcentaje,
                'resultado': request.form.get('resultado_sancionesMagneticas', '0.0'),
                'meta': request.form.get('meta_sancionesMagneticas', ''),
                'uvt': valor_uvt,
                'multa': valor_multa,
                'analisis': request.form.get('analisis_sancionesMagneticas', '')
            }
            rol = session.get('selected_rol', current_user.rol)
            guardar_sancionesMagneticas(datos, rol)
            
            return jsonify({
                'success': True,
                'message': 'Indicador de Sanciones Magnéticas guardado exitosamente',
                'newData': datos 
            })
        except Exception as e:
            print(f"ERROR en guardar_sanciones_magneticas: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})
@ind_bp.route('/guardar_sanciones_fisicos', methods=['POST'])
@login_required
def guardar_sanciones_fisicos():
    if request.method == 'POST':
        try:
            # Leemos los nombres EXACTOS del formulario de Sanciones Físicas
            valor_porcentaje = request.form.get('P_aceptacion_fisicos', '0').replace('%', '').replace(',', '.')
            valor_uvt = request.form.get('UVT_sancionesFisicos', '0').replace('$', '').replace('.', '').replace(',', '.')
            valor_multa = request.form.get('multa_sancionesFisicos', '0').replace('$', '').replace('.', '').replace(',', '.')
            
            # Creamos el diccionario 'datos' con las claves que espera el controlador
            datos = {
                'mes': request.form.get('mes_fisicos', ''),
                'D_extemporaneos2': request.form.get('D_extemporaneos2', '0'),
                'dr_digicom': request.form.get('dr_digicom', '0'),
                'P_aceptacion_fisicos': valor_porcentaje,
                'resultado_sancionesFisicos': request.form.get('resultado_sancionesFisicos', '0.0'),
                'meta_sancionesFisicos': request.form.get('meta_sancionesFisicos', ''),
                'uvt_sancionesFisicos': valor_uvt,
                'multa_sancionesFisicos': valor_multa,
                'analisis_sancionesFisicos': request.form.get('analisis_sancionesFisicos', '')
            }
            rol = session.get('selected_rol', current_user.rol)
            guardar_sancionesFisicos(datos, rol)
            
            return jsonify({
                'success': True,
                'message': 'Indicador de Sanciones Físicos guardado exitosamente', 
                'newData': datos 
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})
@ind_bp.route('/guardar_entrega_fisicos', methods=['POST'])
@login_required
def guardar_entrega_fisicos():
    if request.method == 'POST':
        try:
            datos = {
                'mes': request.form['mes'],
                'documentos_entregados': request.form['doc_entregados'],
                'documentos_extemporaneos': request.form['doc_extemporaneos'],
                'resultado': request.form['resultado_entrgeaFisicos'],
                'meta': request.form['meta_entregaFisicos'],
                'analisis': request.form['analisis_entregaFisicos'],
                'proceso': request.form['proceso']
            }
            rol = session.get('selected_rol', current_user.rol)
            guardar_registrosFisicos(datos, rol)

            return jsonify({'success': True, 'message': 'Indicador guardado correctamente', 'newData': datos})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al guardar: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})
@ind_bp.route('/guardar_inconsistencias_pasivo', methods=['POST'])
@login_required
def guardar_inconsistencias_pasivo():
    if request.method == 'POST':
        try:
            datos = {
                'mes': request.form['mes'],
                't_casos': request.form['t_casos'],
                'e_grabacion_analisis': request.form['e_grabacion_analisis'],
                'resultado': request.form['resultado_inconsistenciasPasivo'],
                'meta': request.form['meta_inconsistenciasPasivo'],
                'analisis': request.form['analisis_inconsistenciasPasivo'],
                'proceso': request.form['proceso']
            }
            rol = session.get('selected_rol', current_user.rol)
            guardar_inconsitenciasPasivo(datos, rol)
            return jsonify({'success': True, 'message': 'Indicador guardado correctamente', 'newData': datos })
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al guardar: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})
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
        try:
            datos = {
                'mes': request.form['mes_TRespuesta'],
                't_creditos': request.form['t_creditos'],
                't_respuesta': t_segundos_respuesta,
                'resultado': t_segundos_resultado,
                'analisis': request.form['Analisis_TRespuesta'],
                'proceso': request.form['proceso']
            }
            rol = session.get('selected_rol', current_user.rol)
            #print(datos)
            guardar_TRespuesta_credito(datos, rol)
            return jsonify({'success': True, 'message': 'Indicador guardado correctamente', 'newData': datos})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al guardar: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})
@ind_bp.route('/get_tiempo_mes_anterior', methods=['GET'])
def get_tiempo_mes_anterior():
    proceso = request.args.get('proceso')
    mes = request.args.get(f'mes')
    rol = session.get('selected_rol', current_user.rol)
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

'''ADMINISTRATIVO'''
@ind_bp.route('/guardar_administrativo', methods=['POST'])
@login_required
def guardar_administrativo():
    if request.method == 'POST':
        try:
            datos = {
                'mes': request.form['mes'],
                'Sol_atendidas': request.form['Sol_atendidas'],
                'Sol_realizadas': request.form['Sol_realizadas'],
                'resultado': request.form['resultado_administrativo'],
                'meta': request.form['meta_administrativo'],
                'analisis': request.form['analisis_administrativo'],
                'proceso': request.form['proceso']
            }
            rol = session.get('selected_rol', current_user.rol)
            guardar_Administrativo(datos, rol)
            return jsonify({'success': True, 'message': 'Indicador guardado correctamente', 'newData': datos})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al guardar: {str(e)}'})
    return jsonify({'success': False, 'message': 'Método no permitido'})

@ind_bp.route('/indicadores/<int:role_id>')
@login_required
def indicadores_por_rol(role_id):
    session['selected_rol'] = role_id
    rol = role_id
    def CONTEXTO():
        
        nombre_del_rol = nombre_rol(rol)
        procesos = PROCESOS_ROL.get(rol, [])
        imagen_rol = ROL_IMAGES.get(rol, 'imgs/user.png')
        '''GESTION DE PRODUCCION'''
        uvt_valor = uvt_rol(rol)

        #agrario
        datos_calidadInformacion_nacionales_agrario = lista_registrosFisicos(rol, 'Nacionales_Agrario_CalidadInformacion')
        datos_registrosMagneticos_nacionales_agrario = lista_registrosFisicos(rol, 'Nacionales_Agrario_RegistrosMagneticos')
        #bancolombia
        datos_entrega_fisicos_nacionales_bancolombia = lista_registrosFisicos(rol, 'Nacionales_Bancolombia_Fisicos')
        datos_registrosMagneticos_nacionales_bancolombia = lista_registrosFisicos(rol, 'Nacionales_Bancolombia_Magneticos')
        datos_entrega_fisicos_Distritales_Bancolombia_Fisicos = lista_registrosFisicos(rol, 'Distritales_Bancolombia_Fisicos')
        datos_entrega_fisicos_Distritales_Bancolombia_CMagneticas = lista_registrosFisicos(rol, 'Distritales_Bancolombia_CMagneticas')
        datos_Departamentales_Bancolombia_informes = lista_registrosFisicos(rol, 'Departamentales_Bancolombia_informes')
        datos_Convenios_Bancolombia_Informes = lista_registrosFisicos(rol, 'Convenios_Bancolombia_Informes')
        datos_Convenios_Bancolombia_Fisicos = lista_registrosFisicos(rol, 'Convenios_Bancolombia_Fisicos')
        datos_Convenios_Bancolombia_Web = lista_registrosFisicos(rol, 'Convenios_Bancolombia_Web')
        #occidnete
        datos_entrega_fisicos_nacionales_occidente = lista_registrosFisicos(rol, 'Nacionales_Occidente_Fisicos')
        datos_registrosMagneticos_nacionales_occidente = lista_registrosFisicos(rol, 'Nacionales_Occidente_Magneticos')
        datos_entrega_fisicos_Distritales_Occidente_Fisicos = lista_registrosFisicos(rol, 'Distritales_Occidente_Fisicos')
        datos_entrega_fisicos_Distritales_Occidente_CMagneticas = lista_registrosFisicos(rol, 'Distritales_Occidente_CMagneticas')
        #itau
        datos_entrega_fisicos_nacionales_itau = lista_registrosFisicos(rol, 'Nacionales_Itau_Fisicos')
        datos_registrosMagneticos_nacionales_itau = lista_registrosFisicos(rol, 'Nacionales_Itau_Magneticos')
        datos_Departamentales_Itau_Fisicos = lista_registrosFisicos(rol, 'Departamentales_Itau_Fisicos')
        datos_Departamentales_Itau_Informes = lista_registrosFisicos(rol, 'Departamentales_Itau_Informes')
        datos_MunicipalesCali_Iatu_Fisicos = lista_registrosFisicos(rol, 'MunicipalesCali_Iatu_Fisicos')
        datos_MunicipalesCali_Iatu_Informes = lista_registrosFisicos(rol, 'MunicipalesCali_Iatu_Informes')
        #cajasocial
        datos_entrega_fisicos_nacionales_cajasocial = lista_registrosFisicos(rol, 'Nacionales_CajaSocial_Fisicos')
        datos_registrosMagneticos_nacionales_cajasocial = lista_registrosFisicos(rol, 'Nacionales_CajaSocial_Magneticos')
        datos_Nacionales_Aduanas_CajaSocial = lista_registrosFisicos(rol, 'Nacionales_Aduanas_CajaSocial')
        datos_Convenios_CajaSocial_Informes = lista_registrosFisicos(rol, 'Convenios_CajaSocial_Informes')
        datos_Convenios_CajaSocial_Fisicos = lista_registrosFisicos(rol, 'Convenios_CajaSocial_Fisicos')
        datos_Convenios_CajaSocial_Web = lista_registrosFisicos(rol, 'Convenios_CajaSocial_Web')
        #davivienda
        datos_Nacionales_Informes_Davivienda = lista_registrosFisicos(rol, 'Nacionales_Informes_Davivienda')
        datos_Nacionales_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Nacionales_CalidadInformes_Davivienda')
        datos_Nacionales_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Nacionales_EntregaImagenes_Davivienda')
        datos_Nacionales_Davivienda_Fisicos = lista_registrosFisicos(rol, 'Nacionales_Davivienda_Fisicos')
        datos_Nacionales_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Nacionales_Inconsistencias_Davivienda')
        datos_Nacionales_Traslados_Davivienda = lista_registrosFisicos(rol, 'Nacionales_Traslados_Davivienda')
        datos_Distritales_Informes_Davivienda = lista_registrosFisicos(rol, 'Distritales_Informes_Davivienda')
        datos_Distritales_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Distritales_CalidadInformes_Davivienda')
        datos_Distritales_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Distritales_EntregaImagenes_Davivienda')
        datos_Distritales_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Distritales_Inconsistencias_Davivienda')
        datos_Distritales_Traslados_Davivienda = lista_registrosFisicos(rol, 'Distritales_Traslados_Davivienda')
        datos_Departamentales_Informes_Davivienda = lista_registrosFisicos(rol, 'Departamentales_Informes_Davivienda')
        datos_Departamentales_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Departamentales_CalidadInformes_Davivienda')
        datos_Departamentales_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Departamentales_EntregaImagenes_Davivienda')
        datos_Departamentales_Davivienda_Fisicos = lista_registrosFisicos(rol, 'Departamentales_Davivienda_Fisicos')
        datos_Departamentales_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Departamentales_Inconsistencias_Davivienda')
        datos_Departamentales_Traslados_Davivienda = lista_registrosFisicos(rol, 'Departamentales_Traslados_Davivienda')
        datos_Convenios_Informes_Davivienda = lista_registrosFisicos(rol, 'Convenios_Informes_Davivienda')
        datos_Convenios_CalidadInformes_Davivienda = lista_registrosFisicos(rol, 'Convenios_CalidadInformes_Davivienda')
        datos_Convenios_EntregaImagenes_Davivienda = lista_registrosFisicos(rol, 'Convenios_EntregaImagenes_Davivienda')
        datos_Convenios_Davivienda_Fisicos = lista_registrosFisicos(rol, 'Convenios_Davivienda_Fisicos')
        datos_Convenios_Inconsistencias_Davivienda = lista_registrosFisicos(rol, 'Convenios_Inconsistencias_Davivienda')
        datos_Convenios_Traslados_Davivienda = lista_registrosFisicos(rol, 'Convenios_Traslados_Davivienda')
        #avvillas
        datos_inconsistencias_pasivo = lista_inconsitenciasPasivo(rol, 'complementacion_pasivo')
        datos_inconsistencias_activo = lista_inconsitenciasPasivo(rol, 'complementacion_activo')
        datos_inconsistencias_repsuestaTradicional = lista_inconsitenciasPasivo(rol, 'complementacion_repsuestaTradicional')
        datos_inconsistencias_repsuestaOCI = lista_inconsitenciasPasivo(rol, 'complementacion_repsuestaOCI')
        datos_repsuestaCreditoOCI = lista_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoOCI')
        datos_repsuestaCreditoTradicional = lista_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoTradicional')
        datos_Radicacion_AvVillas_CalidadInformacion = lista_registrosFisicos(rol, 'Radicacion_AvVillas_CalidadInformacion')
        datos_Radicacion_AvVillas_Informes = lista_registrosFisicos(rol, 'Radicacion_AvVillas_Informes')
        datos_Radicacion_AvVillas_Imagenes = lista_registrosFisicos(rol, 'Radicacion_AvVillas_Imagenes')
        datos_entrega_fisicos_TarjetasDigital = lista_registrosFisicos(rol, 'TarjetasDigital')
        datos_entrega_fisicos_TarjetasFisico = lista_registrosFisicos(rol, 'TarjetasFisico')
        #aplica para to0dos los bancos
        datos_sancionesMagneticas = lista_sancionesMagenticas(rol)
        datos_sancionesFisicos = lista_sancionesFisicos(rol)
        

        '''ADMINISTRATIVO'''
        datos_administrativo_sistemas = lista_Administrativo(rol, 'sistemas')
        datos_administrativo_tecnologia = lista_Administrativo(rol, 'tecnologia')
        datos_administrativo_financiera = lista_Administrativo(rol, 'financiera')
        datos_administrativo_comercial_propuestas = lista_Administrativo(rol, 'comercial_propuestas')
        datos_administrativo_comercial_efectividad = lista_Administrativo(rol, 'comercial_efectividad')
        datos_administrativo_comercial_pqr = lista_Administrativo(rol, 'comercial_pqr')
        datos_administrativo_TH_clima_organizacional = lista_Administrativo(rol, 'TH_clima_organizacional')
        datos_administrativo_TH_Cumplimiento_Capacitaciones = lista_Administrativo(rol, 'TH_Cumplimiento_Capacitaciones')
        datos_administrativo_TH_Eficacia_Capacitaciones = lista_Administrativo(rol, 'TH_Eficacia_Capacitaciones')
        datos_administrativo_TH_Evaluacion_Desempeño = lista_Administrativo(rol, 'TH_Evaluacion_Desempeño')
        datos_administrativo_SGI_Acciones_Correctivas = lista_Administrativo(rol, 'SGI_Acciones_Correctivas')
        datos_administrativo_SGI_Continuidad_Negocio = lista_Administrativo(rol, 'SGI_Continuidad_Negocio')
        datos_administrativo_SGI_Incidentes_Seguridad = lista_Administrativo(rol, 'SGI_Incidentes_Seguridad')
        datos_administrativo_SGI_Producto_No_Conforme = lista_Administrativo(rol, 'SGI_Producto_No_Conforme')
        datos_administrativo_SGI_Riesgos = lista_Administrativo(rol, 'SGI_Riesgos')
        return {
            'uvt_valor': uvt_valor,
            'imagen_rol': imagen_rol,
            'rol_seleccionado': rol,
            'nombre_rol_seleccionado': nombre_del_rol,
            'is_especific_role': True,
            'is_role_override': True,
            #agrario
            'datos_calidadInformacion_nacionales_agrario': datos_calidadInformacion_nacionales_agrario,
            'datos_registrosMagneticos_nacionales_agrario': datos_registrosMagneticos_nacionales_agrario,
            #bancolombia
            'datos_entrega_fisicos_nacionales_bancolombia': datos_entrega_fisicos_nacionales_bancolombia,
            'datos_registrosMagneticos_nacionales_bancolombia': datos_registrosMagneticos_nacionales_bancolombia,
            'datos_entrega_fisicos_Distritales_Bancolombia_Fisicos': datos_entrega_fisicos_Distritales_Bancolombia_Fisicos,
            'datos_entrega_fisicos_Distritales_Bancolombia_CMagneticas': datos_entrega_fisicos_Distritales_Bancolombia_CMagneticas,
            'datos_Departamentales_Bancolombia_informes': datos_Departamentales_Bancolombia_informes,
            'datos_Convenios_Bancolombia_Informes': datos_Convenios_Bancolombia_Informes,
            'datos_Convenios_Bancolombia_Fisicos': datos_Convenios_Bancolombia_Fisicos,
            'datos_Convenios_Bancolombia_Web': datos_Convenios_Bancolombia_Web,
            #occidente
            'datos_entrega_fisicos_nacionales_occidente': datos_entrega_fisicos_nacionales_occidente,
            'datos_registrosMagneticos_nacionales_occidente': datos_registrosMagneticos_nacionales_occidente,
            'datos_entrega_fisicos_Distritales_Occidente_Fisicos': datos_entrega_fisicos_Distritales_Occidente_Fisicos,
            'datos_entrega_fisicos_Distritales_Occidente_CMagneticas': datos_entrega_fisicos_Distritales_Occidente_CMagneticas,
            #itau
            'datos_entrega_fisicos_nacionales_itau': datos_entrega_fisicos_nacionales_itau,
            'datos_registrosMagneticos_nacionales_itau': datos_registrosMagneticos_nacionales_itau,
            'datos_Departamentales_Itau_Fisicos': datos_Departamentales_Itau_Fisicos,
            'datos_Departamentales_Itau_Informes': datos_Departamentales_Itau_Informes,
            'datos_MunicipalesCali_Iatu_Fisicos': datos_MunicipalesCali_Iatu_Fisicos,
            'datos_MunicipalesCali_Iatu_Informes': datos_MunicipalesCali_Iatu_Informes,
            #cajaSocial
            'datos_entrega_fisicos_nacionales_cajasocial': datos_entrega_fisicos_nacionales_cajasocial,
            'datos_registrosMagneticos_nacionales_cajasocial': datos_registrosMagneticos_nacionales_cajasocial,
            'datos_Nacionales_Aduanas_CajaSocial': datos_Nacionales_Aduanas_CajaSocial,
            'datos_Convenios_CajaSocial_Informes': datos_Convenios_CajaSocial_Informes,
            'datos_Convenios_CajaSocial_Fisicos': datos_Convenios_CajaSocial_Fisicos,
            'datos_Convenios_CajaSocial_Web': datos_Convenios_CajaSocial_Web,
            #davivienda
            'datos_Nacionales_Informes_Davivienda': datos_Nacionales_Informes_Davivienda,
            'datos_Nacionales_CalidadInformes_Davivienda': datos_Nacionales_CalidadInformes_Davivienda,
            'datos_Nacionales_EntregaImagenes_Davivienda': datos_Nacionales_EntregaImagenes_Davivienda,
            'datos_Nacionales_Davivienda_Fisicos': datos_Nacionales_Davivienda_Fisicos,
            'datos_Nacionales_Inconsistencias_Davivienda': datos_Nacionales_Inconsistencias_Davivienda,
            'datos_Nacionales_Traslados_Davivienda': datos_Nacionales_Traslados_Davivienda,
            'datos_Distritales_Informes_Davivienda': datos_Distritales_Informes_Davivienda,
            'datos_Distritales_CalidadInformes_Davivienda': datos_Distritales_CalidadInformes_Davivienda,
            'datos_Distritales_EntregaImagenes_Davivienda': datos_Distritales_EntregaImagenes_Davivienda,
            'datos_Distritales_Inconsistencias_Davivienda': datos_Distritales_Inconsistencias_Davivienda,
            'datos_Distritales_Traslados_Davivienda': datos_Distritales_Traslados_Davivienda,
            'datos_Departamentales_Informes_Davivienda': datos_Departamentales_Informes_Davivienda,
            'datos_Departamentales_CalidadInformes_Davivienda': datos_Departamentales_CalidadInformes_Davivienda,
            'datos_Departamentales_EntregaImagenes_Davivienda': datos_Departamentales_EntregaImagenes_Davivienda,
            'datos_Departamentales_Davivienda_Fisicos': datos_Departamentales_Davivienda_Fisicos,
            'datos_Departamentales_Inconsistencias_Davivienda': datos_Departamentales_Inconsistencias_Davivienda,
            'datos_Departamentales_Traslados_Davivienda': datos_Departamentales_Traslados_Davivienda,
            'datos_Convenios_Informes_Davivienda': datos_Convenios_Informes_Davivienda,
            'datos_Convenios_CalidadInformes_Davivienda': datos_Convenios_CalidadInformes_Davivienda,
            'datos_Convenios_EntregaImagenes_Davivienda': datos_Convenios_EntregaImagenes_Davivienda,
            'datos_Convenios_Davivienda_Fisicos': datos_Convenios_Davivienda_Fisicos,
            'datos_Convenios_Inconsistencias_Davivienda': datos_Convenios_Inconsistencias_Davivienda,
            'datos_Convenios_Traslados_Davivienda': datos_Convenios_Traslados_Davivienda,
            #avvillas
            'datos_inconsistencias_pasivo': datos_inconsistencias_pasivo,
            'datos_inconsistencias_activo': datos_inconsistencias_activo,
            'datos_inconsistencias_repsuestaTradicional': datos_inconsistencias_repsuestaTradicional,
            'datos_inconsistencias_repsuestaOCI': datos_inconsistencias_repsuestaOCI,
            'datos_repsuestaCreditoOCI': datos_repsuestaCreditoOCI,
            'datos_repsuestaCreditoTradicional': datos_repsuestaCreditoTradicional,
            'datos_Radicacion_AvVillas_CalidadInformacion': datos_Radicacion_AvVillas_CalidadInformacion,
            'datos_Radicacion_AvVillas_Informes': datos_Radicacion_AvVillas_Informes,
            'datos_Radicacion_AvVillas_Imagenes': datos_Radicacion_AvVillas_Imagenes,
            'datos_entrega_fisicos_TarjetasDigital': datos_entrega_fisicos_TarjetasDigital,
            'datos_entrega_fisicos_TarjetasFisico': datos_entrega_fisicos_TarjetasFisico,
            #todos los bancos
            'usuario': current_user,
            'datos_sancionesMagneticas': datos_sancionesMagneticas,
            'datos_sancionesFisicos': datos_sancionesFisicos,
            'procesos': procesos,
            #administrativo
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
        #Agrario
        meses_calidadInformacion_nacionales_agrario, porcentajes_calidadInformacion_nacionales_agrario = grafica_registrosFisicos(rol, 'Nacionales_Agrario_CalidadInformacion')
        meses_registrosMagneticos_nacionales_agrario, porcentajes_registrosMagneticos_nacionales_agrario = grafica_registrosFisicos(rol, 'Nacionales_Agrario_RegistrosMagneticos')
        #bancolombia
        meses_entregaFisicos_nacionales_bancolombia, porcentajes_entrega_fisicos_nacionales_bancolombia = grafica_registrosFisicos(rol, 'Nacionales_Bancolombia_Fisicos')
        meses_registrosMagneticos_nacionales_bancolombia, porcentajes_registrosMagneticos_nacionales_bancolombia = grafica_registrosFisicos(rol, 'Nacionales_Bancolombia_Magneticos')
        meses_entregaFisicos_Distritales_Bancolombia_Fisicos, porcentajes_entrega_fisicos_Distritales_Bancolombia_Fisicos = grafica_registrosFisicos(rol, 'Distritales_Bancolombia_Fisicos')
        meses_entregaFisicos_Distritales_Bancolombia_CMagneticas, porcentajes_entrega_fisicos_Distritales_Bancolombia_CMagneticas = grafica_registrosFisicos(rol, 'Distritales_Bancolombia_CMagneticas')
        meses_entrega_Departamentales_Bancolombia_informes, porcentajes_Departamentales_Bancolombia_informes = grafica_registrosFisicos(rol, 'Departamentales_Bancolombia_informes')
        meses_Convenios_Bancolombia_Informes, porcentajes_Convenios_Bancolombia_Informes = grafica_registrosFisicos(rol, 'Convenios_Bancolombia_Informes')
        meses_Convenios_Bancolombia_Fisicos, porcentajes_Convenios_Bancolombia_Fisicos = grafica_registrosFisicos(rol, 'Convenios_Bancolombia_Fisicos')
        meses_Convenios_Bancolombia_Web, porcentajes_Convenios_Bancolombia_Web = grafica_registrosFisicos(rol, 'Convenios_Bancolombia_Web')
        #occidente
        meses_entregaFisicos_nacionales_occidente, porcentajes_entrega_fisicos_nacionales_occidente = grafica_registrosFisicos(rol, 'Nacionales_Occidente_Fisicos')
        meses_registrosMagneticos_nacionales_occidente, porcentajes_registrosMagneticos_nacionales_occidente = grafica_registrosFisicos(rol, 'Nacionales_Occidente_Magneticos')
        meses_entregaFisicos_Distritales_Occidente_Fisicos, porcentajes_entrega_fisicos_Distritales_Occidente_Fisicos = grafica_registrosFisicos(rol, 'Distritales_Occidente_Fisicos')
        meses_entregaFisicos_Distritales_Occidente_CMagneticas, porcentajes_entrega_fisicos_Distritales_Occidente_CMagneticas = grafica_registrosFisicos(rol, 'Distritales_Occidente_CMagneticas')
        #itau
        meses_entregaFisicos_nacionales_itau, porcentajes_entrega_fisicos_nacionales_itau = grafica_registrosFisicos(rol, 'Nacionales_Itau_Fisicos')
        meses_registrosMagneticos_nacionales_itau, porcentajes_registrosMagneticos_nacionales_itau = grafica_registrosFisicos(rol, 'Nacionales_Itau_Magneticos')
        meses_Departamentales_Itau_Fisicos, porcentajes_Departamentales_Itau_Fisicos = grafica_registrosFisicos(rol, 'Departamentales_Itau_Fisicos')
        meses_Departamentales_Itau_Informes, porcentajes_Departamentales_Itau_Informes = grafica_registrosFisicos(rol, 'Departamentales_Itau_Informes')
        meses_MunicipalesCali_Iatu_Fisicos, porcentajes_MunicipalesCali_Iatu_Fisicos = grafica_registrosFisicos(rol, 'MunicipalesCali_Iatu_Fisicos')
        meses_MunicipalesCali_Iatu_Informes, porcentajes_MunicipalesCali_Iatu_Informes = grafica_registrosFisicos(rol, 'MunicipalesCali_Iatu_Informes')
        #cajaSocial
        meses_entregaFisicos_nacionales_cajasocial, porcentajes_entrega_fisicos_nacionales_cajasocial = grafica_registrosFisicos(rol, 'Nacionales_CajaSocial_Fisicos')
        meses_registrosMagneticos_nacionales_cajasocial, porcentajes_registrosMagneticos_nacionales_cajasocial = grafica_registrosFisicos(rol, 'Nacionales_CajaSocial_Magneticos')
        meses_Nacionales_Aduanas_CajaSocial, procentajes_Nacionales_Aduanas_CajaSocial = grafica_registrosFisicos(rol, 'Nacionales_Aduanas_CajaSocial')
        meses_Convenios_CajaSocial_Informes, porcentajes_Convenios_CajaSocial_Informes = grafica_registrosFisicos(rol, 'Convenios_CajaSocial_Informes')
        meses_Convenios_CajaSocial_Fisicos, porcentajes_Convenios_CajaSocial_Fisicos = grafica_registrosFisicos(rol, 'Convenios_CajaSocial_Fisicos')
        meses_Convenios_CajaSocial_Web, porcentajes_Convenios_CajaSocial_Web = grafica_registrosFisicos(rol, 'Convenios_CajaSocial_Web')
        #davivienda
        meses_entrega_Nacionales_Informes_Davivienda, porcentajes_Nacionales_Informes_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_Informes_Davivienda')
        meses_Nacionales_CalidadInformes_Davivienda, porcentajes_Nacionales_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_CalidadInformes_Davivienda')
        meses_Nacionales_EntregaImagenes_Davivienda, porcentajes_Nacionales_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_EntregaImagenes_Davivienda')
        meses_Nacionales_Davivienda_Fisicos, porcentajes_Nacionales_Davivienda_Fisicos = grafica_registrosFisicos(rol, 'Nacionales_Davivienda_Fisicos')
        meses_Nacionales_Inconsistencias_Davivienda, porcentajes_Nacionales_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_Inconsistencias_Davivienda')
        meses_Nacionales_Traslados_Davivienda, porcentajes_Nacionales_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Nacionales_Traslados_Davivienda')
        meses_entrega_Distritales_Informes_Davivienda, porcentajes_Distritales_Informes_Davivienda = grafica_registrosFisicos(rol, 'Distritales_Informes_Davivienda')
        meses_Distritales_CalidadInformes_Davivienda, porcentajes_Distritales_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Distritales_CalidadInformes_Davivienda')
        meses_Distritales_EntregaImagenes_Davivienda, porcentajes_Distritales_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Distritales_EntregaImagenes_Davivienda')
        meses_Distritales_Inconsistencias_Davivienda, porcentajes_Distritales_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Distritales_Inconsistencias_Davivienda')
        meses_Distritales_Traslados_Davivienda, porcentajes_Distritales_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Distritales_Traslados_Davivienda')
        meses_entrega_Departamentales_Informes_Davivienda, porcentajes_Departamentales_Informes_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_Informes_Davivienda')
        meses_Departamentales_CalidadInformes_Davivienda, porcentajes_Departamentales_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_CalidadInformes_Davivienda')
        meses_Departamentales_EntregaImagenes_Davivienda, porcentajes_Departamentales_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_EntregaImagenes_Davivienda')
        meses_Departamentales_Davivienda_Fisicos, porcentajes_Departamentales_Davivienda_Fisicos = grafica_registrosFisicos(rol, 'Departamentales_Davivienda_Fisicos')
        meses_Departamentales_Inconsistencias_Davivienda, porcentajes_Departamentales_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_Inconsistencias_Davivienda')
        meses_Departamentales_Traslados_Davivienda, porcentajes_Departamentales_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Departamentales_Traslados_Davivienda')
        meses_entrega_Convenios_Informes_Davivienda, porcentajes_Convenios_Informes_Davivienda = grafica_registrosFisicos(rol, 'Convenios_Informes_Davivienda')
        meses_Convenios_CalidadInformes_Davivienda, porcentajes_Convenios_CalidadInformes_Davivienda = grafica_registrosFisicos(rol, 'Convenios_CalidadInformes_Davivienda')
        meses_Convenios_EntregaImagenes_Davivienda, porcentajes_Convenios_EntregaImagenes_Davivienda = grafica_registrosFisicos(rol, 'Convenios_EntregaImagenes_Davivienda')
        meses_Convenios_Davivienda_Fisicos, porcentajes_Convenios_Davivienda_Fisicos = grafica_registrosFisicos(rol, 'Convenios_Davivienda_Fisicos')
        meses_Convenios_Inconsistencias_Davivienda, porcentajes_Convenios_Inconsistencias_Davivienda = grafica_registrosFisicos(rol, 'Convenios_Inconsistencias_Davivienda')
        meses_Convenios_Traslados_Davivienda, porcentajes_Convenios_Traslados_Davivienda = grafica_registrosFisicos(rol, 'Convenios_Traslados_Davivienda')
        #avvillas
        meses_inconsistenciasPasivo, porcentajes_inconsistenciasPasivo = grafica_inconsitenciasPasivo(rol, 'complementacion_pasivo')
        meses_inconsistenciasActivo, porcentajes_inconsistenciasActivo = grafica_inconsitenciasPasivo(rol, 'complementacion_activo')
        meses_inconsistenciasrepsuestaTradicional, porcentajes_inconsistenciasrepsuestaTradicional = grafica_inconsitenciasPasivo(rol, 'complementacion_repsuestaTradicional')
        meses_inconsistenciasrepsuestaOCI, porcentajes_inconsistenciasrepsuestaOCI = grafica_inconsitenciasPasivo(rol, 'complementacion_repsuestaOCI')
        meses_repsuestaCrerditoOCI, tiempo_repsuestaCreditoOCI = grafica_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoOCI')
        meses_repsuestaCrerditoTradicional, tiempo_repsuestaCreditoTradicional = grafica_TRespuesta_credito(rol, 'complementacion_repsuestaCreditoTradicional')
        meses_Radicacion_AvVillas_CalidadInformacion, porcentajes_Radicacion_AvVillas_CalidadInformacion = grafica_registrosFisicos(rol, 'Radicacion_AvVillas_CalidadInformacion')
        meses_Radicacion_AvVillas_Informes, porcentajes_Radicacion_AvVillas_Informes = grafica_registrosFisicos(rol, 'Radicacion_AvVillas_Informes')
        meses_Radicacion_AvVillas_Imagenes, porcentajes_Radicacion_AvVillas_Imagenes = grafica_registrosFisicos(rol, 'Radicacion_AvVillas_Imagenes')
        meses_entregaFisicos_TarjetasDigital, porcentajes_entrega_fisicos_TarjetasDigital = grafica_registrosFisicos(rol, 'TarjetasDigital')
        meses_entregaFisicos_TarjetasFisico, porcentajes_entrega_fisicos_TarjetasFisico = grafica_registrosFisicos(rol, 'TarjetasFisico')
        #aplica para todos los bancos
        meses_sancionesMagneticas, multas_sancionesMagneticas = grafica_sancionesMagneticas(rol)
        meses_sancionesFisicos, multas_sancionesFisicos = grafica_sancionesFisicos(rol)       
        '''ADMINISTRATIVO'''
        meses_administrativo_sistemas, porcentajes_administrativo_sistemas = grafica_Administrativo(rol, 'sistemas')
        meses_administrativo_tecnologia, porcentajes_administrativo_tecnologia = grafica_Administrativo(rol, 'tecnologia')
        meses_administrativo_financiera, porcentajes_administrativo_financiera = grafica_Administrativo(rol, 'financiera')
        meses_administrativo_comercial_propuestas, porcentajes_administrativo_comercial_propuestas = grafica_Administrativo(rol, 'comercial_propuestas')
        meses_administrativo_comercial_efectividad, porcentajes_administrativo_comercial_efectividad = grafica_Administrativo(rol, 'comercial_efectividad')
        meses_administrativo_comercial_pqr, porcentajes_administrativo_comercial_pqr = grafica_Administrativo(rol, 'comercial_pqr')
        meses_administrativo_TH_clima_organizacional, porcentajes_administrativo_TH_clima_organizacional = grafica_Administrativo(rol, 'TH_clima_organizacional')
        meses_administrativo_TH_Cumplimiento_Capacitaciones, porcentajes_administrativo_TH_Cumplimiento_Capacitaciones = grafica_Administrativo(rol, 'TH_Cumplimiento_Capacitaciones')
        meses_administrativo_TH_Eficacia_Capacitaciones, porcentajes_administrativo_TH_Eficacia_Capacitaciones = grafica_Administrativo(rol, 'TH_Eficacia_Capacitaciones')
        meses_administrativo_TH_Evaluacion_Desempeño, porcentajes_administrativo_TH_Evaluacion_Desempeño = grafica_Administrativo(rol, 'TH_Evaluacion_Desempeño')
        meses_administrativo_SGI_Acciones_Correctivas, porcentajes_administrativo_SGI_Acciones_Correctivas = grafica_Administrativo(rol, 'SGI_Acciones_Correctivas')
        meses_administrativo_SGI_Continuidad_Negocio, porcentajes_administrativo_SGI_Continuidad_Negocio = grafica_Administrativo(rol, 'SGI_Continuidad_Negocio')
        meses_administrativo_SGI_Incidentes_Seguridad, porcentajes_administrativo_SGI_Incidentes_Seguridad = grafica_Administrativo(rol, 'SGI_Incidentes_Seguridad')
        meses_administrativo_SGI_Producto_No_Conforme, porcentajes_administrativo_SGI_Producto_No_Conforme = grafica_Administrativo(rol, 'SGI_Producto_No_Conforme')
        meses_administrativo_SGI_Riesgos, porcentajes_administrativo_SGI_Riesgos = grafica_Administrativo(rol, 'SGI_Riesgos')
        return {
            #agrario
            'meses_calidadInformacion_nacionales_agrario': meses_calidadInformacion_nacionales_agrario,
            'porcentajes_calidadInformacion_nacionales_agrario': porcentajes_calidadInformacion_nacionales_agrario,
            'meses_registrosMagneticos_nacionales_agrario': meses_registrosMagneticos_nacionales_agrario,
            'porcentajes_registrosMagneticos_nacionales_agrario': porcentajes_registrosMagneticos_nacionales_agrario,
            #bancolombia
            'meses_entregaFisicos_nacionales_bancolombia': meses_entregaFisicos_nacionales_bancolombia,
            'porcentajes_entrega_fisicos_nacionales_bancolombia': porcentajes_entrega_fisicos_nacionales_bancolombia,
            'meses_registrosMagneticos_nacionales_bancolombia': meses_registrosMagneticos_nacionales_bancolombia,
            'porcentajes_registrosMagneticos_nacionales_bancolombia': porcentajes_registrosMagneticos_nacionales_bancolombia,
            'meses_entregaFisicos_Distritales_Bancolombia_Fisicos': meses_entregaFisicos_Distritales_Bancolombia_Fisicos,
            'porcentajes_entrega_fisicos_Distritales_Bancolombia_Fisicos': porcentajes_entrega_fisicos_Distritales_Bancolombia_Fisicos,
            'meses_entregaFisicos_Distritales_Bancolombia_CMagneticas': meses_entregaFisicos_Distritales_Bancolombia_CMagneticas,
            'porcentajes_entrega_fisicos_Distritales_Bancolombia_CMagneticas': porcentajes_entrega_fisicos_Distritales_Bancolombia_CMagneticas,
            'meses_entrega_Departamentales_Bancolombia_informes': meses_entrega_Departamentales_Bancolombia_informes,
            'porcentajes_Departamentales_Bancolombia_informes': porcentajes_Departamentales_Bancolombia_informes,
            'meses_Convenios_Bancolombia_Informes': meses_Convenios_Bancolombia_Informes,
            'porcentajes_Convenios_Bancolombia_Informes': porcentajes_Convenios_Bancolombia_Informes,
            'meses_Convenios_Bancolombia_Fisicos': meses_Convenios_Bancolombia_Fisicos,
            'porcentajes_Convenios_Bancolombia_Fisicos': porcentajes_Convenios_Bancolombia_Fisicos,
            'meses_Convenios_Bancolombia_Web': meses_Convenios_Bancolombia_Web,
            'porcentajes_Convenios_Bancolombia_Web': porcentajes_Convenios_Bancolombia_Web,
            #occiedente
            'meses_entregaFisicos_nacionales_occidente': meses_entregaFisicos_nacionales_occidente,
            'porcentajes_entrega_fisicos_nacionales_occidente': porcentajes_entrega_fisicos_nacionales_occidente,
            'meses_registrosMagneticos_nacionales_occidente': meses_registrosMagneticos_nacionales_occidente,
            'porcentajes_registrosMagneticos_nacionales_occidente': porcentajes_registrosMagneticos_nacionales_occidente,
            'meses_entregaFisicos_Distritales_Occidente_Fisicos': meses_entregaFisicos_Distritales_Occidente_Fisicos,
            'porcentajes_entrega_fisicos_Distritales_Occidente_Fisicos': porcentajes_entrega_fisicos_Distritales_Occidente_Fisicos,
            'meses_entregaFisicos_Distritales_Occidente_CMagneticas': meses_entregaFisicos_Distritales_Occidente_CMagneticas,
            'porcentajes_entrega_fisicos_Distritales_Occidente_CMagneticas': porcentajes_entrega_fisicos_Distritales_Occidente_CMagneticas,
            #itau
            'meses_entregaFisicos_nacionales_itau': meses_entregaFisicos_nacionales_itau,
            'porcentajes_entrega_fisicos_nacionales_itau': porcentajes_entrega_fisicos_nacionales_itau,
            'meses_registrosMagneticos_nacionales_itau': meses_registrosMagneticos_nacionales_itau,
            'porcentajes_registrosMagneticos_nacionales_itau': porcentajes_registrosMagneticos_nacionales_itau,
            'meses_Departamentales_Itau_Fisicos': meses_Departamentales_Itau_Fisicos,
            'porcentajes_Departamentales_Itau_Fisicos': porcentajes_Departamentales_Itau_Fisicos,
            'meses_Departamentales_Itau_Informes': meses_Departamentales_Itau_Informes,
            'porcentajes_Departamentales_Itau_Informes': porcentajes_Departamentales_Itau_Informes,
            'meses_MunicipalesCali_Iatu_Fisicos': meses_MunicipalesCali_Iatu_Fisicos,
            'porcentajes_MunicipalesCali_Iatu_Fisicos': porcentajes_MunicipalesCali_Iatu_Fisicos,
            'meses_MunicipalesCali_Iatu_Informes': meses_MunicipalesCali_Iatu_Informes,
            'porcentajes_MunicipalesCali_Iatu_Informes': porcentajes_MunicipalesCali_Iatu_Informes,
            #cajaSocial
            'meses_entregaFisicos_nacionales_cajasocial': meses_entregaFisicos_nacionales_cajasocial,
            'porcentajes_entrega_fisicos_nacionales_cajasocial': porcentajes_entrega_fisicos_nacionales_cajasocial,
            'meses_registrosMagneticos_nacionales_cajasocial': meses_registrosMagneticos_nacionales_cajasocial,
            'porcentajes_registrosMagneticos_nacionales_cajasocial': porcentajes_registrosMagneticos_nacionales_cajasocial,
            'meses_Nacionales_Aduanas_CajaSocial': meses_Nacionales_Aduanas_CajaSocial,
            'procentajes_Nacionales_Aduanas_CajaSocial': procentajes_Nacionales_Aduanas_CajaSocial,
            'meses_Convenios_CajaSocial_Informes': meses_Convenios_CajaSocial_Informes,
            'porcentajes_Convenios_CajaSocial_Informes': porcentajes_Convenios_CajaSocial_Informes,
            'meses_Convenios_CajaSocial_Fisicos': meses_Convenios_CajaSocial_Fisicos,
            'porcentajes_Convenios_CajaSocial_Fisicos': porcentajes_Convenios_CajaSocial_Fisicos,
            'meses_Convenios_CajaSocial_Web': meses_Convenios_CajaSocial_Web,
            'porcentajes_Convenios_CajaSocial_Web': porcentajes_Convenios_CajaSocial_Web,
            #davivienda
            'meses_entrega_Nacionales_Informes_Davivienda': meses_entrega_Nacionales_Informes_Davivienda,
            'porcentajes_Nacionales_Informes_Davivienda': porcentajes_Nacionales_Informes_Davivienda,
            'meses_Nacionales_CalidadInformes_Davivienda': meses_Nacionales_CalidadInformes_Davivienda,
            'porcentajes_Nacionales_CalidadInformes_Davivienda': porcentajes_Nacionales_CalidadInformes_Davivienda,
            'meses_Nacionales_EntregaImagenes_Davivienda': meses_Nacionales_EntregaImagenes_Davivienda,
            'porcentajes_Nacionales_EntregaImagenes_Davivienda': porcentajes_Nacionales_EntregaImagenes_Davivienda,
            'meses_Nacionales_Davivienda_Fisicos': meses_Nacionales_Davivienda_Fisicos,
            'porcentajes_Nacionales_Davivienda_Fisicos': porcentajes_Nacionales_Davivienda_Fisicos,
            'meses_Nacionales_Inconsistencias_Davivienda': meses_Nacionales_Inconsistencias_Davivienda,
            'porcentajes_Nacionales_Inconsistencias_Davivienda': porcentajes_Nacionales_Inconsistencias_Davivienda,
            'meses_Nacionales_Traslados_Davivienda': meses_Nacionales_Traslados_Davivienda,
            'porcentajes_Nacionales_Traslados_Davivienda': porcentajes_Nacionales_Traslados_Davivienda,
            'meses_entrega_Distritales_Informes_Davivienda': meses_entrega_Distritales_Informes_Davivienda,
            'porcentajes_Distritales_Informes_Davivienda': porcentajes_Distritales_Informes_Davivienda,
            'meses_Distritales_CalidadInformes_Davivienda': meses_Distritales_CalidadInformes_Davivienda,
            'porcentajes_Distritales_CalidadInformes_Davivienda': porcentajes_Distritales_CalidadInformes_Davivienda,
            'meses_Distritales_EntregaImagenes_Davivienda': meses_Distritales_EntregaImagenes_Davivienda,
            'porcentajes_Distritales_EntregaImagenes_Davivienda': porcentajes_Distritales_EntregaImagenes_Davivienda,
            'meses_Distritales_Inconsistencias_Davivienda': meses_Distritales_Inconsistencias_Davivienda,
            'porcentajes_Distritales_Inconsistencias_Davivienda': porcentajes_Distritales_Inconsistencias_Davivienda,
            'meses_Distritales_Traslados_Davivienda': meses_Distritales_Traslados_Davivienda,
            'porcentajes_Distritales_Traslados_Davivienda': porcentajes_Distritales_Traslados_Davivienda,
            'meses_entrega_Departamentales_Informes_Davivienda': meses_entrega_Departamentales_Informes_Davivienda,
            'porcentajes_Departamentales_Informes_Davivienda': porcentajes_Departamentales_Informes_Davivienda,
            'meses_Departamentales_CalidadInformes_Davivienda': meses_Departamentales_CalidadInformes_Davivienda,
            'porcentajes_Departamentales_CalidadInformes_Davivienda': porcentajes_Departamentales_CalidadInformes_Davivienda,
            'meses_Departamentales_EntregaImagenes_Davivienda': meses_Departamentales_EntregaImagenes_Davivienda,
            'porcentajes_Departamentales_EntregaImagenes_Davivienda': porcentajes_Departamentales_EntregaImagenes_Davivienda,
            'meses_Departamentales_Davivienda_Fisicos': meses_Departamentales_Davivienda_Fisicos,
            'porcentajes_Departamentales_Davivienda_Fisicos': porcentajes_Departamentales_Davivienda_Fisicos,
            'meses_Departamentales_Inconsistencias_Davivienda': meses_Departamentales_Inconsistencias_Davivienda,
            'porcentajes_Departamentales_Inconsistencias_Davivienda': porcentajes_Departamentales_Inconsistencias_Davivienda,
            'meses_Departamentales_Traslados_Davivienda': meses_Departamentales_Traslados_Davivienda,
            'porcentajes_Departamentales_Traslados_Davivienda': porcentajes_Departamentales_Traslados_Davivienda,
            'meses_entrega_Convenios_Informes_Davivienda': meses_entrega_Convenios_Informes_Davivienda,
            'porcentajes_Convenios_Informes_Davivienda': porcentajes_Convenios_Informes_Davivienda,
            'meses_Convenios_CalidadInformes_Davivienda': meses_Convenios_CalidadInformes_Davivienda,
            'porcentajes_Convenios_CalidadInformes_Davivienda': porcentajes_Convenios_CalidadInformes_Davivienda,
            'meses_Convenios_EntregaImagenes_Davivienda': meses_Convenios_EntregaImagenes_Davivienda,
            'porcentajes_Convenios_EntregaImagenes_Davivienda': porcentajes_Convenios_EntregaImagenes_Davivienda,
            'meses_Convenios_Davivienda_Fisicos': meses_Convenios_Davivienda_Fisicos,
            'porcentajes_Convenios_Davivienda_Fisicos': porcentajes_Convenios_Davivienda_Fisicos,
            'meses_Convenios_Inconsistencias_Davivienda': meses_Convenios_Inconsistencias_Davivienda,
            'porcentajes_Convenios_Inconsistencias_Davivienda': porcentajes_Convenios_Inconsistencias_Davivienda,
            'meses_Convenios_Traslados_Davivienda': meses_Convenios_Traslados_Davivienda,
            'porcentajes_Convenios_Traslados_Davivienda': porcentajes_Convenios_Traslados_Davivienda,
            #avvillas
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
            'meses_Radicacion_AvVillas_CalidadInformacion': meses_Radicacion_AvVillas_CalidadInformacion,
            'porcentajes_Radicacion_AvVillas_CalidadInformacion': porcentajes_Radicacion_AvVillas_CalidadInformacion,
            'meses_Radicacion_AvVillas_Informes': meses_Radicacion_AvVillas_Informes,
            'porcentajes_Radicacion_AvVillas_Informes': porcentajes_Radicacion_AvVillas_Informes,
            'meses_Radicacion_AvVillas_Imagenes': meses_Radicacion_AvVillas_Imagenes,
            'porcentajes_Radicacion_AvVillas_Imagenes': porcentajes_Radicacion_AvVillas_Imagenes,
            'meses_entregaFisicos_TarjetasDigital': meses_entregaFisicos_TarjetasDigital,
            'porcentajes_entrega_fisicos_TarjetasDigital': porcentajes_entrega_fisicos_TarjetasDigital,
            'meses_entregaFisicos_TarjetasFisico': meses_entregaFisicos_TarjetasFisico,
            'porcentajes_entrega_fisicos_TarjetasFisico': porcentajes_entrega_fisicos_TarjetasFisico,
            #aplica para todos los bancos
            'meses_sancionesMagneticas': meses_sancionesMagneticas,
            'multas_sancionesMagneticas': multas_sancionesMagneticas,
            'meses_sancionesFisicos': meses_sancionesFisicos,
            'multas_sancionesFisicos': multas_sancionesFisicos,
            #administrativo
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