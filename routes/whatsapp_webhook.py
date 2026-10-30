"""
Webhook para WhatsApp Cloud API.

Recibe actualizaciones de estado de entrega de mensajes desde Meta.
Meta exige un endpoint HTTPS público configurado en el dashboard de desarrolladores.

USO:
  1. Despliega esta aplicación en un servidor con HTTPS.
  2. En https://developers.facebook.com → tu app → WhatsApp → Configuración
     configura la URL del Webhook como:
       https://servicios.digicom.com.co/Gestion/whatsapp/webhook
  3. El Token de Verificación debe coincidir con WHATSAPP_WEBHOOK_TOKEN
     definido en tu archivo .env
  4. Suscríbete al campo "messages"
"""

import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify

webhook_bp = Blueprint("whatsapp_webhook", __name__)

WEBHOOK_LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
os.makedirs(WEBHOOK_LOG_DIR, exist_ok=True)
WEBHOOK_LOG_FILE = os.path.join(WEBHOOK_LOG_DIR, "whatsapp_webhook.log")


def _log_webhook(prefix: str, data: str):
    """Guarda en archivo y consola cualquier evento del webhook."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {prefix} | {data}"
    print(linea)
    with open(WEBHOOK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


# ─── Verificación del Webhook (GET) ──────────────────────────────────
# Meta llama a este endpoint cuando configuras o verificas el webhook.


@webhook_bp.route("/whatsapp/webhook", methods=["GET"])
def verificar_webhook():
    verify_token = os.environ.get("WHATSAPP_WEBHOOK_TOKEN")
    if not verify_token:
        _log_webhook("❌ WEBHOOK NO CONFIGURADO", "WHATSAPP_WEBHOOK_TOKEN no está definido en .env")
        return "Webhook no configurado", 403

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    _log_webhook("🔐 WEBHOOK GET", f"mode={mode} token={token} challenge={challenge}")

    if mode == "subscribe" and token == verify_token and challenge:
        _log_webhook("✅ WEBHOOK VERIFICADO", f"challenge={challenge}")
        return challenge, 200, {"Content-Type": "text/plain"}

    _log_webhook("❌ WEBHOOK RECHAZADO", f"token_invalido={token}")
    return "Verification failed", 403


# ─── Recepción de eventos (POST) ─────────────────────────────────────
# Meta envía aquí los status de entrega (sent, delivered, read, failed)
# y los mensajes entrantes.


@webhook_bp.route("/whatsapp/webhook", methods=["POST"])
def recibir_eventos():
    data = request.get_json(silent=True) or {}

    _log_webhook("📩 WEBHOOK POST", json.dumps(data, ensure_ascii=False)[:2000])

    try:
        entry = data.get("entry", [])
        for e in entry:
            changes = e.get("changes", [])
            for change in changes:
                value = change.get("value", {})

                # ── Status de mensajes enviados ──
                statuses = value.get("statuses", [])
                for st in statuses:
                    msg_id = st.get("id", "?")
                    status = st.get("status", "?")
                    timestamp = st.get("timestamp", "?")
                    recipient_id = st.get("recipient_id", "?")

                    errors = st.get("errors", [])
                    error_detail = ""
                    if errors:
                        err_code = errors[0].get("code", "?")
                        err_title = errors[0].get("title", "?")
                        err_msg = errors[0].get("message", "?")
                        error_detail = f" error={err_code} title={err_title} msg={err_msg}"

                    linea = (
                        f"📬 STATUS msg={msg_id} status={status} "
                        f"to={recipient_id} ts={timestamp}{error_detail}"
                    )
                    _log_webhook("📬", linea)

                    # Si hay error, lo mostramos con más énfasis
                    if errors:
                        _log_webhook(
                            "❌ ERROR ENTREGA",
                            f"msg_id={msg_id} codigo={err_code} descripcion={err_msg}",
                        )

                # ── Mensajes entrantes (cuando alguien responde) ──
                messages = value.get("messages", [])
                for msg in messages:
                    msg_id = msg.get("id", "?")
                    msg_from = msg.get("from", "?")
                    msg_text = (
                        msg.get("text", {}).get("body", "?")
                        if msg.get("type") == "text"
                        else "?"
                    )
                    _log_webhook(
                        "💬 MSG ENTRANTE",
                        f"from={msg_from} id={msg_id} texto={msg_text}",
                    )

    except Exception as e:
        _log_webhook("❌ ERROR PROCESANDO WEBHOOK", str(e))

    # Meta espera un 200 OK siempre, aunque ignoremos el payload
    return jsonify({"status": "ok"}), 200
