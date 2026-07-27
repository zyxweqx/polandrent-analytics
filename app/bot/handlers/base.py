from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select

from app.bot.kbds.reply import main_menu
from app.core.database import async_session_maker
from app.models.users import User

router = Router()

@router.message(CommandStart())
@router.message(Command("menu"))
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username

    async with async_session_maker() as session:
        query = select(User).where(User.telegram_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            new_user = User(telegram_id=user_id, username=username)
            session.add(new_user)
            await session.commit()
            await message.answer(
                "Welcome! You have been registered. 🎉\nUse the menu below to manage your apartment subscriptions.",
                reply_markup=main_menu
            )
        else:
            await message.answer(
                "Welcome back! 👋\nWhat would you like to do?",
                reply_markup=main_menu
            )