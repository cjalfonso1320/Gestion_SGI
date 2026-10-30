"""Controlador de documentos del sistema de gestión documental.

Gestiona el acceso a los archivos almacenados en carpetas compartidas
de red, aplicando filtros por rol de usuario y utilizando caché con TTL
para optimizar el rendimiento.

Soporta roles de producción (filtran archivos por banco) y roles
administrativos (ven todos los archivos).
"""

from extension import mysql
from controllers.rol_controller import nombre_rol as nombre
import os
import time

ROLES_PRODUCCION = ['bancolombia', 'occidente', 'davivienda', 'banagrario', 'itau', 'popular', 'av villas', 'bancoomeva', 'banco caja social']
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

ROLES_ADMIN = [8, 9, 14, 15, 16, 17, 18, 19, 20, 21]
REFERENCE_ROL_ID = 4
DOC_CACHE_TTL = 30
_DOC_CACHE = {}


def _cache_get(key):
    """Obtiene un valor de la caché de documentos si no ha expirado.

    Args:
        key: Clave del valor en caché.

    Returns:
        Valor almacenado o None si no existe o expiró.
    """
    cached = _DOC_CACHE.get(key)
    if not cached:
        return None
    expires_at, value = cached
    if expires_at < time.time():
        _DOC_CACHE.pop(key, None)
        return None
    return value


def _cache_set(key, value, ttl=DOC_CACHE_TTL):
    """Almacena un valor en la caché de documentos con TTL.

    Args:
        key: Clave para almacenar el valor.
        value: Valor a cachear.
        ttl: Tiempo de vida en segundos (default: 30).

    Returns:
        El mismo value almacenado.
    """
    _DOC_CACHE[key] = (time.time() + ttl, value)
    return value


def _get_files_from_shared_folder(rol, carpeta_nombre, filter_by_name=True):
    """Obtiene archivos de una carpeta compartida aplicando filtros por rol.

    - Para roles de producción, usa una ruta de referencia común y filtra
      los archivos por nombre (solo muestra los que corresponden al banco).
    - Los roles administrativos ven todos los archivos.
    - Si filter_by_name=False, omite el filtro por nombre (útil para
      carpetas como Caracterización donde los archivos no tienen nombre de banco).

    Args:
        rol: ID del rol del usuario.
        carpeta_nombre: Nombre de la carpeta a listar.
        filter_by_name: Si True, filtra archivos por nombre del rol (default: True).

    Returns:
        list: Lista de diccionarios con nombre, tipo y ruta de cada archivo.
    """
    cache_key = ("shared", rol, carpeta_nombre)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    nombre_rol_actual = nombre(rol)
    cur = mysql.connection.cursor()
    archivos = []

    if nombre_rol_actual.lower() in ROLES_PRODUCCION:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = %s AND rol_id = %s", (carpeta_nombre, REFERENCE_ROL_ID))
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = %s", (rol, carpeta_nombre))

    resultado_ruta = cur.fetchone()
    cur.close()

    if not resultado_ruta or not resultado_ruta[0]:
        print(f"ADVERTENCIA: No se encontró ruta para la carpeta '{carpeta_nombre}' y rol {rol}.")
        return []

    ruta = resultado_ruta[0]

    try:
        if not os.path.isdir(ruta):
            print(f"ERROR: La ruta '{ruta}' no es un directorio válido.")
            return []

        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            if not filter_by_name or rol in ROLES_ADMIN or nombre_rol_actual.lower() in archivo.lower():
                tipo = os.path.splitext(archivo)[1].lower()
                archivos.append({
                    'nombre': archivo,
                    'tipo': tipo,
                    'ruta': os.path.join(ruta, archivo),
                })
    except FileNotFoundError:
        print(f"ERROR: La ruta '{ruta}' no fue encontrada.")
    except Exception as e:
        print(f"ERROR inesperado al leer la carpeta '{carpeta_nombre}': {e}")

    return _cache_set(cache_key, archivos)


def _get_files_for_rol(rol, carpeta_nombre):
    """Obtiene todos los archivos de una carpeta específica para un rol.

    Es una función simple sin lógica de filtrado adicional, a diferencia
    de _get_files_from_shared_folder.

    Args:
        rol: ID del rol del usuario.
        carpeta_nombre: Nombre de la carpeta a listar.

    Returns:
        list: Lista de diccionarios con nombre, tipo y ruta de cada archivo.
    """
    cache_key = ("role", rol, carpeta_nombre)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

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
            print(f"ERROR: La ruta '{ruta}' no es un directorio válido.")
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
        print(f"ERROR: La ruta '{ruta}' no fue encontrada.")
    except Exception as e:
        print(f"ERROR inesperado al leer la carpeta '{carpeta_nombre}': {e}")
    finally:
        cur.close()

    return _cache_set(cache_key, archivos)


