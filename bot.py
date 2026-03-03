import asyncio
import logging
import config
import db
from parser import fetch_new_messages, start_client, stop_client
from filter import matches_keywords
from ai_processor import evaluate_and_summarize
from publisher import publish_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def process_channel(channel: str):
    """Process a single channel: fetch, filter, evaluate, publish."""
    last_id = await db.get_last_message_id(channel)
    messages = await fetch_new_messages(channel, min_id=last_id)

    for msg in messages:
        if await db.is_processed(channel, msg["id"]):
            continue

        # Keyword filter
        if not matches_keywords(msg["text"]):
            await db.mark_processed(channel, msg["id"], score=0)
            logger.debug(f"Skipped @{channel}/{msg['id']} — no keyword match")
            continue

        # AI evaluation + summary
        result = await evaluate_and_summarize(msg["text"])
        if result is None:
            logger.warning(f"AI processing failed for @{channel}/{msg['id']}, skipping")
            continue

        await db.mark_processed(channel, msg["id"], score=result["score"])

        if not result["relevant"]:
            logger.info(f"Skipped @{channel}/{msg['id']} — score {result['score']}")
            continue

        # Publish
        await publish_summary(channel, msg["link"], result["summary"], result["score"])
        # Small delay between posts to avoid flooding
        await asyncio.sleep(2)


async def run_cycle():
    """Run one full cycle across all source channels."""
    logger.info("Starting new cycle...")
    for channel in config.SOURCE_CHANNELS:
        try:
            await process_channel(channel)
        except Exception as e:
            logger.error(f"Error processing @{channel}: {e}")
    logger.info("Cycle complete")


async def main():
    logger.info("Bot starting...")
    await db.init_db()
    await start_client()

    try:
        while True:
            await run_cycle()
            logger.info(f"Sleeping for {config.CHECK_INTERVAL_MINUTES} minutes...")
            await asyncio.sleep(config.CHECK_INTERVAL_MINUTES * 60)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await stop_client()


if __name__ == "__main__":
    asyncio.run(main())
