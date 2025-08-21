from extension import mysql
from controllers.rol_controller import nombre_rol as nombre
import os

ROLES_PRODUCCION = ['bancolombia', 'occidente', 'davivienda', 'banagrario', 'itau', 'popular', 'av Villas', 'bancoomeva', 'banco caja social']
PROCESOS = {
    5: ['nacionales'],
    2: ['nacionales', 'distritales', 'departamentales', 'convenios'],
    6: ['nacionales', 'distritales', 'departamentales', 'convenios'],
    4: ['nacionales'],
    7: ['nacionales', 'departamentales'],
    10: ['nacionales', 'convenios', 'departamentales'],
    11: ['nacionales', 'distritales', 'convenios', 'complementacion', 'tarjetas', 'libranzas', 'radicacion'],
    12: ['nacionales'],
    13: ['nacionales', 'recaudos']
}

def procedimientos(rol):
    nombre_rol = nombre(rol)
    cur = mysql.connection.cursor()
    archivos_procedimientos  = []
    if nombre_rol.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT rutas.ruta_compartida FROM rutas INNER JOIN rol ON rutas.rol_id = rol.id WHERE carpeta = 'Procedimientos' AND rol.rol = 'Occidente'")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Procedimientos'", (rol,))
    carpeta_compartida = cur.fetchone()
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith("."):
                continue #ignora temporales y ocultos
            if nombre_rol.lower() in archivo.lower():
                tipo = os.path.splitext(archivo)[1].lower()
                archivos_procedimientos.append({
                    'nombre': archivo,
                    'tipo': tipo,
                    'ruta': os.path.join(ruta, archivo),
                }) 
    cur.close()  
    return archivos_procedimientos

def caracterizacion(rol):
    nombre_rol = nombre(rol)
    cur = mysql.connection.cursor()
    if nombre_rol.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT rutas.ruta_compartida FROM rutas INNER JOIN rol ON rutas.rol_id = rol.id WHERE carpeta = 'Caracterizacion' AND rol.rol = 'Occidente'")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Caracterizacion'", (rol,))
    carpeta_compartida = cur.fetchone()
    cur.close()
    archivos_caracterizacion = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_caracterizacion.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    return archivos_caracterizacion

def formatos_digitales(rol):
    nombre_rol = nombre(rol)
    cur = mysql.connection.cursor()
    if nombre_rol.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT rutas.ruta_compartida FROM rutas INNER JOIN rol ON rutas.rol_id = rol.id WHERE carpeta = 'Formatos Digitales' AND rol.rol = 'Occidente'")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Formatos Digitales'", (rol,))
    carpeta_compartida = cur.fetchone()
    cur.close()
    archivos_formatos_digitales = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_formatos_digitales.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    return archivos_formatos_digitales

def formatos_fisicos(rol):
    nombre_rol = nombre(rol)
    cur = mysql.connection.cursor()
    if nombre_rol.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT rutas.ruta_compartida FROM rutas INNER JOIN rol ON rutas.rol_id = rol.id WHERE carpeta = 'Formatos Fisicos' AND rol.rol = 'Occidente'")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Formatos Fisicos'", (rol,))
    carpeta_compartida = cur.fetchone()
    cur.close()
    archivos_formatos_fisicos = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_formatos_fisicos.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    return archivos_formatos_fisicos

def formatos_externos(rol):
    nombre_rol = nombre(rol)
    cur = mysql.connection.cursor()
    if nombre_rol.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT rutas.ruta_compartida FROM rutas INNER JOIN rol ON rutas.rol_id = rol.id WHERE carpeta = 'Formatos Externos' AND rol.rol = 'Occidente'")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Formatos Externos'", (rol,))
    carpeta_compartida = cur.fetchone()
    cur.close()
    archivos_formatos_externos = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_formatos_externos.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    return archivos_formatos_externos

def formatos_externos_digitales(rol):
    nombre_rol = nombre(rol)
    cur = mysql.connection.cursor()
    if nombre_rol.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT rutas.ruta_compartida FROM rutas INNER JOIN rol ON rutas.rol_id = rol.id WHERE carpeta = 'Formatos Externos Digitales' AND rol.rol = 'Occidente'")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Formatos Externos Digitales'", (rol,))
    carpeta_compartida = cur.fetchone()
    cur.close()
    archivos_formatos_externos_digitales = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_formatos_externos_digitales.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    return archivos_formatos_externos_digitales

def formatos_externos_fisicos(rol):
    nombre_rol = nombre(rol)
    cur = mysql.connection.cursor()
    if nombre_rol.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT rutas.ruta_compartida FROM rutas INNER JOIN rol ON rutas.rol_id = rol.id WHERE carpeta = 'Formatos Externos Fisicos' AND rol.rol = 'Occidente'")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Formatos Externos Fisicos'", (rol,))
    carpeta_compartida = cur.fetchone()
    cur.close()
    archivos_formatos_externos_fisicos = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_formatos_externos_fisicos.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    return archivos_formatos_externos_fisicos

