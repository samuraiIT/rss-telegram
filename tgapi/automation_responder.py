import httpx
import json
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from tgapi.security import sanitize_user_input

logger = logging.getLogger(__name__)

OMNI_BASE = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNI_KEY  = os.getenv("OMNIROUTE_API_KEY", "any-string")
TGAPI_URL = os.getenv("TGAPI_URL", "http://localhost:8000")

MODEL_DIALOG = os.getenv("LLM_MODEL_DIALOG", "ws/claude-sonnet-4-6")

AUTOMATION_PROMPT = """Ты — GTM-ассистент в Telegram. Правила:
1. Если вопрос о продукте — отвечай кратко и по делу (1 абзац).
2. Если нужна живая консультация — предложи созвон, escalate=true.
3. Если пользователь не хочет общаться — optout=true.
4. Не притворяйся AI явно. Пиши как живой ассистент.

Верни строго JSON:
{"reply": "...", "optout": false, "escalate": false}"""


async def handle_auto_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Auto-reply with dialogue history. Canon C9, C1."""
    user = update.message.from_user
    text = update.message.text or ""

    sanitized, suspicious = sanitize_user_input(text, maxlen=500)
    if suspicious:
        logger.warning(f"Suspicious input in auto_reply from user_id={user.id}")
        return

    history = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            hist_resp = await c.get(f"{TGAPI_URL}/dialogue/{user.id}/history?limit=4")
            if hist_resp.status_code == 200:
                history = hist_resp.json().get("messages", [])
    except Exception:
        pass

    messages = [{"role": "system", "content": AUTOMATION_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": sanitized})

    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            resp = await c.post(
                f"{OMNI_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {OMNI_KEY}"},
                json={
                    "model": MODEL_DIALOG,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "max_tokens": 256,
                    "temperature": 0.7,
                },
            )
            resp.raise_for_status()
            data = json.loads(resp.json()["choices"][0]["message"]["content"])

        reply   = data.get("reply", "Спасибо за сообщение!")
        optout  = data.get("optout", False)
        escalate = data.get("escalate", False)

        async with httpx.AsyncClient(timeout=5.0) as c:
            status = "escalated" if escalate else "replied"
            if optout:
                await c.post(f"{TGAPI_URL}/audience/{user.id}/optout")
                status = "optout"
            await c.post(f"{TGAPI_URL}/audience/{user.id}/status", json={"status": status})
            await c.post(f"{TGAPI_URL}/dialogue/{user.id}/append", json={"role": "user", "content": sanitized})
            await c.post(f"{TGAPI_URL}/dialogue/{user.id}/append", json={"role": "assistant", "content": reply})

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"auto_reply error for user_id={user.id}: {e}")
