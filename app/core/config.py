from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    DATABASE_URL: str
    API_KEY: str
    API_URL: str = "http://web:8000/apartments/"

settings = Settings()