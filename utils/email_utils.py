"""Utilidades para el envío de correos electrónicos.

Proporciona funciones para enviar notificaciones por correo utilizando
SMTP con soporte para STARTTLS y SSL. Incluye plantillas HTML para
notificaciones de cursos del sistema SGI.

Configuración requerida (variables de entorno):
    SMTP_SERVER: Servidor SMTP (ej: smtp.gmail.com).
    SMTP_PORT: Puerto SMTP (587 para STARTTLS, 465 para SSL).
    SMTP_USERNAME: Usuario de autenticación SMTP.
    SMTP_PASSWORD: Contraseña de autenticación SMTP.
"""

import smtplib
import mimetypes
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime
import os
import logging
import logging.handlers


# --- LOGGER PARA CORREOS ---
EMAIL_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
EMAIL_LOG_FILE = os.path.join(EMAIL_LOG_DIR, 'email.log')
os.makedirs(EMAIL_LOG_DIR, exist_ok=True)

_email_logger = None
def _get_email_logger():
    global _email_logger
    if _email_logger is not None:
        return _email_logger
    _email_logger = logging.getLogger('email')
    _email_logger.setLevel(logging.DEBUG)
    if not _email_logger.handlers:
        try:
            os.makedirs(EMAIL_LOG_DIR, exist_ok=True)
            handler = logging.handlers.RotatingFileHandler(
                EMAIL_LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
            )
            handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            _email_logger.addHandler(handler)
        except Exception as e:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            _email_logger.addHandler(stream_handler)
            _email_logger.warning(f'⚠️ No se pudo inicializar archivo de log de correos ({e}), usando stream')
    _email_logger.info('📧 Logger de correos iniciado')
    return _email_logger


def enviar_correo(destinatarios, asunto, mensaje_html, mensaje_texto=None, adjuntos=None):
    """Envía un correo electrónico a múltiples destinatarios.

    Utiliza la configuración SMTP definida en variables de entorno.
    Soporta conexiones STARTTLS (puerto 587) y SSL directo (puerto 465).

    Args:
        destinatarios: Lista de direcciones de correo electrónico.
        asunto: Asunto del mensaje.
        mensaje_html: Contenido del correo en formato HTML.
        mensaje_texto: Contenido alternativo en texto plano (opcional).
        adjuntos: Lista de tuplas (nombre de archivo, contenido en bytes).

    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario.
    """
    log = _get_email_logger()

    if not destinatarios:
        log.warning('⚠️ No hay destinatarios para enviar el correo')
        return False

    log.info(f'🔄 Intentando enviar correo a {len(destinatarios)} destinatario(s): {destinatarios}')

    try:
        smtp_server = os.getenv('SMTP_SERVER') or current_app.config.get('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT') or current_app.config.get('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME') or current_app.config.get('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD') or current_app.config.get('SMTP_PASSWORD')

        log.info(f'📧 SMTP: servidor={smtp_server}, puerto={smtp_port}, usuario={smtp_username}')

        if not smtp_server or not smtp_username or not smtp_password:
            log.error('❌ Configuración SMTP incompleta. Verifica las variables de entorno SMTP_SERVER, SMTP_USERNAME y SMTP_PASSWORD en el servidor.')
            log.error('   En desarrollo: el archivo .env debe estar en la raíz del proyecto.')
            log.error('   En producción (IIS): configura las variables como variables de entorno del sistema Windows.')
            return False

        if adjuntos:
            msg = MIMEMultipart('mixed')
            cuerpo = MIMEMultipart('alternative')
            msg.attach(cuerpo)
        else:
            msg = MIMEMultipart('alternative')
            cuerpo = msg

        msg['Subject'] = Header(asunto, 'utf-8')
        msg['From'] = smtp_username
        msg['To'] = ', '.join(destinatarios)

        if mensaje_texto:
            part1 = MIMEText(mensaje_texto, 'plain', 'utf-8')
            cuerpo.attach(part1)

        part2 = MIMEText(mensaje_html, 'html', 'utf-8')
        cuerpo.attach(part2)

        for nombre, contenido in adjuntos or []:
            if not contenido:
                continue
            ctype, encoding = mimetypes.guess_type(nombre)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            adjunto = MIMEBase(maintype, subtype)
            adjunto.set_payload(contenido)
            encoders.encode_base64(adjunto)
            adjunto.add_header('Content-Disposition', 'attachment', filename=nombre)
            msg.attach(adjunto)

        log.info(f'📨 Conectando a {smtp_server}:{smtp_port}...')

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
            log.info('🔒 Usando conexión SSL directa (puerto 465)')
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            log.info('🔒 Usando STARTTLS')

        log.info('🔑 Iniciando sesión SMTP...')
        server.login(smtp_username, smtp_password)

        log.info('📤 Enviando correo...')
        rechazados = server.sendmail(smtp_username, destinatarios, msg.as_string())
        server.quit()

        enviados = len(destinatarios) - len(rechazados)
        if rechazados:
            # No registrar las direcciones personales de los destinatarios.
            log.error(f'⚠️ SMTP rechazó {len(rechazados)} de {len(destinatarios)} destinatario(s)')
        log.info(f'📤 SMTP aceptó {enviados} de {len(destinatarios)} destinatario(s)')
        return enviados > 0 and not rechazados

    except smtplib.SMTPAuthenticationError:
        log.error('❌ Error de autenticación SMTP. Verifica SMTP_USERNAME y SMTP_PASSWORD.')
        return False
    except smtplib.SMTPConnectError as e:
        log.error(f'❌ No se pudo conectar al servidor SMTP {smtp_server}:{smtp_port}. Verifica que el servidor esté accesible y el puerto sea correcto. Error: {e}')
        return False
    except smtplib.SMTPServerDisconnected:
        log.error(f'❌ El servidor SMTP {smtp_server} cerró la conexión inesperadamente.')
        return False
    except Exception as e:
        log.error(f'❌ Error al enviar correo: {str(e)}')
        import traceback
        log.error(f'📋 Traceback: {traceback.format_exc()}')
        return False


