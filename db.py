import aiosqlite
import logging
from datetime import datetime

DB_PATH = "processed_messages.db"

logger = logging.getLogger(__name__)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS processed_messages (
                channel TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                score INTEGER,
                PRIMARY KEY (channel, message_id)
            )
        """)
        await db.commit()
    logger.info("Database initialized")


async def is_processed(channel: str, message_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM processed_messages WHERE channel = ? AND message_id = ?",
            (channel, message_id),
        )
        row = await cursor.fetchone()
        return row is not None


async def mark_processed(channel: str, message_id: int, score: int | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO processed_messages (channel, message_id, timestamp, score) VALUES (?, ?, ?, ?)",
            (channel, message_id, datetime.utcnow().isoformat(), score),
        )
        await db.commit()


async def get_last_message_id(channel: str) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT MAX(message_id) FROM processed_messages WHERE channel = ?",
            (channel,),
        )
        row = await cursor.fetchone()
        return row[0] if row and row[0] is not None else None