def plan_calidad(rol):
    nombre_rol_actual = nombre(rol).lower()
    palabras_clave = PROCESOS.get(rol, []) # Usamos una lista vacía por defecto
    archivos_plan_calidad = []
    
    cur = mysql.connection.cursor()

    # Paso 1: Obtener la ruta. La lógica es diferente para roles de producción y otros.
    # Esta parte de tu código original es importante si tienen carpetas diferentes.
    if nombre_rol_actual in ROLES_PRODUCCION:
        # Todos los roles de producción leen de una carpeta común (ej. la de Occidente)
        # Esto asume que todos los archivos del Plan de Calidad están en un solo lugar.
        cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = 'Plan de Calidad' AND rol_id = 4") # Rol 4 = Occidente
    else:
        # Los roles no-producción (ej. admin) leen de su propia carpeta asignada.
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Plan de Calidad'", (rol,))
    
    resultado_ruta = cur.fetchone()
    cur.close()

    if not resultado_ruta:
        print(f"ADVERTENCIA: No se encontró ruta de 'Plan de Calidad' para el rol {rol}.")
        return []

    ruta = resultado_ruta[0]

    # Paso 2: Iterar y filtrar
    try:
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue

            archivo_lower = archivo.lower()
            
            # Por defecto, asumimos que el archivo es válido para ser añadido.
            debe_anadirse = True 
            
            # Aplicamos el filtro solo si el rol es de producción
            if nombre_rol_actual in ROLES_PRODUCCION:
                
                # REGLA A: ¿El archivo NO contiene los procesos del rol?
                if not any(palabra.lower() in archivo_lower for palabra in palabras_clave):
                    debe_anadirse = False # Si no contiene ninguno, no lo añadimos.

                # REGLA B: ¿El archivo contiene el nombre de OTRO banco?
                # Esta regla solo se aplica si la Regla A no ya lo descartó.
                if debe_anadirse:
                    for otro_banco in ROLES_PRODUCCION:
                        if otro_banco.lower() != nombre_rol_actual and otro_banco.lower() in archivo_lower:
                            debe_anadirse = False # Si es de otro banco, no lo añadimos.
                            break
            
            # DECISIÓN FINAL: Si la bandera 'debe_anadirse' sigue siendo True, añadimos el archivo.
            if debe_anadirse:
                tipo = os.path.splitext(archivo)[1].lower()
                archivos_plan_calidad.append({
                    'nombre': archivo,
                    'tipo': tipo,
                    'ruta': os.path.join(ruta, archivo)
                })

    except FileNotFoundError:
        print(f"ADVERTENCIA DE RUTA: La carpeta '{ruta}' no fue encontrada.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer la carpeta: {e}")

    return archivos_plan_calidad

def requisitos_cliente(rol):
    """
    Lista los archivos de la carpeta 'Requisitos del Cliente' aplicando una lógica
    de filtrado inteligente basada en el rol del usuario.
    """
    nombre_rol_actual = nombre(rol).lower()
    # Usamos .get(rol, []) para obtener la lista o una lista vacía si el rol no está en el diccionario
    palabras_clave = PROCESOS.get(rol, []) 
    archivos_requisitos_cliente = []
    
    cur = mysql.connection.cursor()

    # Paso 1: Obtener la ruta de la carpeta.
    # Se mantiene tu lógica original: los roles de producción leen de una carpeta de referencia,
    # mientras que los otros roles leen de la suya específica.
    if nombre_rol_actual in ROLES_PRODUCCION:
        # Usamos Occidente (rol 4) como referencia para la carpeta principal.
        cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = 'Requisitos del Cliente' AND rol_id = 4")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Requisitos del Cliente'", (rol,))
    
    resultado_ruta = cur.fetchone()
    cur.close()

    if not resultado_ruta:
        print(f"ADVERTENCIA: No se encontró ruta de 'Requisitos del Cliente' para el rol {rol}.")
        return []

    ruta = resultado_ruta[0]

    # Paso 2: Iterar sobre los archivos y aplicar la lógica de filtrado.
    try:
        for archivo in os.listdir(ruta):
            # Ignorar archivos temporales o del sistema
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue

            archivo_lower = archivo.lower()
            
            # Por defecto, asumimos que el archivo es válido para ser añadido.
            debe_anadirse = True
            
            # Aplicamos el filtro solo si el rol es de producción y tiene palabras clave definidas.
            if nombre_rol_actual in ROLES_PRODUCCION and palabras_clave:
                
                # REGLA A: El archivo DEBE contener al menos una de las palabras clave del rol.
                if not any(proceso.lower() in archivo_lower for proceso in palabras_clave):
                    debe_anadirse = False

                # REGLA B: El archivo NO debe contener el nombre de OTRO banco.
                # (Solo se ejecuta si la Regla A no lo descartó ya)
                if debe_anadirse:
                    for otro_banco in ROLES_PRODUCCION:
                        if otro_banco.lower() != nombre_rol_actual and otro_banco.lower() in archivo_lower:
                            debe_anadirse = False
                            break
            
            # DECISIÓN FINAL: Si la bandera sigue siendo True, añadimos el archivo.
            if debe_anadirse:
                tipo = os.path.splitext(archivo)[1].lower()
                archivos_requisitos_cliente.append({
                    'nombre': archivo,
                    'tipo': tipo,
                    'ruta': os.path.join(ruta, archivo)
                })

    except FileNotFoundError:
        print(f"ADVERTENCIA DE RUTA: La carpeta '{ruta}' para 'Requisitos del Cliente' no fue encontrada.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer la carpeta de Requisitos del Cliente: {e}")

    return archivos_requisitos_cliente

