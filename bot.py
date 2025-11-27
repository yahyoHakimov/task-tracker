import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.connection import init_db
from handlers import commands_router, messages_router, callbacks_router
from middleware import LoggingMiddleware

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("=" * 60)
    logger.info("Starting Task Tracker Bot...")
    logger.info("=" * 60)
    
    try:
        logger.info("Initializing database...")
        await init_db()
        logger.info("✓ Database initialized successfully!")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        return

    try:
        logger.info("Creating bot instance...")
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        logger.info("Creating dispatcher with FSM storage...")
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        logger.info("Setting up middleware...")
        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())

        logger.info("Registering handlers...")
        dp.include_router(commands_router)
        dp.include_router(messages_router)
        dp.include_router(callbacks_router)

        logger.info("=" * 60)
        logger.info("✓ Bot started successfully!")
        logger.info("✓ Waiting for messages...")
        logger.info("✓ Press Ctrl+C to stop the bot")
        logger.info("=" * 60)
        
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"✗ Error during bot execution: {e}", exc_info=True)
    finally:
        logger.info("Closing bot session...")
        await bot.session.close()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Bot stopped by user (Ctrl+C)")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}", exc_info=True)