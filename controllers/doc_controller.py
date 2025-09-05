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

# Lista de roles administrativos que pueden ver todos los archivos en carpetas compartidas
ROLES_ADMIN = [8, 9, 14, 15, 16, 17, 18, 19, 20, 21]
# ID del rol de referencia para buscar la ruta de la carpeta compartida (Occidente=4)
REFERENCE_ROL_ID = 4

def _get_files_from_shared_folder(rol, carpeta_nombre):
    """
    Función auxiliar refactorizada para obtener archivos de una carpeta compartida.
    - Para roles de producción, usa una ruta de referencia común y luego filtra los archivos por nombre.
    - Los roles administrativos (definidos en ROLES_ADMIN) ven todos los archivos.
    - Los demás roles ven los archivos de su propia carpeta asignada.
    """
    nombre_rol_actual = nombre(rol)
    cur = mysql.connection.cursor()
    archivos = []
    
    # Los roles de producción usan una carpeta compartida, que está asociada al rol de referencia.
    if nombre_rol_actual.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = %s AND rol_id = %s", (carpeta_nombre, REFERENCE_ROL_ID))
    else:
        # Otros roles (administrativos, etc.) usan su propia ruta asignada.
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = %s", (rol, carpeta_nombre))
    
    resultado_ruta = cur.fetchone()
    cur.close()

    if not resultado_ruta or not resultado_ruta[0]:
        print(f"ADVERTENCIA: No se encontró ruta para la carpeta '{carpeta_nombre}' y rol {rol}.")
        return []

    ruta = resultado_ruta[0]
    
    try:
        if not os.path.isdir(ruta):
            print(f"ERROR: La ruta '{ruta}' no es un directorio válido para la carpeta '{carpeta_nombre}'.")
            return []
            
        for archivo in os.listdir(ruta):
            # Ignorar archivos temporales, ocultos o del sistema
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue

            # Si el rol es administrativo, o si el nombre del rol de producción está en el nombre del archivo, se añade.
            if rol in ROLES_ADMIN or nombre_rol_actual.lower() in archivo.lower():
                tipo = os.path.splitext(archivo)[1].lower()
                archivos.append({
                    'nombre': archivo,
                    'tipo': tipo,
                    'ruta': os.path.join(ruta, archivo),
                })
    except FileNotFoundError:
        print(f"ERROR: La ruta '{ruta}' no fue encontrada para la carpeta '{carpeta_nombre}'.")
    except Exception as e:
        print(f"ERROR inesperado al leer la carpeta '{carpeta_nombre}': {e}")

    return archivos

def _get_files_for_rol(rol, carpeta_nombre):
    """
    Función auxiliar simple para obtener todos los archivos de una carpeta específica para un rol,
    sin lógica de filtrado adicional.
    """
    cur = mysql.connection.cursor()
    archivos = []
    
    try:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = %s", (rol, carpeta_nombre))
        resultado_ruta = cur.fetchone()

        if not resultado_ruta or not resultado_ruta[0]:
            print(f"ADVERTENCIA: No se encontró ruta para la carpeta '{carpeta_nombre}' y rol {rol}.")
            return []

        ruta = resultado_ruta[0]

        if not os.path.isdir(ruta):
            print(f"ERROR: La ruta '{ruta}' no es un directorio válido para la carpeta '{carpeta_nombre}'.")
            return []

        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            
            tipo = os.path.splitext(archivo)[1].lower()
            archivos.append({
                'nombre': archivo,
                'tipo': tipo,
                'ruta': os.path.join(ruta, archivo),
            })
    except FileNotFoundError:
        print(f"ERROR: La ruta '{ruta}' no fue encontrada para la carpeta '{carpeta_nombre}'.")
    except Exception as e:
        print(f"ERROR inesperado al leer la carpeta '{carpeta_nombre}': {e}")
    finally:
        cur.close()

    return archivos

def procedimientos(rol):
    return _get_files_from_shared_folder(rol, 'Procedimientos')

def caracterizacion(rol):
    return _get_files_from_shared_folder(rol, 'Caracterizacion')

def formatos_digitales(rol):
    return _get_files_from_shared_folder(rol, 'Formatos Digitales')

def formatos_fisicos(rol):
    return _get_files_from_shared_folder(rol, 'Formatos Fisicos')

def formatos_externos(rol):
    return _get_files_from_shared_folder(rol, 'Formatos Externos')

def formatos_externos_digitales(rol):
    return _get_files_from_shared_folder(rol, 'Formatos Externos Digitales')

def formatos_externos_fisicos(rol):
    return _get_files_from_shared_folder(rol, 'Formatos Externos Fisicos')

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
    return _get_files_for_rol(rol, 'Actas de Restauración')

def instructivos(rol):
    return _get_files_for_rol(rol, 'Instructivos')

def manuales(rol):
    return _get_files_for_rol(rol, 'Manuales')

def auditorias_ifx(rol):
    return _get_files_for_rol(rol, 'Auditorias IFX')

def auditoria_integrum(rol):
    return _get_files_for_rol(rol, 'Auditoria Integrum')

def auditoria_inter_servicios(rol):
    return _get_files_for_rol(rol, 'Auditoria Inter Servicios')

def ISECpoliticaContinuidad(rol):
    return _get_files_for_rol(rol, 'ISEC Continuidad')

def ISECpoliticaProteccionDatos(rol):
    return _get_files_for_rol(rol, 'ISEC Proteccion Datos')

def ISECpoliticaSeguridadInf(rol):
    return _get_files_for_rol(rol, 'ISEC Seguridad Inf')

def comite_seguridad(rol):
    return _get_files_for_rol(rol, 'Comite de Seguridad')

def vulnerabilidades_2024(rol):
    return _get_files_for_rol(rol, 'Vulnerabilidades 2024')

def vulnerabilidades_2025(rol):
    return _get_files_for_rol(rol, 'Vulnerabilidades 2025')

def vulnerabilidades_ant(rol):
    return _get_files_for_rol(rol, 'Vulnerabilidades Anteriores')

def revision_seguridad_2021(rol):
    return _get_files_for_rol(rol, 'Revision Seguridad 2021')

def revision_seguridad_2022(rol):
    return _get_files_for_rol(rol, 'Revision Seguridad 2022')

def revision_seguridad_2023(rol):
    return _get_files_for_rol(rol, 'Revision Seguridad 2023')

def revision_seguridad_2024(rol):
    return _get_files_for_rol(rol, 'Revision Seguridad 2024')



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
    return _get_files_for_rol(rol, 'Encuestas 2019')

def encuestas_2020(rol):
    return _get_files_for_rol(rol, 'Encuestas 2020')

def encuestas_2021(rol):
    return _get_files_for_rol(rol, 'Encuestas 2021')

def sagrilaft(rol):
    return _get_files_for_rol(rol, 'Sagrilaft')

def ambiental(rol):
    return _get_files_for_rol(rol, 'Ambiental')