def enviar_notificacion_curso(curso_nombre, curso_descripcion, fecha_limite, destinatarios):
    """Envía notificación de nuevo curso a los destinatarios por correo.

    Construye un correo HTML con diseño responsivo que incluye el nombre
    del curso, la descripción, la fecha límite y un enlace al sistema SGI.

    Args:
        curso_nombre: Nombre del curso asignado.
        curso_descripcion: Descripción del contenido del curso.
        fecha_limite: Fecha límite para completar el curso.
        destinatarios: Lista de correos electrónicos de los destinatarios.
    """
    asunto = f"🎓 Nuevo curso asignado: {curso_nombre}"

    mensaje_html = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nuevo Curso</title>
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f4f8;padding:30px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.10);">
          <tr>
            <td style="background-color:#1e3a8a;background:linear-gradient(135deg,#1e3a8a,#2563eb);padding:40px 36px 32px;text-align:center;">
              <div style="font-size:48px;line-height:1;margin-bottom:12px;">🎓</div>
              <h1 style="margin:0 0 6px;color:#ffffff;font-size:26px;font-weight:700;letter-spacing:0.3px;">
                ¡Nuevo Curso Asignado!
              </h1>
              <p style="margin:0;color:#bfdbfe;font-size:15px;font-weight:400;">
                Has sido inscrito a un nuevo curso en el SGI
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:36px 36px 28px;">
              <p style="margin:0 0 22px;color:#1e293b;font-size:16px;line-height:1.6;">
                Hola, te informamos que se te ha asignado un nuevo curso en el
                <strong>Sistema de Gestión Integral (SGI)</strong>.
              </p>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:24px;">
                <tr>
                  <td style="padding:24px;">
                    <h2 style="margin:0 0 16px;color:#1e3a8a;font-size:20px;font-weight:700;line-height:1.3;">
                      📘 {curso_nombre}
                    </h2>
                    <table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;margin-bottom:14px;">
                      <tr>
                        <td valign="top" style="width:24px;padding:0 8px 6px 0;color:#64748b;font-size:16px;">📝</td>
                        <td style="padding-bottom:6px;">
                          <p style="margin:0;color:#334155;font-size:14px;line-height:1.5;">
                            <strong style="color:#1e293b;">Descripción:</strong><br>
                            {curso_descripcion}
                          </p>
                        </td>
                      </tr>
                    </table>
                    <table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">
                      <tr>
                        <td valign="top" style="width:24px;padding:0 8px 0 0;color:#64748b;font-size:16px;">⏰</td>
                        <td>
                          <p style="margin:0;color:#334155;font-size:14px;line-height:1.5;">
                            <strong style="color:#1e293b;">Fecha límite:</strong><br>
                            <span style="font-weight:600;color:#dc2626;">{fecha_limite}</span>
                          </p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 22px;color:#475569;font-size:14px;line-height:1.6;">
                Ingresa al sistema para acceder al material de estudio, ver el
                video del curso y presentar la evaluación correspondiente.
              </p>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:4px 0 10px;">
                    <table role="presentation" cellpadding="0" cellspacing="0">
                      <tr>
                        <td align="center" style="border-radius:10px;">
                          <a href="https://servicios.digicom.com.co/Gestion"
                             style="display:inline-block;padding:14px 40px;background-color:#2563eb;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;border-radius:10px;box-shadow:0 4px 12px rgba(37,99,235,0.30);">
                            🚀 Acceder al Sistema
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              <p style="margin:20px 0 0;color:#94a3b8;font-size:13px;line-height:1.5;text-align:center;border-top:1px solid #e2e8f0;padding-top:18px;">
                Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:<br>
                <span style="color:#3b82f6;word-break:break-all;">https://servicios.digicom.com.co/Gestion</span>
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color:#f8fafc;padding:22px 36px;text-align:center;border-top:1px solid #e2e8f0;">
              <p style="margin:0 0 6px;color:#64748b;font-size:12px;line-height:1.5;">
                <strong>Sistema de Gestión Integral (SGI)</strong><br>
                Este es un mensaje automático, por favor no responder.<br>
                © {datetime.now().year} Digicom Colombia. Todos los derechos reservados.
              </p>
            </td>
          </tr>
        </table>
        <p style="margin:16px 0 0;color:#94a3b8;font-size:11px;text-align:center;">
          Si no visualizas correctamente este correo, ábrelo desde un cliente de correo compatible.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    mensaje_texto = f"""
🎓 NUEVO CURSO ASIGNADO

Has sido inscrito al curso:
  📘 {curso_nombre}

  📝 Descripción: {curso_descripcion}
  ⏰ Fecha límite: {fecha_limite}

Ingresa al sistema SGI para acceder al material y presentar la evaluación:
https://servicios.digicom.com.co/Gestion

---
Sistema de Gestión Integral (SGI)
© {datetime.now().year} Digicom Colombia
"""

    return enviar_correo(destinatarios, asunto, mensaje_html, mensaje_texto)