def procedimientos(rol):
    """Obtiene los archivos de procedimientos para un rol."""
    return _get_files_from_shared_folder(rol, 'Procedimientos')


def caracterizacion(rol):
    """Obtiene los archivos de caracterización (sin filtro por nombre)."""
    return _get_files_from_shared_folder(rol, 'Caracterizacion', filter_by_name=False)


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
    """Obtiene los archivos del Plan de Calidad con filtrado inteligente por rol.

    Aplica reglas de filtrado para roles de producción:
        - El archivo debe contener al menos un proceso del rol.
        - El archivo no debe contener el nombre de otro banco.

    Args:
        rol: ID del rol del usuario.

    Returns:
        list: Lista de archivos filtrados del Plan de Calidad.
    """
    cache_key = ("plan_calidad", rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    nombre_rol_actual = nombre(rol).lower()
    palabras_clave = PROCESOS.get(rol, [])
    archivos_plan_calidad = []

    cur = mysql.connection.cursor()

    if nombre_rol_actual in ROLES_PRODUCCION:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = 'Plan de Calidad' AND rol_id = 4")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Plan de Calidad'", (rol,))

    resultado_ruta = cur.fetchone()
    cur.close()

    if not resultado_ruta:
        return []

    ruta = resultado_ruta[0]

    try:
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            archivo_lower = archivo.lower()
            debe_anadirse = True

            if nombre_rol_actual in ROLES_PRODUCCION:
                if not any(palabra.lower() in archivo_lower for palabra in palabras_clave):
                    debe_anadirse = False
                if debe_anadirse:
                    for otro_banco in ROLES_PRODUCCION:
                        if otro_banco.lower() != nombre_rol_actual and otro_banco.lower() in archivo_lower:
                            debe_anadirse = False
                            break

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

    return _cache_set(cache_key, archivos_plan_calidad)


def requisitos_cliente(rol):
    """Lista los archivos de 'Requisitos del Cliente' con filtrado inteligente.

    Aplica la misma lógica de filtrado que plan_calidad: los roles de producción
    solo ven archivos relevantes para su banco.

    Args:
        rol: ID del rol del usuario.

    Returns:
        list: Lista de archivos filtrados de Requisitos del Cliente.
    """
    cache_key = ("requisitos_cliente", rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    nombre_rol_actual = nombre(rol).lower()
    palabras_clave = PROCESOS.get(rol, [])
    archivos_requisitos_cliente = []

    cur = mysql.connection.cursor()

    if nombre_rol_actual in ROLES_PRODUCCION:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = 'Requisitos del Cliente' AND rol_id = 4")
    else:
        cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'Requisitos del Cliente'", (rol,))

    resultado_ruta = cur.fetchone()
    cur.close()

    if not resultado_ruta:
        return []

    ruta = resultado_ruta[0]

    try:
        for archivo in os.listdir(ruta):
            if archivo.startswith("~") or archivo.startswith(".") or archivo.lower() == "thumbs.db":
                continue
            archivo_lower = archivo.lower()
            debe_anadirse = True

            if nombre_rol_actual in ROLES_PRODUCCION and palabras_clave:
                if not any(proceso.lower() in archivo_lower for proceso in palabras_clave):
                    debe_anadirse = False
                if debe_anadirse:
                    for otro_banco in ROLES_PRODUCCION:
                        if otro_banco.lower() != nombre_rol_actual and otro_banco.lower() in archivo_lower:
                            debe_anadirse = False
                            break

            if debe_anadirse:
                tipo = os.path.splitext(archivo)[1].lower()
                archivos_requisitos_cliente.append({
                    'nombre': archivo,
                    'tipo': tipo,
                    'ruta': os.path.join(ruta, archivo)
                })
    except FileNotFoundError:
        print(f"ADVERTENCIA DE RUTA: La carpeta '{ruta}' no fue encontrada.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer la carpeta: {e}")

    return _cache_set(cache_key, archivos_requisitos_cliente)


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
    """Obtiene la estructura de carpetas y archivos de SST (Seguridad y Salud en el Trabajo).

    Construye un árbol jerárquico con todas las subcarpetas y archivos.

    Args:
        rol: ID del rol del usuario (debe ser 17 para SST).

    Returns:
        list: Estructura jerárquica de carpetas y archivos.
    """
    cache_key = ("sst", rol)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = %s AND carpeta = 'SST'", (rol,))
    carpeta_compartida = cur.fetchone()[0]
    estructura = []

    for raiz, subdirs, files in os.walk(carpeta_compartida):
        nivel = raiz.replace(carpeta_compartida, '').count(os.sep)
        nombre = os.path.basename(raiz)
        archivos = [f for f in files if not f.startswith('~$') and not f.startswith('.')]
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
    return _cache_set(cache_key, estructura if estructura else [])


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
