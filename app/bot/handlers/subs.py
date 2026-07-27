from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot.kbds.inline import get_cities_keyboard
from app.bot.states.sub_states import SubFSM

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
async def min_rooms(message: Message, state: FSMContext) -> None:
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


