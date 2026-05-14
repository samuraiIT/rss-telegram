import httpx
import json
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

OMNI_BASE = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNI_KEY  = os.getenv("OMNIROUTE_API_KEY", "any-string")
TGAPI_URL = os.getenv("TGAPI_URL", "http://localhost:8000")

MODEL_PROFILE = os.getenv("LLM_MODEL_PROFILE", "gc/gemini-3-flash")
STREAM_CHUNK  = int(os.getenv("STREAM_CHUNK_SIZE", "80"))
STREAM_DELAY  = float(os.getenv("STREAM_UPDATE_DELAY", "0.4"))

PROFILE_SYSTEM = """Ты — аналитик Telegram-каналов. Изучи канал и верни JSON:
{"main_pain": "...", "tone": "...", "audience_portrait": "...",
 "hot_topics": ["t1","t2","t3"], "vocabulary": ["w1","w2","w3","w4","w5"],
 "segment": "...", "avg_post_length": 0, "posting_frequency": "daily|weekly|sporadic"}
Отвечай строго JSON, не добавляй markdown."""


async def cmd_profile_stream(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Stream live channel profile via OmniRoute (cheap tier, gc/gemini-3-flash)."""
    if not ctx.args:
        await update.message.reply_text("Usage: /profile <@channel_username>")
        return

    channel = ctx.args[0].lstrip("@")
    msg = await update.message.reply_text(f"⏳ Профилирую @{channel}...")

    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            info_resp = await c.get(f"{TGAPI_URL}/channel/{channel}/info")
            info_resp.raise_for_status()
            info = info_resp.json()
    except Exception as e:
        await msg.edit_text(f"❌ Не удалось получить данные канала: {e}")
        return

    user_content = (
        f"Канал: {info.get('title', channel)} (@{channel})\n"
        f"Описание: {info.get('about', '')[:500]}\n"
        f"Подписчики: {info.get('subscribers', '?')}\n"
        f"Примеры постов:\n{info.get('sample_posts', '')[:1000]}"
    )

    full_text = ""
    last_len = 0
    step_i = 0
    steps = ["📊 Анализирую аудиторию...", "🔍 Выявляю боли...", "✍️ Формирую профиль..."]

    try:
        async with httpx.AsyncClient(timeout=120.0) as c:
            async with c.stream(
                "POST",
                f"{OMNI_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {OMNI_KEY}"},
                json={
                    "model": MODEL_PROFILE,
                    "messages": [
                        {"role": "system", "content": PROFILE_SYSTEM},
                        {"role": "user", "content": user_content},
                    ],
                    "stream": True,
                    "max_tokens": 800,
                    "temperature": 0.4,
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                full_text += delta
                                if len(full_text) - last_len >= STREAM_CHUNK:
                                    step = steps[min(step_i, len(steps) - 1)]
                                    await msg.edit_text(
                                        f"@{channel} {step} [{len(full_text)} chars...]"
                                    )
                                    last_len = len(full_text)
                                    step_i += 1
                                    await asyncio.sleep(STREAM_DELAY)
                        except Exception:
                            pass

        try:
            profile = json.loads(full_text)
            result = (
                f"📋 *@{channel}*\n"
                f"🎯 Боль: {profile.get('main_pain', '?')}\n"
                f"🗣 Тон: {profile.get('tone', '?')}\n"
                f"👥 Сегмент: {profile.get('segment', '?')}\n"
                f"🔥 Топики: {', '.join(profile.get('hot_topics', []))}\n"
                f"📝 Слова: {', '.join(profile.get('vocabulary', [])[:5])}"
            )
        except Exception:
            result = f"Raw profile:\n{full_text[:800]}"

        await msg.edit_text(result, parse_mode="Markdown")

        async with httpx.AsyncClient(timeout=10.0) as c:
            await c.post(
                f"{TGAPI_URL}/internal/channel-profile",
                json={"channel_name": channel, "profile": full_text},
            )

    except Exception as e:
        await msg.edit_text(f"❌ Ошибка профилирования: {e}")
        logger.error(f"streaming_profiler error for @{channel}: {e}")
