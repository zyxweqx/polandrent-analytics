import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv

from app.bot.auth.middlewares import DbSessionMiddleware
from app.bot.handlers import base, subs
from app.core.database import async_session_maker
from app.core.logging_config import setup_logging

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await setup_bot_commands(bot)
    dp = Dispatcher()

    dp.include_router(base.router)
    dp.include_router(subs.router)
    dp.update.middleware(DbSessionMiddleware(session_maker=async_session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Restart the bot"),
        BotCommand(command="menu", description="Show main menu"),
    ]
    await bot.set_my_commands(commands)

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())