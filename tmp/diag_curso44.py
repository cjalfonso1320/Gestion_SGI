# -*- coding: utf-8 -*-
"""Revisa el curso 'todos' reciente: fecha, asignaciones y si hay registro de correo."""
import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, 'env', 'Lib', 'site-packages'))
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE, '.env'))
import pymysql

conn = pymysql.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'),
                       password=os.getenv('MYSQL_PASSWORD'), database=os.getenv('MYSQL_DB'),
                       cursorclass=pymysql.cursors.DictCursor, connect_timeout=10)
cur = conn.cursor()

cur.execute("SHOW TABLES LIKE 'curso%'")
print('tablas:', [list(t.values())[0] for t in cur.fetchall()])

cur.execute("SELECT id, nombre, dirigido_a, estado, fecha_creacion, fecha_limite FROM cursos ORDER BY id DESC LIMIT 5")
for r in cur.fetchall():
    print(r)

cur.execute("SELECT curso_id, COUNT(*) c FROM curso_empleados GROUP BY curso_id ORDER BY curso_id DESC LIMIT 5")
print('asignaciones por curso:', cur.fetchall())

cur.execute("""SELECT COUNT(*) c FROM curso_empleados ce
               JOIN users_rrhh u ON u.id = ce.empleado_id
               WHERE ce.curso_id = 44""")
print('empleados asignados al curso 44:', cur.fetchall())

cur.execute("""SELECT COUNT(*) c FROM curso_empleados ce
               JOIN users_rrhh u ON u.id = ce.empleado_id
               WHERE ce.curso_id = 44 AND u.activo = 2""")
print('de esos, RETIRADOS:', cur.fetchall())

cur.execute("""SELECT u.id, u.correo, u.activo FROM curso_empleados ce
               JOIN users_rrhh u ON u.id = ce.empleado_id
               WHERE ce.curso_id = 44 AND u.activo = 2 LIMIT 10""")
print('muestra retirados asignados:', cur.fetchall())

# ¿empleados activos que NO quedaron asignados al curso 44?
cur.execute("""SELECT COUNT(*) c FROM users_rrhh u
               WHERE u.activo = 1 AND NOT EXISTS
               (SELECT 1 FROM curso_empleados ce WHERE ce.curso_id = 44 AND ce.empleado_id = u.id)""")
print('activos SIN asignar al curso 44:', cur.fetchall())

cur.close()
conn.close()
