import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv

from app.bot.auth.middlewares import DbSessionMiddleware
from app.core.database import async_session_maker
from app.bot.handlers import base
from app.bot.handlers import subs

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
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())