from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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