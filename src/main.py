import asyncio
import nest_asyncio
import logging
import logging.handlers
from signal import SIGINT, SIGTERM

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TELEGRAM_TOKEN, CHECK_INTERVAL
from handlers import (
    start,
    help_command,
    handle_message,
    remove_url,
    clear_seen,
    list_urls,
    button_callback,
    stop_bot,
    resume_bot,
    unknown_command,
    error_handler,
)
from tasks import check_for_new_ads

log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler = logging.handlers.TimedRotatingFileHandler("bot.log", when="midnight", interval=1, backupCount=2)
file_handler.setFormatter(log_formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(console_handler)

async def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("remove", remove_url))
    app.add_handler(CommandHandler("list", list_urls))
    app.add_handler(CommandHandler("clear_seen", clear_seen))
    app.add_handler(CommandHandler("stop", stop_bot))
    app.add_handler(CommandHandler("resume", resume_bot))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    app.add_handler(CallbackQueryHandler(button_callback))

    app.add_error_handler(error_handler)

    asyncio.create_task(check_for_new_ads(app, CHECK_INTERVAL))

    logger.info("Bot running...")
    await app.run_polling(close_loop=False, stop_signals=[SIGINT, SIGTERM])

if __name__ == "__main__":
    try:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped manually.")