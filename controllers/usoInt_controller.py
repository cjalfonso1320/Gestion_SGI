"""Controlador de documentos de uso interno.

Proporciona funciones para listar y estructurar los archivos
almacenados en las carpetas de uso interno del sistema,
excluyendo carpetas específicas como 'Indicadores'.
"""

from extension import mysql
import os


def subC_doc_UsoInt(proceso):
    """Obtiene la estructura de carpetas y archivos de uso interno.

    Recorre recursivamente la carpeta compartida correspondiente al proceso
    'Información de Uso Interno' y construye un árbol con la jerarquía
    de directorios y archivos, excluyendo carpetas no deseadas.

    Args:
        proceso: Nombre del proceso/carpeta a listar.

    Returns:
        list: Lista anidada con la estructura de carpetas y archivos.
              Cada nodo contiene: ruta, nivel, nombre, tipo, archivos, hijos.
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta_compartida FROM rutas WHERE rol_id = 22 AND carpeta = %s", (proceso,))
    carpeta_compartida = cur.fetchone()[0]
    estructura = []
    excluir_carpetas = ["Indicadores"]  # Excluir Carpetas
    for raiz, subdirs, files in os.walk(carpeta_compartida):
        subdirs[:] = [d for d in subdirs if d not in excluir_carpetas]
        nivel = raiz.replace(carpeta_compartida, '').count(os.sep)
        nombre = os.path.basename(raiz)
        archivos = [f for f in files if not f.startswith('~$') and not f.startswith('.') and not f.lower() == "thumbs.db" and not f.lower() == "desktop.ini"]

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
