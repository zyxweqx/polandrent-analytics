from aiogram import Bot

from app.core.config import settings

async def send_tg_message(text: str) -> None:

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        print("Token or chat id is missing")
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    try:
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        print("Successfully sent message")
    except Exception as e:
        print(f"Failed to send message: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio

    test_message = "test message"
    asyncio.run(send_tg_message(test_message))