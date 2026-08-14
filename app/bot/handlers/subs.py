from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.kbds.inline import get_cities_keyboard, get_delete_sub_keyboard
from app.bot.states.sub_states import SubFSM
from app.models.subscriptions import Subscription
from app.models.users import User

router = Router()

@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message, state: FSMContext) -> None:
    await state.set_state(SubFSM.city)

    await message.answer(
        "Great! Lets set up new apartment alert. \n\n Which city should we search in?",
        reply_markup = get_cities_keyboard()
    )

@router.callback_query(SubFSM.city, F.data.startswith("city_"))
async def cmd_city(callback: CallbackQuery, state: FSMContext) -> None:
    city = callback.data.split("_")[1]

    cities_map = {
        "poznan": "Poznań",
        "warszawa": "Warszawa",
        "krakow": "Kraków",
        "wroclaw": "Wrocław",
        "gdansk": "Gdańsk"
    }
    selected_city = cities_map.get(city, city.capitalize())

    await state.update_data(city=selected_city)

    await state.set_state(SubFSM.min_rooms)

    await callback.message.edit_text(
        f"City: {selected_city} \n"
        "What is the minimum number of rooms an apartment should have? (Write a number, for example: 1 or 2)",
        parse_mode="HTML"
    )

    await callback.answer()

@router.message(SubFSM.min_rooms)
async def cmd_min_rooms(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.isdigit():
        await message.answer("Please enter the number of rooms as a digit (e.g., 1, 2, or 3).")
        return

    rooms = int(message.text)

    if rooms < 1 or rooms > 10:
        await message.answer("This doesn't seem to be a typical apartment 😅 Please enter the actual number of rooms (from 1 to 10).")
        return

    await state.update_data(min_rooms=rooms)

    await state.set_state(SubFSM.min_rooms)

    await state.set_state(SubFSM.max_price)

    await message.answer(
        f"Minimum room number: {rooms} \n"
        "Now specify the maximum rental price including all fees (in zlotys).\n"
        "Just enter the number, for example: 3500",
        parse_mode="HTML"
    )

@router.message(SubFSM.max_price)
async def cmd_max_price(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text or not message.text.isdigit():
        await message.answer("Please enter the maximum price as a digit (e.g., 3500).")
        return

    max_price = float(message.text)

    if max_price < 500 or max_price > 50000:
        await message.answer("The amount looks suspicious 🤔. Please enter the actual maximum price in zlotys.")
        return


    user_query = select(User).where(User.telegram_id == message.from_user.id)
    user_result = await session.execute(user_query)
    db_user = user_result.scalar_one_or_none()

    if not db_user:
        await message.answer("Error: You are not registered in the database. Please send /start first.")
        await state.clear()
        return

    data = await state.get_data()
    city = data.get("city")
    min_rooms = int(data.get("min_rooms"))

    new_sub = Subscription(
        user_id=db_user.id,
        city=city,
        rooms_min=min_rooms,
        price_max=max_price
    )

    session.add(new_sub)
    await session.commit()

    await message.answer(
        f"✅ <b>Subscription successfully created!</b>\n\n"
        f"📍 City: <b>{city}</b>\n"
        f"🛏 Rooms (min.): <b>{min_rooms}</b>\n"
        f"💰 Price (max.): <b>{max_price} PLN</b>\n\n"
        f"As soon as a suitable apartment becomes available, I'll send it to you right away!",
        parse_mode="HTML"
    )

    await state.clear()

@router.message(F.text == "➕ New Subscription")
async def cmd_new_sub(message: Message, state: FSMContext) -> None:
    await state.clear()

    await state.set_state(SubFSM.city)

    await message.answer(
        "Great! Let's set up a new subscription. \n\n"
        "📍 <b>Step 1:</b> Choose a city from the list below:",
        reply_markup=get_cities_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text == "📋 My Subscriptions")
async def cmd_my_subscriptions(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()

    user_query = select(User).where(User.telegram_id == message.from_user.id)
    user_result = await session.execute(user_query)
    db_user = user_result.scalar_one_or_none()

    if not db_user:
        await message.answer("Error: You are not registered or have no subscriptions yet")
        return

    subs_query = select(Subscription).where(Subscription.user_id == db_user.id)
    subs_result = await session.execute(subs_query)
    subscriptions = subs_result.scalars().all()

    if not subscriptions:
        await message.answer("You don't have any subscriptions yet.")
        return

    await message.answer("Here are your active subscriptions:")

    for sub in subscriptions:
        text = (
            f"📍 City: <b>{sub.city}</b>\n"
            f"🛏 Rooms (min.): <b>{sub.rooms_min}</b>\n"
            f"💰 Price (max.): <b>{sub.price_max} PLN</b>\n"
        )
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_delete_sub_keyboard(sub.id)
        )

@router.callback_query(F.data.startswith("del_sub_"))
async def cmd_delete_subscription(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    sub_id = int(callback.data.split("_")[1])

    user_query = select(User).where(User.telegram_id == callback.from_user.id)
    user_result = await session.execute(user_query)
    db_user = user_result.scalar_one_or_none()
    if not db_user:
        await callback.answer("Error: You are not registered or have no subscriptions yet", show_alert=True)
        return

    delete_query = delete(Subscription).where(
        Subscription.id == sub_id,
        Subscription.user_id == db_user.id,
    )
    result = await session.execute(delete_query)
    await session.commit()
    if result.rowcount == 0:
        await callback.answer("Subscription not found or doesn't belong to you.", show_alert=True)
        return
    await callback.answer("Subscription successfully deleted!", show_alert=False)
    await callback.message.delete()