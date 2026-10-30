import sys, os
sys.path.insert(0, 'Z:/')

from extension import mysql
from controllers.rol_controller import nombre_rol

cur = mysql.connection.cursor()

print('=== TODOS LOS ROLES EN DB ===')
cur.execute('SELECT id, rol FROM rol')
for r in cur.fetchall():
    print(f'  ID {r[0]}: {r[1]}')

print()
print('=== RUTAS PARA Caracterizacion CON OCCIDENTE (rol_id=4) ===')
cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = 'Caracterizacion' AND rol_id = 4")
row = cur.fetchone()
if row:
    print(f'  Ruta encontrada: {row[0]}')
    ruta = row[0]
    if os.path.isdir(ruta):
        print(f'  La ruta EXISTE en el sistema de archivos')
        archivos = os.listdir(ruta)
        print(f'  Archivos en la carpeta ({len(archivos)} total):')
        for a in sorted(archivos):
            if a.startswith('~') or a.startswith('.') or a.lower() == 'thumbs.db':
                continue
            contiene_bancolombia = 'bancolombia' in a.lower()
            print(f'    {"[BANCOLOMBIA]" if contiene_bancolombia else "[OTRO]       "} {a}')
    else:
        print(f'  ERROR: La ruta NO existe en el sistema de archivos')
else:
    print('  No se encontro ruta para Caracterizacion con Occidente')
    
    # Buscar si hay ruta para Caracterizacion para cualquier rol
    print()
    print('=== BUSCANDO CUALQUIER RUTA DE Caracterizacion ===')
    cur.execute("SELECT rol_id, ruta_compartida FROM rutas WHERE carpeta = 'Caracterizacion'")
    for r in cur.fetchall():
        print(f'  Rol ID {r[0]}: {r[1]}')

print()
print('=== TODAS LAS RUTAS EN BD ===')
cur.execute('SELECT id, rol_id, carpeta, ruta_compartida FROM rutas')
for r in cur.fetchall():
    print(f'  ID {r[0]}, Rol {r[1]}, Carpeta "{r[2]}": {r[3]}')

cur.close()
