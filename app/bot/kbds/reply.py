from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ New Subscription"),
            KeyboardButton(text="📋 My Subscriptions")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an action..."
)