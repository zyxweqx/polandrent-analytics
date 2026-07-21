from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.subscriptions import router as subscriptions_router
app = FastAPI(
    title="PolandRent Analytics"
)

app.include_router(user_router)
app.include_router(subscriptions_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}


