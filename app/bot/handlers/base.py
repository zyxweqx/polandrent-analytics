from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.users import User

router = Router()

@router.message(CommandStart())
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
            await message.answer("You have been registered")
        else:
            await message.answer("You are already registered")