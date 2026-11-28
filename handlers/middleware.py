import logging 

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class ErrorLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict
    ):

        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(
                f"Unhandled error: {type(e).__name__}: {e}",
                exc_info=True
            )