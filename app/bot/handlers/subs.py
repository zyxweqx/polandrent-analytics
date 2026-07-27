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


