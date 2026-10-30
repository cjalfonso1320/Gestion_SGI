# -*- coding: utf-8 -*-
"""Diagnóstico: empleados activos/retirados con correo + prueba de conexión SMTP (sin enviar)."""
import os, sys, socket, ssl

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE, '.env'))
except Exception as e:
    print('dotenv no disponible:', e)

import pymysql

host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
pwd = os.getenv('MYSQL_PASSWORD')
db = os.getenv('MYSQL_DB')
print(f'== DB {user}@{host}/{db}')

conn = pymysql.connect(host=host, user=user, password=pwd, database=db,
                       cursorclass=pymysql.cursors.DictCursor, connect_timeout=10)
cur = conn.cursor()


def q(sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()


print('\n-- users_rrhh por estado activo --')
for r in q("SELECT activo, COUNT(*) c FROM users_rrhh GROUP BY activo"):
    print(r)

print('\n-- activos con correo vacio/nulo --')
print(q("SELECT COUNT(*) c FROM users_rrhh WHERE activo = 1 AND (correo IS NULL OR TRIM(correo)='')"))

print('\n-- RETIRADOS (activo=2) con correo --')
print(q("SELECT COUNT(*) c FROM users_rrhh WHERE activo = 2 AND correo IS NOT NULL AND correo<>''"))

print('\n-- posibles retirados todavia marcados activos? (mira fecha_retiro/motivo_retiro si existen)')
cols = [r['Field'] for r in q("SHOW COLUMNS FROM users_rrhh")]
print('columnas:', cols)
for cand in ('fecha_retiro', 'motivo_retiro', 'estado', 'estado_laboral'):
    if cand in cols:
        print(f'-- {cand} por activo --')
        for r in q(f"SELECT activo, {cand} v, COUNT(*) c FROM users_rrhh GROUP BY activo, {cand} ORDER BY activo, c DESC LIMIT 30"):
            print('  ', r)

print('\n-- destinatarios que usaria dirigido_a=todos (activo=1 y con correo) --')
r = q("SELECT COUNT(DISTINCT LOWER(TRIM(correo))) c FROM users_rrhh WHERE activo=1 AND correo IS NOT NULL AND TRIM(correo)<>''")
print(r)

print('\n-- duplicados de correo entre activos --')
for r in q("""SELECT LOWER(TRIM(correo)) e, COUNT(*) c FROM users_rrhh
              WHERE activo=1 AND correo IS NOT NULL AND TRIM(correo)<>''
              GROUP BY LOWER(TRIM(correo)) HAVING c>1 ORDER BY c DESC LIMIT 10"""):
    print('  ', r)

print('\n-- correos con formato raro (no contienen @) entre activos --')
for r in q("SELECT id, correo FROM users_rrhh WHERE activo=1 AND correo IS NOT NULL AND TRIM(correo)<>'' AND correo NOT LIKE %s LIMIT 20", ('%@%',)):
    print('  ', r)

print('\n-- ultimos cursos --')
print([r['Field'] for r in q('SHOW COLUMNS FROM cursos')])
for r in q('SELECT id, nombre, dirigido_a, estado, fecha_limite FROM cursos ORDER BY id DESC LIMIT 8'):
    print('  ', r)

cur.close()
conn.close()

# ---- Prueba SMTP (solo conexión/login, NO se envía nada) ----
srv = os.getenv('SMTP_SERVER')
port = int(os.getenv('SMTP_PORT') or 587)
u = os.getenv('SMTP_USERNAME')
p = os.getenv('SMTP_PASSWORD')
print(f'\n== SMTP {srv}:{port} usuario={u}')
import smtplib
try:
    if port == 465:
        s = smtplib.SMTP_SSL(srv, port, timeout=15)
    else:
        s = smtplib.SMTP(srv, port, timeout=15)
        s.starttls()
    code, msg = s.login(u, p)
    print('login OK:', code, msg)
    s.quit()
except Exception as e:
    print('SMTP ERROR:', type(e).__name__, e)
