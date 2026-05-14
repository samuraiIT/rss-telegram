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

MODEL_QUALIFY = os.getenv("LLM_MODEL_QUALIFY", "ws/claude-haiku-4-5")

QUALIFY_PROMPT = """Ты — GTM-квалификатор входящих Telegram-сообщений.
Определи тему и является ли сообщение горячим лидом.
Ответь строго JSON без markdown:
{"topic": "it|trading|marketing|other", "hot": true|false, "reply": "<ответ 1 предложение>"}"""


async def handle_guest_mention(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Canon C9: sanitize → qualify via OmniRoute (cheap tier) → save lead."""
    msg = update.message
    if not msg:
        return

    bot_username = ctx.bot.username
    is_mention = msg.entities and any(
        e.type == "mention" and msg.text[e.offset:e.offset + e.length] == f"@{bot_username}"
        for e in msg.entities
    )
    if not is_mention:
        return

    sanitized, suspicious = sanitize_user_input(msg.text, maxlen=500)
    if suspicious:
        logger.warning(f"Suspicious input from user_id={msg.from_user.id}, blocked.")
        return

    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            resp = await c.post(
                f"{OMNI_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {OMNI_KEY}"},
                json={
                    "model": MODEL_QUALIFY,
                    "messages": [
                        {"role": "system", "content": QUALIFY_PROMPT},
                        {"role": "user", "content": sanitized},
                    ],
                    "response_format": {"type": "json_object"},
                    "max_tokens": 150,
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            data = json.loads(resp.json()["choices"][0]["message"]["content"])

        if data.get("hot"):
            async with httpx.AsyncClient(timeout=5.0) as c:
                await c.post(
                    f"{TGAPI_URL}/internal/lead",
                    json={
                        "user_id": msg.from_user.id,
                        "username": msg.from_user.username,
                        "source_channel": msg.chat_id,
                        "segment": data.get("topic", "other"),
                        "activity_score": 3,
                        "is_hot": True,
                        "raw_text": sanitized,
                    },
                )

        await msg.reply_text(data.get("reply", "Спасибо за сообщение!"))

    except Exception as e:
        logger.error(f"guest_handler error: {e}")
