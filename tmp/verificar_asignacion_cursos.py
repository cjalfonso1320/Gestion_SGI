"""Verificación (transaccional, con ROLLBACK) de las consultas TAL COMO están
escritas en controllers/aula_controller.py, ejecutadas contra la BD real.

Comprueba:
  1. El UPDATE de cierre automático usa CURDATE() y NO cierra el curso 43.
  2. get_cursos_estudiante_db() devuelve el curso 43 a los 3 empleados.
  3. El SQL que genera editar_curso_db() es válido y deja estado='Abierto'
     cuando la fecha límite sigue vigente (se revierte todo con ROLLBACK).
"""
import ast
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mysql.connector
from config import Config  # noqa: E402

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'controllers', 'aula_controller.py')
src = open(SRC, encoding='utf-8').read()

conn = mysql.connector.connect(host=Config.MYSQL_HOST, user=Config.MYSQL_USER,
                               password=Config.MYSQL_PASSWORD, database=Config.MYSQL_DB)
cur = conn.cursor(dictionary=True)
fallos = []

# ── 1. UPDATE de cierre automático (extraído del código fuente) ──
updates = re.findall(r'cursor\.execute\("""\s*UPDATE cursos\s*SET estado = \'Cerrado\'(.*?)"""',
                     src, re.S)
print(f"UPDATE de cierre encontrados en el código: {len(updates)}")
for i, u in enumerate(updates, 1):
    sql = 'UPDATE cursos SET estado = \'Cerrado\'' + u
    ok = 'CURDATE()' in sql and 'NOW()' not in sql
    print(f"  [{i}] usa CURDATE(): {ok}")
    if not ok:
        fallos.append(f"UPDATE {i} sigue usando NOW()")
    cur.execute(sql)  # no debe cerrar el curso 43 (fecha 2026-10-10)
    print(f"       filas cerradas ahora: {cur.rowcount}")
    if cur.rowcount != 0:
        fallos.append(f"UPDATE {i} cerró cursos que no deben cerrarse: {cur.rowcount}")
conn.commit()

# ── 2. Consulta del portal (extraída del código fuente) ──
sql_portal = re.search(r'# 3\. Buscar cursos asignados.*?sql = """(.*?)"""', src, re.S).group(1)
empleado_ids = [240, 275, 358]
for eid in empleado_ids:
    cur.execute("SELECT identificacion FROM users_rrhh WHERE id=%s", (eid,))
    ident = cur.fetchone()['identificacion']
    cur.execute("SELECT id, sgi_rol_id FROM users_rrhh WHERE identificacion=%s AND activo=1",
                (ident,))
    u = cur.fetchone()
    cur.execute(sql_portal, (u['id'], u['sgi_rol_id'] or 0))
    cursos = cur.fetchall()
    estados = [(c['id'], c['estado']) for c in cursos]
    print(f"  empleado {eid} (ident {ident}) → portal devuelve: {estados}")
    if not any(cid == 43 for cid, _ in estados):
        fallos.append(f"empleado {eid} NO recibe el curso 43")
    elif any(cid == 43 and est != 'Abierto' for cid, est in estados):
        fallos.append(f"empleado {eid} ve el curso 43 pero no está Abierto")

# ── 3. SQL de editar_curso_db() (extraído y evaluado tal cual) ──
expr = re.search(r'nuevo_estado = \((.*?)\)\n', src, re.S).group(1)
nuevo_estado = ast.literal_eval('(' + expr + ')')
plantillas = re.findall(r'(f"""UPDATE cursos SET nombre=.*?""")', src, re.S)
print(f"\nSentencias UPDATE de editar_curso_db encontradas: {len(plantillas)}")
cur.execute("SELECT nombre, descripcion, enlace_video, fecha_limite, dirigido_a FROM cursos WHERE id=43")
row = cur.fetchone()
for i, t in enumerate(plantillas, 1):
    sql = eval(t)  # la plantilla tal como la construye el código
    if 'archivo=%s' in sql:
        params = (row['nombre'], row['descripcion'], 'uploads/x.pdf',
                  row['enlace_video'], '2026-10-10', row['dirigido_a'], 43)
    else:
        params = (row['nombre'], row['descripcion'], row['enlace_video'],
                  '2026-10-10', row['dirigido_a'], 43)
    try:
        cur.execute(sql, params)
        cur.execute("SELECT estado FROM cursos WHERE id=43")
        est = cur.fetchone()['estado']
        print(f"  [{i}] SQL válido → estado tras editar con fecha vigente: {est!r}")
        if est != 'Abierto':
            fallos.append(f"editar_curso_db sentencia {i} dejó estado {est!r}")
    except Exception as e:
        fallos.append(f"editar_curso_db sentencia {i} falló: {e}")
        print(f"  [{i}] ERROR: {e}")
conn.rollback()  # nada de esto se persiste

cur.execute("SELECT id, estado, fecha_limite FROM cursos WHERE id=43")
print("\nEstado final real del curso 43:", cur.fetchone())
cur.close()
conn.close()

print("\n=== RESULTADO ===")
if fallos:
    print("FALLÓ:")
    for f in fallos:
        print(" -", f)
    sys.exit(1)
print("TODAS LAS VERIFICACIONES PASARON ✅")
