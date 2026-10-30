# -*- coding: utf-8 -*-
"""Lista todos los cursos con fecha, dirigido_a y nº de asignaciones."""
import os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'env', 'Lib', 'site-packages'))
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE, '.env'))
import pymysql
conn = pymysql.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'),
                       password=os.getenv('MYSQL_PASSWORD'), database=os.getenv('MYSQL_DB'),
                       cursorclass=pymysql.cursors.DictCursor, connect_timeout=10)
cur = conn.cursor()
cur.execute("""
    SELECT c.id, c.nombre, c.dirigido_a, c.estado, c.fecha_creacion, c.fecha_limite,
           (SELECT COUNT(*) FROM curso_empleados ce WHERE ce.curso_id = c.id) n_emp,
           (SELECT COUNT(*) FROM curso_roles cr WHERE cr.curso_id = c.id) n_roles
    FROM cursos c ORDER BY c.id DESC LIMIT 20""")
for r in cur.fetchall():
    print(r)
cur.close(); conn.close()
