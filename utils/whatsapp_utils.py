"""Utilidad para enviar notificaciones por WhatsApp.

Modo actual:
  - SIMULACIÓN (default): Solo registra en consola y archivo de logs.
  - PRODUCCIÓN: Envía mensajes reales vía WhatsApp Cloud API de Meta.

Para activar el modo real, define estas variables de entorno en .env:

    WHATSAPP_MODE=real
    WHATSAPP_TOKEN=EAAT...
    WHATSAPP_PHONE_ID=123456...
    WHATSAPP_FROM=15551234567       (código de país + número, sin +)

Para probar la simulación, no hace falta configurar nada.
"""

import os
import json
from datetime import datetime

# ─────────────────────────────── Configuración ───────────────────────────────

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'whatsapp.log')

# Modo: 'simulacion' o 'real'
MODE = os.getenv('WHATSAPP_MODE', 'simulacion').lower()

# ─────────────────────────────── Utilidad interna ────────────────────────────


def _formatear_numero(numero):
    """Formatea un número telefónico a formato internacional sin el signo +.

    Elimina cualquier caracter no numérico y antepone el código de país 57
    (Colombia) si no está presente.

    Args:
        numero: Número telefónico en cualquier formato.

    Returns:
        str: Número formateado, ej: 573001234567.
    """
    limpio = ''.join(c for c in str(numero) if c.isdigit())
    if not limpio.startswith('57'):
        limpio = '57' + limpio
    return limpio


