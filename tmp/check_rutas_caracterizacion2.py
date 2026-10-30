"""Script para diagnosticar cuántas rutas hay en total y contar archivos de Caracterización."""
import sys, os
sys.path.insert(0, 'Z:/')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app import app
from extension import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    
    print("=" * 70)
    print("TOTAL DE RUTAS EN BD (ruta_compartida):")
    print("=" * 70)
    cur.execute("SELECT COUNT(DISTINCT ruta_compartida) FROM rutas")
    total = cur.fetchone()[0]
    print(f"  Total rutas únicas: {total}")
    
    cur.execute("SELECT COUNT(*) FROM rutas")
    total_rows = cur.fetchone()[0]
    print(f"  Total registros en tabla rutas: {total_rows}")
    
    print()
    print("=" * 70)
    print("ARCHIVOS EN Caracterización DE OCCIDENTE (rol_id=4):")
    print("=" * 70)
    cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = 'Caracterizacion' AND rol_id = 4")
    row = cur.fetchone()
    if row and row[0]:
        ruta = row[0]
        print(f"  Ruta: {ruta}")
        try:
            files = os.listdir(ruta)
            # Filtrar archivos basura
            real_files = [f for f in files 
                         if not f.startswith('~') and not f.startswith('.') and f.lower() != 'thumbs.db']
            print(f"  Total archivos en carpeta: {len(real_files)}")
            for f in sorted(real_files):
                f_ext = os.path.splitext(f)[1].lower()
                print(f"    [{f_ext or '(sin ext)'}] {f}")
        except Exception as e:
            print(f"  Error al listar: {e}")
    else:
        print("  No se encontró ruta")
    
    print()
    print("=" * 70)
    print("RUTAS DE PROCEDIMIENTOS (comparación - Occidente):")
    print("=" * 70)
    cur.execute("SELECT ruta_compartida FROM rutas WHERE carpeta = 'Procedimientos' AND rol_id = 4")
    proc_row = cur.fetchone()
    if proc_row and proc_row[0]:
        proc_ruta = proc_row[0]
        try:
            proc_files = [f for f in os.listdir(proc_ruta) 
                         if not f.startswith('~') and not f.startswith('.') and f.lower() != 'thumbs.db']
            print(f"  Archivos: {len(proc_files)}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print()
    print("=" * 70)
    print("COMPARACIÓN PROXY: servicios.digicom.com.co vs 192.168.40.150")
    print("=" * 70)
    print("  Las rutas UNC apuntan a 192.168.40.150 (IP local de red)")
    print("  El sitio web corre en servicios.digicom.com.co")
    print("  El servidor Flask necesita acceder a \\\\192.168.40.150\\...")
    print("  Esto requiere que el servidor tenga acceso a esa carpeta compartida")
    print()
    print("  Posible problema: el pool de aplicaciones IIS que ejecuta Flask")
    print("  no tiene permisos de red para acceder a \\\\192.168.40.150\\...")
    print("  O el servidor está teniendo problemas de latencia/concurrencia")
    print("  al abrir múltiples conexiones UNC simultáneas desde los iframes")
    
    cur.close()
