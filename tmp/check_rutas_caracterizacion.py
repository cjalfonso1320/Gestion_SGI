"""Script para diagnosticar rutas UNC de Caracterización."""
import sys, os
sys.path.insert(0, 'Z:/')

from app import app
from extension import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    
    print("=" * 70)
    print("TODAS LAS RUTAS PARA 'Caracterizacion' EN BD:")
    print("=" * 70)
    cur.execute("""
        SELECT r.id, r.rol_id, rol.rol AS nombre_rol, r.ruta_compartida
        FROM rutas r
        LEFT JOIN rol ON r.rol_id = rol.id
        WHERE r.carpeta = 'Caracterizacion'
    """)
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"  ID={row[0]}, Rol ID={row[1]} ({row[2]}), Ruta={row[3]}")
            # Probar si la ruta existe
            if row[3]:
                exists = os.path.exists(row[3])
                is_dir = os.path.isdir(row[3])
                print(f"    -> Existe={exists}, Es directorio={is_dir}")
                if exists and is_dir:
                    try:
                        files = [f for f in os.listdir(row[3]) 
                                if not f.startswith('~') and not f.startswith('.') and f.lower() != 'thumbs.db']
                        print(f"    → Archivos visibles: {len(files)}")
                        for f in sorted(files)[:20]:
                            print(f"      - {f.encode('ascii', errors='replace').decode()}")
                        if len(files) > 20:
                            print(f"      ... y {len(files)-20} más")
                    except Exception as e:
                        print(f"    -> Error al listar: {e}")
    else:
        print("  ¡No se encontró ninguna ruta para Caracterización!")
    
    print()
    print("=" * 70)
    print("COMPARACIÓN: RUTAS PARA 'Procedimientos' (para verificar):")
    print("=" * 70)
    cur.execute("""
        SELECT r.id, r.rol_id, rol.rol AS nombre_rol, r.ruta_compartida
        FROM rutas r
        LEFT JOIN rol ON r.rol_id = rol.id
        WHERE r.carpeta = 'Procedimientos' LIMIT 3
    """)
    for row in cur.fetchall():
        print(f"  ID={row[0]}, Rol ID={row[1]} ({row[2]}), Ruta={row[3]}")
        if row[3]:
            exists = os.path.exists(row[3])
            print(f"    -> Existe={exists}")
    
    print()
    print("=" * 70)
    print("VERIFICANDO CONEXIÓN A SERVIDOR REMOTO (si aplica):")
    print("=" * 70)
    # Buscar rutas UNC con servicios.digicom.com.co
    cur.execute("SELECT DISTINCT ruta_compartida FROM rutas WHERE ruta_compartida LIKE '%digicom%'")
    digicom_paths = cur.fetchall()
    if digicom_paths:
        for p in digicom_paths:
            ruta_str = p[0].encode('ascii', errors='replace').decode() if p[0] else 'None'
            print(f"  Ruta: {ruta_str}")
            # Extraer el host UNC
            if p[0] and p[0].startswith('\\\\'):
                host = p[0].split('\\')[2] if '\\' in p[0] else p[0]
                print(f"  Host UNC: {host.encode('ascii', errors='replace').decode()}")
    else:
        print("  No se encontraron rutas con 'digicom'")
    
    cur.close()
