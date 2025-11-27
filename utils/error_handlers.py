import logging
from functools import wraps
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


def handle_errors(func):
    """Decorator to handle errors in handlers"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            
            # Try to send error message to user
            for arg in args:
                if isinstance(arg, Message):
                    await arg.answer(
                        "❌ An unexpected error occurred. Please try again or contact support."
                    )
                    break
                elif isinstance(arg, CallbackQuery):
                    await arg.answer(
                        "❌ An error occurred. Please try again.",
                        show_alert=True
                    )
                    break
            
            # Re-raise to let aiogram handle it
            raise
    
    return wrapper