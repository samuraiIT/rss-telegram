import httpx
import json
import os
import logging
from telegram import Update, Bot
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

OMNI_BASE = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNI_KEY  = os.getenv("OMNIROUTE_API_KEY", "any-string")
TGAPI_URL = os.getenv("TGAPI_URL", "http://localhost:8000")

TRUSTED_BOT_IDS: set[int] = set(
    map(int, filter(None, os.getenv("TRUSTED_BOT_IDS", "").split(",")))
)
QUALIFY_BOT_TOKEN = os.getenv("QUALIFY_BOT_TOKEN", "")

MODEL_HUMANIZE = os.getenv("LLM_MODEL_HUMANIZE", "ws/claude-haiku-4-5")

HUMANIZE_PROMPT = """Ты — Telegram-копирайтер. Перепиши текст живым человеческим языком:
- 40–120 символов
- Без AI-клише: leverage, delve, synergy, tapestry
- Без жёстких CTA
- Звучи как живой человек
Верни только готовый текст."""


async def handle_bot_pipeline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Humanize → Qualify bot-to-bot pipeline. Canon C2, C9."""
    sender = update.message.from_user if update.message else None
    if not sender or not sender.is_bot or sender.id not in TRUSTED_BOT_IDS:
        return

    raw = update.message.text or ""
    if "::" not in raw:
        return

    step, payload_str = raw.split("::", 1)
    try:
        payload = json.loads(payload_str)
    except Exception:
        return

    chat_id = update.message.chat_id

    if step == "HUMANIZE":
        try:
            async with httpx.AsyncClient(timeout=30.0) as c:
                resp = await c.post(
                    f"{OMNI_BASE}/chat/completions",
                    headers={"Authorization": f"Bearer {OMNI_KEY}"},
                    json={
                        "model": MODEL_HUMANIZE,
                        "messages": [
                            {"role": "system", "content": HUMANIZE_PROMPT},
                            {"role": "user", "content": payload.get("text", "")},
                        ],
                        "max_tokens": 256,
                        "temperature": 0.7,
                    },
                )
                resp.raise_for_status()
                humanized = resp.json()["choices"][0]["message"]["content"].strip()

            qualify_bot = Bot(token=QUALIFY_BOT_TOKEN)
            await qualify_bot.send_message(
                chat_id=chat_id,
                text=f"QUALIFY::{json.dumps({'text': humanized, 'user_id': payload.get('user_id'), 'channel_id': payload.get('channel_id')})}",
            )
        except Exception as e:
            logger.error(f"bot2bot HUMANIZE error: {e}")

    elif step == "QUALIFY":
        user_id = payload.get("user_id")
        try:
            async with httpx.AsyncClient(timeout=5.0) as c:
                r = await c.get(f"{TGAPI_URL}/audience/{user_id}/score")
                score = r.json().get("lead_score", 0) if r.status_code == 200 else 0

            result = "SEND_APPROVED" if score > 50 else "SEND_DEFERRED"
            await ctx.bot.send_message(
                chat_id=chat_id,
                text=f"{result}::{json.dumps({**payload, 'score': score})}",
            )
        except Exception as e:
            logger.error(f"bot2bot QUALIFY error: {e}")
