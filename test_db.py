import asyncio
from app.core.database import engine
from app.models.apartments import Base


async def init_models():
    print("Connecting to database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Success")

if __name__ == "__main__":
    asyncio.run(init_models())