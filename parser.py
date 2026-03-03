import logging
from telethon import TelegramClient
from telethon.tl.types import Message
import config

logger = logging.getLogger(__name__)

client = TelegramClient("session", config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)


async def start_client():
    await client.start(phone=config.TELEGRAM_PHONE)
    logger.info("Telethon client started")


async def stop_client():
    await client.disconnect()
    logger.info("Telethon client disconnected")


async def fetch_new_messages(channel: str, min_id: int | None = None, limit: int = 50) -> list[dict]:
    """Fetch new messages from a public channel since min_id."""
    messages = []
    try:
        entity = await client.get_entity(channel)
        kwargs = {"entity": entity, "limit": limit}
        if min_id is not None:
            kwargs["min_id"] = min_id

        async for msg in client.iter_messages(**kwargs):
            if not isinstance(msg, Message) or not msg.text:
                continue
            messages.append({
                "channel": channel,
                "id": msg.id,
                "text": msg.text,
                "date": msg.date.isoformat(),
                "link": f"https://t.me/{channel}/{msg.id}",
            })

        logger.info(f"Fetched {len(messages)} new messages from @{channel}")
    except Exception as e:
        logger.error(f"Error fetching from @{channel}: {e}")

    return messages
