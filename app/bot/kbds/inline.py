from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_cities_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Poznań", callback_data="city_poznan")],
        [InlineKeyboardButton(text="Warszawa", callback_data="city_warszawa")],
        [InlineKeyboardButton(text="Kraków", callback_data="city_krakow")],
        [InlineKeyboardButton(text="Wrocław", callback_data="city_wroclaw")],
        [InlineKeyboardButton(text="Gdańsk", callback_data="city_gdansk")]
    ])
    return keyboard