from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_cities_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Poznań", callback_data="city_poznan")],
        [InlineKeyboardButton(text="Warszawa", callback_data="city_warszawa")],
        [InlineKeyboardButton(text="Kraków", callback_data="city_krakow")],
        [InlineKeyboardButton(text="Wrocław", callback_data="city_wroclaw")],
        [InlineKeyboardButton(text="Gdańsk", callback_data="city_gdansk")]
    ])
    return keyboard

def get_delete_sub_keyboard(sub_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Delete Subscription",
                    callback_data=f"del_sub_{sub_id}"
                )
            ]
        ]
    )