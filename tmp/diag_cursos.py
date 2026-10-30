"""Diagnóstico SOLO LECTURA: ¿por qué un empleado no ve su curso asignado?"""
import os
import sys
import mysql.connector

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config  # noqa: E402

conn = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB,
)
cur = conn.cursor(dictionary=True)

print("== ÚLTIMOS 5 CURSOS ==")
cur.execute("""
    SELECT id, nombre, dirigido_a, estado, fecha_limite, creado_por
    FROM cursos ORDER BY id DESC LIMIT 5""")
cursos = cur.fetchall()
for c in cursos:
    print(c)

print("\n== ASIGNACIONES POR CURSO (curso_empleados / curso_roles) ==")
for c in cursos:
    cur.execute("SELECT COUNT(*) n FROM curso_empleados WHERE curso_id=%s", (c['id'],))
    ce = cur.fetchone()['n']
    cur.execute("SELECT COUNT(*) n FROM curso_roles WHERE curso_id=%s", (c['id'],))
    cr = cur.fetchone()['n']
    print(f"curso {c['id']} ({c['nombre'][:40]!r}, dirigido_a={c['dirigido_a']}): "
          f"curso_empleados={ce}, curso_roles={cr}")

print("\n== ESQUEMA curso_empleados ==")
cur.execute("SHOW CREATE TABLE curso_empleados")
print(cur.fetchone())

if cursos:
    cid = cursos[0]['id']
    print(f"\n== EMPLEADOS ASIGNADOS AL CURSO {cid} ==")
    cur.execute("""
        SELECT ce.empleado_id, u.identificacion, u.nombres, u.apellidos,
               u.activo, u.sgi_rol_id, u.correo
        FROM curso_empleados ce
        LEFT JOIN users_rrhh u ON u.id = ce.empleado_id
        WHERE ce.curso_id = %s""", (cid,))
    rows = cur.fetchall()
    for r in rows:
        print(r)
        # Simular la consulta del portal
        cur.execute("""
            SELECT id, sgi_rol_id FROM users_rrhh
            WHERE identificacion = %s AND activo = 1""",
            (r['identificacion'],))
        match = cur.fetchone()
        if not match:
            print("   !! PORTAL: users_rrhh no encontró esta identificacion con activo=1")
        else:
            if match['id'] != r['empleado_id']:
                print(f"   !! PORTAL: identificacion resuelve al id {match['id']}, "
                      f"pero la asignación usa id {r['empleado_id']}")
            cur.execute("""
                SELECT c.id, c.nombre FROM cursos c
                LEFT JOIN curso_empleados ce ON c.id = ce.curso_id AND ce.empleado_id = %s
                LEFT JOIN curso_roles cr ON c.id = cr.curso_id AND cr.rol_id = %s
                WHERE c.id = %s AND (ce.empleado_id IS NOT NULL OR cr.rol_id IS NOT NULL
                    OR (NOT EXISTS (SELECT 1 FROM curso_empleados WHERE curso_id = c.id)
                        AND NOT EXISTS (SELECT 1 FROM curso_roles WHERE curso_id = c.id)))""",
                (match['id'], match['sgi_rol_id'] or 0, cid))
            visible = cur.fetchone()
            print(f"   PORTAL ve el curso: {'SÍ' if visible else 'NO'} "
                  f"(sgi_rol_id={match['sgi_rol_id']})")

print("\n== ESTADO: cursos sin NINGUNA asignación (visibles para todos) ==")
cur.execute("""
    SELECT c.id, c.nombre FROM cursos c
    WHERE NOT EXISTS (SELECT 1 FROM curso_empleados ce WHERE ce.curso_id = c.id)
      AND NOT EXISTS (SELECT 1 FROM curso_roles cr WHERE cr.curso_id = c.id)""")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
