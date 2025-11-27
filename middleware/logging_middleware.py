from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from typing import Callable, Dict, Any, Awaitable
import logging
import time

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware to log all incoming updates and track response time"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Get update info
        update: Update = data.get("event_update")
        
        if update and update.message:
            user = update.message.from_user
            message_text = update.message.text or "[non-text message]"
            logger.info(
                f"Message from user {user.id} (@{user.username}): {message_text[:50]}"
            )
        elif update and update.callback_query:
            user = update.callback_query.from_user
            callback_data = update.callback_query.data
            logger.info(
                f"Callback from user {user.id} (@{user.username}): {callback_data}"
            )
        
        # Track response time
        start_time = time.time()
        
        try:
            result = await handler(event, data)
            
            # Log response time
            duration = (time.time() - start_time) * 1000  # Convert to ms
            logger.debug(f"Handler executed in {duration:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in handler: {e}", exc_info=True)
            raise


class UserTrackingMiddleware(BaseMiddleware):
    """Middleware to track user activity"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        update: Update = data.get("event_update")
        
        # You could update last_seen timestamp in database here
        # For now, we'll just pass through
        
        return await handler(event, data)