def actas_restauracion(rol):
    cur = mysql.connection.cursor()
    archivos_actas_restauracion = []
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Actas de Restauración'", (rol,))
    carpeta_compartida = cur.fetchone()
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_actas_restauracion.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_actas_restauracion

def instructivos(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Instructivos'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_instructivos = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_instructivos.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_instructivos

def manuales(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Manuales'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_manuales = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_manuales.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_manuales


def auditorias_ifx(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Auditorias IFX'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_auditorias_ifx = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_auditorias_ifx.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_auditorias_ifx

def auditoria_integrum(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Auditoria Integrum'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_auditoria_integrum = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_auditoria_integrum.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_auditoria_integrum

def auditoria_inter_servicios(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Auditoria Inter Servicios'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_auditoria_inter_servicios = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_auditoria_inter_servicios.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_auditoria_inter_servicios

def ISECpoliticaContinuidad(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'ISEC Continuidad'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_ISECpoliticaContinuidad = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_ISECpoliticaContinuidad.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_ISECpoliticaContinuidad

def ISECpoliticaProteccionDatos(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'ISEC Proteccion Datos'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_ISECpoliticaProteccionDatos = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_ISECpoliticaProteccionDatos.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_ISECpoliticaProteccionDatos

def ISECpoliticaSeguridadInf(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'ISEC Seguridad Inf'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_ISECpoliticaSeguridadInf = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_ISECpoliticaSeguridadInf.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_ISECpoliticaSeguridadInf

def comite_seguridad(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Comite de Seguridad'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_comite_seguridad = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_comite_seguridad.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_comite_seguridad

def vulnerabilidades_2024(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Vulnerabilidades 2024'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_vulnerabilidades_2024 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_vulnerabilidades_2024.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_vulnerabilidades_2024

def vulnerabilidades_2025(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Vulnerabilidades 2025'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_vulnerabilidades_2025 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_vulnerabilidades_2025.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_vulnerabilidades_2025

def vulnerabilidades_ant(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Vulnerabilidades Anteriores'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_vulnerabilidades_ant = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_vulnerabilidades_ant.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_vulnerabilidades_ant

def revision_seguridad_2021(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Revision Seguridad 2021'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_revision_seguridad_2021 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_revision_seguridad_2021.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_revision_seguridad_2021

def revision_seguridad_2022(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Revision Seguridad 2022'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_revision_seguridad_2022 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_revision_seguridad_2022.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_revision_seguridad_2022

def revision_seguridad_2023(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Revision Seguridad 2023'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_revision_seguridad_2023 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_revision_seguridad_2023.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_revision_seguridad_2023

def revision_seguridad_2024(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Revision Seguridad 2024'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_revision_seguridad_2024 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_revision_seguridad_2024.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_revision_seguridad_2024



def sst(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'SST'", (rol,))
    carpeta_compartida = cur.fetchone()[0]
    estructura = []

    for raiz, subdirs, files in os.walk(carpeta_compartida):
        nivel = raiz.replace(carpeta_compartida, '').count(os.sep)
        nombre = os.path.basename(raiz)
        archivos = [f for f in files if not f.startswith('~$') and not f.startswith('.')]  # Evita temporales y ocultos

        data = {
            'ruta': raiz,
            'nivel': nivel,
            'nombre': nombre,
            'tipo': 'carpeta',
            'archivos': archivos,
            'hijos': []
        }

        if nivel == 0:
            estructura.append(data)
        else:
            padre = estructura
            for i in range(nivel - 1):
                padre = padre[-1]['hijos']
            padre[-1]['hijos'].append(data)
    cur.close()
    return estructura if estructura else []

def encuestas_2019(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Encuestas 2019'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_encuestas_2019 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_encuestas_2019.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_encuestas_2019

def encuestas_2020(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Encuestas 2020'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_encuestas_2020 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_encuestas_2020.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_encuestas_2020

def encuestas_2021(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Encuestas 2021'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_encuestas_2021 = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_encuestas_2021.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_encuestas_2021

def sagrilaft(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Sagrilaft'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_sagrilaft = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_sagrilaft.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_sagrilaft

def ambiental(rol):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Ambiental'", (rol,))
    carpeta_compartida = cur.fetchone()
    archivos_ambiental = []
    if carpeta_compartida:
        ruta = carpeta_compartida[0]
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            tipo = os.path.splitext(archivo)[1].lower()
            archivos_ambiental.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    cur.close()
    return archivos_ambiental