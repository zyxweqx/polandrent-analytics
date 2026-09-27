import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

_bot: Bot | None = None
def _get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


def _wait_for_telegram(retry_state):
    exc = retry_state.outcome.exception()
    if isinstance(exc, TelegramRetryAfter):
        return exc.retry_after
    return wait_exponential(multiplier=1, min=1, max=10)(retry_state)

@retry(
    stop=stop_after_attempt(3),
    wait=_wait_for_telegram,
    retry=retry_if_exception_type((TelegramNetworkError,TelegramRetryAfter))
)
async def send_tg_message(chat_id: int | str, text: str) -> None:

    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not set, skipping Telegram notification.")
        return
    await _get_bot().send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)