def enviar_notificacion_prorroga(empleado_nombre, curso_nombre, nueva_fecha_limite, motivo, destinatario_email):
    """Envía correo al colaborador notificando que se le concedió prórroga individual."""
    asunto = f"⏳ Prórroga Concedida: {curso_nombre} - SGI"

    mensaje_html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="font-family:'Segoe UI',Roboto,sans-serif;background:#f1f5f9;margin:0;padding:24px;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.08);">
    <tr>
      <td style="background:linear-gradient(135deg,#d97706,#b45309);padding:24px 32px;color:#fff;">
        <h1 style="margin:0;font-size:22px;font-weight:700;">⏳ Prórroga Concedida</h1>
        <p style="margin:4px 0 0;font-size:14px;color:#fef3c7;">Se ha ampliado tu plazo para completar el curso en el SGI</p>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 32px;">
        <p style="font-size:15px;color:#1e293b;margin:0 0 16px;">
          Hola <strong>{empleado_nombre}</strong>,
        </p>
        <p style="font-size:14px;color:#475569;margin:0 0 20px;line-height:1.5;">
          Te informamos que se te ha concedido una <strong>prórroga individual</strong> para que puedas ingresar, consultar el material de estudio y presentar la evaluación del curso asignado.
        </p>
        <div style="background:#fef3c7;border-left:4px solid #f59e0b;padding:16px 20px;border-radius:6px;margin-bottom:24px;">
          <p style="margin:0 0 8px;font-size:16px;font-weight:700;color:#92400e;">📘 {curso_nombre}</p>
          <p style="margin:0 0 6px;font-size:14px;color:#78350f;"><strong>Nueva fecha límite:</strong> <span style="font-size:15px;font-weight:700;color:#b45309;">{nueva_fecha_limite}</span></p>
          <p style="margin:0;font-size:13px;color:#92400e;"><strong>Motivo / Observación:</strong> {motivo}</p>
        </div>
        <div style="text-align:center;margin:28px 0 20px;">
          <a href="https://servicios.digicom.com.co/Gestion" style="display:inline-block;padding:12px 32px;background:#2563eb;color:#fff;font-weight:600;font-size:15px;text-decoration:none;border-radius:8px;box-shadow:0 3px 8px rgba(37,99,235,0.3);">
            🚀 Ingresar al Aula Virtual
          </a>
        </div>
      </td>
    </tr>
    <tr>
      <td style="background:#f8fafc;padding:16px 32px;text-align:center;font-size:12px;color:#64748b;border-top:1px solid #e2e8f0;">
        Sistema de Gestión Integral (SGI) • Digicom Colombia
      </td>
    </tr>
  </table>
</body>
</html>"""

    mensaje_texto = f"""
⏳ PRÓRROGA INDIVIDUAL CONCEDIDA

Hola {empleado_nombre},

Se te ha concedido una prórroga para presentar el curso:
📘 {curso_nombre}

📅 Nueva Fecha Límite: {nueva_fecha_limite}
📝 Motivo: {motivo}

Ingresa al sistema para realizar tu evaluación:
https://servicios.digicom.com.co/Gestion
"""
    return enviar_correo([destinatario_email], asunto, mensaje_html, mensaje_texto)
