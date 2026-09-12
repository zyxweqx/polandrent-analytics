from fastapi import FastAPI

from app.api.apartments import router as apartments_router
from app.api.subscriptions import router as subscriptions_router
from app.api.user import router as user_router

app = FastAPI(
    title="PolandRent Analytics"
)

app.include_router(user_router)
app.include_router(subscriptions_router)
app.include_router(apartments_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}


