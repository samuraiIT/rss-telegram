"""Register all new-feature handlers on the PTB Application."""
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)
from tgapi.handlers.guest_handler import handle_guest_mention
from tgapi.handlers.bot2bot import handle_bot_pipeline
from tgapi.handlers.streaming_profiler import cmd_profile_stream
from tgapi.automation_responder import handle_auto_reply


def register_new_feature_handlers(app: Application) -> None:
    """Attach guest mode, bot2bot pipeline, streaming profiler, and auto-reply."""
    # Guest Mode: replies when bot is @mentioned in channels/groups
    app.add_handler(MessageHandler(filters.TEXT & filters.Entity("mention"), handle_guest_mention))

    # Bot-to-Bot pipeline: trusted bots only
    app.add_handler(MessageHandler(filters.VIA_BOT | filters.User(bot=True), handle_bot_pipeline))

    # Streaming channel profiler: /profile @channel
    app.add_handler(CommandHandler("profile", cmd_profile_stream))

    # Private chat auto-reply with dialogue memory
    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
        handle_auto_reply,
    ))
