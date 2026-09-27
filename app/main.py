from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.apartments import router as apartments_router
from app.api.subscriptions import router as subscriptions_router
from app.api.user import router as user_router
from app.core.database import get_db
from app.core.logging_config import setup_logging

setup_logging()
app = FastAPI(
    title="PolandRent Analytics"
)

app.include_router(user_router)
app.include_router(subscriptions_router)
app.include_router(apartments_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}