def _log(numero, mensaje, estado, detalle=None):
    """Escribe una entrada en el archivo de log y en consola.

    Args:
        numero: Número telefónico destino.
        mensaje: Contenido del mensaje enviado.
        estado: Estado del envío (simulación, enviado, error).
        detalle: Información adicional opcional (ID del mensaje, error).
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    linea = f"[{timestamp}] {estado} | {numero} | {mensaje[:80]}"
    if detalle:
        linea += f" | {detalle}"
    print(linea)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(linea + '\n')


# ───────────────────────── Modo simulación ────────────────────────────────────


def enviar_whatsapp_simulacion(numero, mensaje):
    """Simula el envío de un mensaje de WhatsApp sin enviarlo realmente.

    Útil para desarrollo y pruebas. Solo registra en consola y archivo.

    Args:
        numero: Número telefónico destino.
        mensaje: Contenido del mensaje a enviar.

    Returns:
        bool: True siempre (simulación exitosa).
    """
    num = _formatear_numero(numero)
    _log(num, mensaje, '📲 [SIMULACIÓN]')
    return True


# ───────────────────────── Modo real (Meta Cloud API) ────────────────────────


def enviar_whatsapp_meta(numero, mensaje):
    """Envía un mensaje de texto real vía WhatsApp Cloud API de Meta.

    Requiere variables de entorno:
      WHATSAPP_TOKEN    → Token de acceso permanente (System User)
      WHATSAPP_PHONE_ID → ID del número de teléfono en Meta
      WHATSAPP_FROM     → Número emisor (código de país + número, sin +)

    Args:
        numero: Número telefónico destino en cualquier formato.
        mensaje: Contenido del mensaje de texto a enviar.

    Returns:
        bool: True si el mensaje se envió correctamente, False en caso contrario.
    """
    token = os.getenv('WHATSAPP_TOKEN')
    phone_id = os.getenv('WHATSAPP_PHONE_ID')
    from_number = os.getenv('WHATSAPP_FROM')

    if not token or not phone_id or not from_number:
        error_msg = "❌ WHATSAPP_TOKEN, WHATSAPP_PHONE_ID y WHATSAPP_FROM son obligatorios en modo real."
        print(error_msg)
        return False

    num = _formatear_numero(numero)
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": num,
        "type": "text",
        "text": {"preview_url": False, "body": mensaje}
    }

    try:
        import requests
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        result = response.json()

        if response.ok:
            msg_id = result.get('messages', [{}])[0].get('id', 'sin-id')
            _log(num, mensaje, '✅ [ENVIADO]', f"ID: {msg_id}")
            return True
        else:
            error_detail = result.get('error', {}).get('message', str(result))
            _log(num, mensaje, '❌ [ERROR API]', error_detail)
            return False

    except ImportError:
        _log(num, mensaje, '❌ [ERROR]', 'requests no instalado. Corre: pip install requests')
        return False
    except Exception as e:
        _log(num, mensaje, '❌ [ERROR]', str(e))
        return False


# ─────────────────────────── Función principal ────────────────────────────────


def enviar_whatsapp(numero, mensaje):
    """Punto de entrada único para enviar mensajes de WhatsApp.

    Decide automáticamente si simular o enviar real según la variable de
    entorno WHATSAPP_MODE.

    Args:
        numero: Número telefónico destino.
        mensaje: Contenido del mensaje a enviar.

    Returns:
        bool: True si el mensaje se procesó correctamente.
    """
    if MODE == 'real':
        return enviar_whatsapp_meta(numero, mensaje)
    else:
        return enviar_whatsapp_simulacion(numero, mensaje)


# ─────────────────────── Notificaciones de cursos ────────────────────────────


def enviar_notificacion_curso_whatsapp(curso_nombre, fecha_limite, destinatarios):
    """Envía notificación de nuevo curso por WhatsApp a una lista de destinatarios.

    Construye un mensaje formateado con la información del curso y lo envía
    a cada destinatario usando el modo configurado (simulación o real).

    Args:
        curso_nombre: Nombre del curso a notificar.
        fecha_limite: Fecha límite del curso en formato de texto.
        destinatarios: Lista de números de teléfono de los destinatarios.

    Returns:
        int: Cantidad de mensajes enviados exitosamente.
    """
    try:
        if not destinatarios:
            print("⚠️ No hay destinatarios para notificar por WhatsApp")
            return 0

        mensaje = (
            f"🎓 *Nuevo curso disponible en SGI*\n\n"
            f"📘 *{curso_nombre}*\n\n"
            f"Has sido asignado a este curso. "
            f"Ingresa al sistema para ver el material y completar la evaluación.\n\n"
            f"📅 *Fecha límite:* {fecha_limite}\n\n"
            f"🔗 https://servicios.digicom.com.co/Gestion"
        )

        exitosos = 0
        destinatarios_unicos = list(set(destinatarios))
        total = len(destinatarios_unicos)

        for idx, num in enumerate(destinatarios_unicos, start=1):
            print(f"  [{idx}/{total}] Enviando WhatsApp a {num}...")
            ok = enviar_whatsapp(num, mensaje)
            if ok:
                exitosos += 1

        print(f"📊 WhatsApp: {exitosos}/{total} enviados exitosamente")
        return exitosos
    except Exception as e:
        print(f"❌ Error inesperado en notificación WhatsApp: {e}")
        import traceback
        traceback.print_exc()
        return 0


def enviar_notificacion_prorroga_whatsapp(empleado_nombre, curso_nombre, nueva_fecha_limite, numero_celular):
    """Envía notificación de prórroga por WhatsApp a un colaborador."""
    try:
        mensaje = (
            f"⏳ *Prórroga Concedida en Aula Virtual SGI*\n\n"
            f"Hola *{empleado_nombre}*,\n"
            f"Se ha ampliado tu plazo para realizar el curso:\n"
            f"📘 *{curso_nombre}*\n\n"
            f"📅 *Nueva fecha límite:* {nueva_fecha_limite}\n\n"
            f"Por favor ingresa y completa tu evaluación a tiempo:\n"
            f"🔗 https://servicios.digicom.com.co/Gestion"
        )
        return enviar_whatsapp(numero_celular, mensaje)
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp de prórroga: {e}")
        return False

