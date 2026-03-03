import asyncio
import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import RetryAfter, TelegramError
import config

logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)


async def publish_summary(channel: str, message_link: str, summary: str, score: int):
    """Publish a formatted summary to the target channel."""
    text = (
        f"<b>AI/ML Digest</b> | Score: {score}/10\n\n"
        f"{summary}\n\n"
        f'<a href="{message_link}">Источник: @{channel}</a>'
    )

    try:
        await bot.send_message(
            chat_id=config.TARGET_CHANNEL,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
        )
        logger.info(f"Published summary from @{channel} to {config.TARGET_CHANNEL}")
    except RetryAfter as e:
        logger.warning(f"Rate limited, retrying after {e.retry_after}s")
        await asyncio.sleep(e.retry_after)
        await bot.send_message(
            chat_id=config.TARGET_CHANNEL,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
        )
    except TelegramError as e:
        logger.error(f"Telegram error publishing: {e}")
